# stamp_sw.py — sw.js 의 화면 캐시 이름에 화면 파일들의 지문을 찍는다.
#
# 화면 캐시 이름이 그대로면 브라우저가 옛 화면을 계속 쓸 수 있다.
# 아래 화면 가운데 하나라도 고친 뒤에는 반드시 한 번 돌려 주세요.
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
SW = os.path.join(HERE, "sw.js")

# 지문에 넣을 화면들. 중급반만 고친 날에도 캐시 이름이 바뀌어야 하므로 함께 넣는다.
SCREENS = ["index.html", "jung.html", "gyeopbatchim.html"]

h = hashlib.sha256()
for name in SCREENS:
    p = os.path.join(HERE, name)
    if not os.path.exists(p):
        sys.exit(f"{name} 이 없습니다. 저장소 맨 위에 있어야 합니다.")
    h.update(name.encode("utf-8"))
    h.update(open(p, "rb").read())
digest = h.hexdigest()[:10]
sw = open(SW, encoding="utf-8", newline="").read()

new, n = re.subn(r"hangul-shell-[0-9a-f]{10}", "hangul-shell-" + digest, sw)
if not n:
    sys.exit("sw.js 에서 hangul-shell-<지문> 을 찾지 못했습니다.")
new = re.sub(r"빌드 때 [0-9a-f]{10} 이", f"빌드 때 {digest} 이", new)

open(SW, "w", encoding="utf-8", newline="").write(new)
print(f"sw.js 화면 캐시 이름: hangul-shell-{digest} ({n}곳)")
print("지문에 넣은 화면: " + ", ".join(SCREENS))
