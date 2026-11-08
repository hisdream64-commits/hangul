# make_icons.py — 한글뚝딱(초급) 홈 화면 아이콘을 만든다.
#
#   python tools/make_icons.py
#
# 만드는 것 (모두 저장소 맨 위에)
#   icon-180.png           아이폰 홈 화면 (index.html 의 apple-touch-icon)
#   icon-192.png           안드로이드
#   icon-512.png           설치용 큰 그림
#   icon-512-maskable.png  안드로이드가 동그랗게 잘라 쓰는 그림(가장자리 여백 넉넉히)
#
# 2026-11-07 사용자(진민주님) 결정으로 글자를 「한글」 → 「뚝딱」. 색·여백은 그 전 아이콘 그대로.
#   한글뚝딱(초급) = 청록 바탕에 「뚝딱」   ← 이 파일
#   한글뚝딱(중급) = 주황 바탕에 「중급」   (tools/dictation/make_icons_jung.py)
#   한글뚝딱(고급) = 남색 바탕에 「고급」   (go/tools/make_icons_go.py)
#
# 글꼴: 굵은 한글 글꼴이 있어야 획이 또렷합니다. 'Noto Sans CJK KR'(리눅스: fonts-noto-cjk),
# 'Noto Sans KR', 윈도우 '맑은 고딕' 순서로 찾습니다. 크로미움(또는 크롬)으로 그립니다.
# 아이콘을 바꾼 뒤에는 python tools/stamp_sw.py — 지문이 바뀌어야 휴대폰이 새 그림을 받습니다.

import glob
import os
import shutil
import subprocess
import sys
import tempfile

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TEAL = "#14646E"     # 바탕색 (화면의 --accent 와 같음)
CREAM = "#FBF7EF"    # 안쪽 네모 색 (화면의 --bg 와 같음)
TEXT = ["뚝", "딱"]   # 위아래로 한 글자씩

TPL = """<!doctype html><html><head><meta charset="utf-8"><style>
  html, body {{ margin: 0; padding: 0; }}
  body {{ width: {size}px; height: {size}px; background: {teal};
          display: flex; align-items: center; justify-content: center; }}
  .box {{ width: {inner}px; height: {inner}px; background: {cream};
          border-radius: {round}px; display: flex; flex-direction: column;
          align-items: center; justify-content: center; }}
  .box span {{ font-family: 'Noto Sans CJK KR', 'Noto Sans KR', 'Malgun Gothic', 'Apple SD Gothic Neo', sans-serif;
               font-weight: 700; color: {teal}; font-size: {font}px;
               line-height: 1.0; letter-spacing: -0.02em; }}
</style></head><body>
  <div class="box">{spans}</div>
</body></html>
"""


def find_chrome():
    cands = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        shutil.which("google-chrome"),
        shutil.which("chromium"),
        shutil.which("chromium-browser"),
    ]
    cands += sorted(glob.glob("/opt/pw-browsers/chromium-*/chrome-linux*/chrome"))
    for c in cands:
        if c and os.path.exists(c):
            return c
    return None


def render(chrome, tmp, name, size, pad_ratio):
    inner = int(size * (1 - pad_ratio * 2))
    spans = "".join(f"<span>{t}</span>" for t in TEXT)
    html = TPL.format(size=size, inner=inner, teal=TEAL, cream=CREAM, spans=spans,
                      round=int(inner * 0.24), font=int(inner * 0.40))
    page = os.path.join(tmp, name + ".html")
    with open(page, "w", encoding="utf-8") as f:
        f.write(html)
    shot = os.path.join(tmp, name + ".png")
    subprocess.run([chrome, "--headless", "--disable-gpu", "--no-sandbox",
                    "--hide-scrollbars", "--default-background-color=00000000",
                    f"--screenshot={shot}", f"--window-size={size},{size}",
                    "file:///" + page.replace("\\", "/")],
                   check=True, capture_output=True, timeout=120)
    out = os.path.join(ROOT, name + ".png")
    shutil.copy(shot, out)
    print(f"{name}.png  {size}x{size}  {os.path.getsize(out):,} 바이트")


def main():
    chrome = find_chrome()
    if not chrome:
        sys.exit("크로미움(또는 크롬)을 찾지 못했습니다. 아이콘을 만들 수 없습니다.")
    tmp = tempfile.mkdtemp()
    try:
        render(chrome, tmp, "icon-180", 180, 0.14)
        render(chrome, tmp, "icon-192", 192, 0.14)
        render(chrome, tmp, "icon-512", 512, 0.14)
        render(chrome, tmp, "icon-512-maskable", 512, 0.22)   # 잘려도 글씨가 남도록
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("이어서:  python tools/stamp_sw.py")


if __name__ == "__main__":
    main()
