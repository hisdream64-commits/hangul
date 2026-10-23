# make_icons_go.py — 고급반 홈 화면 아이콘을 만든다.
#
#   python go/tools/make_icons_go.py
#
# 만드는 것 (모두 go/ 안에)
#   go/icon-180.png          아이폰 홈 화면
#   go/icon-192.png          안드로이드
#   go/icon-512.png          설치용 큰 그림
#   go/icon-512-maskable.png 안드로이드가 동그랗게 잘라 쓰는 그림(가장자리 여백 넉넉히)
#
# 왜 따로 만드나: 기초반 아이콘과 나란히 놓이므로 한눈에 구별되어야 합니다.
#   기초반 = 청록 바탕에 「한글」  ·  고급반 = 남색 바탕에 「고급」
#
# 글꼴은 크로미움이 가진 것을 씁니다(안내문 만들 때와 같은 방법).

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

GO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

NAVY = "#2E5B9A"     # 고급반 바탕색 (화면의 --accent 와 같음)
CREAM = "#FBF7EF"    # 안쪽 네모 색

# pad  = 바깥 여백 비율. maskable 은 동그랗게 잘려 나가므로 넉넉히 둡니다.
# round = 안쪽 네모의 둥근 정도
TPL = """<!doctype html><html><head><meta charset="utf-8"><style>
  html, body {{ margin: 0; padding: 0; }}
  body {{ width: {size}px; height: {size}px; background: {navy};
          display: flex; align-items: center; justify-content: center; }}
  .box {{ width: {inner}px; height: {inner}px; background: {cream};
          border-radius: {round}px; display: flex; flex-direction: column;
          align-items: center; justify-content: center; }}
  .box span {{ font-family: 'Noto Sans KR', 'Malgun Gothic', 'WenQuanYi Zen Hei', sans-serif;
               font-weight: 800; color: {navy}; font-size: {font}px;
               line-height: 0.98; letter-spacing: -0.02em; }}
</style></head><body>
  <div class="box"><span>고</span><span>급</span></div>
</body></html>
"""


def find_chrome():
    cands = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
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
    html = TPL.format(size=size, inner=inner, navy=NAVY, cream=CREAM,
                      round=int(inner * 0.24), font=int(inner * 0.46))
    page = os.path.join(tmp, name + ".html")
    with open(page, "w", encoding="utf-8") as f:
        f.write(html)
    shot = os.path.join(tmp, name + ".png")
    subprocess.run([chrome, "--headless", "--disable-gpu", "--no-sandbox",
                    "--hide-scrollbars", "--default-background-color=00000000",
                    f"--screenshot={shot}", f"--window-size={size},{size}",
                    "file:///" + page.replace("\\", "/")],
                   check=True, capture_output=True, timeout=120)
    out = os.path.join(GO, name + ".png")
    shutil.copy(shot, out)
    print(f"go/{name}.png  {size}x{size}  {os.path.getsize(out):,} 바이트")


def main():
    chrome = find_chrome()
    if not chrome:
        sys.exit("크로미움(또는 크롬)을 찾지 못했습니다. 아이콘을 만들 수 없습니다.")
    tmp = tempfile.mkdtemp()
    try:
        render(chrome, tmp, "icon-180", 180, 0.10)
        render(chrome, tmp, "icon-192", 192, 0.10)
        render(chrome, tmp, "icon-512", 512, 0.10)
        render(chrome, tmp, "icon-512-maskable", 512, 0.20)   # 잘려도 글씨가 남도록
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
