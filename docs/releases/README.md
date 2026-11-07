# 판 기록 (태그 메시지)

판마다 git 태그를 붙입니다. 돌아올 자리를 만들어 두는 일입니다
([MIGRATION.md 10절](../MIGRATION.md#10-판-되돌리기)).

여기에는 **태그에 넣을 글**을 둡니다. 클라우드 세션(claude.ai/code)에서는 태그를
올릴 수 없습니다 — `refs/tags` 푸시와 git 쓰기 API가 둘 다 막혀 있어 **브랜치만**
올라갑니다. 그래서 글은 여기 남기고, 태그는 PC에서 한 줄로 답니다.

**PC의 PowerShell 에 이 한 줄** (v1.2 · v1.3 두 개를 한 번에):

```powershell
cd $HOME\projects\hangul; git pull; git tag -a v1.2 -F docs/releases/v1.2.txt 0a74da9; git tag -a v1.3 -F docs/releases/v1.3.txt af70200; git push origin v1.2 v1.3
```

"already exists" 는 이미 붙어 있다는 뜻이라 괜찮습니다. 마지막에 `[new tag]` 두 줄이 나오면 끝입니다.

| 판 | 글 | 커밋 | 올렸나 |
|---|---|---|---|
| v1.1 | (태그에만 있음) | — | ✅ |
| v1.2 | `v1.2.txt` | `0a74da9` | ✅ 2026-11-06 |
| v1.3 | `v1.3.txt` | `af70200` | ✅ 2026-11-06 |

다음 판부터는 같은 꼴로: 글을 `vX.Y.txt` 로 남기고, 위 한 줄의 판 번호와 커밋만 바꿉니다.

이미 붙어 있는지는 이렇게 봅니다.

```bash
git ls-remote --tags origin
```

판 목록: https://github.com/hisdream64-commits/hangul/releases
