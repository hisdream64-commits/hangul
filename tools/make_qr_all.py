# make_qr_all.py — 세 과정의 QR 코드와 인쇄용 안내문을 한 번에 만든다.
#
#   pip install "qrcode[pil]" opencv-python-headless
#   python tools/make_qr_all.py                      # 운영 주소로
#   python tools/make_qr_all.py https://새주소/       # 주소가 바뀌었을 때
#
# 만드는 것
#   qr-jung.png       중급 QR (초급 qr.png · 고급 go/qr.png 는 각자 도구가 만듭니다)
#   poster-jung.pdf   중급 안내문 A4 한 장
#   poster-all.pdf    세 과정을 한 장에 모은 안내문 (교실 벽보·강사용)
#
# ⚠️ 초급·고급 안내문은 건드리지 않습니다.
#    초급: python tools/regen_qr_poster.py <주소>
#    고급: python go/tools/regen_qr_poster_go.py <주소>/go/
#
# QR 규칙 (초급에서 실측으로 정한 값을 그대로 씁니다. 바꾸지 마세요)
#   - 단축주소(bit.ly 등) 금지. 국내 통신사·백신 앱이 스미싱으로 차단합니다.
#   - 순수 검정. 색을 넣으면 대비가 떨어져 인식률이 낮아집니다.
#   - 오류복원 Q등급, 여백 4칸.
#   - 낱장 안내문의 QR 은 70mm 이상. 세 과정을 한 장에 모은 것은 62mm 라
#     조금 작으므로, 어르신께 나눠 드릴 때는 낱장 안내문을 쓰십시오.

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

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

BASE = sys.argv[1] if len(sys.argv) > 1 else "https://urihangul.vercel.app/"
if not BASE.endswith("/"):
    BASE += "/"
for bad in ("bit.ly", "tinyurl", "goo.gl", "han.gl", "url.kr"):
    if bad in BASE:
        sys.exit(f"단축주소({bad})는 쓰지 마세요. 통신사·백신 앱이 차단합니다.")

# 과정 셋 — (키, 이름, 새싹, 주소, 색, 한 줄 설명)
COURSES = [
    ("cho",  "한글뚝딱(초급)",  "🌱", BASE,                "#14646E", "자음·모음부터 낱말까지"),
    ("jung", "한글뚝딱(중급)",  "🌿", BASE + "jung.html",  "#A65A28", "듣고 받아쓰기"),
    ("go",   "한글뚝딱(고급)",  "📘", BASE + "go/",        "#2E5B9A", "서류 읽고 쓰기"),
]


def short(url):
    return re.sub(r"^https?://", "", url).rstrip("/")


def make_qr(url, out_path):
    qr = qrcode.QRCode(error_correction=ERROR_CORRECT_Q, box_size=10, border=4)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    img = img.resize((1400, 1400), 0)          # 0 = NEAREST, 칸이 번지지 않게
    img.save(out_path)
    data, _, _ = cv2.QRCodeDetector().detectAndDecode(cv2.imread(out_path))
    if data != url:
        sys.exit(f"QR 검증 실패 — {out_path}: 읽힌 값 {data!r}, 바라던 값 {url!r}")
    return qr.modules_count


def find_chrome():
    cands = [r"C:\Program Files\Google\Chrome\Application\chrome.exe",
             r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
             "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
             shutil.which("google-chrome"), shutil.which("chromium"),
             shutil.which("chromium-browser")]
    cands += sorted(glob.glob("/opt/pw-browsers/chromium-*/chrome-linux*/chrome"))
    for c in cands:
        if c and os.path.exists(c):
            return c
    return None


def to_pdf(chrome, html, images, out_name):
    """html 을 A4 한 장 PDF 로 굽는다. images 는 {파일이름: 원본경로}."""
    tmp = tempfile.mkdtemp()
    try:
        for name, src in images.items():
            shutil.copy(src, os.path.join(tmp, name))
        page = os.path.join(tmp, "p.html")
        with open(page, "w", encoding="utf-8") as f:
            f.write(html)
        out = os.path.join(tmp, "p.pdf")
        subprocess.run([chrome, "--headless", "--disable-gpu", "--no-sandbox",
                        "--no-pdf-header-footer", f"--print-to-pdf={out}",
                        "file:///" + page.replace("\\", "/")],
                       check=True, capture_output=True, timeout=120)
        dest = os.path.join(HERE, out_name)
        shutil.copy(out, dest)
        print(f"{out_name}  {os.path.getsize(dest):,} 바이트")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


COMMON_CSS = """
  @page {{ size: A4; margin: 0; }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0; width: 210mm; height: 297mm;
    font-family: 'Malgun Gothic', 'Noto Sans KR', 'Apple SD Gothic Neo', sans-serif;
    color: #1b1b1b; background: #FBF7EF;
  }}
  .nb {{ white-space: nowrap; }}
"""

ONE = """<!doctype html><html lang="ko"><head><meta charset="utf-8"><style>
""" + COMMON_CSS + """
  body {{ display: flex; flex-direction: column; align-items: center; padding: 12mm 14mm 10mm; }}
  h1 {{ font-size: 19mm; margin: 0; letter-spacing: -1mm; color: {color}; }}
  .sub {{ font-size: 7mm; margin: 3mm 0 0; color: #3d3d3d; }}
  .qr {{ margin: 6mm 0 3mm; padding: 4mm; background: #fff;
         border: 1.2mm solid {color}; border-radius: 4mm; }}
  .qr img {{ width: 72mm; height: 72mm; display: block; }}
  .howto {{ font-size: 7.2mm; margin: 1mm 0 0; font-weight: 700; }}
  .url {{ margin: 5mm 0 0; font-size: 6mm; text-align: center; }}
  .url b {{ font-size: 7mm; color: {color}; }}
  ol {{ font-size: 7.4mm; line-height: 1.55; margin: 6mm 0 0; padding: 0 0 0 10mm;
        width: 100%; max-width: 168mm; }}
  ol li {{ margin-bottom: 2.5mm; }}
  .note {{ margin-top: auto; width: 100%; max-width: 168mm;
           border-top: 0.5mm solid #cfc7b6; padding-top: 4mm;
           font-size: 5mm; line-height: 1.55; color: #4a4a4a; }}
  .note b {{ color: {color}; }}
</style></head><body>
  <h1>{name}</h1>
  <p class="sub">{desc} · 무료</p>
  <div class="qr"><img src="qr.png" alt="QR"></div>
  <p class="howto">휴대폰 카메라로 이 그림을 비추세요</p>
  <p class="url">주소를 직접 치셔도 됩니다<br><b>{short}</b></p>
  <ol>
    <li>카메라를 켜고 위 그림을 비춥니다</li>
    <li>화면에 뜨는 주소를 한 번 누릅니다</li>
    <li><b>「홈 화면에 추가」</b>를 눌러 두면<br>다음부터는 단추 하나로 열립니다</li>
  </ol>
  <div class="note">
    {long_desc}<br>
    단추를 누르면 <b>성우 목소리로 읽어</b> 드립니다. 설치하지 않아도 되고, 요금도 들지 않습니다.<br>
    홈 화면에 넣으신 뒤 <b>「📥 소리 모두 받기」</b>를 한 번 눌러 두시면
    <b>인터넷이 없어도</b> 쓰실 수 있습니다.
  </div>
</body></html>
"""

ALL = """<!doctype html><html lang="ko"><head><meta charset="utf-8"><style>
""" + COMMON_CSS + """
  body {{ display: flex; flex-direction: column; padding: 11mm 12mm 9mm; }}
  h1 {{ font-size: 15mm; margin: 0; text-align: center; letter-spacing: -0.8mm; color: #14646E; }}
  .sub {{ font-size: 5.6mm; margin: 2mm 0 5mm; text-align: center; color: #3d3d3d; }}
  .row {{ display: flex; gap: 4mm; }}
  .card {{ flex: 1; background: #fff; border-radius: 4mm; padding: 4mm 3mm;
           border: 1mm solid var(--c); text-align: center; }}
  .card .leaf {{ font-size: 7.5mm; display: block; line-height: 1; margin-bottom: 1mm; }}
  .card h2 {{ font-size: 5.4mm; margin: 0 0 1mm; color: var(--c); white-space: nowrap; }}
  .card .d {{ font-size: 4.2mm; color: #4a4a4a; margin: 0 0 2.5mm; min-height: 9mm; }}
  .card img {{ width: 52mm; height: 52mm; display: block; margin: 0 auto; }}
  .card .u {{ font-size: 4.1mm; margin: 2mm 0 0; color: var(--c); font-weight: 700; }}
  ol {{ font-size: 5.8mm; line-height: 1.55; margin: 6mm 0 0; padding: 0 0 0 8mm; }}
  ol li {{ margin-bottom: 2.2mm; }}
  /* 기종별 안내 — 가운데 빈 자리를 채웁니다 */
  .os {{ display: flex; gap: 4mm; margin: 6mm 0 0; }}
  .os > div {{ flex: 1; background: #fff; border: 0.4mm solid #cfc7b6;
               border-radius: 3mm; padding: 3.5mm 4mm; }}
  .os h3 {{ font-size: 5.4mm; margin: 0 0 2mm; color: #14646E; }}
  .os p {{ font-size: 4.6mm; line-height: 1.5; margin: 0; color: #3d3d3d; }}
  .os b {{ color: #1b1b1b; }}
  .note {{ margin-top: auto; border-top: 0.5mm solid #cfc7b6; padding-top: 3mm;
           font-size: 4.3mm; line-height: 1.5; color: #4a4a4a; }}
  .note b {{ color: #14646E; }}
</style></head><body>
  <h1>한글뚝딱</h1>
  <p class="sub">휴대폰으로 배우는 한글 · 세 과정 모두 무료</p>
  <div class="row">{cards}</div>
  <ol>
    <li>휴대폰 <b>카메라</b>를 켜고 QR 그림을 비춥니다</li>
    <li>화면에 뜨는 <b>주소를 한 번</b> 누릅니다</li>
    <li><b>「홈 화면에 추가」</b>를 누르면 아이콘이 생깁니다</li>
    <li>그 아이콘으로 열고 <b>「📥 소리 모두 받기」</b>를 한 번 누릅니다</li>
  </ol>
  <div class="os">
    <div>
      <h3>🤖 안드로이드 (삼성 등)</h3>
      <p>첫 화면의 <b>「📱 앱으로 설치하기」</b>를 누릅니다.<br>
      안 보이면 오른쪽 위 <b>⋮</b> → <b>홈 화면에 추가</b>.</p>
    </div>
    <div>
      <h3>🍎 아이폰 · 아이패드</h3>
      <p>꼭 <b>사파리</b>로 엽니다. 아래 가운데
      <b>공유 단추</b>(□에 ↑) → <b>홈 화면에 추가</b>.</p>
    </div>
  </div>
  <div class="note">
    처음이신 분은 <b>초급</b>부터, 글자를 아시는 분은 <b>중급</b>,
    서류를 혼자 읽고 쓰고 싶으신 분은 <b>고급</b>입니다. 세 과정은 서로 오갈 수 있습니다.<br>
    <b>아이폰</b>은 홈 화면 앱으로 연 뒤 <b>소리를 한 번 더</b> 받아 주세요
    (사파리와 저장 공간이 다릅니다).<br>
    소리를 받아 두면 <b>인터넷이 없어도</b> 쓰실 수 있습니다. 요금은 들지 않습니다.
  </div>
</body></html>
"""

LONG = {
    "cho":  "자음·모음, 소리 합치기, 받침, 생활 낱말, 글씨 쓰는 순서, 낱말 놀이를 배웁니다.",
    "jung": "들려 드리는 낱말과 문장을 받아쓰며 익힙니다. 겹받침 연습도 함께 있습니다.",
    "go":   "관공서 말, 서식 채워 쓰기, 돈과 계약 글, 병원과 약, 편지와 문자, 긴 글 읽기를 배웁니다. "
            "마지막 과에서는 소리 내어 읽은 것을 녹음해 점수를 알려 드립니다.",
}


def main():
    chrome = find_chrome()
    tmpdir = tempfile.mkdtemp()
    qr_files = {}
    try:
        for key, name, leaf, url, color, desc in COURSES:
            p = os.path.join(tmpdir, f"{key}.png")
            n = make_qr(url, p)
            qr_files[key] = p
            print(f"{name}  {n}x{n} 칸, 검증 OK -> {url}")

        # 중급 QR 은 저장소에도 남깁니다 (초급·고급은 각자 도구가 이미 만들어 둡니다)
        shutil.copy(qr_files["jung"], os.path.join(HERE, "qr-jung.png"))
        print("qr-jung.png 저장")

        if not chrome:
            print("⚠️ Chrome 을 찾지 못해 안내문(PDF)은 건너뜁니다. QR 그림은 만들었습니다.")
            return

        # ① 중급 낱장 안내문
        key, name, leaf, url, color, desc = COURSES[1]
        to_pdf(chrome,
               ONE.format(color=color, name=name, desc=desc, short=short(url), long_desc=LONG[key]),
               {"qr.png": qr_files["jung"]},
               "poster-jung.pdf")

        # ② 세 과정 한 장
        cards = "".join(
            f'<div class="card" style="--c:{color}">'
            f'<span class="leaf">{leaf}</span><h2>{name}</h2><p class="d">{desc}</p>'
            f'<img src="{key}.png" alt="QR"><p class="u">{short(url)}</p></div>'
            for key, name, leaf, url, color, desc in COURSES)
        to_pdf(chrome, ALL.format(cards=cards),
               {f"{k}.png": v for k, v in qr_files.items()},
               "poster-all.pdf")
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


if __name__ == "__main__":
    main()
