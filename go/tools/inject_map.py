# -*- coding: utf-8 -*-
# inject_map.py — tools/audio_map.json 을 index.html 안에 window.AUDIO 로 넣는다.
#
#   python tools/inject_map.py
#
# 이미 들어 있으면 갈아 끼웁니다. 넣는 자리는 「소리 들려 주기」 스크립트 **바로 앞**
# 입니다. 그 뒤에 넣으면 앱이 시작될 때 지도가 비어 있어, 모든 말이 기기 음성으로
# 새어 나갑니다. 기초반에서도 같은 자리 문제로 버그가 났었습니다.

import io
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
HTML = os.path.join(ROOT, "index.html")
MAP = os.path.join(HERE, "audio_map.json")

try:
    import sys
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def key(t):
    t = re.sub(r"<br\s*/?>", " ", t, flags=re.I)
    t = re.sub(r"<[^>]+>", "", t)
    t = re.sub(r"\s+", " ", t).strip()
    return re.sub(r"[!?.]+$", "", t).strip()


s = io.open(HTML, encoding="utf-8").read()
raw = json.load(io.open(MAP, encoding="utf-8"))

amap = {}
for text, path in raw.items():
    k = key(text)
    if k and k not in amap:
        amap[k] = path

payload = json.dumps(amap, ensure_ascii=False, separators=(",", ":"))
block = u"<script>window.AUDIO = %s;</script>\n" % payload

s = re.sub(r"<script>window\.AUDIO = \{.*?\};</script>\n?", "", s, flags=re.S)
anchor = u"<script>\n/* ===================== 소리 들려 주기"
if s.count(anchor) != 1:
    raise SystemExit("index.html 에서 소리 스크립트 자리를 찾지 못했습니다.")
s = s.replace(anchor, block + anchor)
io.open(HTML, "w", encoding="utf-8").write(s)
print("소리 지도 %d개를 index.html 에 넣었습니다. (%.1f KB)" % (len(amap), len(payload) / 1024))
