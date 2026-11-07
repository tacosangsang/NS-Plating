# rea-video 스킬 출처

- 원본: https://github.com/JuneYaooo/rea-video (Apache-2.0, `LICENSE`, `NOTICE` 동봉)
- 가져온 커밋: `c9359c46f90c9824713081ea18fd207a45a0636a` (2026-11-06)
- 가져온 범위: `skills/rea-video/` 전체 (SKILL.md, references/)

## 이 프로젝트에서 바꾼 것

- `SKILL.md` 0절 설치 안내: `references/setup.md`(최신판 설치) 대신 `scripts/setup-rea-video.sh`(커밋 고정) 사용, 출력은 `out/`.

## 업스트림 갱신 절차

1. 원본을 새 커밋으로 받아 `skills/rea-video/`를 이 폴더에 덮어쓰기
2. 위 "바꾼 것"을 다시 적용
3. `scripts/setup-rea-video.sh`의 `REF` 기본값을 같은 커밋으로 변경
4. 이 파일의 커밋 갱신
