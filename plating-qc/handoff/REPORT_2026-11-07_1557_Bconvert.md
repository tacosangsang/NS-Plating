# B convert 단계 보고 (2026-11-07 15:57 KST)

## 1. 한 줄 상태

- 현재 단계: B 구조 복구 중, convert 단계 진행.
- 다음 행동: compare의 프레임별 밝기 정규화와 지정 사례를 구현한다.
- 막힌 것: 없음.

## 2. 작업 체크리스트

| 항목 | 상태 | 근거 | 검수 기준 | 충족 |
| --- | --- | --- | --- | --- |
| ProRes 인코딩 | 진행 | `20ac33f`, `src/plating_qc/backend/ffmpeg.py` | 백엔드의 인코딩 명령, 기존 검증 보존 | 일부: 검증 로직과 타임스탬프 호출은 아직 core 의존 |
| 충돌 및 하드링크 폴백 | 완료 | `src/plating_qc/publish.py`, `tests/test_convert.py` | Windows rename 폴백, 충돌 시 보존 | 예: Windows 테스트 |
| 240자 경로 | 진행 | `src/plating_qc/layout.py` | 입력·출력 경로 전반 | 일부: probe 입력과 convert 출력에 적용, 나머지 출력 경로 미적용 |
| compare·tiles·split 및 CLI 설정 | 미착수 | 06 1장 | 각 거부·부분 승인 항목 | 아니오 |

## 3. 결과물 목록

| 종류 | 경로 또는 URL | 비고 |
| --- | --- | --- |
| 저장소·브랜치·HEAD | `design/plating-qc-request`, `20ac33f` | 단계 커밋 |
| PR | https://github.com/tacosangsang/plating-qc-workflows/pull/1 | 병합 금지 |
| 테스트 로그 | `handoff/logs/win_20ac33f_2026-11-07_155737.txt` | Windows 전체 54건 통과, 종료 0 |
| 샘플 실행 로그 | 미착수 | 해당 없음 |
| 설계 요청·초안 | `design/requests/plating-qc.md`, `design/plating-qc.md` | 원문 |
| STATE.md 최신판 | `handoff/STATE.md` | 다음 단계에서 갱신 |

## 4. 사용량

| 항목 | 값 | 확인 방법·시각 |
| --- | --- | --- |
| 코덱스 주간 한도 잔여 | 미확인 | 화면 미조회 |
| 모델·effort별 작업 수 | 미확인 | 실제 라우팅 미확인 |
| 초기화권 사용 여부 | 미확인 | 이번 작업에서 요청 없음 |
| Claude API 호출 수·누적 토큰 | 1회, 입력 108·출력 62 | 기존 장부, 이번 단계 호출 없음 |
| Console 프로모션 잔액 | US$99.99 | 사용자 제공 화면 |
| Claude Code CLI 사용 | 없음 | 이번 작업 기준 |

## 5. 사용자 답이 필요한 것

없음.

## 6. 규칙 위반 자가 점검

이번 단계 기준 실제 작업 폴더 raw 쓰기, 원본·기존 결과 덮어쓰기, 금지 문서 편집, API 키 기록, 유료 생성 호출 없음. B 구조 복구는 미완료다.
