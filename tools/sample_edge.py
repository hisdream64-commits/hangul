# sample_edge.py — edge-tts 로 시험 음성을 만들어 지금 소리와 견준다. (계정·요금 없음)
#
#   python tools/sample_edge.py
#
# 왜 만드나: 지금 소리는 edge-tts 가 준 48kbps mp3 를 32kbps 로 **다시 담은** 것입니다.
# mp3 를 다시 담으면 품질이 떨어집니다. 받은 그대로 쓰면 재압축 손실이 없어집니다.
# 용량은 늘어나므로, 그만한 값을 하는지 귀로 확인하려는 것입니다.
#
# 만드는 것
#   현재       지금 배포된 소리 (32kbps, 재압축됨)
#   raw48      edge-tts 가 준 그대로 (48kbps, 재압축 없음)
#   re40       40kbps 로 담기 (중간 절충)

import asyncio
import json
import os
import re
import shutil
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")   # 윈도우 명령창에서 한글이 깨지지 않게
except Exception:
    pass

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import clips                                    # noqa: E402
import regen_audio_azure as az                  # noqa: E402  (비교 페이지 만드는 함수를 빌려 쓴다)

import edge_tts                                 # noqa: E402

VOICE = "ko-KR-SunHiNeural"                     # 지금 쓰는 목소리 그대로
HERE = clips.HERE
OUT = os.path.join(HERE, "tools", "samples")

# 이름: (다시 담을 bitrate, 표본율, 설명).  bitrate 가 None 이면 받은 그대로.
VARIANTS = {
    "raw48": (None, None, "48kbps · 받은 그대로, 재압축 손실 없음"),
    "re40": ("40k", "24000", "40kbps · 중간 절충"),
}


async def synth(text, rate):
    for attempt in range(3):
        try:
            buf = b""
            async for ch in edge_tts.Communicate(text, VOICE, rate=rate).stream():
                if ch["type"] == "audio":
                    buf += ch["data"]
            if buf:
                return buf
        except Exception:
            await asyncio.sleep(1.5 * (attempt + 1))
    return None


async def main():
    c = clips.build()
    keys = clips.SAMPLE_KEYS
    os.makedirs(OUT, exist_ok=True)

    print(f"edge-tts 로 {len(keys)}조각을 받아 옵니다… (목소리 {VOICE})")
    sem = asyncio.Semaphore(4)

    async def one(k):
        async with sem:
            return k, await synth(c[k][0], c[k][1])

    raws = dict(await asyncio.gather(*[one(k) for k in keys]))
    missing = [k for k, v in raws.items() if not v]
    if missing:
        sys.exit(f"받지 못한 조각이 있습니다: {missing}\n"
                 f"edge-tts 는 비공식 경로라 가끔 막힙니다. 잠시 뒤 다시 해 보세요.")

    sizes = {}
    for label, (bitrate, rate_hz, note) in VARIANTS.items():
        d = os.path.join(OUT, label)
        os.makedirs(d, exist_ok=True)
        total = 0
        for k in keys:
            data = az.shrink(raws[k], bitrate, rate_hz)
            open(os.path.join(d, k + ".mp3"), "wb").write(data)
            total += len(data)
        sizes[label] = (total, note)

    # 지금 배포된 소리도 나란히 듣도록 복사
    now = os.path.join(OUT, "현재")
    os.makedirs(now, exist_ok=True)
    A = json.loads(re.search(r'window\.AUDIO = (\{.*?\});</script>',
                             open(clips.IDX, encoding="utf-8").read(), re.S).group(1))
    cur = 0
    for k in keys:
        src = os.path.join(HERE, A[k])
        shutil.copy(src, os.path.join(now, k + ".mp3"))
        cur += os.path.getsize(src)

    az._write_compare_page(["현재"] + list(VARIANTS), c)

    # 표본 12조각은 긴 문장이 섞여 평균보다 깁니다. 개수로 곱하면 과대평가되므로,
    # "지금 소리 대비 몇 배인가"를 재서 실제 전체 용량(10.18MB)에 곱합니다.
    now_total = sum(os.path.getsize(os.path.join(HERE, p)) for p in set(A.values()))
    print(f"\n전체 용량 (지금 {now_total / 1048576:.2f}MB 기준으로 환산)")
    print(f"  {'현재':8} {now_total / 1048576:5.1f}MB   32kbps · 지금 배포된 것")
    for label, (total, note) in sizes.items():
        print(f"  {label:8} {total / cur * now_total / 1048576:5.1f}MB   "
              f"(표본 {total / cur:.2f}배)  {note}")
    print(f"\n들어 보세요:  tools/samples/비교.html")


asyncio.run(main())
