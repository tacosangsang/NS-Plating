---
name: prompt-check
description: 프롬프트 페이지(아티팩트 링크)나 prompt-page JSON이 형식(입력 그림·한글 촬영 표·구간 표·점검 8줄·복사 버튼·[최신] 맨 위)을 지켰는지 점검할 때 사용한다. 사용자가 /prompt-check 뒤에 링크나 JSON 경로를 주면 실행한다.
---

# prompt-check

프롬프트 페이지가 형식을 지켰는지 점검한다. 형식은 `prompt-page` 스킬과 핸드북 5-14장을 따른다. 점검만 하고 고치지 않는다. 고칠 때는 `prompt-page`로 다시 만든다.

## 입력별 실행

- **JSON 경로**(`*.json`)
  - `python3 .claude/skills/prompt-page/prompt_page.py <json> --check`
- **아티팩트 링크**(claude.ai/artifact/…)
  1. Artifact 도구를 `action: "read"`, `path: "index.html"`, `out_dir: <스크래치>/check/<id>`로 불러 저장한다.
  2. `python3 .claude/skills/prompt-check/audit_page.py <저장된 index.html>`
- **여러 개**: 링크마다 1번을 하고, `audit_page.py`에 파일을 한꺼번에 넘긴다.

## 보는 것 (맨 위 생성 기준)

- 맨 위 생성 제목에 [최신] 또는 [생성 대기]가 있는가
- 프롬프트가 부르는 @image·@video 수만큼 입력 그림이 있는가
- 그림이 작은 격자(2열 이상)가 아닌가
- 각 입력의 파일 경로가 프롬프트 밖 본문에 있는가
- 한글 촬영 정보(샷 크기·앵글·렌즈·mm·카메라 위치·눈높이·화면 배치·빛 방향)가 3개 이상 있는가
- 점검 8줄 칸이 표로 있고, 답(예/아니오/해당 없음)이 8개 이상인가
- 복사 버튼이 있는가
- 영상 생성이면 한글 구간 표(초 단위)가 있는가. video_edit은 빼고 본다.

## 결과 보고

- 걸린 항목을 그대로 한국어로 짧게 전한다.
- 이 점검은 HTML 모양으로 추정하는 휴리스틱이다. 내용이 맞는지(mm 값, 원본 해상도, 컷표와 같은지)는 보지 않는다.
- 통과했어도 내용 확인은 점검 칸 몫이라고 같이 말한다.
- 옛 페이지가 걸리면 지금 돌리는 컷만 prompt-page로 다시 만들자고 제안한다. 끝난 컷은 옮기지 않는다.
