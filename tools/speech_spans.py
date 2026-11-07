# speech_spans.py — 자음·모음 소리 녹음에서 "말소리가 있는 구간"을 재어 index.html 에 적는다.
#
#   python tools/speech_spans.py
#
# 왜: 녹음 앞뒤에 무음이 0.3초·1.1초씩 붙어 있어, 기초 학습 3단계 「천천히 합쳐 듣기」의
# 1·2번(「드」·「아」)을 이어 틀어도 사이가 1초쯤 빕니다. 2026-11-07 사용자 결정으로 1·2번을
# 붙여 읽게 하면서, 앱은 이 구간만 틉니다. 녹음 파일은 그대로이고 자르거나 고치지 않습니다.
# 틀기 시작하는 자리(currentTime)와 다음으로 넘어가는 자리만 정합니다.
#
# 자음·모음 소리(s_그…s_흐, s_아…s_이)를 다시 녹음했다면 이것을 다시 돌리고 stamp_sw.py.
# (tools/pc_record.py 가 녹음 뒤에 알아서 돌립니다)

import json
import os
import re
import subprocess
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import imageio_ffmpeg

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IDX = os.path.join(HERE, "index.html")
FF = imageio_ffmpeg.get_ffmpeg_exe()

# 3단계에서 쓰는 소리: 자음 소리(자음+ㅡ, ㅇ 은 소리 없음)와 모음 소리
CONS = "그 느 드 르 므 브 스 즈 츠 크 트 프 흐".split()
VOWS = "아 야 어 여 오 요 우 유 으 이".split()
PAD_START, PAD_END = 0.02, 0.04     # 말소리 앞뒤로 남겨 둘 여유(초). 첫소리·끝소리가 잘리지 않게
NOISE = "-40dB"


def span(path):
    r = subprocess.run([FF, "-hide_banner", "-i", path, "-af",
                        f"silencedetect=noise={NOISE}:d=0.05", "-f", "null", "-"],
                       capture_output=True, text=True, encoding="utf-8", errors="replace").stderr
    dur = float(re.search(r"Duration: (\d+):(\d+):([\d.]+)", r).group(3))
    starts = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", r)]
    ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", r)]
    s = ends[0] if starts and starts[0] == 0 and ends else 0.0
    tail = [x for x in starts if x > s]
    e = tail[-1] if tail else dur
    return [round(max(0.0, s - PAD_START), 3), round(min(dur, e + PAD_END), 3)]


def main():
    html = open(IDX, encoding="utf-8", newline="").read()
    amap = json.loads(re.search(r'window\.AUDIO = (\{.*?\});</script>', html, re.S).group(1))
    out = {}
    for ch in CONS + VOWS:
        k = "s_" + ch
        if k not in amap:
            sys.exit(f"{k} 녹음이 없습니다.")
        out[k] = span(os.path.join(HERE, amap[k]))
        a, b = out[k]
        if not (0 <= a < b) or b - a < 0.1:
            sys.exit(f"{k} 의 말소리 구간이 이상합니다: {out[k]}")
    block = "<script>window.SPEECH_SPAN = " + json.dumps(out, ensure_ascii=False) + ";</script>"
    if "window.SPEECH_SPAN = " in html:
        html = re.sub(r"<script>window\.SPEECH_SPAN = \{.*?\};</script>", block, html, flags=re.S)
    else:
        # 화면 안내 말(UI_SAY) 바로 앞에 둔다
        i = html.index("<script>window.UI_SAY = ")
        html = html[:i] + block + "\n" + html[i:]
    open(IDX, "w", encoding="utf-8", newline="").write(html)
    print(f"말소리 구간 {len(out)}개를 index.html 에 적었습니다. 예) s_드 {out['s_드']} · s_아 {out['s_아']}")
    print("이어서:  python tools/stamp_sw.py")


if __name__ == "__main__":
    main()
