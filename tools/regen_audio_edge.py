# regen_audio_edge.py — edge-tts 로 소리 1,226개를 다시 만든다. (무료, 계정 없음)
#
# 지금 배포된 소리가 이 방식으로 만들어졌습니다.
#
#   pip install edge-tts imageio-ffmpeg
#   python tools/regen_audio_edge.py --sample            # 먼저 시험 음성부터
#   python tools/regen_audio_edge.py --all --yes         # 전체 (지금과 같은 32kbps)
#   python tools/regen_audio_edge.py --all --raw --yes   # 재압축 없이 (15.1MB, 음질↑)
#
# 뒤에 반드시 이어서:
#   python tools/build_audio_bundle.py
#   python tools/stamp_sw.py
#
# ⚠️ edge-tts 는 비공식 경로입니다. 공짜지만 예고 없이 막힐 수 있습니다.
#    정식 경로가 필요하면 tools/regen_audio_azure.py 를 쓰세요.

import argparse
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
import regen_audio_azure as az                  # noqa: E402  (shrink / 비교 페이지를 빌려 쓴다)

import edge_tts                                 # noqa: E402

VOICE = "ko-KR-SunHiNeural"                     # 지금 쓰는 목소리
HERE = clips.HERE
IDX = clips.IDX
AUDIO_DIR = os.path.join(HERE, "audio")


async def synth(text, rate, sem):
    async with sem:
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


async def fetch(items, workers=6):
    """items: [(이름, 문장, 속도)] -> {이름: 받은 mp3 바이트 또는 None}"""
    sem = asyncio.Semaphore(workers)
    done = [0]

    async def one(it):
        name, text, rate = it
        raw = await synth(text, rate, sem)
        done[0] += 1
        if done[0] % 50 == 0 or done[0] == len(items):
            print(f"  {done[0]:,}/{len(items):,}", end="\r", flush=True)
        return name, raw

    out = dict(await asyncio.gather(*[one(it) for it in items]))
    print()
    return out


def settings(raw):
    # edge-tts 는 24kHz·48kbps mp3 를 줍니다.
    # --raw 면 그대로 쓰고(재압축 손실 0), 아니면 지금처럼 32kbps 로 다시 담습니다.
    return (None, None, "48kbps · 받은 그대로") if raw else ("32k", "24000", "32kbps · 지금과 같게")


def do_sample(raw):
    c = clips.build()
    bitrate, rate_hz, note = settings(raw)
    label = "raw48" if raw else "re32"
    d = os.path.join(HERE, "tools", "samples", label)
    os.makedirs(d, exist_ok=True)
    items = [(k, c[k][0], c[k][1]) for k in clips.SAMPLE_KEYS]
    print(f"[{label}] {note} — {len(items)}조각")
    got = asyncio.run(fetch(items))
    miss = [k for k, v in got.items() if not v]
    if miss:
        sys.exit(f"받지 못한 조각: {miss}\nedge-tts 가 막혔을 수 있습니다. 잠시 뒤 다시 해 보세요.")
    for k, v in got.items():
        open(os.path.join(d, k + ".mp3"), "wb").write(az.shrink(v, bitrate, rate_hz))
    print(f"만들었습니다: tools/samples/{label}/")
    print("나란히 견주려면:  python tools/sample_edge.py")


def do_all(raw, yes):
    c = clips.build()
    bitrate, rate_hz, note = settings(raw)
    print(f"목소리 {VOICE}")
    print(f"설정  {note}")
    print(f"조각  {len(c):,}개 · {sum(len(t) for t, _ in c.values()):,}자")
    if not yes:
        sys.exit("\n정말 바꾸시려면 --yes 를 붙여 주세요. 지금 audio/ 는 그대로 둡니다.")

    tmp = os.path.join(HERE, "tools", "_newaudio")
    shutil.rmtree(tmp, ignore_errors=True)
    os.makedirs(tmp)

    keys = list(c)
    print("\n만드는 중… (15~20분)")
    got = asyncio.run(fetch([(k, c[k][0], c[k][1]) for k in keys]))
    failed = [k for k in keys if not got.get(k)]
    if failed:
        shutil.rmtree(tmp, ignore_errors=True)
        sys.exit(f"{len(failed)}개를 만들지 못했습니다: {failed[:10]}\n"
                 f"audio/ 는 건드리지 않았습니다.")

    data = {k: az.shrink(got[k], bitrate, rate_hz) for k in keys}
    total = sum(len(v) for v in data.values())

    # 말 속도가 지켜졌는지 확인한다. 같은 bitrate 면 파일 크기가 곧 길이입니다.
    if bitrate:
        old_map = json.loads(re.search(r'window\.AUDIO = (\{.*?\});</script>',
                                       open(IDX, encoding="utf-8").read(), re.S).group(1))
        pairs = [(os.path.getsize(os.path.join(HERE, old_map[k])), len(data[k]))
                 for k in keys
                 if k in old_map and os.path.exists(os.path.join(HERE, old_map[k]))]
        if pairs:
            was, now = sum(a for a, _ in pairs), sum(b for _, b in pairs)
            diff = (now - was) / was * 100
            print(f"길이 견주기   예전 {was/1048576:.2f}MB → 지금 {now/1048576:.2f}MB ({diff:+.1f}%)")
            if diff < -15:
                shutil.rmtree(tmp, ignore_errors=True)
                sys.exit(f"\n중단했습니다. 새 소리가 {-diff:.0f}% 짧습니다. "
                         f"말 속도 지정이 무시된 듯합니다.\naudio/ 는 건드리지 않았습니다.")

    amap = {}
    for i, k in enumerate(keys):
        name = f"a{i}.mp3"
        open(os.path.join(tmp, name), "wb").write(data[k])
        amap[k] = "audio/" + name
    print(f"\n{len(amap):,}개 · {total/1048576:.2f}MB")

    old = os.path.join(HERE, "tools", "_oldaudio")
    shutil.rmtree(old, ignore_errors=True)
    os.rename(AUDIO_DIR, old)
    os.rename(tmp, AUDIO_DIR)
    shutil.rmtree(old, ignore_errors=True)

    html = open(IDX, encoding="utf-8", newline="").read()
    block = "<script>window.AUDIO = " + json.dumps(amap, ensure_ascii=False) + ";</script>"
    html = re.sub(r"<script>window\.AUDIO = \{.*?\};</script>", block, html, flags=re.S)
    html = re.sub(r"\n?<script>window\.AUDIO_BIN = \{.*?\};</script>\n?", "\n", html, flags=re.S)
    open(IDX, "w", encoding="utf-8", newline="").write(html)

    print("\naudio/ 와 index.html 을 갱신했습니다. 이어서:")
    print("  python tools/build_audio_bundle.py")
    print("  python tools/stamp_sw.py")


def main():
    ap = argparse.ArgumentParser(description="edge-tts 로 소리를 다시 만든다 (무료)")
    ap.add_argument("--sample", action="store_true", help="시험 음성만 (권장 첫 단계)")
    ap.add_argument("--all", action="store_true", help="1,226개 전부 다시 만들기")
    ap.add_argument("--raw", action="store_true",
                    help="다시 담지 않고 받은 그대로 (48kbps, 15.1MB, 재압축 손실 0)")
    ap.add_argument("--yes", action="store_true", help="--all 을 정말 실행")
    a = ap.parse_args()
    if a.sample:
        do_sample(a.raw)
    elif a.all:
        do_all(a.raw, a.yes)
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
