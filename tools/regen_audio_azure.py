# regen_audio_azure.py — Azure Speech(정식 API)로 소리 1,226개를 다시 만든다.
#
# 지금까지는 edge-tts(비공식 경로)로 같은 목소리를 공짜로 썼습니다. 이 도구는
# 같은 목소리를 정식 계약으로 받아 오고, 덤으로 48kHz 고음질 모델을 쓸 수 있습니다.
#
# ── 열쇠(키)는 이 파일에도, 저장소에도 들어가지 않습니다 ───────────────────
#   PowerShell:  $env:AZURE_SPEECH_KEY = "붙여넣기"
#                $env:AZURE_SPEECH_REGION = "koreacentral"
#   Git Bash:    export AZURE_SPEECH_KEY=...
#                export AZURE_SPEECH_REGION=koreacentral
#   창을 닫으면 사라집니다. 저장소에 절대 적지 마세요.
#
# ── 쓰는 법 ────────────────────────────────────────────────────────────
#   python tools/regen_audio_azure.py --voices        # 쓸 수 있는 한국어 목소리 보기
#   python tools/regen_audio_azure.py --sample        # 시험 음성 만들어 듣기 (12조각 x 설정들)
#   python tools/regen_audio_azure.py --all --preset hifi-keep --yes
#   python tools/regen_audio_azure.py --all --free --yes      # 무료(F0) 등급이면
#
# ── 요금과 속도 제한 (Azure 문서 기준) ──────────────────────────────────
#   단가        100만 자당 $15  ->  이 앱 전체 3,872자 = 약 $0.06 (80원쯤)
#   무료(F0)    60초에 20건. 1,226개면 최소 1시간. --free 를 붙이세요.
#   유료(S0)    초당 30건. 5~15분이면 끝납니다.
#   한 번 만들어 두면 끝이라, 어르신이 아무리 많이 눌러도 더 나가지 않습니다.
#
# --all 뒤에는 반드시 이어서:
#   python tools/build_audio_bundle.py
#   python tools/stamp_sw.py
#
# ── 왜 48kHz 를 받아서 다시 줄이나 ──────────────────────────────────────
# Azure 문서: "48kHz 출력 형식을 고르면 48kHz 고음질 음성 모델이 호출됩니다."
# 즉 48kHz 로 요청하면 더 좋은 모델이 읽어 줍니다. 그걸 받아 두고 용량에 맞춰
# 줄이는 편이, 처음부터 24kHz 모델로 받는 것보다 또렷합니다. 특히 ㅅ·ㅊ 같은
# 마찰음이 살아나는데, 이 앱은 받침 소리를 가르치는 앱이라 그게 중요합니다.

import argparse
import concurrent.futures as futures
import json
import os
import re
import shutil
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
import xml.sax.saxutils as sax

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")   # 윈도우 명령창에서 한글이 깨지지 않게
except Exception:
    pass

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import clips  # noqa: E402

HERE = clips.HERE
IDX = clips.IDX
AUDIO_DIR = os.path.join(HERE, "audio")
SAMPLE_DIR = os.path.join(HERE, "tools", "samples")

DEFAULT_VOICE = "ko-KR-SunHiNeural"          # 지금 쓰는 목소리. 어르신이 낯설어하지 않게 그대로.
HIFI = "audio-48khz-96kbitrate-mono-mp3"     # 48kHz 고음질 모델을 부르는 형식

# 받아 온 뒤 어떤 크기로 저장할지. (Azure 출력 형식, 다시 담을 bitrate, 표본율)
# bitrate 가 None 이면 다시 담지 않고 받은 그대로 씁니다.
PRESETS = {
    # 지금과 같은 용량인데 원본 모델만 좋아진다 — 무난한 선택
    "hifi-keep": (HIFI, "32k", "24000", "10.2MB · 지금과 같은 용량, 원본만 48kHz 고음질"),
    # 한 단계 올린다. 저장공간이 넉넉한 요즘 기기라면 이쪽
    "hifi-plus": (HIFI, "48k", "32000", "15.3MB · 뚜렷하게 좋아짐. 기기 저장공간 16MB 이상 필요"),
    # 다시 담지 않는다. 가장 좋지만 어르신 휴대폰에는 부담
    "hifi-raw":  (HIFI, None, None,     "26MB · 다시 담지 않아 손실 0. 용량이 큽니다"),
    # 예전 방식 그대로 (비교용)
    "same-as-now": ("audio-24khz-48kbitrate-mono-mp3", "32k", "24000",
                    "10.2MB · 예전과 똑같이. 비교용"),
}


def creds():
    key = os.environ.get("AZURE_SPEECH_KEY", "").strip()
    region = os.environ.get("AZURE_SPEECH_REGION", "").strip()
    if not key or not region:
        sys.exit(
            "AZURE_SPEECH_KEY 와 AZURE_SPEECH_REGION 을 환경변수로 넣어 주세요.\n"
            '  PowerShell:  $env:AZURE_SPEECH_KEY = "..."; $env:AZURE_SPEECH_REGION = "koreacentral"\n'
            "이 값은 화면에 찍히지도, 파일에 적히지도 않습니다."
        )
    return key, region


def list_voices():
    key, region = creds()
    url = f"https://{region}.tts.speech.microsoft.com/cognitiveservices/voices/list"
    req = urllib.request.Request(url, headers={"Ocp-Apim-Subscription-Key": key})
    data = json.loads(urllib.request.urlopen(req, timeout=30).read())
    ko = [v for v in data if v.get("Locale") == "ko-KR"]
    print(f"{region} 에서 쓸 수 있는 한국어 음성 {len(ko)}개\n")
    for v in sorted(ko, key=lambda v: (v["Gender"], v["ShortName"])):
        styles = ",".join(v.get("StyleList", [])) or "-"
        print(f"  {v['ShortName']:42} {v['Gender']:6} {v.get('SampleRateHertz','?'):>5}Hz  {styles[:40]}")
    print("\n지금 쓰는 목소리:", DEFAULT_VOICE)


def ssml(text, voice, rate):
    body = sax.escape(text)
    if rate:
        body = f"<prosody rate='{rate}'>{body}</prosody>"
    return (f"<speak version='1.0' xml:lang='ko-KR'>"
            f"<voice name='{voice}'>{body}</voice></speak>")


def synth(key, region, text, voice, rate, fmt, tries=4, pace=None):
    url = f"https://{region}.tts.speech.microsoft.com/cognitiveservices/v1"
    body = ssml(text, voice, rate).encode("utf-8")
    headers = {
        "Ocp-Apim-Subscription-Key": key,
        "Content-Type": "application/ssml+xml",
        "X-Microsoft-OutputFormat": fmt,
        "User-Agent": "urihangul-regen",
    }
    for n in range(tries):
        try:
            if pace:
                pace.wait()
            req = urllib.request.Request(url, data=body, headers=headers, method="POST")
            raw = urllib.request.urlopen(req, timeout=60).read()
            if raw:
                return raw
        except urllib.error.HTTPError as e:
            if e.code == 429:                       # 너무 빨리 보냄 — 쉬었다 다시
                time.sleep(3 * (n + 1))
                continue
            if e.code in (401, 403):
                sys.exit(f"인증 실패({e.code}). 키와 지역({region})이 맞는지 확인해 주세요.")
            if e.code == 400:
                sys.exit(f"요청이 거절됐습니다(400). 목소리 이름 '{voice}' 가 이 지역에 있는지 "
                         f"--voices 로 확인해 주세요.")
            time.sleep(1.5 * (n + 1))
        except Exception:
            time.sleep(1.5 * (n + 1))
    return None


class Pace:
    """요청 속도를 묶어 둔다.

    무료(F0) 등급은 텍스트 음성 변환이 **60초에 20건**으로 제한됩니다.
    1,226개를 만들려면 최소 1시간이 걸리고, 동시에 여러 건 보내면 계속 429가 납니다.
    유료(S0)는 초당 30건이라 넉넉합니다.
    """

    def __init__(self, per_minute):
        self.gap = 60.0 / per_minute if per_minute else 0.0
        self.next = 0.0
        self.lock = threading.Lock()

    def wait(self):
        if not self.gap:
            return
        with self.lock:
            now = time.monotonic()
            due = max(now, self.next)
            self.next = due + self.gap
        d = due - time.monotonic()
        if d > 0:
            time.sleep(d)


FF = None


def ffmpeg():
    global FF
    if FF is None:
        try:
            import imageio_ffmpeg
            FF = imageio_ffmpeg.get_ffmpeg_exe()
        except ImportError:
            FF = shutil.which("ffmpeg") or ""
    return FF


def shrink(raw, bitrate, rate_hz):
    if not bitrate:
        return raw
    ff = ffmpeg()
    if not ff:
        sys.exit("ffmpeg 이 없습니다.  pip install imageio-ffmpeg")
    p = subprocess.run([ff, "-hide_banner", "-loglevel", "error", "-i", "pipe:0",
                        "-ar", rate_hz, "-ac", "1", "-b:a", bitrate, "-f", "mp3", "pipe:1"],
                       input=raw, capture_output=True)
    if p.returncode != 0 or not p.stdout:
        raise RuntimeError("ffmpeg 변환 실패")
    return p.stdout


def make(items, voice, fmt, bitrate, rate_hz, workers=6, per_minute=0):
    """items: [(이름, 문장, 속도)] -> {이름: mp3 바이트}"""
    key, region = creds()
    pace = Pace(per_minute)
    out, failed = {}, []
    done = [0]

    def one(it):
        name, text, rate = it
        raw = synth(key, region, text, voice, rate, fmt, pace=pace)
        done[0] += 1
        if done[0] % 50 == 0 or done[0] == len(items):
            print(f"  {done[0]:,}/{len(items):,}", end="\r", flush=True)
        if raw is None:
            return name, None
        try:
            return name, shrink(raw, bitrate, rate_hz)
        except RuntimeError:
            return name, None

    with futures.ThreadPoolExecutor(max_workers=workers) as ex:
        for name, data in ex.map(one, items):
            if data:
                out[name] = data
            else:
                failed.append(name)
    print()
    return out, failed


def do_sample(voice, presets, workers, per_minute):
    c = clips.build()
    os.makedirs(SAMPLE_DIR, exist_ok=True)
    rows = []
    for label in presets:
        fmt, bitrate, rate_hz, note = PRESETS[label]
        d = os.path.join(SAMPLE_DIR, label)
        os.makedirs(d, exist_ok=True)
        items = [(k, c[k][0], c[k][1]) for k in clips.SAMPLE_KEYS]
        print(f"[{label}] {note}")
        got, failed = make(items, voice, fmt, bitrate, rate_hz, workers, per_minute)
        for k, data in got.items():
            open(os.path.join(d, k + ".mp3"), "wb").write(data)
        total = sum(len(v) for v in got.values())
        per = total / max(len(got), 1)
        rows.append((label, note, len(got), total, per * 1226))
        if failed:
            print("  실패:", failed)

    # 지금 쓰는 소리도 나란히 듣도록 복사
    now = os.path.join(SAMPLE_DIR, "현재")
    os.makedirs(now, exist_ok=True)
    A = json.loads(re.search(r'window\.AUDIO = (\{.*?\});</script>',
                             open(IDX, encoding="utf-8").read(), re.S).group(1))
    for k in clips.SAMPLE_KEYS:
        src = os.path.join(HERE, A[k])
        if os.path.exists(src):
            shutil.copy(src, os.path.join(now, k + ".mp3"))

    _write_compare_page(["현재"] + list(presets), c)
    print("\n예상 전체 용량")
    print(f"  {'현재':14} 10.2MB")
    for label, note, n, total, est in rows:
        print(f"  {label:14} {est/1048576:5.1f}MB   {note}")
    print(f"\n들어 보세요:  tools/samples/비교.html")


def _write_compare_page(labels, c):
    keys = clips.SAMPLE_KEYS
    head = "".join(f"<th>{l}</th>" for l in labels)
    rows = []
    for k in keys:
        text, rate = c[k]
        cells = "".join(
            f'<td><audio controls preload="none" src="{l}/{k}.mp3"></audio></td>' for l in labels)
        rows.append(f"<tr><td class=k>{k}<br><small>{rate}</small></td>"
                    f"<td class=t>{text}</td>{cells}</tr>")
    html = f"""<!doctype html><html lang=ko><meta charset=utf-8>
<title>음성 비교 — 우리 한글 교실</title>
<style>
 body{{font-family:'Malgun Gothic',sans-serif;margin:24px;background:#FBF7EF;color:#1b1b1b}}
 h1{{color:#14646E}} table{{border-collapse:collapse;width:100%}}
 th,td{{border-bottom:1px solid #ddd;padding:8px 10px;text-align:left;vertical-align:middle}}
 th{{background:#14646E;color:#fff;position:sticky;top:0}}
 .k{{font-family:monospace;white-space:nowrap;color:#555}}
 .t{{font-size:15px;max-width:340px}} audio{{width:210px;height:34px}}
 p.note{{background:#fff;border-left:4px solid #14646E;padding:10px 14px;line-height:1.6}}
</style>
<h1>음성 비교</h1>
<p class=note>
 왼쪽부터 차례로 들어 보세요. 특히 이 세 가지를 보셔야 합니다.<br>
 ① <b>r_ㅅ · t_읏</b> — ㅅ·ㅊ 마찰음이 또렷한가 (받침 가르치는 데 중요)<br>
 ② <b>b_가 · b2_밥</b> — 「그아」「바읍」이 이어 읽히는가<br>
 ③ <b>말 속도</b> — 어르신용으로 느리게 읽히는가.
 HD·MAI 계열 목소리는 속도 지정을 무시하는 경우가 있어, 여기서 꼭 확인해야 합니다.
</p>
<table><tr><th>조각</th><th>읽는 말</th>{head}</tr>
{"".join(rows)}
</table></html>"""
    open(os.path.join(SAMPLE_DIR, "비교.html"), "w", encoding="utf-8").write(html)


def do_all(voice, preset, yes, workers, per_minute):
    fmt, bitrate, rate_hz, note = PRESETS[preset]
    c = clips.build()
    print(f"목소리 {voice}")
    print(f"설정  {preset} — {note}")
    print(f"조각  {len(c):,}개 · {sum(len(t) for t, _ in c.values()):,}자")
    if not yes:
        sys.exit("\n정말 바꾸시려면 --yes 를 붙여 주세요. 지금 audio/ 는 그대로 둡니다.")

    tmp = os.path.join(HERE, "tools", "_newaudio")
    shutil.rmtree(tmp, ignore_errors=True)
    os.makedirs(tmp)

    keys = list(c)
    items = [(k, c[k][0], c[k][1]) for k in keys]
    print("\n만드는 중… (5~15분)")
    got, failed = make(items, voice, fmt, bitrate, rate_hz, workers, per_minute)
    if failed:
        shutil.rmtree(tmp, ignore_errors=True)
        sys.exit(f"{len(failed)}개를 만들지 못했습니다: {failed[:10]}\naudio/ 는 건드리지 않았습니다.")

    amap = {}
    for i, k in enumerate(keys):
        name = f"a{i}.mp3"
        open(os.path.join(tmp, name), "wb").write(got[k])
        amap[k] = "audio/" + name

    total = sum(len(v) for v in got.values())
    print(f"\n{len(amap):,}개 · {total/1048576:.2f}MB")

    # 여기까지 온 뒤에야 바꿔치기한다 (중간에 실패해도 audio/ 는 멀쩡)
    old = os.path.join(HERE, "tools", "_oldaudio")
    shutil.rmtree(old, ignore_errors=True)
    os.rename(AUDIO_DIR, old)
    os.rename(tmp, AUDIO_DIR)
    shutil.rmtree(old, ignore_errors=True)

    html = open(IDX, encoding="utf-8", newline="").read()
    block = "<script>window.AUDIO = " + json.dumps(amap, ensure_ascii=False) + ";</script>"
    html = re.sub(r"<script>window\.AUDIO = \{.*?\};</script>", block, html, flags=re.S)
    # 묶음 색인은 낡았으므로 지운다. build_audio_bundle.py 가 새로 넣는다.
    html = re.sub(r"\n?<script>window\.AUDIO_BIN = \{.*?\};</script>\n?", "\n", html, flags=re.S)
    open(IDX, "w", encoding="utf-8", newline="").write(html)

    print("\naudio/ 와 index.html 을 갱신했습니다. 이어서 이것들을 돌려 주세요:")
    print("  python tools/build_audio_bundle.py")
    print("  python tools/stamp_sw.py")
    print("  python tools/verify.py https://urihangul.vercel.app/     (푸시한 뒤)")


def main():
    ap = argparse.ArgumentParser(description="Azure Speech 로 소리를 다시 만든다")
    ap.add_argument("--voices", action="store_true", help="쓸 수 있는 한국어 목소리 보기")
    ap.add_argument("--sample", action="store_true", help="시험 음성 만들어 비교 (권장 첫 단계)")
    ap.add_argument("--all", action="store_true", help="1,226개 전부 다시 만들기")
    ap.add_argument("--voice", default=DEFAULT_VOICE)
    ap.add_argument("--preset", default="hifi-keep", choices=list(PRESETS))
    ap.add_argument("--presets", default="hifi-keep,hifi-plus",
                    help="--sample 에서 견줄 설정들 (쉼표로)")
    ap.add_argument("--yes", action="store_true", help="--all 을 정말 실행")
    ap.add_argument("--free", action="store_true",
                    help="무료(F0) 등급. 60초에 20건으로 늦춘다. 1,226개면 약 1시간")
    ap.add_argument("--workers", type=int, default=0, help="동시 요청 수 (기본: 유료 6, 무료 2)")
    a = ap.parse_args()

    per_minute = 20 if a.free else 0            # 무료 등급: 60초에 20건
    workers = a.workers or (2 if a.free else 6)

    if a.voices:
        list_voices()
    elif a.sample:
        ps = [p.strip() for p in a.presets.split(",") if p.strip()]
        bad = [p for p in ps if p not in PRESETS]
        if bad:
            sys.exit(f"모르는 설정: {bad}. 쓸 수 있는 것: {list(PRESETS)}")
        do_sample(a.voice, ps, workers, per_minute)
    elif a.all:
        do_all(a.voice, a.preset, a.yes, workers, per_minute)
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
