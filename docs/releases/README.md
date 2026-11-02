# 판 기록 (태그 메시지)

판마다 git 태그를 붙입니다. 돌아올 자리를 만들어 두는 일입니다
([MIGRATION.md 10절](../MIGRATION.md#10-판-되돌리기)).

여기에는 **태그에 넣을 글**을 둡니다. 클라우드 세션(claude.ai/code)에서는 태그를
올릴 수 없습니다 — `refs/tags` 푸시와 git 쓰기 API가 둘 다 막혀 있어 **브랜치만**
올라갑니다. 그래서 글은 여기 남기고, 태그는 PC에서 한 줄로 답니다.

```bash
cd ~/projects/hangul && git pull
git tag -a v1.2 -F docs/releases/v1.2.txt <커밋>
git push origin v1.2
```

| 판 | 글 | 커밋 | 올렸나 |
|---|---|---|---|
| v1.1 | (태그에만 있음) | — | ✅ |
| v1.2 | `v1.2.txt` | `0a74da9` | ❗ PC에서 위 세 줄 |

이미 붙어 있는지는 이렇게 봅니다.

```bash
git ls-remote --tags origin | grep v1.2
```

판 목록: https://github.com/hisdream64-commits/hangul/releases
