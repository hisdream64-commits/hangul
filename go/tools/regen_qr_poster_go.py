# regen_qr_poster_go.py — 고급반 주소의 QR 코드와 인쇄용 안내문을 만든다.
#
#   pip install "qrcode[pil]" opencv-python-headless
#   python go/tools/regen_qr_poster_go.py https://urihangul.vercel.app/go/
#
# 만드는 것 (모두 go/ 안에 넣습니다)
#   go/qr.png      1400x1400, 오류복원 Q등급, 순수 검정
#   go/poster.pdf  A4 한 장 (QR + 주소 + 3단계 사용법)
#
# ⚠️ 기초반 것(뿌리의 qr.png·poster.pdf·README.md)은 건드리지 않습니다.
#    기초반 주소를 다시 만들려면 뿌리의 tools/regen_qr_poster.py 를 쓰세요.
#
# QR 규칙 (기초반에서 실측으로 정한 값을 그대로 씁니다. 바꾸지 마세요)
#   - 단축주소(bit.ly 등)를 쓰지 말 것. 국내 통신사·백신 앱이 스미싱으로 차단합니다.
#   - 순수 검정. 색을 넣으면 대비가 떨어져 인식률이 낮아집니다.
#   - 오류복원 Q등급. H로 올리면 칸이 촘촘해져 오히려 멀리서 읽기 어렵습니다.
#   - 여백(quiet zone) 4칸 유지, 인쇄물에는 70mm 이상.

import glob
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

# 이 파일은 go/tools/ 에 있습니다. 결과물은 한 칸 위(go/)에 넣습니다.
GO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DEFAULT_URL = "https://urihangul.vercel.app/go/"
URL = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_URL
if not URL.endswith("/"):
    URL += "/"
SHORT = re.sub(r"^https?://", "", URL).rstrip("/")

for bad in ("bit.ly", "tinyurl", "goo.gl", "han.gl", "url.kr"):
    if bad in URL:
        sys.exit(f"단축주소({bad})는 쓰지 마세요. 통신사·백신 앱이 차단합니다.")

# 기초반 주소 — 안내문 아래에 함께 적어 둡니다.
BASE_URL = re.sub(r"go/$", "", URL)
BASE_SHORT = re.sub(r"^https?://", "", BASE_URL).rstrip("/")

# ---------- QR ----------
qr = qrcode.QRCode(error_correction=ERROR_CORRECT_Q, box_size=10, border=4)
qr.add_data(URL)
qr.make(fit=True)
img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
img = img.resize((1400, 1400), 0)              # 0 = NEAREST, 칸이 번지지 않게
qr_path = os.path.join(GO, "qr.png")
img.save(qr_path)

data, _, _ = cv2.QRCodeDetector().detectAndDecode(cv2.imread(qr_path))
if data != URL:
    sys.exit(f"QR 검증 실패 — 읽힌 값: {data!r}")
print(f"go/qr.png  {qr.modules_count}x{qr.modules_count} 칸, 검증 OK -> {URL}")

# ---------- 안내문 ----------
# 색은 고급반 화면과 같은 남색(--accent: #2E5B9A)을 씁니다.
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
  h1 {{ font-size: 19mm; margin: 0; letter-spacing: -1mm; color: #2E5B9A; }}
  .sub {{ font-size: 7mm; margin: 3mm 0 0; color: #3d3d3d; }}
  .qr {{ margin: 6mm 0 3mm; padding: 4mm; background: #fff;
         border: 1.2mm solid #2E5B9A; border-radius: 4mm; }}
  .qr img {{ width: 72mm; height: 72mm; display: block; }}
  .howto {{ font-size: 7.2mm; margin: 1mm 0 0; color: #1b1b1b; font-weight: 700; }}
  .url {{ margin: 5mm 0 0; font-size: 6mm; word-break: break-all; text-align: center; }}
  .url b {{ font-size: 7mm; color: #2E5B9A; }}
  ol {{ font-size: 7.4mm; line-height: 1.55; margin: 6mm 0 0; padding: 0 0 0 10mm;
        width: 100%; max-width: 168mm; }}
  ol li {{ margin-bottom: 2.5mm; }}
  .note {{ margin-top: auto; width: 100%; max-width: 168mm;
           border-top: 0.5mm solid #cfc7b6; padding-top: 4mm;
           font-size: 5mm; line-height: 1.55; color: #4a4a4a; }}
  .note b {{ color: #2E5B9A; }}
</style></head><body>
  <h1>한글 교실 고급반</h1>
  <p class="sub">혼자서 서류를 읽고 쓰기 · 무료</p>

  <div class="qr"><img src="qr.png" alt="QR"></div>
  <p class="howto">휴대폰 카메라로 이 그림을 비추세요</p>

  <p class="url">주소를 직접 치셔도 됩니다<br><b>{short}</b></p>

  <ol>
    <li>카메라를 켜고 위 그림을 비춥니다</li>
    <li>화면에 뜨는 주소를 한 번 누릅니다</li>
    <li><b>「홈 화면에 추가」</b>를 눌러 두면<br>
        다음부터는 단추 하나로 열립니다</li>
  </ol>

  <div class="note">
    관공서 말, 서식 채워 쓰기, 돈과 계약 글, 병원과 약 글, 문자와 편지 쓰기,
    경조사 봉투, 긴 글 읽기, 사자성어까지 <b>열두 과와 졸업 시험</b>을
    성우 목소리로 배웁니다. 마지막 과에서는 <b>소리 내어 읽은 것을 녹음해
    점수를 알려 드립니다</b>(마이크 「허용」을 한 번 눌러 주세요).<br>
    설치하지 않아도 되고, 요금도 들지 않습니다.
    한글이 처음이신 분은 기초반 <b>{base}</b> 부터 하십시오.
  </div>
</body></html>
"""

chrome = None
candidates = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    shutil.which("google-chrome"),
    shutil.which("chromium"),
    shutil.which("chromium-browser"),
]
candidates += sorted(glob.glob("/opt/pw-browsers/chromium-*/chrome-linux*/chrome"))
for c in candidates:
    if c and os.path.exists(c):
        chrome = c
        break

if not chrome:
    print("⚠️ Chrome 을 찾지 못해 go/poster.pdf 는 건너뜁니다. go/qr.png 는 새로 만들었습니다.")
    sys.exit(0)

tmp = tempfile.mkdtemp()
shutil.copy(qr_path, os.path.join(tmp, "qr.png"))
html_path = os.path.join(tmp, "poster.html")
with open(html_path, "w", encoding="utf-8") as f:
    f.write(POSTER.format(short=SHORT, base=BASE_SHORT))
out = os.path.join(tmp, "poster.pdf")

subprocess.run([chrome, "--headless", "--disable-gpu", "--no-sandbox", "--no-pdf-header-footer",
                f"--print-to-pdf={out}", "file:///" + html_path.replace("\\", "/")],
               check=True, capture_output=True, timeout=120)
shutil.copy(out, os.path.join(GO, "poster.pdf"))
shutil.rmtree(tmp, ignore_errors=True)
print(f"go/poster.pdf  {os.path.getsize(os.path.join(GO, 'poster.pdf')):,} 바이트")
