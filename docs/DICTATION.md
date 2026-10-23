# 받아쓰기 중급반 · 겹받침 쓰기 — 인수인계

기초를 마치신 분들이 **직접 써 보는** 과정입니다. 기초반(`index.html`)과 같은 저장소,
같은 소리 파일을 씁니다.

- 기초반·배포·소리 만들기 전반 → **[MIGRATION.md](MIGRATION.md)**
- 새 PC 준비(clone·git config·gh·pip) → **[MIGRATION.md 0절](MIGRATION.md#0-새-pc에서-이어서-작업하기)**
- 이 문서는 **받아쓰기 중급반과 겹받침 도구**, 그리고 **Claude Code 환경 이전**만 다룹니다.

최종 갱신 2026-10-23

---

## 1. 지금 상태

| 갈래 | 파일 | 상태 |
|---|---|---|
| 받아쓰기 중급반 | `jung.html` | 완성 · 기초반 첫 화면 메뉴에서 들어갑니다 |
| 겹받침 쓰기 연습 | `gyeopbatchim.html` | 완성 · 기초반·받아쓰기 양쪽에서 들어갑니다 |
| 오프라인(묶음) 연동 | — | 됩니다 · 브라우저로 확인함 |
| 3단계 생활 문장 음성 12개 | — | **아직 안 만듦** · 만들 준비는 끝 (5-1) |

> 📍 메뉴 연결과 오프라인 소리는 가지 **`wip/dictation-offline`** 에 있습니다 (`main` 아님).
> Vercel 은 가지에 미리보기만 만들고 운영 주소(`urihangul.vercel.app`)는 그대로 둡니다.
> 보시고 괜찮으면 `main` 에 합쳐 주세요. 기초반 가지와 겹치는 곳은 **5-3** 에 적어 두었습니다.

소리를 파일 안에 넣어 둔 미리보기입니다. 저장소를 받지 않아도 열립니다. (계정 로그인 필요)

- 받아쓰기 교실 — https://claude.ai/artifact/LskW33gytt1gqGRQkbPwKt
- 겹받침 쓰기 연습 — https://claude.ai/artifact/1Ds7L6UR7yTd358pkU1KFi

### 내 PC에서 이어가기

이미 `~/projects/hangul` 이 있으시면 **세 줄**이면 됩니다.

```bash
cd ~/projects/hangul
git fetch origin
git switch wip/dictation-offline        # 중급반 작업이 있는 가지
```

그 뒤 Claude 앱 → Code 탭 → 그 폴더를 고르고, 첫마디로
**"`wip/dictation-offline` 가지에서 받아쓰기 중급반을 이어서 해줘."** 하시면 됩니다.
저장소 맨 위에 **`CLAUDE.md`** 가 있어 규칙(소리를 가공하지 말 것 · 고친 뒤
`stamp_sw.py` · 커밋은 경로 지정)과 읽을 문서는 Claude 가 알아서 봅니다.

제대로 왔는지 보려면:

```bash
cd tools/dictation && node build.js ../../index.html   # 「녹음이 필요한 낱말 0 개」
cd ../.. && python tools/dictation/check_offline.py    # 비행기 모드 소리까지 확인
python -m http.server 8000                             # http://localhost:8000/
```

첫 화면 메뉴 맨 아래에 **📝 받아쓰기 교실 · 🧩 겹받침 쓰기 연습** 두 줄이 보이면 맞습니다.

> `main` 에는 아직 없습니다. `git switch main` 하시면 메뉴 두 줄과 오프라인 소리가
> 없는 옛 화면이 나옵니다. 합치는 것은 **5-3** 을 보세요.

### 처음 쓰는 PC라면

`tools/setup-newpc.ps1` 한 번이면 끝납니다. 필요한 프로그램(Node 포함)을 깔고,
저장소를 받고, **중급반이 제대로 왔는지 다시 만들어 확인까지** 합니다. 중급반 가지가
따로 있으면 그것도 알려 줍니다. 자세한 것은
[MIGRATION.md 0절](MIGRATION.md#0-새-pc에서-이어서-작업하기).

```powershell
irm https://raw.githubusercontent.com/hisdream64-commits/hangul/main/tools/setup-newpc.ps1 -OutFile setup-newpc.ps1
powershell -ExecutionPolicy Bypass -File .\setup-newpc.ps1
```

### 배우는 내용

**1부 낱말 쓰기** — 단계마다 10문제를 무작위로 냅니다.

| 단계 | 내용 | 보기 |
|---|---|---|
| 1 | 받침 없는 낱말 | 모자 · 바지 · 사과 · 어머니 |
| 2 | 받침 있는 낱말 | 김치 · 수건 · 병원 · 경로당 |
| 3 | 소리와 글자가 다른 낱말 | 부엌 · 무릎 · 밥솥 · 깻잎 |
| 4 | 겹받침 낱말 | 값 · 흙 · 닭 · 많다 · 짧다 |

**2부 문장 쓰기** — 1단계 짧은 인사말(글자 카드) · 2단계 띄어 쓰는 인사말(낱말 카드) ·
3단계 생활 문장(소리대로 쓴 말과 바른 말 가리기)

쓰는 방법은 두 가지입니다. **글자 만들어 쓰기**(첫소리 → 가운뎃소리 → 받침을 차례로 골라
글자를 조립, 틀린 자리를 짚어 줌)와 **종이에 쓰기**(듣고 종이에 쓴 뒤 정답을 열어 스스로 채점).

**겹받침 도구** — 배우기(11가지) · 받침 채워 쓰기 · 듣고 쓰기 · 어느 쪽이 소리 날까요

---

## 2. 파일 구성

```
jung.html                             받아쓰기 중급반 (만들어진 결과물)
gyeopbatchim.html                     겹받침 쓰기 연습 (만들어진 결과물)
tools/dictation/build.js              위 둘을 만드는 스크립트 ← 고칠 곳은 여기
tools/dictation/jung.template.html         화면·동작 원본
tools/dictation/gyeopbatchim.template.html 화면·동작 원본
tools/dictation/check_offline.py      비행기 모드에서 소리가 나는지 확인 (브라우저로)
tools/dictation/녹음이-필요한-말.txt       아직 녹음이 없는 문장 12개 (build.js 가 씁니다)
tools/dictation/문장목록.json              3단계 문장 목록 (build.js 가 씁니다 · clips.py 가 읽습니다)
CLAUDE.md                            작업 규칙 (Claude 가 세션 시작 때 읽습니다)
```

> 뒤의 두 파일은 **손으로 고치지 마세요.** `build.js` 를 돌릴 때마다 다시 쓰입니다.

> ⚠️ `jung.html` 과 `gyeopbatchim.html` 은 **`index.html` 바로 옆**에 두어야 합니다.
> 소리를 `audio/aN.mp3` 상대경로로 찾기 때문에, 하위 폴더로 옮기면 소리가 나지 않습니다.

### 소리를 어떻게 찾는가

`build.js` 가 `index.html` 의 `window.AUDIO` 를 읽어, 쓰는 낱말만 골라
`{"김치": "audio/a123.mp3", …}` 형태로 결과물 안에 심습니다. 키 규칙은
[MIGRATION.md 5절](MIGRATION.md#5-소리-키-규칙)과 같습니다 (`w_낱말`).

재생은 기초반과 **똑같은 방식**입니다. `<audio>` 하나로 그냥 틀고, 음색을 다듬거나
크기를 키우거나 **빠르기를 바꾸지 않습니다.** 손대면 기초반과 다른 목소리가 됩니다.
합성 음성(브라우저 TTS)은 한 줄도 쓰지 않습니다 — 녹음이 없는 말은 소리 단추를 아예 내보내지 않습니다.

### 오프라인에서도 소리가 납니다

기초반에서 「소리 모두 받기」를 누르면 소리가 낱개 mp3 가 아니라 `audio/audio.bin`
**한 덩어리**로 저장됩니다. 그래서 낱개 주소(`audio/aN.mp3`)로 틀면 비행기 모드에서
소리가 나지 않습니다. 중급반도 기초반과 똑같이, 저장해 둔 묶음을 열어 두고
필요한 자리만 `blob.slice()` 로 잘라 씁니다. **자리를 잘라 내기만 하므로 목소리는
조금도 달라지지 않습니다.**

자리표는 `build.js` 가 `window.AUDIO_BIN` 을 읽어 쓰는 소리 127개만큼만 심습니다.
묶음이 없으면(아직 안 받았거나 인터넷이 있으면) 예전처럼 낱개 주소로 재생합니다.

**인터넷이 있는 PC에서 🔊 를 눌러 보는 것으로는 이게 멀쩡한지 알 수 없습니다.**
그 상태를 실제로 만들어 보는 확인 도구를 넣어 두었습니다.

```bash
pip install playwright && python -m playwright install chromium   # 처음 한 번
python tools/dictation/check_offline.py
```

네 가지를 봅니다 — 묶음에서 잘라낸 127조각이 낱개 mp3 와 **바이트 단위로** 같은가 ·
인터넷이 있으면 낱개 주소로 재생하는가 · 묶음을 받아 둔 뒤 비행기 모드에서 `blob:` 로
소리가 읽히는가 · 묶음이 없는 비행기 모드에서는 안 나는가(그게 정상).
`playwright` 가 없으면 바이트 비교만 하고 넘어갑니다.

---

## 3. 고치고 다시 만들기

낱말·문장을 바꾸시려면 **`tools/dictation/build.js` 안의 자료**를 고칩니다.
`jung.html` 을 직접 고치면 다음 빌드 때 덮어써집니다.

```bash
cd tools/dictation && node build.js ../../index.html && mv -f jung.html gyeopbatchim.html ../../
```

Node 18 이상이 필요합니다. 결과는 이렇게 나옵니다.

```
jung.html 50KB
gyeopbatchim.html 46KB
녹음이 필요한 낱말 0 개 / 문장 12 개
통문장 받아쓰기  0 / 12 문장
오프라인 소리  묶음 자리표 127개 넣었습니다 (audio/audio.bin)
```

**「녹음이 필요한 낱말」이 0이 아니면 멈추세요.** 그 낱말은 `index.html` 자료에 없어서
소리가 나지 않습니다. 기초반에 낱말을 먼저 추가하고 소리를 만든 뒤에 쓰세요.

> ⚠️ `build.js` 는 **보이는 낱말과 들리는 소리가 어긋나면 일부러 실패합니다.**
> 받아쓰기에서 화면에는 「괜찮다」가 뜨는데 소리는 "괜찮습니다"가 나오면 학습자가
> 틀린 답을 쓰게 됩니다. 실제로 그 버그가 있었고, 그래서 검사를 넣었습니다.

### 소리까지 넣은 미리보기

저장소를 올리지 않고 **그 자리에서 들어 보실 때** 씁니다. 소리 127개를 파일 안에
넣으므로 한 개가 1.6MB쯤 됩니다. 배포용이 아니라 확인용입니다.

```bash
cd tools/dictation && node build.js ../../index.html --preview
```

`jung-preview.html` 과 `gyeopbatchim-preview.html` 이 생깁니다. 더블클릭해서 열어도
소리가 납니다. 확인이 끝나면 지우세요 — 저장소에는 넣지 않습니다.

---

## 4. 기초반에 연결하기 (끝났습니다)

### 4-1. 메뉴

`index.html` 첫 화면 메뉴 맨 아래 두 줄이 들어가 있습니다. 다른 메뉴와 달리
화면을 바꾸는 단추가 아니라 **주소로 넘어가는 `<a>`** 입니다.

```html
<a class="menu-btn" href="jung.html">…받아쓰기 교실 (중급)…</a>
<a class="menu-btn" href="gyeopbatchim.html">…겹받침 쓰기 연습…</a>
```

그래서 화면 바꾸기 코드는 `data-go` 가 있는 줄만 집어 갑니다
(`document.querySelectorAll('.menu-btn[data-go]')`). 메뉴를 더하실 때 이 점만 기억하세요.

### 4-2. 오프라인에서 열리기

`sw.js` 의 `SHELL_FILES` 에 `'./jung.html'`, `'./gyeopbatchim.html'` 이 들어가 있습니다.
소리도 납니다 ([2절 오프라인](#오프라인에서도-소리가-납니다)).

### 4-3. 화면을 고친 뒤에는 반드시

```bash
python tools/stamp_sw.py
```

빠뜨리면 휴대폰이 옛 화면을 계속 써서 "고쳤는데 그대로인데요"가 됩니다.
이 스크립트는 이제 **`index.html` · `jung.html` · `gyeopbatchim.html` 세 화면**의 지문을
함께 찍습니다. 중급반만 고친 날에도 캐시 이름이 바뀝니다.

---

## 5. 남은 일

### 5-1. 3단계 생활 문장 음성 12개 — 이것만 남았습니다

지금은 통문장 녹음이 없어, 낱말 소리를 들으며 문장을 만드는 방식으로 되어 있습니다.
녹음이 들어오면 그 단계가 **통문장 받아쓰기로 저절로 바뀝니다.**

**손으로 적어 넣을 것은 없습니다.** 문장 목록은 `build.js` 가 `문장목록.json` 으로
내보내고, `tools/clips.py` 가 그것을 읽어 `d_<문장>` 키로 소리를 만듭니다.
인터넷이 되는 PC에서 이 네 줄이면 끝납니다.

```bash
python tools/regen_audio_edge.py --missing               # 없는 조각만 만들기
python tools/build_audio_bundle.py                       # 묶음 다시 만들기
python tools/stamp_sw.py                                 # 캐시 지문
cd tools/dictation && node build.js ../../index.html && mv -f jung.html gyeopbatchim.html ../../
```

`--missing` 은 **이미 있는 소리를 건드리지 않습니다.** 대본에 있는데 녹음이 없는 조각만
`a1226` 부터 뒤에 덧붙입니다. 어르신이 듣던 소리는 한 개도 바뀌지 않고, 15~20분 기다릴 일도 없습니다.

> ⚠️ `--missing` 은 기초반 가지 **`wip/voice-guide`** 에서 만들어진 기능입니다.
> `main` 에만 있는 상태라면 아직 없습니다. 먼저 그 가지를 `main` 에 합치시거나
> (`git merge wip/voice-guide`), 그 가지에서 위 명령을 돌리세요.
> 자세한 것은 [MIGRATION.md 0-1절](MIGRATION.md#0-1-진행-중인-작업-이어받기-2026-10-23-기준).

목소리는 기초반과 같은 edge-tts `ko-KR-SunHiNeural`, 말 속도는 문장이므로 **-10%** 로
`clips.py` 가 알아서 잡습니다 ([MIGRATION.md 4절](MIGRATION.md#4-소리-파일-다시-만들기) 속도표).

끝난 뒤 `build.js` 가 이렇게 나오면 된 것입니다.

```
녹음이 필요한 낱말 0 개 / 문장 0 개
통문장 받아쓰기  12 / 12 문장
오프라인 소리  묶음 자리표 139개 넣었습니다 (audio/audio.bin)
```

> ⚠️ `edge-tts` 는 `speech.platform.bing.com` 에 연결합니다. 회사망이나 클라우드 환경에서는
> 막혀 있을 수 있습니다. 집 PC나 휴대폰 테더링에서 하시면 됩니다.

### 5-2. 그 밖에

- `audio/` 의 mp3 가 32kbps 로 세게 눌려 있습니다. 원본이 남아 있으면 더 좋게 다시 뽑을 수
  있습니다 (`tools/dictation/녹음이-필요한-말.txt` 아래쪽 ffmpeg 명령)

### 5-3. 다른 가지와 겹치는 곳 (합치실 때 보세요)

같은 저장소에서 기초반(`wip/voice-guide`)과 고급반(`go/`)이 함께 돌아갑니다.
고급반은 `go/` 안에만 있어 겹치지 않습니다. 기초반 가지와는 겹칩니다.

미리 합쳐 보았습니다(`git merge wip/voice-guide`). 부딪히는 곳은 **두 파일, 네 군데**입니다.

| 파일 | 결과 | 어떻게 |
|---|---|---|
| `tools/clips.py` | 저절로 합쳐집니다 | 둘 다 `build()` 끝쪽에 더하는데 자리가 달라 안 부딪힙니다. 합친 뒤 `python tools/clips.py` 가 **1,252개**(1,226 + 안내 14 + 문장 12)를 보여 주면 맞습니다 |
| `sw.js` | 부딪힘 (지문 한 줄) | 아무 쪽이나 고르고 **`python tools/stamp_sw.py` 를 다시 돌리면** 올바른 지문이 찍힙니다 |
| `index.html` 메뉴 | 부딪힘 | `wip/voice-guide` 쪽(`<div class="menu-item">` 으로 감싸고 🔊 를 나란히 둔 것)을 **살리고**, 그 아래에 중급반 두 줄(`<a class="menu-btn" href="jung.html">`, `…gyeopbatchim.html`)을 그대로 붙이세요 |
| `index.html` 메뉴 선택자 | 부딪힘 | `wip/voice-guide` 쪽(`go()` 에 `history.pushState` 를 넣은 것)을 **살리고**, 그 안의 `querySelectorAll('.menu-btn')` 만 **`'.menu-btn[data-go]'`** 로 바꾸세요. 안 바꾸면 중급반 줄을 눌렀을 때 `go(undefined)` 가 불려 화면이 하나도 안 보입니다 |

- **`APP_VERSION` 은 올리지 않았습니다** (`1.1` 그대로). `wip/voice-guide` 가 `1.2` 와
  `v1.2` 태그를 쓰기로 해 두었기 때문입니다. 중급반 메뉴는 그 판에 같이 실리면 됩니다.
  화면이 새것으로 바뀌는 것은 판 번호가 아니라 `stamp_sw.py` 의 캐시 지문이 합니다 (4-3).
- 소리 번호도 겹칩니다. 두 가지가 모두 `a1226` 부터 쓰려고 합니다. **합친 뒤에
  `--missing` 을 한 번만** 돌리면 26개(14 + 12)가 한꺼번에 제 번호를 받습니다.
  따로따로 돌리면 번호가 어긋나 묶음을 다시 만들어야 합니다.

---

## 6. Claude Code 환경 옮기기

새 노트북에서 **같은 작업 환경**을 만드는 방법입니다. 저장소와는 별개입니다.

### 6-1. 설정 파일

Claude 데스크톱 앱(https://claude.ai/download)을 깔고 같은 계정으로 로그인한 뒤,
`~/.claude/settings.json` 에 넣습니다.

```json
{
  "permissions": { "defaultMode": "bypassPermissions" },
  "model": "claude-opus-5-5",
  "hooks": {
    "Stop": [
      {
        "hooks": [
          { "type": "command", "command": "bash /c/Users/<사용자>/.claude/skills/gstack/hosts/claude/hooks/timeline-stop-hook", "timeout": 5 }
        ]
      }
    ]
  },
  "effortLevel": "medium",
  "autoUpdatesChannel": "latest",
  "skipDangerousModePermissionPrompt": true,
  "inputNeededNotifEnabled": true,
  "agentPushNotifEnabled": true,
  "theme": "dark"
}
```

`<사용자>` 를 새 노트북 계정 이름으로 바꾸세요. 경로가 틀리면 훅이 조용히 실패합니다.
gstack 을 안 쓰실 거면 `hooks` 는 통째로 지우면 됩니다.

> ⚠️ `defaultMode: bypassPermissions` 는 **묻지 않고 실행**합니다.
> 공용 노트북이라면 이 줄을 빼세요.

### 6-2. gstack 스킬 (60개)

복사하지 말고 새로 설치하세요. 설치 과정에서 경로를 새로 잡아 줍니다.

```bash
git clone --single-branch --depth 1 https://github.com/garrytan/gstack.git ~/.claude/skills/gstack && cd ~/.claude/skills/gstack && ./setup
```

### 6-3. gbrain (기억)

```bash
gbrain bootstrap harness --harness all --yes
```

기억을 그대로 옮기시려면 `~/.gbrain/` 폴더를 복사하세요.
두 노트북에서 **같은 기억을 함께** 쓰시려면 한쪽에서 공유 서버를 띄우고 양쪽을 붙입니다.

```bash
gbrain serve --http
```

> 💡 한 노트북에서 세션을 여러 개 켜면 `brain.pglite is open in another gbrain serve` 가
> 뜹니다. 기억 파일은 한 번에 한 서버만 열 수 있어서 그렇습니다. 세션 하나를 닫거나
> 위의 공유 서버로 바꾸면 됩니다.

### 6-4. 복사할 것 / 하지 말 것

| | 파일 | 비고 |
|---|---|---|
| ✅ | `~/.claude/settings.json` | 6-1 내용 |
| ✅ | `~/.gbrain/` | 기억을 옮길 때만 |
| ✅ | `~/.claude.json` 의 `mcpServers` 블록 | **블록만** 떼어 옮기세요 |
| ❌ | `~/.claude/.credentials.json` | 로그인 토큰 — 새로 로그인 |
| ❌ | `~/.claude.json` 통째로 | 옛 PC 경로와 입력 기록이 들어 있습니다 |
| ❌ | `~/.claude/projects/`, `sessions/` | 옛 PC 경로에 묶인 기록 |

---

## 7. 대화를 그대로 이어가기

| 방법 | 쓰는 때 | 조건 |
|---|---|---|
| Remote Control | 이 PC를 켜 둔 채 다른 기기에서 조작 | 이 PC가 켜져 있어야 함 |
| 세션을 클라우드로 옮기기 | 이 PC를 꺼도 이어가기 | 파일은 저장소 기준 |
| 새 세션 + 이 문서 | 가장 단순 | 저장소만 있으면 됨 |

새 노트북에서 새로 시작하실 때는 이렇게 말씀하시면 됩니다.

> `~/projects/hangul` 에서 작업합니다. `docs/MIGRATION.md` 와 `docs/DICTATION.md` 를
> 읽고 시작해 주세요.

---

## 8. 점검

- [ ] `node --version` 이 18 이상
- [ ] `jung.html` · `gyeopbatchim.html` 이 `index.html` 옆에 있다
- [ ] 브라우저로 `jung.html` 을 열고 🔊 를 눌렀을 때 **소리가 난다**
- [ ] `cd tools/dictation && node build.js ../../index.html` 이 오류 없이 끝난다
- [ ] 「녹음이 필요한 낱말 0 개」가 나온다
- [ ] 「오프라인 소리 묶음 자리표 …개」가 나온다 (0개나 안내문이면 묶음이 없는 것)
- [ ] 기초반 첫 화면 맨 아래 메뉴에 받아쓰기·겹받침 두 줄이 보인다
- [ ] `python tools/dictation/check_offline.py` 가 「모두 통과했습니다」로 끝난다
- [ ] (마지막으로 휴대폰에서) 「소리 모두 받기」 → 비행기 모드 → 받아쓰기에서 **소리가 난다**
