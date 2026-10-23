# 한글 교실 고급반 — 다른 노트북으로 옮기기

이 문서 하나로 **새 노트북에 작업 환경을 깔고, 고급반 웹앱 작업을 이어서** 할 수 있도록 적었습니다.

- 만든 것: **한글 교실 고급반** (기초반 → 중급반 다음 과정)
- 쓰던 컴퓨터: Windows 11, 사용자 `Jb`, Git Bash
- 갱신일: 2026-10-23
- 함께 받는 것: `hangul-go.zip` (앱 + 음성 375개 + 도구 + 이 문서)

> ⚠️ **지금 고급반은 어느 저장소에도 올라가 있지 않습니다.** 챗에 올린 `hangul-go.zip` 이
> 유일한 사본입니다. 새 노트북에서 가장 먼저 할 일은 이것을 **저장소에 넣고 푸시**하는
> 것입니다(5절). 기초반 `hisdream64-commits/hangul` 은 이미 올라가 있어 안전합니다.

---

## 0. 급하면 이것만 — 30분 설치

새 노트북(윈도우 기준)에서 Git Bash 를 열고 차례대로 합니다.

```bash
# 1) 기본 도구 — 이미 있으면 건너뜁니다
#    Git, Node.js 24+, Python 3.12+, Bun 1.4.2+ 를 각 홈페이지에서 설치
node -v && python -V && bun -v && git --version

# 2) Claude Code 설치 후 같은 계정으로 로그인 (설정 일부가 계정 따라 옵니다)

# 3) gstack 스킬 61개
git clone --single-branch --depth 1 https://github.com/garrytan/gstack.git ~/.claude/skills/gstack \
  && cd ~/.claude/skills/gstack && ./setup

# 4) 음성 만들기 도구
pip install edge-tts

# 5) 저장소
mkdir -p ~/projects && cd ~/projects
git clone https://github.com/hisdream64-commits/hangul.git      # 기초반
```

그다음 Claude Code 안에서 `/setup-gbrain` 을 실행해 gbrain(기억)을 연결하고,
`~/.claude/settings.json` 을 3절 내용으로 맞추면 끝입니다.

고급반 파일은 `hangul-go.zip` 을 풀어 쓰시면 되고, 바로 열어 보려면:

```bash
cd hangul-go && npx -y http-server -p 8777 -c-1
# 브라우저에서 http://localhost:8777/hangul-go.html
```

---

## 1. 옮겨야 하는 것 — 한눈에

| 갈래 | 지금 상태 | 옮기는 법 |
|---|---|---|
| 계정 설정 | Remote Control 켬, PR 닫히면 자동 보관, 브랜치 접두사 `claude` | **자동.** 같은 계정 로그인만 하면 따라옵니다 |
| 지난 대화 | `~/.claude/sessions`, `~/.claude/projects/*.jsonl` | 이 컴퓨터 로컬. 들고 가려면 폴더째 복사 |
| Claude Code 설정 | `~/.claude/settings.json` | 3절 그대로 붙여넣기 (훅 경로 주의) |
| 스킬 | gstack **1.91.181.0**, 스킬 61개 | 0절 명령으로 재설치 |
| 플러그인 | 마켓플레이스 `anthropics/claude-plugins-official` | 새 노트북에서 다시 추가 |
| MCP | `gbrain` (stdio) | `/setup-gbrain` |
| gbrain 기억 | `~/.gbrain/brain.pglite` (로컬 DB) | 4절 — 내보내기 또는 공유 전환 |
| 외부 도구 | Node 24.20.0 · Python 3.13.14 · Bun 1.4.4 · edge-tts 7.2.8 · gh · Aside CLI | 각각 설치 |
| 저장소 | `~/projects/hangul` 외 9개 | `git clone` |
| **고급반 앱** | **임시 폴더에만 있음** | `hangul-go.zip` → 저장소 (5절) |

**복사하면 안 되는 것**

- `~/.claude/.credentials.json` — 로그인 토큰입니다. 새 노트북에서 로그인하세요
- `~/.claude.json` **통째로** — `machineID`·`userID`·이 컴퓨터 경로 17개가 들어 있습니다
- 원격이 없는 저장소 `~/Documents/kids-cinema-web`, `~/Documents/thegrain` 은
  복사하지 않으면 못 가져갑니다. 옮기기 전에 GitHub 에 올려 두세요

---

## 2. 지금 하던 대화를 이어받기

Remote Control 이 켜져 있어 **새 노트북에서 같은 계정으로 Claude 앱을 열면 이 세션이
목록에 그대로 보입니다.** 대화 맥락을 잃지 않고 이어서 시킬 수 있습니다.

단, 세션 **기록 원본**과 지난 대화 검색은 이 컴퓨터 안에만 있습니다. 옛 대화까지
필요하면 `~/.claude/sessions` 와 `~/.claude/projects` 를 복사하세요.

---

## 3. Claude Code 설정

새 노트북의 `~/.claude/settings.json` 을 이렇게 맞춥니다.

```json
{
  "permissions": { "defaultMode": "bypassPermissions" },
  "model": "claude-opus-5-5",
  "effortLevel": "medium",
  "autoUpdatesChannel": "latest",
  "skipDangerousModePermissionPrompt": true,
  "inputNeededNotifEnabled": true,
  "agentPushNotifEnabled": true,
  "theme": "dark",
  "hooks": {
    "Stop": [
      { "hooks": [ { "type": "command",
        "command": "bash $HOME/.claude/skills/gstack/hosts/claude/hooks/timeline-stop-hook",
        "timeout": 5 } ] }
    ]
  }
}
```

**두 가지 주의**

1. 원래 파일에는 훅 경로가 `/c/Users/Jb/...` 로 박혀 있었습니다. 위처럼 `$HOME` 으로
   바꾸거나 새 사용자 이름으로 고쳐야 합니다. gstack `./setup` 이 훅을 알아서 넣어
   주기도 하니, **훅 부분을 빼고 넣은 뒤 setup 을 돌리는 편**이 안전합니다.
2. `bypassPermissions` 와 `skipDangerousModePermissionPrompt` 는 **승인 창 없이 명령이
   실행되는** 설정입니다. 편하지만 그만큼 위험하니, 모르고 켜지지 않도록 새 노트북에서
   의식하고 켜 주세요.

---

## 4. gbrain (기억) 옮기기

지금 구성입니다.

| 항목 | 값 |
|---|---|
| CLI | `gbrain` 0.60.388.0 (`~/.bun/bin/gbrain.exe`) |
| MCP 등록 | `gbrain serve --surface full`, 환경변수 `GBRAIN_SOURCE=default` |
| 엔진 | PGLite (로컬 파일 DB) — `~/.gbrain/brain.pglite` |
| 스키마 | `gbrain-base-v2` · 임베딩 꺼짐 · 자동 기록 꺼짐 · 공개 범위 `world` |

설치는 Claude Code 안에서 `/setup-gbrain` 이면 끝납니다(CLI 설치 + 브레인 생성 + MCP 등록).
기억 내용은 **둘 중 하나**를 고르세요.

```bash
# (가) 복사본 — 지금 컴퓨터에서 내보내고, 새 노트북에서 들여옵니다
gbrain export --dir ~/gbrain-snapshot      # 여기서
gbrain import ~/gbrain-snapshot            # 새 노트북에서
```
→ 그 시점의 복사본이라 **두 컴퓨터의 기억이 따로 자랍니다.**

```bash
# (나) 공유 — 브레인을 Postgres(Supabase)로 올려 두 노트북이 같은 기억을 봅니다
gbrain migrate --to postgres
```
→ "두 컴퓨터에서 이어서 작업"이 목적이라면 **이쪽**입니다.

---

## 5. 고급반 앱 — 저장소에 넣기

아직 올라가 있지 않습니다. 기초반과 같은 저장소에 두는 것을 권합니다.

```bash
cd ~/projects/hangul
mkdir -p go
# hangul-go.zip 을 풀어 hangul-go.html, audio/, tools/, MIGRATION.md 를 go/ 로 옮긴 뒤
git add go
git commit -m "한글 교실 고급반 추가"
git push
```

음성 7.2MB 가 함께 올라갑니다. 기초반도 `audio/` 1,226개(10MB)를 같은 방식으로
담고 있으니 전례는 있습니다. 배포는 기초반처럼 Vercel 을 쓰면 되고,
`https://<주소>/go/hangul-go.html` 로 열립니다.

> **마이크는 https 에서만 열립니다.** 「소리 내어 읽기」 과정이 동작하려면 반드시
> https 주소(또는 localhost)여야 합니다. 파일을 더블클릭해 `file://` 로 열면 녹음이
> 되지 않습니다.

---

## 6. 앱 구성

```
go/
├─ hangul-go.html        172 KB   앱 전체 (HTML+CSS+JS+배움자료 인라인)
├─ audio/                7.2 MB   성우 음성 375개 (v<해시>.mp3)
├─ tools/
│   ├─ extract_used.js            앱이 읽는 말 뽑기
│   ├─ make_audio.py              edge-tts 로 mp3 만들기 / 안 쓰는 것 지우기
│   ├─ inject_map.py              window.AUDIO 지도 넣기
│   ├─ used.json                  읽는 말 375개
│   └─ audio_map.json             말 → mp3 대응표
└─ MIGRATION.md                   이 문서
```

서버·빌드 도구·프레임워크가 없습니다. 정적 파일만으로 동작합니다.

**과정 12개 + 졸업 시험**

| 과 | 제목 | 비고 |
|---|---|---|
| 1 | 🔍 가려 써야 할 낱말 | 다르다·틀리다 / 웬·왠 … 카드 12, 문제 12 |
| 2 | 🔗 문장 이어 쓰기 | -고 / -지만 / -아서 / -니까 |
| 3 | 🏛️ 관공서 말 익히기 | 신청·접수·구비서류·감면 |
| 4 | 📋 서식 채워 쓰기 | **놀이**: 칸 찾기 16문 (`game: 'slot'`) |
| 5 | 💳 돈과 계약 글 읽기 | 고지서·명세서·보증·사기 문자 |
| 6 | 💊 병원과 약 글 읽기 | 처방전·검진 결과·119 |
| 7 | 📱 스마트폰으로 글 쓰기 | 문자·카톡·인증번호 |
| 8 | ✉️ 편지와 짧은 글 쓰기 | **놀이**: 문장 차례 맞추기 10문 (`game: 'order'`) |
| 9 | 🎗️ 경조사 봉투와 인사말 | 부의·축의·부고 읽기 |
| 10 | 📰 긴 글 읽고 알아보기 | 안내문·공고문·기사 |
| 11 | 🧧 사자성어와 관용구 | 유비무환 / 발이 넓다 |
| 12 | 📢 소리 내어 읽기 | **놀이**: 녹음 + 읽기 채점 12문장 (`game: 'voice'`) |
| 졸업 | 🎓 졸업 시험 | 각 과에서 2문제씩, 모자라면 채워 20문제 |

> 처음에는 「높임말 바르게 쓰기」가 제 2 과로 있었으나 **뺐습니다**(2026-09-21).
> 과를 빼면 졸업 시험 문항이 모자라므로, 남은 문제로 20개를 채우도록 고쳐 두었습니다.

**배움 자료 짜임** (`const MODULES` 안)

| 열쇠 | 뜻 |
|---|---|
| `cards[]` | 배우기 화면 한 장. `glyph`(큰 글자) `name` `formula` `doc`(문서 모양) `vs`(맞고 틀림 비교) `ex`(눌러 듣는 낱말) `note`(풀이) `say`(읽어 줄 말 배열) |
| `quiz[]` | `ask` `big` `doc` `listen` `choices` `answer`(0부터) `why` |
| `forms[]` | 서식 칸 찾기 — `tag` `rows[]` `asks[{ask, slot, why}]` (`slot` 은 1부터) |
| `orders[]` | 문장 차례 맞추기 — `parts[]` 가 **바른 차례**, 화면에서 섞어 보여 줍니다 |
| `sentences[]` | 소리 내어 읽기 — `text` |

진도는 `localStorage` 에 **`hangul3:progress`**, 글자 크기는 **`hangul3:size`** 로 저장합니다
(기초반 `hangul:`, 중급반 `hangul2:` 와 겹치지 않습니다). 7할 이상 맞히면 ✅ 도장이 찍힙니다.

---

## 7. 소리 — 성우 음성 만드는 법

기계 음성(윈도우 기본 목소리)은 어색해서 쓰지 않습니다. **기초반과 같은 성우 목소리**
`ko-KR-SunHiNeural` 로 미리 mp3 를 만들어 두고, 앱은 그 파일을 틉니다.

| 설정 | 값 |
|---|---|
| 목소리 | `ko-KR-SunHiNeural` (edge-tts, 무료) |
| 빠르기 | `-10%` |
| 형식 | 받은 그대로 (24kHz 48kbps mono, 다시 압축하지 않음 → ffmpeg 필요 없음) |
| 개수 | 375개 · 7.2 MB |
| 파일 이름 | `v<말 내용의 md5 앞 10자>.mp3` |

**말을 고치거나 더했을 때 — 세 줄이면 끝납니다**

```bash
node tools/extract_used.js hangul-go.html tools/used.json   # 1) 읽을 말 다시 뽑기
python tools/make_audio.py                                   # 2) 빠진 것만 받고 안 쓰는 것 지우기
python tools/inject_map.py                                   # 3) 지도를 html 에 넣기
```

이름이 내용 해시라서 **고친 문장 한 조각만** 새로 받습니다. 무엇이 바뀌는지 먼저 보려면
`python tools/make_audio.py --dry-run`.

**주의할 점 넷**

1. `window.AUDIO` 지도는 「소리 들려 주기」 스크립트 **바로 앞**에 들어가야 합니다.
   뒤에 넣으면 앱이 시작될 때 지도가 비어 모든 말이 기기 음성으로 새어 나갑니다.
   `inject_map.py` 가 그 자리를 찾아 넣습니다.
2. 찾는 이름(`sayKey`)은 **태그를 걷어 내고, 공백을 하나로 줄이고, 끝의 `! ? .` 을 떼어**
   만듭니다. 앱의 `sayKey()` 와 `extract_used.js` 의 `key()` 와 `make_audio.py` 의 `key()`
   **셋이 같아야** 합니다. 하나만 어긋나도 그 말이 기기 음성으로 나옵니다.
3. 숫자가 섞여 미리 만들 수 없는 말(「12문제 가운데 8문제를 맞혔습니다」)은 **소리에서
   빼고 화면 글씨로만** 보여 줍니다. 오답 풀이는 「정답은」 + 정답 보기 **두 조각을 이어**
   틀어 전부 성우 목소리로 들리게 했습니다.
4. 미리 만든 소리가 없는 말은 기기 음성으로 넘어갑니다(안전망). 새어 나가는 말이 없는지
   확인하려면 브라우저 콘솔에서 `extract_used.js` 와 같은 규칙으로 `AUDIO[sayKey(t)]` 를
   훑어 보세요. 마지막 확인 때는 **375개 전부 통과(새는 말 0개)** 였습니다.

「🐢 천천히 듣기」는 재생 속도 `0.72` 배입니다. 음높이는 그대로입니다.

---

## 8. 소리 내어 읽기 — 녹음과 채점

제 12 과만 쓰는 기능입니다.

- **녹음**: `MediaRecorder` 로 담고 「▶ 내 소리 듣기」로 다시 들려줍니다
- **알아듣기**: 브라우저 음성 인식(`SpeechRecognition`, `ko-KR`, 후보 3개 중 원문과
  가장 가까운 것 채택)
- **채점**: 원문과 들린 말을 글자 단위로 견주어(레벤슈타인 거리) 100점 만점.
  낱말별로도 견주어 **0.6 미만이면 그 낱말을 붉게** 표시합니다

| 점수 | 표시 | 집계 |
|---|---|---|
| 90 이상 | ⭐⭐⭐ 아주 잘 읽으셨습니다 | 맞힘 |
| 75 이상 | ⭐⭐ 잘 읽으셨습니다 | 맞힘 |
| 55 이상 | ⭐ 조금만 더 또박또박 | — |
| 그 아래 | 🌱 한 번 더 읽어 보세요 | — |

다시 읽기는 몇 번을 해도 **중복으로 집계되지 않습니다**. 음성 인식이 없는 브라우저
(파이어폭스 등)에서는 자동 채점 대신 **녹음만 하고 「내 소리 ↔ 바른 소리」를 번갈아 들은 뒤
👍 스스로 확인**하는 화면으로 자동 전환됩니다.

> 음성 인식은 **맞춤법대로 받아 적습니다.** 그래서 낱말을 빠뜨리거나 뭉개 읽은 것은 잘
> 잡아내지만, 된소리·장단 같은 **세밀한 발음 교정은 하지 못합니다.** 어르신 읽기 연습에는
> 이 정도가 오히려 덜 주눅 들게 하는 수준이라 이렇게 잡았습니다.

---

## 9. 알려진 문제 · 아직 못 한 것

1. **실기기 녹음을 확인하지 못했습니다.** 개발에 쓴 브라우저 창이 마이크를 막아,
   인식 결과를 흉내 내어 채점·화면 흐름만 검증했습니다. **배포 후 휴대폰에서 한 번
   눌러 보셔야 합니다.**
2. **오프라인(인터넷 없이 쓰기)이 없습니다.** 기초반에는 음성을 한 덩어리로 묶는
   `tools/build_audio_bundle.py` 와 서비스 워커가 있지만 고급반에는 아직 붙이지
   않았습니다. 지금은 누를 때마다 한 조각씩 받아 옵니다(처음에 7.2MB 를 한꺼번에
   받지는 않습니다).
3. **중급반에도 같은 CSS 버그가 남아 있습니다.** 비교 상자(`.vs-item`)가 긴 문장에서
   세로로 찌그러집니다. 고급반은 `flex-wrap: wrap` 과 `.m { flex: 1 1 9rem; min-width: 0 }`
   으로 고쳤으니 중급반 파일에도 같은 수정을 넣으시면 됩니다.
4. **기초 → 중급 → 고급 링크가 이어져 있지 않습니다.** 고급반 첫 화면에는 기초반으로
   가는 링크만 있습니다.
5. 중급반(`hangul-jung.html`)도 아직 저장소 밖에 있습니다. 함께 챙기세요.

---

## 10. 새 노트북 확인 목록

- [ ] Claude Code 로그인 → 이 세션이 목록에 보이는지
- [ ] `node -v` · `python -V` · `bun -v` · `git --version`
- [ ] gstack 설치 후 `/gstack` 이 뜨는지
- [ ] `/setup-gbrain` 후 기억이 불러와지는지 (`gbrain recall`)
- [ ] `~/.claude/settings.json` 훅 경로가 새 사용자 이름에 맞는지
- [ ] `pip install edge-tts` 후 `python tools/make_audio.py --dry-run` 이 **「받아야 할 것 0개」**
- [ ] 로컬 서버로 고급반을 열어 **🔊 다시 듣기가 성우 목소리로** 나오는지
- [ ] 고급반을 저장소에 넣고 푸시 (5절)
- [ ] **배포 후 휴대폰에서 제 12 과 녹음 한 번** (9-1)

마지막 두 항목이 남아 있습니다. 특히 녹음은 실기기에서만 확인할 수 있습니다.
