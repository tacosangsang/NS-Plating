# PLATING Prompts

AI 이미지 생성 프롬프트 + 리소스 버전 관리.

## 구조
- `base_prompt.md` — 최신본 (항상 여기 참조)
- `backups/base_prompt_MMDD.md` — 날짜별 스냅샷
- `resources/` — 리소스 파일 (이미지 등)

## 워크플로
1. `base_prompt.md` 수정
2. `backups/base_prompt_MMDD.md`로 스냅샷 복사
3. commit + push
