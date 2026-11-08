# 블록아웃 규약 도구 최종 보고 (2026-11-08, 세 번째 실행)

## 1. 한 줄 상태

- 현재 단계: 브리핑 B, 18번 1~5단계 구현·문서·단계별 커밋 완료. 최종 전체 222건 통과, 실패·오류·skip 0. Blender 실제 저장 실행은 미검증이다.
- 다음 행동: 클로드 프로젝트가 이 REPORT와 로컬 단계 커밋을 검수한다. Blender 실행 검증은 별도 환경에서 수행한다.
- 막힘: 없음. 독립 클론 `C:/Users/uicus/Dev/pqw-bo`, 브랜치 `dot/blockout-convention`, Git 메타데이터는 작업 폴더 내부 `.git`이다. 이번 Git add·commit은 모두 성공했다.
- 미완료 구현 단계: 없음. 실제 PLATING 적용·Drive 정리·push는 이번 범위 밖이다.

## 2. 작업 체크리스트

| 항목 | 상태 | 근거 | 검수 기준 | 충족 |
| --- | --- | --- | --- | --- |
| A1 세 저장소 클론 | 일부 | 이번 독립 클론 pqw-bo, 기준 3ea3022 | 다른 저장소의 경로·HEAD 재감사는 범위 밖 | 일부 |
| A2 스킬 | 일부 | C:/Users/uicus/.codex/skills/{caveman,ponytail,i-have-adhd}/SKILL.md 읽고 적용 | 프로젝트 스킬 4개 설치는 범위 밖. Python·Git 보조 스킬도 적용 | 일부 |
| A3 모델 | 완료 | CLI 실행, 모델 gpt-6.1-sol, effort xhigh(클로드 프로젝트 지정) | 사용자 지정값이다. 런타임 독립 확인·실제 모델 목록·Astra 선택 가능 여부는 미확인 | 예 |
| A4 인계 | 완료 | 이 REPORT, handoff/STATE.md, usage-log.md, logs/ | 기존 Claude 사용·잔액 장부는 수정·커밋하지 않음 | 예 |
| A5 Claude 도구·시험 호출 | 해당 없음 | 이번 호출 0회 | 네트워크·API·설치 금지 준수 | 예 |
| B1 push | 해당 없음 | 이번 push 없음 | 원격 조회도 하지 않음 | 예 |
| B2 기반 모듈 | 완료 | 최종 전체 로그 | 기존 테스트 통과, 코드 변경 없음 | 예 |
| B3 probe | 완료 | 같은 로그 | 기존 테스트 통과. 별도 PC 실행 파일 경로 감사는 미실시 | 일부 |
| B4 convert | 완료 | 같은 로그 | 기존 합성 테스트 통과. 새 실제 클립 변환 없음 | 예 |
| B5 compare | 완료 | 같은 로그 | head2·tail11·other_clip 포함 | 예 |
| B6 tiles·split·Blender | 일부 | 기존 테스트·4단계 스크립트 | tiles·split 회귀 통과. Blender 실제 저장은 미검증 | 일부 |
| B7 샘플·PR | 해당 없음 | PR 조회·변경 없음 | 이번 범위 밖 | 해당 없음 |
| C 워크플로우 감사·템플릿 | 미착수 | 해당 없음 | 이번 범위 밖 | 해당 없음 |
| D sangsang-voice | 미착수 | 해당 없음 | 이번 범위 밖 | 해당 없음 |
| E CMMI | 미착수 | 해당 없음 | 이번 범위 밖 | 해당 없음 |

| 18번 단계 | 상태 | 커밋 | 구현·검증 근거 |
| --- | --- | --- | --- |
| 1 모델·manifest·버전 규칙 | 완료 | ee20db7 | model.py:13, manifest.py:14. 복사된 파일 재검토, 전체 191건 통과 |
| 2 init·new-version | 완료 | 80dae48 | storage.py:17·40, __init__.py:16, cli.py:62. 집중 11건·전체 202건 통과 |
| 3 check·pin | 완료 | f03cd95, 보완 ff92944 | check.py:20, model.py:69, renders.py. 최초 집중 18건·전체 220건, 보완 후 집중 20건·전체 222건 통과 |
| 4 Blender 저장 스크립트 | 완료 | 4321655 | tools/blender/save_next_version.py:26. 정적 검사 통과, 전체 회귀 220건. Blender 실행 미검증 |
| 5 README | 완료 | 1d0b867 | tools/plating/README.md:58. 네 명령·Blender 주 경로·보존·판정·실행 한계 문서화. 최종 전체 222건 통과 |

위 표의 짧은 파일명은 `src/plating_tools/blockout/` 기준이다. 3단계 보완 커밋은 4단계 뒤 최종 규약 대조에서 발견한 기존 요구의 검사 누락을 수정한 것이다. 설계 변경은 없다.

구현된 동작:

- ManifestStore·VersionStore Protocol과 파일시스템 구현 하나씩을 둔다. stdlib만 사용하며 기존 `plating_tools/versions/`는 변경하지 않았다.
- init은 빈 current·versions·pins와 필수 폴더를 staging에서 공개한다. 자산이 이미 있으면 종료 2다.
- new-version은 manifest·versions·archive의 최대 번호 다음 vNNN을 사용한다. 파일과 NOTES.md를 staging에 만들고 전체 SHA-256을 기록한 뒤 rename한다. 기존 버전을 덮어쓰지 않으며 current는 --set-current일 때만 갱신한다.
- pin은 비어 있지 않은 승인 인용문·승인자·유효 날짜·기록된 버전·S#NN 씬이 필요하다. current를 바꾸지 않는다. 같은 자산의 쓰기는 배타적 잠금으로 겹치지 않게 한다.
- check는 입력을 바꾸지 않고 JSON·Markdown·run.json을 설정 output_root의 새 실행 폴더에 공개한다. STALE·PINNED·CONVENTION·IMMUTABLE을 각각 판정한다. PINNED만 있으면 종료 0, 위반은 1이다. 나머지는 기존 입력 불량 2·출력 충돌 3·모듈 없음 4·I/O 실패 5 의미를 유지한다.

렌더 이름은 `<asset>_vNNN_<view>[_<variant>].png`다. 날짜·접미사·미등록 판·폴더와 파일 버전 불일치를 검출한다. 파일명 또는 렌더 루트 자체부터의 경로에 명시한 정확한 S#NN만 pin 범위로 읽는다. 씬을 추정하지 않으며 다른 렌더는 current와 비교한다. --renders는 기본 자산별 renders 대신 지정한 루트를 검사한다.

불변 검사는 versions와 archive 양쪽의 파일 목록·해시·버전 폴더 누락을 확인한다. `tests/test_pt_blockout_check.py:112`는 파일을 정확히 1바이트 변조해 IMMUTABLE을 확인한다. 추가·삭제·중복 정본·아카이브·읽기 전용 mtime 보존도 검증했다. 렌더 날짜·명시 루트 문맥 회귀는 같은 파일 :212 이후다.

실패 staging과 manifest 저장 실패 뒤 미등록 버전은 진단용으로 남긴다. 자동 삭제·덮어쓰기·archive 이동·렌더 정리는 하지 않는다. NOTES.md도 불변 해시에 포함된다.

## 3. 결과물 목록

- 저장소: `C:/Users/uicus/Dev/pqw-bo`, 브랜치 `dot/blockout-convention`, 기준 HEAD `3ea3022`, 구현·문서 완료 HEAD `1d0b867`. 최종 REPORT·STATE 확정은 별도 인계 커밋이다.
- 코드: `src/plating_tools/blockout/{__init__,model,manifest,storage,check,renders}.py`, `src/plating_tools/cli.py:62`.
- 스크립트: `tools/blender/save_next_version.py:26`.
- 문서: `tools/plating/README.md:58`.
- 테스트: `tests/test_pt_blockout_{model,commands,check}.py`, 총 37건(모델 6·생성 11·검사 20). 기존 185건과 합쳐 최종 222건이다.
- 인계: 이 REPORT, `handoff/STATE.md`, `handoff/usage-log.md`. 복사된 `REPORT_0823_blockout.md`와 이전 로그 5개는 과거 기록으로 보존·커밋했다.
- 설계 근거: 저장소 밖 `dot-handoff/18_블록아웃규약도구_구현지시_2026-11-08.md`, `blockout_plan_2026-11-07.md`, 02·05·07·08·09·12번. 읽기만 했다.
- PR·원격 URL·새 실제 미디어 출력: 해당 없음.

| 검증 시점 | 전체 테스트 | 실패·오류·skip | 전체 출력 로그 |
| --- | --- | --- | --- |
| 1단계 | 191건, 19.222초 | 0·0·0 | handoff/logs/win_3ea3022_20261108_092404_659.txt |
| 2단계 | 202건, 21.051초 | 0·0·0 | handoff/logs/win_ee20db7_20261108_092834_351.txt |
| 3단계 | 220건, 25.541초 | 0·0·0 | handoff/logs/win_80dae48_20261108_093504_498.txt |
| 4단계 | 220건, 17.018초 | 0·0·0 | handoff/logs/win_f03cd95_20261108_093736_131.txt |
| 3단계 보완 | 222건, 42.127초 | 0·0·0 | handoff/logs/win_4321655_20261108_094016_849.txt |
| 5단계 최종 | 222건, 38.915초 | 0·0·0 | handoff/logs/win_ff92944_20261108_094222_763.txt |

테스트 실행 명령은 아래 단독 명령 또는 지정한 단일 모듈 명령만 사용했다. PATH 설정·구분자·파이프·리다이렉트를 붙이지 않았다.

```powershell
python -m unittest discover -s tests -v
python -m unittest tests.test_pt_blockout_commands -v
python -m unittest tests.test_pt_blockout_check -v
```

로그는 출력 전체를 받은 뒤 별도 단계에서 저장했다. 파일명 해시는 실행 당시 HEAD다. 수정 전 DEL 인용문 회귀 1건 실패와 렌더 날짜·루트 문맥 회귀 2건 실패 원문도 각각의 3단계 로그에 보존했다. 수정 후 전부 통과했다. 기존 모의 오류 출력의 깨진 한국어 문자열은 임의 복원하지 않았다.

최종 정적 검사: programming 스킬의 기존 stdlib AST 검사기로 신규 패키지·테스트·Blender 스크립트 10파일을 검사해 `no violations in 10 file(s)`, 종료 0을 확인했다. 최종 로그에 원문을 함께 저장했다. 별도 도구 설치는 없다.

Blender 저장 실행은 **미검증**이다. bpy·Blender를 실행하거나 모의 실행하지 않았다. 스크립트는 현재 장면을 `copy=True, relative_remap=False`로 저장소 out/blockout-save/<uuid>/<asset>.blend에 사본 저장한 뒤 외부 Python 3.12의 CLI를 argv·shell=False로 호출하도록 작성했다. bpy import는 이 스크립트 main 안에만 있다. 성공 시 자신의 임시 파일·빈 폴더만 정리하고 실패 사본은 남긴다. 정적 검사와 전체 unittest는 실제 Blender 저장 성공·원본 filepath 유지·외부 자산 상대 경로 해석을 보증하지 않는다.

로그 저장 경위: 3단계 출력 전체를 셸 인자로 합치다 Windows CreateProcessAsUserW 206 길이 제한으로 파일 작성 전에 실패했다. 보존한 출력을 apply_patch로 저장했으며 로그를 얻으려고 테스트를 반복하지 않았다.

## 4. 사용량

| 항목 | 값 | 확인 방법 |
| --- | --- | --- |
| 코덱스 주간 한도 잔여 | 미확인 | 네트워크 금지로 조회하지 않음 |
| 모델·effort | CLI 실행, 모델 gpt-6.1-sol, effort xhigh(클로드 프로젝트 지정) | 사용자 지정, 런타임 독립 확인 미확인 |
| 이번 작업 수 | 단계 5건·3단계 보완 1건·최종 인계 1건 | handoff/usage-log.md, 총 7건 |
| 초기화권 | 해당 없음 | 요청·사용 없음 |
| Claude API | 이번 0회·0토큰 | 기존 사용·잔액 장부를 수정하지 않음 |
| Console 잔액 | 미확인 | 조회하지 않음 |
| claude -p | 없음 | 실행하지 않음 |

## 5. 사용자 답이 필요한 것·설계 변경 제안

중간 질문 없음. 사용자 답이 필요한 미결 없음. **설계 변경 제안 0건.**

사용자 확인(2026-11-08 ts): 새 블록아웃 버전은 build.py가 아니라 Blender에서 저장해 만든다. 4단계 스크립트를 주 경로로 문서화했다. Drive에는 최신 5개만 두고 더 옛 버전은 프로젝트 폴더에만 둔다. Drive 보관·동기화는 이번 범위 밖이며 기록만 했다.

## 6. 규칙 위반 자가 점검

- raw 직접 쓰기 없음: 예.
- 원본·기존 버전·기존 결과 덮어쓰기 없음: 예. 인계 파일은 지시대로 갱신했다.
- 핸드북 md·노션·workflow·specification 변경 없음: 예.
- API 키 조회·출력·저장, 네트워크·push·API 호출·설치 없음: 예.
- 검수 없는 설계 변경 없음: 예.
- 쓰기는 pqw-bo 작업 폴더와 그 안 .git뿐: 예. dot-handoff·스킬 파일은 읽기만 했다.
- src/plating_qc·기존 plating_tools/versions·루트 config.toml 변경 없음: 예. 기준 3ea3022 대비 금지 경로 diff에 파일 없음.
- handoff/claude-usage.*·claude-balance.json 수정·stage·커밋 없음: 예.
- 테스트 단독 명령·출력 수신 후 로그 저장 준수: 예.
- 테스트 파일에는 테스트 코드만 작성: 예. 로그 저장 코드를 넣지 않았다.
- 합성 파일·기본 tempfile은 out/pt-tests 안: 예.
- Blender 실행을 검증했다고 주장하지 않음: 예.
- Git 쓰기 실패 시 1회 확인 후 중단 조건: 이번 해당 없음. 모든 단계 커밋 성공.
