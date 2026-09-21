# clips.py — 소리 조각 1,226개의 "무엇을, 얼마나 느리게 읽을지"를 index.html 에서 읽어 온다.
#
# 대본을 따로 관리하지 않습니다. index.html 안의 자료(JAUM/MOUM/BATCHIM/WORDS_DATA)가
# 유일한 원본이고, 여기서는 그것을 읽어 조각 목록을 만들 뿐입니다.
# 낱말을 추가하려면 index.html 의 자료를 고치세요.
#
# 말하기 속도는 교육 설계의 일부입니다. 함부로 바꾸지 마세요.
#   -10%  퀴즈 칭찬·점수 (문장이라 너무 느리면 답답합니다)
#   -15%  낱말, 글자 설명
#   -20%  한 글자 또렷이 읽기
#   -25%  소리를 이어 붙여 읽기 (귀로 합쳐지는 과정을 들려주는 대목)

import json
import os
import re

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IDX = os.path.join(HERE, "index.html")


def _grab(html, pat):
    m = re.search(pat, html, re.S)
    if not m:
        raise SystemExit(f"index.html 에서 찾지 못했습니다: {pat}")
    return m.group(1)


def build(html=None):
    """소리 키 -> (읽을 문장, 말하기 속도) 를 돌려준다."""
    if html is None:
        html = open(IDX, encoding="utf-8").read()

    JAUM = re.findall(r"\['(.)','(.*?)','(.*?)','(.*?)'\]", _grab(html, r"const JAUM = \[(.*?)\];"))
    MOUM = re.findall(r"\['(.)','(.*?)','(.*?)'\]", _grab(html, r"const MOUM = \[(.*?)\];"))
    CHO = dict((m[0], int(m[1])) for m in
               re.findall(r"'(.)':(\d+)", _grab(html, r"const CHO_IDX = \{(.*?)\};")))
    JUNG = dict((m[0], int(m[1])) for m in
                re.findall(r"'(.)':(\d+)", _grab(html, r"const JUNG_IDX = \{(.*?)\};")))
    WORDS = json.loads(_grab(html, r'window\.WORDS_DATA = (\{.*?\});</script>'))

    BAT = {}
    for m in re.finditer(r"'(.)': \{ name: '(.*?)', tail: '(.*?)'.*?ex: \[(.*?)\] \}",
                         _grab(html, r"const BATCHIM = \{(.*?)\n  \};")):
        g, name, tail, exs = m.groups()
        BAT[g] = (name, tail, re.findall(r"\['(.*?)','(.*?)','(.*?)'\]", exs))

    JA_SOUND = {g: s for g, _n, _e, s in JAUM}
    MO_SOUND = {g: n for g, n, _e in MOUM}

    c = {}
    for cat in WORDS.values():
        for w, _e in cat:
            c["w_" + w] = (w, "-15%")

    for g, name, ex, snd in JAUM:
        c["l1_" + g] = (f"이 글자의 이름은, {name}.", "-15%")
        c["l2_" + g] = ("첫소리에서는 소리가 없어요. 모음을 그대로 읽어요." if g == "ㅇ"
                        else f"소리는, {snd}.", "-15%")
        c["l3_" + g] = (f"예를 들면, {ex}.", "-15%")
    for g, name, ex in MOUM:
        c["l1_" + g] = (f"이 글자의 이름은, {name}.", "-15%")
        c["l2_" + g] = (f"소리도 그대로, {name}.", "-15%")
        c["l3_" + g] = (f"예를 들면, {ex}.", "-15%")

    for cho, ci in CHO.items():
        for jung, ji in JUNG.items():
            s = chr(0xAC00 + (ci * 21 + ji) * 28)
            c["s_" + s] = (s, "-20%")
            if cho != "ㅇ":                              # ㅇ은 첫소리가 없다
                c["b_" + s] = (JA_SOUND[cho] + MO_SOUND[jung], "-25%")
    for g, snd in JA_SOUND.items():
        if snd:
            c["s_" + snd] = (snd, "-20%")
    for g, snd in MO_SOUND.items():
        c["s_" + snd] = (snd, "-20%")

    EXC = {"ㄱ", "ㄷ", "ㅅ"}                              # 이름과 소리가 다른 받침
    for g, (name, tail, exs) in BAT.items():
        c["r_" + g] = ((f"조심하세요! 이름은 {name}이지만, 받침으로 쓰면, {tail}, 소리가 나요."
                        if g in EXC else
                        f"받침으로 쓰면, {name}의 끝소리, {tail}, 소리가 나요."), "-15%")
        c["t_" + tail] = (tail, "-20%")
        for made, base, _hint in exs:
            c["b2_" + made] = (base + tail, "-25%")
            c["s2_" + made] = (made, "-20%")
            c["s_" + base] = (base, "-20%")

    c["p_praise"] = ("딩동댕! 참 잘하셨어요!", "-10%")
    c["p_wrong"] = ("괜찮아요. 정답은,", "-10%")
    for n in range(11):
        c[f"sc_{n}"] = (f"10문제 가운데 {n}문제를 맞히셨어요.", "-10%")
    c["g_perfect"] = ("만점입니다! 정말 훌륭하세요!", "-10%")
    c["g_good"] = ("아주 잘하셨어요! 조금만 더 하면 만점이에요!", "-10%")
    c["g_ok"] = ("잘하고 계세요. 천천히 다시 한번 해 볼까요?", "-10%")
    return c


# 시험 음성으로 들어 볼 대표 조각들.
# 각 갈래에서 하나씩 골랐고, 특히 받침 예외(ㅅ)와 소리 합치기는 이 앱의 핵심이라 꼭 넣습니다.
SAMPLE_KEYS = [
    "l1_ㄱ", "l2_ㄱ", "l3_ㄱ",     # 글자 이름 / 소리 / 보기  (세 도막)
    "s_가", "b_가",                # 한 글자 / 「그아」 이어 읽기
    "r_ㅅ", "t_읏", "b2_밥",       # 받침 예외 설명 / 끝소리 / 「바읍」
    "w_어머니", "w_할아버지",      # 낱말
    "sc_10", "g_perfect",          # 퀴즈 총평
]

if __name__ == "__main__":
    import sys
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    c = build()
    print(f"조각 {len(c):,}개, 글자 {sum(len(t) for t, _r in c.values()):,}자")
    for k in SAMPLE_KEYS:
        t, r = c[k]
        print(f"  {k:12} {r:>5}  {t}")
