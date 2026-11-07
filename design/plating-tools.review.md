# 설계 초안 검수 결정

| ID | 결정 |
| --- | --- |
| D1 | 허용. `plating_tools`가 ffmpeg를 argv로 직접 호출한다. 경로는 `plating.toml [tools] ffmpeg_path`. 없으면 종료 4. P1 일이다 |
| D2 | 설계 기본값 채택. 골격은 영상만, 이미지는 `prompt check`만 |
| D3 | 공식 진입점 `python -m plating_tools`. `pyproject.toml`에 `plating` 스크립트 항목은 추가하되 재설치는 하지 않는다(설치 금지 규칙) |
| I1 | 불필요. dot가 NS-Plating HEAD 577c3d4 `workflow/`를 직접 읽는다. 앵커 명세는 원문으로만 작성한다 |
| I2~I4, I7, I8, I12, I13, I16 | dot가 원문(workflow, 핸드북, plating-qc 코드)에서 찾는다. 원문에 없으면 설계 기본값대로 `미확인` 처리하고 REPORT에 목록으로 남긴다. 추정 금지 |
| I5 | 셀·span 색도 행과 같은 뜻으로 해당 요소 상태를 낸다: green=done, gray=removed, red=todo, yellow=revise. 행 상태와 합치지 않는다(사용자 규칙 "칸이면 그 항목만"의 연장). 사용자에게 확인 요청 중이며 답이 다르면 프로필 한 곳만 고친다 |
| I6 | 색이 붙은 필드에만 todo. S#01-C001은 대사 필드만 todo. 사운드 필드는 셀 색이 없으면 상태 없음 |
| I9, I10 | 사용자에게 묻는 중. 답 전까지 `--require-approval`은 구현하되 승인 증거 형식은 "인용문 + 위치 + 날짜" 자유 기록, 프롬프트 SHA-256 결속은 설계대로 |
| I11 | 계획 파일(plan.toml)에 사람이 적는 방식 유지 |
| I14, I15 | P1. 11/9 전에 사용자에게 묻는다. 지금은 구현하지 않는다 |
| I17 | 허용. `out/`을 `.gitignore`에 추가 |
| I18 | fixture 커밋 금지. 테스트는 F를 읽기 전용 경로로 참조하고, 없으면 skip. 합성 fixture(직접 만든 짧은 HTML 표)는 커밋 가능 |
| I19 | 설계 기본값 수용 |
| A1~A11 | `cuts inventory`를 실제 F로 돌려 A1~A5·A10을 확인하고 결과를 REPORT에 원문으로 |
