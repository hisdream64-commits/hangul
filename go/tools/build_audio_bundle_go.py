# build_audio_bundle_go.py — go/audio/v*.mp3 를 go/audio/audio.bin 한 덩어리로 묶는다.
#
#   python go/tools/build_audio_bundle_go.py
#
# 왜 묶나: 브라우저 캐시는 파일 하나마다 약 1.25KB의 관리 정보를 덧붙인다.
# 소리 375개면 데이터 8.0MB가 실제로는 8.5MB를 차지하고, 받을 때 요청도 375번이다.
# 한 덩어리로 묶으면 요청 1번, 덧붙는 관리 정보도 1번치로 줄어든다.
#
# 원본 mp3를 그대로 이어 붙이기만 한다. 다시 압축하지 않으므로 음질 손실이 없다.
# 재생은 blob.slice(offset, offset+len, 'audio/mpeg') 으로 잘라 쓴다.
#
# 기초반(tools/build_audio_bundle.py)과 다른 점
#   기초반은 파일 이름이 a0.mp3 … aN.mp3 로 이어져 있어 길이 배열만 있으면 된다.
#   고급반은 이름이 말 내용의 해시(v4d4c0bb737.mp3)라 순서가 없다.
#   그래서 이름 목록과 길이 목록을 짝으로 싣고, 앱이 그 둘로 자리표를 만든다.
#
# 하는 일
#   1) go/index.html 의 window.AUDIO 에 적힌 소리만 순서대로 이어 go/audio/audio.bin 생성
#   2) go/index.html 끝에 <script>window.AUDIO_BIN = {...}</script> 삽입(있으면 교체)
#   3) 잘라낸 조각이 원본과 바이트 단위로 같은지 전수 확인

import hashlib
import json
import os
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")   # 윈도우 명령창에서 한글이 깨지지 않게
except Exception:
    pass

GO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUDIO_DIR = os.path.join(GO, "audio")
BUNDLE = os.path.join(AUDIO_DIR, "audio.bin")
IDX = os.path.join(GO, "index.html")
SW = os.path.join(GO, "sw.js")

BIN_RE = re.compile(r"\n?<script>window\.AUDIO_BIN = \{.*?\};</script>\n?", re.S)


def main():
    html = open(IDX, encoding="utf-8").read()

    m = re.search(r'window\.AUDIO = (\{.*?\});</script>', html, re.S)
    if not m:
        sys.exit("go/index.html 에서 window.AUDIO 를 찾지 못했습니다.")
    amap = json.loads(m.group(1))

    # 같은 소리를 여러 말이 함께 쓰므로 중복을 걷어 내고, 이름순으로 고정한다.
    # (순서를 고정해야 소리가 안 바뀌었을 때 묶음도 똑같이 나온다)
    paths = sorted(set(amap.values()))
    if not paths:
        sys.exit("window.AUDIO 가 비어 있습니다.")

    bad = [p for p in paths if not p.startswith("audio/")]
    if bad:
        sys.exit(f"audio/ 밖을 가리키는 소리가 있습니다: {bad[:5]}")

    missing = [p for p in paths if not os.path.exists(os.path.join(GO, p))]
    if missing:
        sys.exit(f"소리 파일 {len(missing)}개가 없습니다: {missing[:5]}")

    print(f"소리 {len(paths)}개를 묶습니다…")

    names, lens, raws = [], [], []
    for p in paths:
        raw = open(os.path.join(GO, p), "rb").read()
        if not raw:
            sys.exit(f"{p} 가 비어 있습니다.")
        raws.append(raw)
        lens.append(len(raw))
        names.append(p[len("audio/"):])          # 'audio/' 는 앱이 다시 붙인다

    with open(BUNDLE, "wb") as f:
        for raw in raws:
            f.write(raw)

    total = sum(lens)
    if os.path.getsize(BUNDLE) != total:
        sys.exit("묶음 크기가 맞지 않습니다. 중단합니다.")

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
             + json.dumps({"file": "audio/audio.bin", "total": total,
                           "names": names, "lens": lens},
                          separators=(",", ":"), ensure_ascii=False)
             + ";</script>\n")

    html = BIN_RE.sub("\n", html)
    if not html.endswith("\n"):
        html += "\n"
    html += block
    open(IDX, "w", encoding="utf-8", newline="").write(html)

    before = total + len(paths) * 1280          # 파일마다 붙는 관리 정보(기초반에서 실측한 약 1.25KB)
    print(f"go/audio/audio.bin  {total/1048576:.2f} MB  (자리표 {len(block)/1024:.1f} KB)")
    print(f"캐시 차지 용량  {before/1048576:.2f} MB → 약 {(total+1280)/1048576:.2f} MB")
    print(f"받을 때 요청 수  {len(paths)}번 → 1번")

    stamp_sw()


def stamp_sw():
    """go/sw.js 의 판 번호를 go/index.html 내용에서 뽑아 박는다.

    화면이 바뀌면 판 번호가 바뀌어 저장해 둔 옛 화면이 밀려난다.
    소리 묶음 칸('hangul3-audio')은 판이 바뀌어도 그대로 두므로 다시 받지 않는다.
    """
    if not os.path.exists(SW):
        print("go/sw.js 가 없어 판 번호 박기는 건너뜁니다.")
        return
    digest = hashlib.md5(open(IDX, "rb").read()).hexdigest()[:10]
    src = open(SW, encoding="utf-8").read()
    new = re.sub(r"hangul3-shell-[0-9a-f]{10}", "hangul3-shell-" + digest, src)
    new = re.sub(r"빌드 때 [0-9a-f]{10} 이", "빌드 때 " + digest + " 이", new)
    if new != src:
        open(SW, "w", encoding="utf-8", newline="").write(new)
    print(f"go/sw.js 판 번호 -> hangul3-shell-{digest}")


if __name__ == "__main__":
    main()
