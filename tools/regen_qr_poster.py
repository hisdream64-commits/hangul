# regen_qr_poster.py — 주소가 바뀌면 QR 코드와 인쇄용 안내문을 다시 만든다.
#
#   pip install "qrcode[pil]" opencv-python-headless
#   python tools/regen_qr_poster.py https://새주소/
#
# 만드는 것
#   qr.png      1400x1400, 오류복원 Q등급, 순수 검정
#   poster.pdf  A4 한 장 (QR + 주소 + 3단계 사용법)
#   README.md   바로가기 주소 갱신
#
# QR 규칙 (실측으로 정한 값입니다. 바꾸지 마세요)
#   - 단축주소(bit.ly 등)를 쓰지 말 것. 국내 통신사·백신 앱이 스미싱으로 차단합니다.
#   - 순수 검정. 색을 넣으면 대비가 떨어져 인식률이 낮아집니다.
#   - 오류복원 Q등급. H로 올리면 칸이 촘촘해져 오히려 멀리서 읽기 어렵습니다.
#     Q는 대개 M과 같은 칸수를 유지하면서 복원력은 더 높습니다.
#     (지금 주소는 29x29 — 짧은 주소일수록 칸이 커져 잘 읽힙니다)
#   - 여백(quiet zone) 4칸 유지, 인쇄물에는 70mm 이상.

import os
import re
import shutil
import subprocess
import sys
import tempfile

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")   # 윈도우 명령창에서 한글이 깨지지 않게
except Exception:
    pass

import cv2
import qrcode
from qrcode.constants import ERROR_CORRECT_Q

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if len(sys.argv) < 2:
    sys.exit("사용법: python tools/regen_qr_poster.py https://새주소/")

URL = sys.argv[1]
if not URL.endswith("/"):
    URL += "/"
SHORT = re.sub(r"^https?://", "", URL).rstrip("/")

for bad in ("bit.ly", "tinyurl", "goo.gl", "han.gl", "url.kr"):
    if bad in URL:
        sys.exit(f"단축주소({bad})는 쓰지 마세요. 통신사·백신 앱이 차단합니다.")

# ---------- QR ----------
qr = qrcode.QRCode(error_correction=ERROR_CORRECT_Q, box_size=10, border=4)
qr.add_data(URL)
qr.make(fit=True)
img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
img = img.resize((1400, 1400), 0)              # 0 = NEAREST, 칸이 번지지 않게
qr_path = os.path.join(HERE, "qr.png")
img.save(qr_path)

data, _, _ = cv2.QRCodeDetector().detectAndDecode(cv2.imread(qr_path))
if data != URL:
    sys.exit(f"QR 검증 실패 — 읽힌 값: {data!r}")
print(f"qr.png  {qr.modules_count}x{qr.modules_count} 칸, 검증 OK -> {URL}")

# ---------- 안내문 ----------
POSTER = """<!doctype html>
<html lang="ko"><head><meta charset="utf-8">
<style>
  @page {{ size: A4; margin: 0; }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0; width: 210mm; height: 297mm;
    font-family: 'Malgun Gothic', 'Noto Sans KR', 'Apple SD Gothic Neo', sans-serif;
    color: #1b1b1b; background: #FBF7EF;
    display: flex; flex-direction: column; align-items: center;
    padding: 12mm 14mm 10mm;
  }}
  h1 {{ font-size: 21mm; margin: 0; letter-spacing: -1mm; color: #14646E; }}
  .sub {{ font-size: 7.2mm; margin: 3mm 0 0; color: #3d3d3d; }}
  .qr {{ margin: 7mm 0 3mm; padding: 4mm; background: #fff;
         border: 1.2mm solid #14646E; border-radius: 4mm; }}
  .qr img {{ width: 72mm; height: 72mm; display: block; }}
  .howto {{ font-size: 7.2mm; margin: 1mm 0 0; color: #1b1b1b; font-weight: 700; }}
  .url {{ margin: 5mm 0 0; font-size: 6mm; word-break: break-all; text-align: center; }}
  .url b {{ font-size: 7.2mm; color: #14646E; }}
  ol {{ font-size: 7.6mm; line-height: 1.6; margin: 7mm 0 0; padding: 0 0 0 10mm;
        width: 100%; max-width: 168mm; }}
  ol li {{ margin-bottom: 2.5mm; }}
  .note {{ margin-top: auto; width: 100%; max-width: 168mm;
           border-top: 0.5mm solid #cfc7b6; padding-top: 4mm;
           font-size: 5.2mm; line-height: 1.55; color: #4a4a4a; }}
</style></head><body>
  <h1>우리 한글 교실</h1>
  <p class="sub">휴대폰으로 배우는 기초 한글 · 무료</p>

  <div class="qr"><img src="qr.png" alt="QR"></div>
  <p class="howto">휴대폰 카메라로 이 그림을 비추세요</p>

  <p class="url">주소를 직접 치셔도 됩니다<br><b>{short}</b></p>

  <ol>
    <li>카메라를 켜고 위 그림을 비춥니다</li>
    <li>화면에 뜨는 주소를 한 번 누릅니다</li>
    <li>맨 아래 <b>「소리 모두 받기」</b>를 눌러 두면<br>
        인터넷이 없어도 쓸 수 있습니다</li>
  </ol>

  <div class="note">
    자음·모음, 소리 합치기, 받침, 생활 낱말 761개, 글씨 쓰는 순서, 낱말 놀이를
    성우 목소리로 배웁니다. 설치하지 않아도 되고, 요금도 들지 않습니다.<br>
    아이폰은 <b>①주소를 열고 ②홈 화면에 추가한 뒤 ③그 앱 안에서</b> 소리를 받아 주세요.
  </div>
</body></html>
"""

chrome = None
for c in (r"C:\Program Files\Google\Chrome\Application\chrome.exe",
          r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
          "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
          shutil.which("google-chrome"), shutil.which("chromium")):
    if c and os.path.exists(c):
        chrome = c
        break

if not chrome:
    print("⚠️ Chrome 을 찾지 못해 poster.pdf 는 건너뜁니다. qr.png 는 새로 만들었습니다.")
    sys.exit(0)

tmp = tempfile.mkdtemp()
shutil.copy(qr_path, os.path.join(tmp, "qr.png"))
html_path = os.path.join(tmp, "poster.html")
open(html_path, "w", encoding="utf-8").write(POSTER.format(short=SHORT))
out = os.path.join(tmp, "poster.pdf")

subprocess.run([chrome, "--headless", "--disable-gpu", "--no-pdf-header-footer",
                f"--print-to-pdf={out}", "file:///" + html_path.replace("\\", "/")],
               check=True, capture_output=True, timeout=120)
shutil.copy(out, os.path.join(HERE, "poster.pdf"))
shutil.rmtree(tmp, ignore_errors=True)
print(f"poster.pdf  {os.path.getsize(os.path.join(HERE, 'poster.pdf')):,} 바이트")

# ---------- README 주소 ----------
rp = os.path.join(HERE, "README.md")
r = open(rp, encoding="utf-8", newline="").read()
r2 = re.sub(r"\*\*바로가기: https?://[^\*]+\*\*", f"**바로가기: {URL}**", r)
if r2 != r:
    open(rp, "w", encoding="utf-8", newline="").write(r2)
    print(f"README.md 바로가기 -> {URL}")
