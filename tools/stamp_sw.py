# stamp_sw.py — sw.js 의 화면 캐시 이름에 index.html 내용의 지문을 찍는다.
#
# 화면 캐시 이름이 그대로면 브라우저가 옛 화면을 계속 쓸 수 있다.
# index.html 을 고친 뒤에는 반드시 한 번 돌려 주세요.
#
#   python tools/stamp_sw.py

import hashlib
import os
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")   # 윈도우 명령창에서 한글이 깨지지 않게
except Exception:
    pass

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IDX = os.path.join(HERE, "index.html")
SW = os.path.join(HERE, "sw.js")

digest = hashlib.sha256(open(IDX, "rb").read()).hexdigest()[:10]
sw = open(SW, encoding="utf-8", newline="").read()

new, n = re.subn(r"hangul-shell-[0-9a-f]{10}", "hangul-shell-" + digest, sw)
if not n:
    sys.exit("sw.js 에서 hangul-shell-<지문> 을 찾지 못했습니다.")
new = re.sub(r"빌드 때 [0-9a-f]{10} 이", f"빌드 때 {digest} 이", new)

open(SW, "w", encoding="utf-8", newline="").write(new)
print(f"sw.js 화면 캐시 이름: hangul-shell-{digest} ({n}곳)")
