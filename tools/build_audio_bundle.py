# build_audio_bundle.py — audio/aN.mp3 1,226개를 audio/audio.bin 한 덩어리로 묶는다.
#
# 왜 묶나: 브라우저 캐시는 파일 하나마다 약 1.25KB의 관리 정보를 덧붙인다.
# 10.18MB 데이터가 실제로는 12.43MB를 차지해, 저장공간이 빠듯한 기기에서 일부만 저장된다.
# 한 덩어리로 묶으면 덧붙는 관리 정보가 1번치로 줄어 10.2MB에 들어간다.
#
# 원본 mp3를 그대로 이어 붙이기만 한다. 다시 압축하지 않으므로 음질 손실이 없다.
# 재생은 blob.slice(offset, offset+len, 'audio/mpeg') 으로 잘라 쓴다.
#
#   python tools/build_audio_bundle.py
#
# 하는 일
#   1) audio/a0.mp3 … a1225.mp3 를 순서대로 이어 audio/audio.bin 생성
#   2) index.html 끝에 <script>window.AUDIO_BIN = {...}</script> 삽입(있으면 교체)
#   3) 잘라낸 조각이 원본과 바이트 단위로 같은지 전수 확인

import json
import os
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")   # 윈도우 명령창에서 한글이 깨지지 않게
except Exception:
    pass

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUDIO_DIR = os.path.join(HERE, "audio")
BUNDLE = os.path.join(AUDIO_DIR, "audio.bin")
IDX = os.path.join(HERE, "index.html")

BIN_RE = re.compile(r"\n?<script>window\.AUDIO_BIN = \{.*?\};</script>\n?", re.S)


def main():
    html = open(IDX, encoding="utf-8").read()

    m = re.search(r'window\.AUDIO = (\{.*?\});</script>', html, re.S)
    if not m:
        sys.exit("index.html 에서 window.AUDIO 를 찾지 못했습니다.")
    amap = json.loads(m.group(1))

    paths = sorted(set(amap.values()),
                   key=lambda p: int(re.search(r"a(\d+)\.mp3$", p).group(1)))
    nums = [int(re.search(r"a(\d+)\.mp3$", p).group(1)) for p in paths]
    if nums != list(range(len(nums))):
        sys.exit("a0..aN 번호가 이어지지 않습니다. 묶음 색인이 길이 배열이라 번호가 연속이어야 합니다.")

    missing = [p for p in paths if not os.path.exists(os.path.join(HERE, p))]
    if missing:
        sys.exit(f"소리 파일 {len(missing)}개가 없습니다: {missing[:5]}")

    print(f"소리 {len(paths)}개를 묶습니다…")

    lens, raws = [], []
    for p in paths:
        raw = open(os.path.join(HERE, p), "rb").read()
        if not raw:
            sys.exit(f"{p} 가 비어 있습니다.")
        raws.append(raw)
        lens.append(len(raw))

    with open(BUNDLE, "wb") as f:
        for raw in raws:
            f.write(raw)

    total = sum(lens)
    assert os.path.getsize(BUNDLE) == total

    # 전수 확인: 묶음에서 잘라낸 조각이 원본과 완전히 같은가
    with open(BUNDLE, "rb") as f:
        off = 0
        for p, raw, n in zip(paths, raws, lens):
            f.seek(off)
            if f.read(n) != raw:
                sys.exit(f"{p} 가 묶음과 다릅니다. 중단합니다.")
            off += n
    print(f"바이트 동일성 확인 완료 ({len(paths)}개)")

    block = ("<script>window.AUDIO_BIN = "
             + json.dumps({"file": "audio/audio.bin", "total": total, "lens": lens},
                          separators=(",", ":"))
             + ";</script>\n")

    html = BIN_RE.sub("\n", html)
    if not html.endswith("\n"):
        html += "\n"
    html += block
    open(IDX, "w", encoding="utf-8", newline="").write(html)

    before = total + len(paths) * 1280          # 파일마다 붙는 관리 정보(실측 약 1.25KB)
    print(f"audio/audio.bin  {total/1048576:.2f} MB  (색인 {len(block)/1024:.1f} KB)")
    print(f"캐시 차지 용량  {before/1048576:.2f} MB → 약 {(total+1280)/1048576:.2f} MB")
    print(f"받을 때 요청 수  {len(paths)}번 → 1번")


if __name__ == "__main__":
    main()
