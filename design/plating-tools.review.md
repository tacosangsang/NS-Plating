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

## 15번 추가 결정 (2026-11-07)

근거: `C:/Users/uicus/Dev/dot-handoff/15_P0검수_설계변경결정_2026-11-07.md`. 앞선 REPORT의 보류 2건을 승인한 결정이다.

1. 씬 안 표의 첫 두 머리 칸이 컷·TC이면 컷표다. header-row 속성은 판정에서 제외한다. 속성이 없으면 CT018 info를 남기며 종료 코드에 영향은 없다. 판정은 profile_plating.py에 모은다. 녹음 표는 씬 경계로 제외한다. 새 수동 선택 옵션은 추가하지 않는다. 구현 `9b5981a`.
2. SS(.f)–SS(.f)는 같은 표의 바로 앞 행 끝 TC 분을 상속한다. 직전 행 해석 실패·시작 역행·시작 > 끝은 원문과 CT006을 유지한다. 끝만 분 생략한 A5는 명시된 시작 분을 사용한다. 성공한 생략 형식은 원문과 minute_inherited true를 함께 기록한다. 구현 `ee24f85`.

실측·검증: `handoff/REPORT_2152_P0b.md`. 신규 테스트는 합성 HTML만 사용하며 실제 F 출력은 out/에만 둔다.

## V4 예시 정정 (2026-11-07 23:25 KST)

설계 4.6 V4의 예시 "pin(v50, S#10, W04 135 근거)"는 사실이 아니다. ts 확인: S#10을 v50으로 고정한 적이 없다. NS-Plating workflow 04:135의 해당 구절은 PR #6에서 삭제한다. pin 기능 자체(근거 있는 승인 고정만 허용)는 유지하고, 테스트는 실제 씬 번호가 아닌 합성 라벨(S#98·S#99)로 바꾼다. 설계 원문(draft)은 기록으로 두고 고치지 않는다.
