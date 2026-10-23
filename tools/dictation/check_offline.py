# check_offline.py — 받아쓰기 중급반이 비행기 모드에서도 소리를 내는지 실제 브라우저로 확인한다.
#
#   pip install playwright && python -m playwright install chromium     (처음 한 번)
#   python tools/dictation/check_offline.py
#
# 왜 손으로는 못 보는가: 휴대폰에서 「소리 모두 받기」를 누르면 소리가 낱개 mp3 가 아니라
# audio/audio.bin 한 덩어리로만 저장됩니다. 그래서 인터넷이 있는 PC에서 🔊 를 눌러 보는
# 것으로는 비행기 모드가 멀쩡한지 알 수 없습니다. 실제로 그 상태를 만들어 보고 확인합니다.
#
# 보는 것 네 가지
#   1) 묶음에서 잘라낸 조각이 낱개 mp3 와 바이트 단위로 같은가
#   2) 인터넷이 있고 묶음이 없으면 — 낱개 주소로 재생하는가
#   3) 묶음을 받아 둔 뒤 비행기 모드에서 — blob: 주소로 소리가 읽히는가  ← 핵심
#   4) 묶음이 없는 비행기 모드에서는 — 안 나는가 (그게 정상)

import functools
import http.server
import json
import os
import pathlib
import re
import socketserver
import sys
import threading

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")   # 윈도우 명령창에서 한글이 깨지지 않게
except Exception:
    pass

HERE = pathlib.Path(__file__).resolve().parent.parent.parent      # 저장소 맨 위
SCREENS = ["jung.html", "gyeopbatchim.html"]

failures = []


def fail(msg):
    failures.append(msg)
    print(f"  FAIL {msg}")


def ok(msg):
    print(f"  ok   {msg}")


# ---------- 1) 자리표가 낱개 파일과 같은가 (브라우저 없이) ----------

def read_data(screen):
    html = (HERE / screen).read_text(encoding="utf-8")
    m = re.search(r"var DATA = (\{.*?\});\n", html, re.S)
    if not m:
        sys.exit(f"{screen} 에서 DATA 를 찾지 못했습니다. build.js 로 다시 만들어 주세요.")
    return json.loads(m.group(1))


def check_offsets(screen):
    D = read_data(screen)
    BIN = D.get("BIN")
    if not BIN:
        fail(f"{screen} 에 묶음 자리표가 없습니다 (build.js 를 다시 돌려 주세요)")
        return None
    blob = HERE / BIN["file"]
    if not blob.exists():
        fail(f"{BIN['file']} 이 없습니다 (python tools/build_audio_bundle.py)")
        return None
    raw = blob.read_bytes()
    if len(raw) != BIN["total"]:
        fail(f"{BIN['file']} 길이가 자리표와 다릅니다 ({len(raw):,} ≠ {BIN['total']:,})"
             " — 묶음을 다시 만든 뒤 build.js 를 돌려 주세요")
        return None
    bad = 0
    for p, (start, ln) in BIN["off"].items():
        f = HERE / p
        if not f.exists() or raw[start:start + ln] != f.read_bytes():
            bad += 1
            if bad <= 3:
                print(f"       다름: {p}")
    if bad:
        fail(f"{screen}: 묶음에서 잘라낸 조각 {bad}개가 낱개 mp3 와 다릅니다")
        return None
    ok(f"자리표 {len(BIN['off'])}개가 낱개 mp3 와 바이트 단위로 같음")

    # 쓰는 소리가 모두 자리표에 들어 있는가
    used = set(D["A"].values())
    used |= {v for v in D.get("SENT_AUDIO", {}).values() if v}
    used |= {v for v in D["FX"].values() if v}
    used |= {v for v in D["SC"] if v}
    lost = sorted(used - set(BIN["off"]))
    if lost:
        fail(f"{screen}: 자리표에 없는 소리 {len(lost)}개 — {lost[:3]}")
    return BIN


# ---------- 2~4) 실제 브라우저 ----------

PROBE = """
async (path) => {
  loadBundle();
  await new Promise(r => setTimeout(r, 400));
  setSrc(path);
  const loaded = await new Promise(r => {
    player.addEventListener('loadedmetadata', () => r(true), { once: true });
    player.addEventListener('error', () => r(false), { once: true });
    player.load();
    setTimeout(() => r(false), 5000);
  });
  return { src: player.src.slice(0, 5), loaded, dur: player.duration, bundled: !!bundle.blob };
}
"""

PRIME = """
async () => {
  const res = await fetch('audio/audio.bin', { cache: 'reload' });
  const blob = await res.blob();
  await (await caches.open('hangul-audio')).put('audio/audio.bin', new Response(blob));
  return blob.size;
}
"""


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


def serve():
    h = functools.partial(Quiet, directory=str(HERE))
    srv = socketserver.TCPServer(("127.0.0.1", 0), h)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, f"http://127.0.0.1:{srv.server_address[1]}/"


def launch(p):
    """설치해 둔 크로미움을 찾아 띄운다. 환경마다 자리가 달라 몇 군데를 본다."""
    try:
        return p.chromium.launch()
    except Exception:
        pass
    roots = [os.environ.get("PLAYWRIGHT_BROWSERS_PATH", ""), "/opt/pw-browsers"]
    for root in filter(None, roots):
        for exe in sorted(pathlib.Path(root).glob("chromium*/chrome-linux*/chrome")):
            try:
                return p.chromium.launch(executable_path=str(exe))
            except Exception:
                continue
    sys.exit("크로미움을 띄우지 못했습니다.  python -m playwright install chromium")


def check_browser(screen, br, base):
    ctx = br.new_context()
    page = ctx.new_page()
    page.on("pageerror", lambda e: fail(f"{screen} 자바스크립트 오류: {e}"))
    page.goto(base + screen)
    paths = page.evaluate("() => Object.keys(DATA.BIN.off)")
    first, last = paths[0], paths[-1]

    r = page.evaluate(PROBE, first)
    (ok if (r["loaded"] and r["src"] == "http:") else fail)(
        f"인터넷 있음 · 묶음 없음 → 낱개 주소 (src={r['src']} 길이={r['dur']})")

    size = page.evaluate(PRIME)                      # 「소리 모두 받기」와 같은 상태를 만든다
    page.reload()
    ctx.set_offline(True)
    r = page.evaluate(PROBE, first)
    (ok if (r["loaded"] and r["src"] == "blob:" and (r["dur"] or 0) > 0.1) else fail)(
        f"비행기 모드 · 묶음 있음 → 묶음에서 잘라 재생 (src={r['src']} 길이={r['dur']}"
        f" 묶음={size:,}바이트)")

    # 앞에서 쓴 소리는 브라우저가 따로 쥐고 있으므로, 한 번도 안 쓴 소리로 본다
    ctx.set_offline(False)
    page.evaluate("async () => { await (await caches.open('hangul-audio')).delete('audio/audio.bin'); }")
    page.reload()
    ctx.set_offline(True)
    r = page.evaluate(PROBE, last)
    (ok if (not r["loaded"] and r["src"] == "http:") else fail)(
        f"비행기 모드 · 묶음 없음 → 안 나는 것이 정상 (src={r['src']} 읽힘={r['loaded']})")
    ctx.close()


def main():
    for screen in SCREENS:
        if not (HERE / screen).exists():
            sys.exit(f"{screen} 이 저장소 맨 위에 없습니다. docs/DICTATION.md 2절을 보세요.")

    print(f"저장소  {HERE}")
    for screen in SCREENS:
        print(f"\n■ {screen}")
        check_offsets(screen)

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("\n브라우저 확인은 건너뜁니다 (playwright 없음).")
        print("  pip install playwright && python -m playwright install chromium")
        sys.exit(1 if failures else 0)

    srv, base = serve()
    try:
        with sync_playwright() as p:
            br = launch(p)
            for screen in SCREENS:
                print(f"\n■ {screen} — 브라우저")
                check_browser(screen, br, base)
            br.close()
    finally:
        srv.shutdown()

    print()
    if failures:
        print(f"확인 실패 {len(failures)}건:")
        for f in failures:
            print(" -", f)
        sys.exit(1)
    print("모두 통과했습니다. 비행기 모드에서도 소리가 납니다.")


if __name__ == "__main__":
    main()
