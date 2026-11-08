# 블록아웃 규약 도구 보고 (2026-11-08, 세 번째 실행)

## 1. 한 줄 상태

- 현재 단계: 브리핑 B, 18번 1~5단계 구현·문서 작성 완료. 최종 전체 222건 통과, Blender 실행 미검증.
- 다음 행동: 5단계 커밋 후 최종 인계에 단계별 해시 확정.
- 막힘: 없음. 독립 클론 `C:/Users/uicus/Dev/pqw-bo`, `.git`은 작업 폴더 내부다. 이전 worktree의 Git 권한 문제는 과거 기록으로 보존한다.

## 2. 작업 체크리스트

| 항목 | 상태 | 근거 | 검수 기준 | 충족 |
| --- | --- | --- | --- | --- |
| A1 세 저장소 클론 | 일부 | 이번 pqw-bo 독립 클론, 기준 HEAD 3ea3022 | 다른 저장소는 이번 범위 밖 | 일부 |
| A2 스킬 | 일부 | `C:/Users/uicus/.codex/skills/{caveman,ponytail,i-have-adhd}/SKILL.md` 읽음·적용 | 프로젝트 스킬 4개 설치는 이번 범위 밖 | 일부 |
| A3 모델 | 완료 | CLI 실행, 모델 gpt-6.1-sol, effort xhigh(클로드 프로젝트 지정) | 사용자 지정값 기록. 실제 모델 목록·런타임 독립 확인·Astra 선택 가능 여부 미확인 | 예 |
| A4 인계 | 진행 | 이 REPORT, STATE.md, usage-log.md | 기존 Claude 장부 변경 금지 | 예 |
| A5 Claude 도구·시험 호출 | 해당 없음 | 이번 호출 0회 | 네트워크·API·설치 금지 | 예 |
| B1 push | 해당 없음 | 이번 push 없음 | 네트워크 금지 | 예 |
| B2 기반 모듈 | 완료 | 전체 테스트 로그 | 기존 코드 변경 없이 회귀 통과 | 예 |
| B3 probe | 완료 | 같은 로그 | 기존 테스트 통과. 별도 PC 경로 감사 미실시 | 일부 |
| B4 convert | 완료 | 같은 로그 | 기존 합성 테스트 통과. 새 실제 클립 변환 없음 | 예 |
| B5 compare | 완료 | 같은 로그 | head2·tail11·other_clip 포함 | 예 |
| B6 tiles·split·Blender | 일부 | 기존 테스트 통과 | 이번 Blender 저장 스크립트 4단계 예정 | 일부 |
| B7 샘플·PR | 해당 없음 | PR 조회·변경 없음 | 이번 범위 밖 | 해당 없음 |
| C 워크플로우 감사·템플릿 | 미착수 | 해당 없음 | 이번 범위 밖 | 해당 없음 |
| D sangsang-voice | 미착수 | 해당 없음 | 이번 범위 밖 | 해당 없음 |
| E CMMI | 미착수 | 해당 없음 | 이번 범위 밖 | 해당 없음 |

| 18번 단계 | 상태 | 근거 | 검수 |
| --- | --- | --- | --- |
| 1 모델·manifest·버전 규칙 | 완료 | ee20db7, `tests/test_pt_blockout_model.py` | 전체 191건 / 실패 0 / 오류 0 / skip 0 |
| 2 init·new-version | 완료 | 80dae48, `tests/test_pt_blockout_commands.py` | 집중 11건·전체 202건 / 실패 0 / 오류 0 / skip 0 |
| 3 check·pin | 완료 | f03cd95, `tests/test_pt_blockout_check.py` | 집중 18건·전체 220건 / 최종 실패 0 / 오류 0 / skip 0 |
| 4 Blender 저장 스크립트 | 완료 | 4321655, `tools/blender/save_next_version.py` | 전체 회귀 220건 통과·정적 검사 통과. Blender 저장 실행 미검증 |
| 5 README | 완료 | `tools/plating/README.md:58` | 명령·Blender 주 경로·보존·판정·검증 한계 문서화, 최종 전체 222건 통과 |

## 3. 결과물 목록

- 저장소: `C:/Users/uicus/Dev/pqw-bo`, 브랜치 `dot/blockout-convention`, 기준 HEAD `3ea3022`.
- REPORT: `handoff/REPORT_0924_blockout.md`. 기존 `REPORT_0823_blockout.md`와 이전 로그 5개는 과거 기록으로 보존한다.
- 1단계 전체 로그: `handoff/logs/win_3ea3022_20261108_092404_659.txt`, 191건 / 실패 0 / 오류 0 / skip 0, 19.222초.
- 테스트 명령: `python -m unittest discover -s tests -v` 단독. 출력 수신 후 별도 단계로 로그 저장. 파일명 해시는 실행 당시 HEAD다.
- PR·원격 URL·새 실제 미디어 출력: 해당 없음.
- 설계 근거: 저장소 밖 `dot-handoff/18_블록아웃규약도구_구현지시_2026-11-08.md`, `blockout_plan_2026-11-07.md`, 02·05·07·08·09·12번 읽기 전용.

## 4. 사용량

| 항목 | 값 | 확인 방법 |
| --- | --- | --- |
| 코덱스 주간 한도 | 미확인 | 네트워크 금지로 조회하지 않음 |
| 모델·effort | CLI 실행, 모델 gpt-6.1-sol, effort xhigh(클로드 프로젝트 지정) | 사용자 지정 |
| 이번 작업 수 | 진행 중, 단계별 usage-log.md 기록 | 로컬 파일 |
| 초기화권 | 해당 없음 | 요청·사용 없음 |
| Claude API | 이번 0회·0토큰 | 기존 장부 읽기·수정 불필요 |
| Console 잔액 | 미확인 | 조회하지 않음 |
| claude -p | 없음 | 실행하지 않음 |

## 5. 사용자 답이 필요한 것·설계 변경 제안

중간 질문 없음. 설계 변경 제안 0건.

사용자 확인(2026-11-08 ts): 새 버전은 build.py가 아니라 Blender 직접 저장으로 만든다. 4단계 저장 스크립트가 주 경로다. Drive에는 최신 5개만 두고 그보다 옛 버전은 프로젝트 폴더에만 둔다. Drive 보관·동기화는 이번 범위 밖이며 기록만 한다.

## 6. 규칙 위반 자가 점검

- raw 직접 쓰기·원본·기존 버전 덮어쓰기 없음: 예.
- 핸드북·노션·workflow·specification 변경 없음: 예.
- API 키 조회·출력·저장, 네트워크·push·API·설치 없음: 예.
- 설계 무단 변경 없음: 예.
- 쓰기는 pqw-bo 작업 폴더 안만: 예.
- src/plating_qc·기존 plating_tools/versions·루트 config.toml 변경 없음: 예.
- handoff/claude-usage.*·claude-balance.json 수정·stage·커밋 없음: 예.
- 테스트 단독 명령·출력 수신 후 로그 저장·테스트 코드만 작성 준수: 예.
- 합성 파일·tempfile은 out/pt-tests 안: 예.

2단계 검증 로그: handoff/logs/win_ee20db7_20261108_092834_351.txt. 집중 11건, 전체 202건(21.051초), 실패·오류·skip 0. staging 공개·파일 목록/SHA-256·NOTES.md·명시적 current·원본 보존·충돌·실패·자산 쓰기 잠금을 검증했다. 실패 staging과 manifest 저장 실패 뒤 고아 버전은 삭제하지 않고 check에서 진단할 수 있게 보존한다.

3단계 검증 로그: handoff/logs/win_80dae48_20261108_093504_498.txt. 집중 18건 중 DEL 인용문 재읽기 1건 실패를 재현했고 TOML raw DEL escape 수정 뒤 집중 18건·전체 220건(25.541초) 통과, 실패·오류·skip 0. 수정 전 실패 원문도 같은 로그에 보존했다.

검사 구현: STALE(일반 렌더는 current보다 옛 버전, pin 씬은 pin과 불일치), PINNED(명시한 S#NN 씬·고정 판 일치), CONVENTION(미등록·접미사·날짜·중복 정본·렌더 이름 위반), IMMUTABLE(파일 목록·SHA-256·폴더 누락). PINNED만 있으면 종료 0, 위반은 1. 잘못된 명령 입력은 2, 쓰기 충돌 3, 모듈 없음 4, I/O 실패 5다.

렌더 파일명이나 렌더 루트 아래 상대 경로의 정확한 S#NN 토큰만 pin 범위로 읽는다. 씬을 추정하지 않으며 명시하지 않은 렌더는 current와 비교한다. --renders는 기본 자산별 renders 대신 지정한 렌더·시트 루트를 검사한다. 결과 blockout.json·blockout.md·run.json은 설정 output_root의 새 실행 폴더에만 공개한다. 버전은 versions와 archive 양쪽의 파일 목록·해시를 검사하며 자동 이동·삭제하지 않는다.

로그 저장 경위: 출력 전체를 셸 인자로 합치다 Windows CreateProcessAsUserW 206 길이 제한으로 파일 작성 전 실패했다. 테스트 재실행 없이 보존한 출력을 apply_patch로 저장했다.

4단계 로그: handoff/logs/win_f03cd95_20261108_093736_131.txt. 전체 220건 / 실패·오류·skip 0, 17.018초. 저장 스크립트는 save_as_mainfile(copy=True, relative_remap=False)로 현재 장면을 저장소 out/blockout-save/<uuid>/<asset>.blend에 사본 저장하고 외부 Python 3.12의 CLI를 argv·shell=False로 호출한다. --set-current는 명시적으로만 전달한다. 원본 filepath 유지, 성공 시 자신의 임시 파일·빈 폴더만 정리, 실패 사본은 보존한다. bpy import는 이 스크립트 main 안에만 있다.

Blender 저장 실행은 미검증이다. 이번에는 Blender·bpy를 실행하거나 모의 실행하지 않았다. 정적 검사는 AST 구문·규칙 검사이며 실제 Blender 저장 성공이나 외부 자산의 상대 경로 해석을 보증하지 않는다. 예외 타입 지적 2건을 SaveError의 경로 필드로 수정했고 최종 정적 검사 10파일 통과다.

3단계 보완: 규약 원문의 렌더 파일명 날짜 금지와 --renders 루트 자체가 S#NN·vNNN일 때의 문맥 유지를 보완했다. 수정 전 집중 20건 중 2건 실패 재현, 수정 후 집중 20건·전체 222건(42.127초) 통과, 최종 실패·오류·skip 0. 로그 handoff/logs/win_4321655_20261108_094016_849.txt. 설계 변경 없이 기존 규약의 검사 누락을 수정했다.

5단계 최종 로그: handoff/logs/win_ff92944_20261108_094222_763.txt. 전체 222건(38.915초), 실패·오류·skip 0. 기존 185건 + 블록아웃 37건(모델 6·생성 11·검사 20). 최종 정적 검사 10파일 통과. 금지된 코드·Claude 장부는 기준 3ea3022 대비 변경 파일 없음을 확인했다.
