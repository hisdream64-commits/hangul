# pc_record.py — 녹음이 필요한 말을 PC에서 한 번에 처리한다. (인터넷 되는 PC 전용)
#
#   PowerShell 에 이 한 줄:
#     cd $HOME\projects\hangul; git fetch; git switch main-ta7yke; git pull; python tools\pc_record.py
#
# 하는 일 (순서대로, 하나라도 실패하면 그 자리에서 멈춥니다)
#   1. 준비 확인 — 가지, 다른 작업이 섞였는지, 파이썬 패키지, Node
#   2. 대본에 있는데 녹음이 없는 말 만들기          regen_audio_edge.py --missing
#   3. 글을 고친 안내 말 다시 녹음 (첫 화면 인사)   regen_audio_edge.py --redo ui_greet
#   4. 소리 묶음 다시 만들기                        build_audio_bundle.py
#   5. 받아쓰기 화면 다시 만들기 (묶음이 바뀌었으므로) tools/dictation/build.js
#   6. 캐시 지문                                    stamp_sw.py
#   7. 확인 — 소리 전수(verify.py) · 받아쓰기 오프라인(check_offline.py)
#   8. 커밋하고 가지(main-ta7yke)에 올리기. main(운영)에는 올리지 않습니다.
#
# 중간에 멈춰도 다시 실행하면 이어서 합니다(이미 만든 녹음은 다시 받지 않음).

import os
import shutil
import socket
import subprocess
import sys
import time
import urllib.request

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BRANCH = "main-ta7yke"
REDO = ["ui_greet"]                      # 글을 고친 안내 말. 다음에 또 고치면 여기에 더하세요.
# build.js 가 함께 쓰는 목록 두 개. git 이 한글 이름을 \354… 처럼 따옴표로 감싸 보여 주므로
# 비교는 core.quotepath=false 로 받은 이름으로 합니다.
DICT_LISTS = ("tools/dictation/문장목록.json", "tools/dictation/녹음이-필요한-말.txt")
OURS = ("audio/", "index.html", "sw.js", "jung.html", "gyeopbatchim.html", "tools/__pycache__/") + DICT_LISTS
PY = sys.executable
ENV = dict(os.environ, PYTHONIOENCODING="utf-8")


def stop(msg):
    print("\n" + "=" * 60)
    print("❌ 멈췄습니다. " + msg)
    print("이 창의 글을 그대로 복사해서 Claude 에게 보여 주세요.")
    print("=" * 60)
    sys.exit(1)


def step(n, title):
    print(f"\n[{n}/8] {title}")


def run(args, cwd=HERE, what=""):
    r = subprocess.run(args, cwd=cwd, env=ENV)
    if r.returncode != 0:
        stop(f"{what or ' '.join(args)} 이(가) 실패했습니다.")


def git(*args):
    return subprocess.run(["git", "-c", "core.quotepath=false", *args], cwd=HERE, capture_output=True, text=True,
                          encoding="utf-8", errors="replace")


def precheck():
    step(1, "준비 확인")
    if not os.path.exists(os.path.join(HERE, ".git")):
        stop(f"저장소 폴더가 아닙니다: {HERE}")
    br = git("rev-parse", "--abbrev-ref", "HEAD").stdout.strip()
    if br != BRANCH:
        stop(f"지금 가지가 {br} 입니다. 먼저  git switch {BRANCH}")
    # 이 도구가 고치는 파일 말고 다른 것이 바뀌어 있으면 남의 작업이 섞일 수 있어 멈춘다
    others = []
    for line in git("status", "--porcelain", "--untracked-files=no").stdout.splitlines():
        path = line[3:].strip().strip('"')
        if not path.startswith(OURS):
            others.append(path)
    if others:
        stop("이 도구와 상관없는 파일이 고쳐져 있습니다 (다른 작업이 섞일 수 있음):\n  "
             + "\n  ".join(others[:10]))
    print("  ✓ 가지", BRANCH)

    try:
        import edge_tts, imageio_ffmpeg  # noqa: F401
    except ImportError:
        print("  파이썬 패키지를 설치합니다…")
        run([PY, "-m", "pip", "install", "--quiet", "-r", "tools/requirements.txt"],
            what="패키지 설치")
    print("  ✓ 파이썬 패키지")

    if not shutil.which("node"):
        stop("Node.js 가 없습니다. 받아쓰기 화면을 다시 만들 때 필요합니다.\n"
             "  winget install OpenJS.NodeJS.LTS   를 실행하고, PowerShell 을 새로 연 뒤 다시 해 주세요.")
    print("  ✓ Node.js")

    try:
        socket.create_connection(("speech.platform.bing.com", 443), timeout=10).close()
    except OSError:
        stop("녹음 서버(speech.platform.bing.com)에 연결되지 않습니다. 인터넷을 확인해 주세요.")
    print("  ✓ 녹음 서버 연결")


def free_port():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


def check():
    step(7, "확인")
    port = free_port()
    srv = subprocess.Popen([PY, "-m", "http.server", str(port), "--bind", "127.0.0.1"],
                           cwd=HERE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        url = f"http://127.0.0.1:{port}/"
        for _ in range(50):
            try:
                urllib.request.urlopen(url, timeout=2).read(1)
                break
            except OSError:
                time.sleep(0.2)
        run([PY, "tools/verify.py", url], what="소리 전수 확인(verify.py)")
    finally:
        srv.terminate()
    run([PY, "tools/dictation/check_offline.py"], what="받아쓰기 오프라인 확인(check_offline.py)")


def main():
    os.chdir(HERE)
    precheck()

    step(2, "녹음이 없는 말 만들기")
    run([PY, "tools/regen_audio_edge.py", "--missing"], what="새 말 녹음")

    step(3, "글을 고친 안내 말 다시 녹음: " + ", ".join(REDO))
    run([PY, "tools/regen_audio_edge.py", "--redo", *REDO], what="다시 녹음")

    step(4, "소리 묶음 다시 만들기")
    run([PY, "tools/build_audio_bundle.py"], what="묶음 만들기")

    step(5, "받아쓰기 화면 다시 만들기")
    d = os.path.join(HERE, "tools", "dictation")
    run(["node", "build.js", os.path.join("..", "..", "index.html")], cwd=d, what="받아쓰기 화면 만들기")
    for name in ("jung.html", "gyeopbatchim.html"):
        os.replace(os.path.join(d, name), os.path.join(HERE, name))   # 윈도우에서도 덮어쓰기

    step(6, "캐시 지문")
    run([PY, "tools/stamp_sw.py"], what="캐시 지문")

    check()

    step(8, f"커밋하고 가지({BRANCH})에 올리기")
    git("checkout", "--", "tools/__pycache__")          # 파이썬이 저절로 고친 파일은 되돌린다
    r = git("add", "--", "audio", "index.html", "sw.js", "jung.html", "gyeopbatchim.html", *DICT_LISTS)
    if r.returncode != 0:
        stop("git add 실패:\n" + r.stderr)
    if not git("diff", "--cached", "--quiet").returncode:
        print("  바뀐 것이 없습니다. 이미 끝난 상태입니다.")
    else:
        r = git("commit", "-m",
                "소리 녹음: 녹음이 없던 말 + 첫 화면 인사 「한글뚝딱」 다시 녹음\n\n"
                "tools/pc_record.py 로 PC에서 만듦 (edge-tts SunHi). 묶음·받아쓰기 화면·캐시 지문 갱신,\n"
                "verify.py · check_offline.py 통과.")
        if r.returncode != 0:
            stop("커밋 실패:\n" + r.stdout + r.stderr)
        print("  ✓ 커밋")
    r = git("push", "-u", "origin", BRANCH)
    if r.returncode != 0:
        stop("GitHub 에 올리지 못했습니다 (녹음과 커밋은 PC에 남아 있습니다):\n" + r.stderr)
    print("  ✓ GitHub 에 올림")

    print("\n" + "=" * 60)
    print("✅ 끝났습니다. 이제 Claude 에게  「main에 합쳐 줘」  라고 말씀하세요.")
    print("=" * 60)


if __name__ == "__main__":
    main()
