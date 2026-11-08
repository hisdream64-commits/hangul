# 한글뚝딱 — 작업 규칙

성인 문해학습자(주로 어르신)가 쓰는 한글 학습 웹앱입니다. 글을 못 읽는 분이 쓰십니다.
**소리와 큰 글자가 이 앱의 본체입니다.** 손대기 전에 아래를 읽어 주세요.

> **교육과정 기본 원칙: [docs/PRINCIPLES.md](docs/PRINCIPLES.md)** (2026-11-07 진민주님).
> 세 갈래의 모든 콘텐츠 분석·수정·기능 개발에 적용합니다. 수정 전에 분석, 콘텐츠와 기능은 나눠서,
> 한 번에 하나씩, 요청하지 않은 기능은 더하거나 빼지 않기. 현재 상태 분석과 해야 할 일 순서는
> [docs/CURRICULUM_REVIEW.md](docs/CURRICULUM_REVIEW.md).

## 세 갈래가 한 저장소에 있습니다

| 갈래 | 파일 | 읽을 문서 |
|---|---|---|
| 기초반 | `index.html` | `docs/MIGRATION.md` |
| 받아쓰기 중급반 · 겹받침 | `jung.html`, `gyeopbatchim.html` | `docs/DICTATION.md` |
| 한글뚝딱(고급) | `go/` | `go/MIGRATION.md` |

고치실 갈래의 문서를 **먼저 읽으세요.** 서로 건드리는 파일이 다릅니다.

## 절대 하지 말 것

1. **소리를 가공하지 마세요.** 음색(EQ)·크기·빠르기(`playbackRate`)를 건드리지 않습니다.
   `<audio>` 로 그냥 틉니다. 전에 EQ와 0.7배속을 넣었다가 "기계음 같다"는 말을 듣고
   전부 걷어냈습니다. 세 갈래 모두 같은 규칙입니다.
2. **브라우저 합성음성(`speechSynthesis`)을 새로 쓰지 마세요.** 녹음이 없는 말은
   소리 단추를 아예 내보내지 않습니다. (기초반의 안내문 읽기에만 예외로 남아 있습니다)
3. **화면에 보이는 말과 들리는 녹음이 달라서는 안 됩니다.** 받아쓰기에서는 학습자가
   틀린 답을 쓰게 됩니다. 실제로 「괜찮다」를 보여 주며 "괜찮습니다"를 들려주던 버그가
   있었고, 그래서 `tools/dictation/build.js` 가 어긋나면 **일부러 실패**합니다.
4. **`jung.html` · `gyeopbatchim.html` 을 직접 고치지 마세요.** 만들어진 결과물입니다.
   `tools/dictation/build.js` 와 템플릿을 고치고 다시 만듭니다 (아래).

## 고친 뒤 반드시

```bash
# 중급반을 고쳤다면 — 다시 만들어 저장소 맨 위로
cd tools/dictation && node build.js ../../index.html && mv -f jung.html gyeopbatchim.html ../../

# 화면(index.html · jung.html · gyeopbatchim.html)을 고쳤다면 — 캐시 지문
python tools/stamp_sw.py
```

`stamp_sw.py` 를 빠뜨리면 휴대폰이 옛 화면을 계속 써서 "고쳤는데 그대로인데요"가 됩니다.

## 확인

```bash
python tools/clips.py                         # 소리 대본 개수
python tools/dictation/check_offline.py       # 중급반이 비행기 모드에서도 소리 나는지
python -m http.server 8000                    # 그 뒤 http://localhost:8000/jung.html
```

소리는 `audio/audio.bin` **묶음 한 덩어리**로 저장됩니다. 그래서 인터넷이 있는 PC에서
🔊 를 눌러 보는 것으로는 비행기 모드가 멀쩡한지 알 수 없습니다. 위 `check_offline.py` 가
그 상태를 실제로 만들어 확인합니다.

## 커밋

- 작성자는 저장소 안에서만 `hisdream64-commits <hisdream64@gmail.com>` 로 잡혀 있습니다.
- **여러 세션이 같은 작업 트리를 함께 씁니다.** 커밋할 때는 반드시 **경로를 지정**해서
  남의 변경을 쓸어 담지 마세요 — `git commit <경로> -m ...`. 실제로 한 번 섞인 적이 있습니다.
- **일을 집기 전에 [docs/CURRICULUM_REVIEW.md](docs/CURRICULUM_REVIEW.md) 4절의 목록을
  먼저 보고, 그 줄에 「🔸 진행 중」을 적어 밀어 올리세요.** 2026-11-08 에 두 세션이 같은
  기능을 따로 만들어 한쪽을 버린 적이 있습니다. 🔸 가 붙은 줄은 집지 마세요.
- `main` 에 올리면 **운영 주소(https://urihangul.vercel.app/)가 바로 바뀝니다.**
  어르신이 쓰시는 화면이므로, 묻지 않고 올리지 마세요. 가지에 올리면 미리보기만 생깁니다.
- **클라우드 세션에서는 태그를 못 올립니다.** `refs/tags` 푸시와 git 쓰기 API가 둘 다
  막혀 있어 브랜치만 올라갑니다. 태그 글은 `docs/releases/` 에 남기고 PC에서 답니다
  ([docs/releases/README.md](docs/releases/README.md)).

## 지금 상태 (2026-11-07)

`main` 이 판 **1.3** 입니다. 세 갈래 이름이 **한글뚝딱(초급) · (중급) · (고급)** 으로
맞춰져 있습니다. 기초반 소리 안내, 진도 저장, 중급반(오프라인 소리 · 첫 화면 메뉴
연결)이 모두 합쳐져 있습니다. 판 1.2 를 합칠 때 부딪힌 네 군데를 어떻게 풀었는지는
`docs/DICTATION.md` **5-3절**에 적혀 있습니다.

태그는 **`v1.1` · `v1.2` · `v1.3` 이 모두 붙어 있습니다.** 다음 판의 글은 전처럼
`docs/releases/` 에 남기고 PC에서 답니다 ([docs/releases/README.md](docs/releases/README.md)).

**소리는 다 만들어졌습니다.** 대본 1,254개와 녹음 1,254개가 같습니다. 받아쓰기
3단계 생활 문장도 **통문장 받아쓰기 12 / 12** 로 돌아갑니다(묶음 자리표 139개).
`python tools/regen_audio_edge.py --missing` 을 돌리면 「새로 만들 조각이 없습니다」가
나옵니다.

남은 일은 **급한 것이 없습니다.** 손볼 만한 곳은 `docs/DICTATION.md` 5절에 적어
두었습니다 (틀린 문제만 다시 풀기 · PC 화면 배치 · 키보드 입력 · 중간 진도 저장).

> 나중에 소리를 더하면 `audio.bin` 크기가 바뀝니다. 그러면 **중급반을 반드시 다시
> 만들어야** 합니다(위 「고친 뒤 반드시」). 안 하면 비행기 모드에서 중급반 소리가
> 안 납니다. 그리고 `--missing` 은 `index.html` 에서 묶음 색인을 지우므로, 바로
> 이어서 `python tools/build_audio_bundle.py` 를 돌려야 합니다.
