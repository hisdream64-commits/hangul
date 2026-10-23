# -*- coding: utf-8 -*-
# make_audio.py — tools/used.json 의 말들을 성우 음성 mp3 로 만든다.
#
#   python tools/make_audio.py              # 빠진 것만 받고, 안 쓰는 것은 지웁니다
#   python tools/make_audio.py --dry-run    # 무엇을 받고 무엇을 지울지만 보여 줍니다
#
# 목소리는 기초반과 같은 ko-KR-SunHiNeural(아나운서), 빠르기 -10% 입니다.
# edge-tts 는 마이크로소프트 엣지의 읽어 주기 기능을 쓰는 무료 경로입니다.
# 계약이 필요하면 기초반 저장소의 tools/regen_audio_azure.py 와 같은 방식으로
# Azure Speech 에서 같은 목소리를 받아 쓸 수 있습니다.
#
# 파일 이름은 말 내용의 해시입니다(v<md5 앞 10자>.mp3).
# 그래서 문장을 하나 고치면 그 한 조각만 새로 받습니다. 다시 돌려도 결과가 같습니다.
#
# 준비물:  pip install edge-tts

import asyncio
import hashlib
import io
import json
import os
import re
import sys

import edge_tts

VOICE = "ko-KR-SunHiNeural"   # 기초반과 같은 목소리
RATE = "-10%"                 # 어르신이 따라오시기 좋은 차분한 빠르기
WORKERS = 6                   # 동시에 받는 개수. 너무 올리면 거절당합니다

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
AUDIO_DIR = os.path.join(ROOT, "audio")
USED = os.path.join(HERE, "used.json")
MAP = os.path.join(HERE, "audio_map.json")
DRY = "--dry-run" in sys.argv

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")   # 윈도우 명령창 한글 깨짐 방지
except Exception:
    pass


def key(t):
    """앱의 sayKey() 와 같은 규칙으로 다듬는다."""
    t = re.sub(r"<br\s*/?>", " ", t, flags=re.I)
    t = re.sub(r"<[^>]+>", "", t)
    t = re.sub(r"\s+", " ", t).strip()
    return re.sub(r"[!?.]+$", "", t).strip()


def name_of(text):
    return "v" + hashlib.md5(text.encode("utf-8")).hexdigest()[:10] + ".mp3"


used = [key(t) for t in json.load(io.open(USED, encoding="utf-8"))]
used = [t for t in dict.fromkeys(used) if t]
os.makedirs(AUDIO_DIR, exist_ok=True)

want = {t: name_of(t) for t in used}
have = set(f for f in os.listdir(AUDIO_DIR) if f.endswith(".mp3"))
missing = [t for t in used if want[t] not in have or os.path.getsize(os.path.join(AUDIO_DIR, want[t])) < 400]
extra = sorted(have - set(want.values()))

print("읽는 말 %d개 · 받아야 할 것 %d개 · 안 쓰는 파일 %d개" % (len(used), len(missing), len(extra)))
if DRY:
    for t in missing[:10]:
        print("  받을 것:", t[:40])
    for f in extra[:10]:
        print("  지울 것:", f)
    sys.exit(0)

failed = []


async def fetch_all(texts):
    sem = asyncio.Semaphore(WORKERS)
    done = [0]

    async def one(t):
        dest = os.path.join(AUDIO_DIR, want[t])
        async with sem:
            for attempt in range(4):
                try:
                    buf = bytearray()
                    async for ch in edge_tts.Communicate(t, VOICE, rate=RATE).stream():
                        if ch["type"] == "audio":
                            buf += ch["data"]
                    if len(buf) < 400:
                        raise RuntimeError("소리가 너무 짧습니다")
                    open(dest, "wb").write(bytes(buf))
                    done[0] += 1
                    if done[0] % 50 == 0:
                        print("  %d / %d" % (done[0], len(texts)), flush=True)
                    return
                except Exception as e:
                    if attempt == 3:
                        failed.append((t, str(e)))
                    else:
                        await asyncio.sleep(1.5 * (attempt + 1))

    await asyncio.gather(*[one(t) for t in texts])


if missing:
    print("edge-tts 로 받아 옵니다… (목소리 %s, 빠르기 %s)" % (VOICE, RATE), flush=True)
    asyncio.run(fetch_all(missing))

for f in extra:
    os.remove(os.path.join(AUDIO_DIR, f))

amap = {}
for t in used:
    if os.path.exists(os.path.join(AUDIO_DIR, want[t])):
        amap[t] = "audio/" + want[t]
json.dump(amap, io.open(MAP, "w", encoding="utf-8"), ensure_ascii=False)

total = sum(os.path.getsize(os.path.join(AUDIO_DIR, f)) for f in os.listdir(AUDIO_DIR) if f.endswith(".mp3"))
print("소리 %d개 · 지운 것 %d개 · 모두 %.1f MB" % (len(amap), len(extra), total / 1024 / 1024))
if failed:
    print("받지 못한 말 %d개 (다시 돌리면 이어서 받습니다):" % len(failed))
    for t, e in failed[:5]:
        print("  ", t[:40], "|", e)
    sys.exit(1)
print("다음: python tools/inject_map.py")
