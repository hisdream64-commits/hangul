# 우리 한글 교실 — 작업 규칙

성인 문해학습자(주로 어르신)가 쓰는 한글 학습 웹앱입니다. 글을 못 읽는 분이 쓰십니다.
**소리와 큰 글자가 이 앱의 본체입니다.** 손대기 전에 아래를 읽어 주세요.

## 세 갈래가 한 저장소에 있습니다

| 갈래 | 파일 | 읽을 문서 |
|---|---|---|
| 기초반 | `index.html` | `docs/MIGRATION.md` |
| 받아쓰기 중급반 · 겹받침 | `jung.html`, `gyeopbatchim.html` | `docs/DICTATION.md` |
| 고급반 | `go/` | `go/MIGRATION.md` |

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
- `main` 에 올리면 **운영 주소(https://urihangul.vercel.app/)가 바로 바뀝니다.**
  어르신이 쓰시는 화면이므로, 묻지 않고 올리지 마세요. 가지에 올리면 미리보기만 생깁니다.
- **클라우드 세션에서는 태그를 못 올립니다.** `refs/tags` 푸시와 git 쓰기 API가 둘 다
  막혀 있어 브랜치만 올라갑니다. 태그 글은 `docs/releases/` 에 남기고 PC에서 답니다
  ([docs/releases/README.md](docs/releases/README.md)).

## 지금 상태 (2026-10-23)

`main` 이 판 **1.2** 입니다. 기초반 소리 안내와 중급반(오프라인 소리 · 첫 화면 메뉴
연결)이 모두 합쳐져 있습니다. 합칠 때 부딪힌 네 군데를 어떻게 풀었는지는
`docs/DICTATION.md` **5-3절**에 적혀 있습니다.

**`v1.2` 태그는 아직 안 붙었습니다.** 글은 `docs/releases/v1.2.txt` 에 있고,
PC에서 세 줄이면 됩니다 — `docs/releases/README.md` 참고.

남은 일은 **받아쓰기 3단계 생활 문장 소리 12개**뿐입니다 (`docs/DICTATION.md` 5-1절).
`python tools/regen_audio_edge.py --missing` 로 만듭니다. 인터넷이 막힌 곳에서는
안 됩니다 — `edge-tts` 가 `speech.platform.bing.com` 에 연결합니다.

> 소리를 더하면 `audio.bin` 크기가 바뀝니다. 그러면 **중급반을 반드시 다시 만들어야**
> 합니다(위 「고친 뒤 반드시」). 안 하면 비행기 모드에서 중급반 소리가 안 납니다.
