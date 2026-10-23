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
| 받아쓰기 중급반 | `jung.html` | 완성 · 기초반 메뉴에 **아직 연결 안 됨** |
| 겹받침 쓰기 연습 | `gyeopbatchim.html` | 완성 · 받아쓰기 첫 화면에서 들어갑니다 |
| 3단계 생활 문장 음성 12개 | — | **아직 안 만듦** (5-1) |
| 오프라인(묶음) 연동 | — | **안 됨** (5-2) |

소리를 파일 안에 넣어 둔 미리보기입니다. 저장소를 받지 않아도 열립니다. (계정 로그인 필요)

- 받아쓰기 교실 — https://claude.ai/artifact/LskW33gytt1gqGRQkbPwKt
- 겹받침 쓰기 연습 — https://claude.ai/artifact/1Ds7L6UR7yTd358pkU1KFi

### 새 PC에서 시작하신다면

`tools/setup-newpc.ps1` 한 번이면 끝납니다. 필요한 프로그램(Node 포함)을 깔고,
저장소를 받고, **중급반이 제대로 왔는지 다시 만들어 확인까지** 합니다.
자세한 것은 [MIGRATION.md 0절](MIGRATION.md#0-새-pc에서-이어서-작업하기).

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
tools/dictation/녹음이-필요한-말.txt       아직 녹음이 없는 문장 12개
```

> ⚠️ `jung.html` 과 `gyeopbatchim.html` 은 **`index.html` 바로 옆**에 두어야 합니다.
> 소리를 `audio/aN.mp3` 상대경로로 찾기 때문에, 하위 폴더로 옮기면 소리가 나지 않습니다.

### 소리를 어떻게 찾는가

`build.js` 가 `index.html` 의 `window.AUDIO` 를 읽어, 쓰는 낱말만 골라
`{"김치": "audio/a123.mp3", …}` 형태로 결과물 안에 심습니다. 키 규칙은
[MIGRATION.md 5절](MIGRATION.md#5-소리-키-규칙)과 같습니다 (`w_낱말`).

재생은 기초반과 **똑같은 방식**입니다. `<audio>` 하나로 그냥 틀고, 음색을 다듬거나
크기를 키우거나 **빠르기를 바꾸지 않습니다.** 손대면 기초반과 다른 목소리가 됩니다.
합성 음성(브라우저 TTS)은 한 줄도 쓰지 않습니다 — 녹음이 없는 말은 소리 단추를 아예 내보내지 않습니다.

---

## 3. 고치고 다시 만들기

낱말·문장을 바꾸시려면 **`tools/dictation/build.js` 안의 자료**를 고칩니다.
`jung.html` 을 직접 고치면 다음 빌드 때 덮어써집니다.

```bash
cd tools/dictation && node build.js ../../index.html && mv -f jung.html gyeopbatchim.html ../../
```

Node 18 이상이 필요합니다. 결과는 이렇게 나옵니다.

```
jung.html 45KB
gyeopbatchim.html 41KB
녹음이 필요한 낱말 0 개 / 문장 12 개
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

## 4. 기초반에 연결하기

### 4-1. 메뉴에 넣기

`index.html` 첫 화면 메뉴에 두 줄을 더하면 어르신이 찾아 들어가실 수 있습니다.
`index.html` 을 고친 뒤에는 **반드시** 캐시 지문을 새로 찍으세요.

```bash
python tools/stamp_sw.py
```

빠뜨리면 휴대폰이 옛 화면을 계속 써서 "고쳤는데 그대로인데요"가 됩니다.

### 4-2. 오프라인에서도 열리게

`sw.js` 의 `SHELL_FILES` 에 두 줄을 더합니다.

```js
'./jung.html',
'./gyeopbatchim.html'
```

이러면 **화면**은 오프라인에서 열립니다. 다만 **소리**는 5-2를 보세요.

---

## 5. 남은 일

### 5-1. 3단계 생활 문장 음성 12개

지금은 통문장 녹음이 없어, 낱말 소리를 들으며 문장을 만드는 방식으로 되어 있습니다.
문장 목록은 `tools/dictation/녹음이-필요한-말.txt` 에 있습니다.

기초반과 **같은 목소리**(edge-tts `ko-KR-SunHiNeural`)로 만들 수 있습니다.
[MIGRATION.md 4-1절](MIGRATION.md#4-1-edge-tts-지금-쓰는-방식-무료) 참고.

만든 뒤 `build.js` 의 `DATA.SENT_AUDIO` 에 이렇게 적으면 그 단계가 바로 받아쓰기로 바뀝니다.

```js
"오늘 병원에 갑니다": "audio/s1.mp3"
```

말 속도는 기초반 규칙을 따르세요. 문장이므로 **-10%** 가 맞습니다
([MIGRATION.md 4절](MIGRATION.md#4-소리-파일-다시-만들기) 속도표).

### 5-2. 오프라인에서 소리가 안 납니다

기초반은 소리를 `audio/audio.bin` **묶음 한 덩어리**로 받아 두고,
`blob.slice(시작, 끝, 'audio/mpeg')` 로 필요한 자리만 잘라 씁니다.
받아쓰기 중급반은 아직 **낱개 `audio/aN.mp3`** 로만 재생합니다.

인터넷이 있으면 문제없지만, 「소리 모두 받기」로 묶음만 받아 둔 휴대폰에서
비행기 모드로 들어가면 **중급반 소리가 나지 않습니다.**
`index.html` 의 묶음 재생 코드를 그대로 가져다 쓰면 해결됩니다.

### 5-3. 그 밖에

- 기초반 메뉴 연결 (4-1)
- 판 올릴 때 `APP_VERSION` + `stamp_sw.py` + 태그 ([MIGRATION.md 10절](MIGRATION.md#10-판-되돌리기))

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
