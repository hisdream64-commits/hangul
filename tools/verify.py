# verify.py — 배포된 주소에 소리가 하나도 빠짐없이 올라갔는지 전수 확인한다.
#
#   python tools/verify.py https://새주소/
#
# 표본만 보면 놓칩니다. 1,226개를 모두 확인합니다.

import json
import re
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")   # 윈도우 명령창에서 한글이 깨지지 않게
except Exception:
    pass

BASE = (sys.argv[1] if len(sys.argv) > 1 else "").rstrip("/") + "/"
if BASE == "/":
    sys.exit("사용법: python tools/verify.py https://새주소/")

print(f"확인할 주소: {BASE}")
html = urllib.request.urlopen(BASE, timeout=30).read().decode("utf-8")

AUDIO = json.loads(re.search(r'window\.AUDIO = (\{.*?\});</script>', html, re.S).group(1))
mbin = re.search(r'window\.AUDIO_BIN = (\{.*?\});</script>', html, re.S)
BIN = json.loads(mbin.group(1)) if mbin else None

ok = True
print(f"소리 키 {len(AUDIO)}개 (1226이어야 정상)")
if len(AUDIO) != 1226:
    ok = False


def head(u):
    try:
        r = urllib.request.urlopen(urllib.request.Request(BASE + u, method="HEAD"), timeout=30)
        return u, r.status, int(r.headers.get("content-length") or 0)
    except Exception as e:
        return u, "ERR", str(e)[:60]


# 1) 낱개 mp3 — 묶음을 받기 전에 인터넷으로 듣는 용도라 전부 있어야 한다
bad = []
with ThreadPoolExecutor(max_workers=16) as ex:
    for u, st, n in ex.map(head, sorted(set(AUDIO.values()))):
        if st != 200 or (isinstance(n, int) and n < 500):
            bad.append((u, st, n))
print(f"낱개 소리 파일 문제: {len(bad)}개 {bad[:5]}")
if bad:
    ok = False

# 2) 묶음 — 길이가 색인과 정확히 같아야 하고, 잘라낸 조각이 낱개 파일과 같아야 한다
if not BIN:
    print("⚠️ window.AUDIO_BIN 이 없습니다. tools/build_audio_bundle.py 를 돌리셨나요?")
    ok = False
else:
    u, st, n = head(BIN["file"])
    print(f"묶음 {BIN['file']}: {st}, {n:,} 바이트 (색인 {BIN['total']:,})")
    if st != 200 or n != BIN["total"]:
        ok = False
    elif sum(BIN["lens"]) != BIN["total"]:
        print("⚠️ 색인의 길이 합이 전체 길이와 다릅니다.")
        ok = False
    else:
        # 표본 12개를 묶음에서 잘라 내려받아 낱개 파일과 바이트 단위로 맞춰 본다
        offs, at = [], 0
        for L in BIN["lens"]:
            offs.append((at, L))
            at += L
        picks = [0, 1, 2, 611, 612, 613, 1222, 1223, 1224, 1225, 400, 900]
        diff = []
        for i in picks:
            o, L = offs[i]
            req = urllib.request.Request(BASE + BIN["file"],
                                         headers={"Range": f"bytes={o}-{o+L-1}"})
            try:
                res = urllib.request.urlopen(req, timeout=30)
                if res.status != 206:            # 조각 요청을 못 받는 서버 (예: 로컬 시험용)
                    picks = []
                    print("묶음 조각 대조: 이 서버는 조각 요청을 지원하지 않아 건너뜁니다.")
                    break
                whole = urllib.request.urlopen(BASE + f"audio/a{i}.mp3", timeout=30).read()
                if res.read() != whole:
                    diff.append(i)
            except Exception as e:
                diff.append(f"a{i}({str(e)[:30]})")
        if picks:
            print(f"묶음 조각 대조 {len(picks)}개 — 다른 것: {diff if diff else '없음'}")
        if diff:
            ok = False

print("\n결과:", "✅ 이상 없음" if ok else "❌ 문제가 있습니다. 위 내용을 보세요.")
sys.exit(0 if ok else 1)
