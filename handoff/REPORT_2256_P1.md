# P1 진행 보고 (2026-11-07 22:56 KST)

## 1. 한 줄 상태

- 현재 단계: 16번 P1 1~4단계 구현·검증·단계별 커밋 완료. 최종 전체 185건, 실패·오류·skip 0.
- 다음 행동: 클로드 프로젝트가 이 REPORT와 로컬 커밋 4개를 검수한다. push는 이번에 하지 않았다.
- 막힌 것: 없음. R16 실제 GET, 실제 블록아웃 경로 설정·실행, 선택 Q7 실제 QC 통합은 이번 실행에서 제외했다.
- 시작: `C:/Users/uicus/Dev/plating-qc-workflows`, `design/plating-qc-request`, HEAD `709d9de337b2eb43230a3b026c32e27143fdffcb` 확인. 구현 완료 HEAD `a259cf0`. REPORT·STATE·사용 기록은 별도 후속 커밋이다.

## 2. 작업 체크리스트

### 16번 실행 범위

| 단계 | 상태·커밋 | 근거 | 검수 기준·결과 |
| --- | --- | --- | --- |
| 1 refs check + R1~R15 | 완료 `7612db8` | `src/plating_tools/refs/`, `tests/test_pt_refs.py`, `tests/test_pt_refs_fetch.py` | 17개 신규 테스트. 정상 JPEG·PNG·WebP 헤더, 해시 대응, HTML·상태 오류·timeout·redirect·크기 한도, 번호·장수 권고·시트/검수 상태·최대 원본·축소본 거부·썸네일·기본 GET 0회. 전체 157건 통과 |
| 2 versions check + V1~V10 | 완료 `b8755fc` | `src/plating_tools/versions/`, `tests/test_pt_versions.py` | 14개 신규 테스트. v9/v10 정수 비교, 판 없음·옛 판·범위 pin·근거 거부·접미사 순서·계열/백업 분리·출처 충돌·읽기 전용·미검증 표시. 전체 171건 통과 |
| 3 QC 위임 + Q1~Q6 | 완료 `cbe3519` | `src/plating_tools/qc.py`, `tests/test_pt_qc.py` | 13개 신규 테스트. argv 배열·shell=False, 작업/로그 격리, 원바이트와 종료 1 보존, 종료 4/5·timeout 격리, convert dry-run 강제, 하위 출력 인자 거부, AST import 금지. 전체 184건 통과 |
| 4 P0 회귀 | 완료 `a259cf0` | `tests/test_pt_independence.py:27`, `tests/__init__.py:1`, `tools/plating/README.md` | P1이 없는 사본에서 모든 P0 명령 실행. 잘못된 P1 설정도 P0에 영향 없음. 사본 하위 프로세스마다 소켓 연결 0회·P1/QC import 없음 확인. 최종 185건 통과 |

**refs 경계.** `HttpFetcher`, `ImageTool`, `ReferenceResolver` 추상 경계를 뒀다. 모든 새 테스트는 가짜 HTTP 응답·가짜 이미지 도구를 사용하며 실제 GET·실제 이미지 FFmpeg 호출은 하지 않았다. `UrllibFetcher`의 opener도 가짜로 바꿨다. 본문 SHA-256이 같을 때만 바이트 동일이다. 응답 한도 초과는 해시 대응 미확인으로 남는다. 후보 전수 선언·근거·선택 파일의 최대 픽셀 조건을 모두 만족해야 최대 원본 확인됨이다.

`--thumbs` 구현은 승인 D1에 따라 `[tools] ffmpeg_path`를 읽는다. 디렉터리 또는 실행 파일을 받고, 빈 값이면 PATH 탐색이다. 기존 FFmpeg를 argv로 직접 호출하며 `-n`과 새 실행 폴더로 덮어쓰기를 막는다. 도구 없음은 종료 4·결과 없음이다. `contact.html`에는 번호·파일명·역할·시트 상태·검수 상태와 보기용 표기를 둔다. 이 HTML과 썸네일은 가짜 도구로 생성·검사했다. 실제 썸네일 디코딩·육안 검수는 미확인이다.

**versions 경계.** 합성 이름·README만 `out/pt-tests/`에서 만들었다. 실제 블록아웃 폴더 설정·스캔은 하지 않았다. `.blend`와 스크립트는 이름으로만 비교하며 실행하거나 본문을 읽지 않는다. README만 읽고, mtime은 판 근거로 쓰지 않는다. pin 승인자는 `ts`로 검증한다. I14 실제 경로·계열 규칙은 미확인이다. I15 실제 적용 범위도 미확인이므로 spec/pins에 명시한 씬 범위만 적용하는 설계 기본값을 유지한다. 실제 pin 파일은 만들지 않았다. 테스트의 S#10/v50 근거는 W04:135의 `S#10은 v50 유지`를 읽기 전용 확인했다. 모든 렌더 결과에 형상 동일성·실제 치수 미검증을 남긴다.

**QC 경계.** `QcRunner` 추상 경계와 `SubprocessQcRunner`를 뒀다. 실행은 `[python, '-m', 'plating_qc', ...]`뿐이다. `plating_qc`를 import하지 않는 AST 검사를 새 테스트에 고정했다. 환경은 부모 환경 복사에 `PLATING_QC_LOG_DIR`, `PYTHONIOENCODING` 두 값만 바꾼다. 입력은 절대 경로, cwd는 실행 폴더의 `qc/1/`, 로그와 하위 출력도 그 안이다. stdout/stderr는 원바이트로 저장하고 생성물 경로·크기·SHA-256과 입력 부모 폴더의 전후 차이를 기록한다. 종료 1을 성공으로 바꾸지 않으며 결과와 생성물을 공개한다. 종료 2~5와 timeout은 `_failed/`에 원출력·qc.json·run.json을 보존한다. timeout은 상위 종료 5다. 모듈 없음의 하위 종료 1은 기록에 그대로 남기고 상위 종료 4로 분류한다.

QC 사용자 하위 인자의 `--out`, `--log`, `--config`는 거부한다. 기존 CLI의 `--out`은 툴킷 실행 폴더를 지정하는 용도로만 사용하며, 하위 QC 출력 경로는 코드가 지정한다. `convert`는 `--dry-run` 없으면 프로세스 시작 전에 종료 2다. 실제 QC 통합은 하지 않았고, subprocess 경계에 가짜를 주입해 원출력·인자·종료·생성물을 검증했다. 생성물·로그·stdout/stderr 경로는 공개된 실행 폴더 기준이고, argv·cwd·환경은 실행 당시 staging 경로를 그대로 보존한다.

**P0 독립성.** 사본에 refs/, versions/, qc.py가 없음을 먼저 확인했다. `--help`, P1 그룹의 `--help`, cuts inventory/extract, prompt skeleton/check, gate check/cost를 실행했다. 미완성 프롬프트·게이트의 정상 경고 종료 1도 확인했다. 사본의 P1 실제 명령은 각각 종료 4다. 테스트 전용 sitecustomize는 각 하위 프로세스에서 소켓 연결 시도와 P1/QC 모듈 적재를 기록하고, 둘 다 0임을 단언한다. P0의 정적 표준 라이브러리 의존 검사도 유지했다.

### 05 형식의 기존 브리핑 항목

| 항목 | 상태 | 근거 | 검수 기준·충족 |
| --- | --- | --- | --- |
| A1 세 저장소 클론 | 일부 확인 | 현재 저장소·시작 HEAD 709d9de | 다른 저장소 HEAD는 이번 범위 밖, 미확인 |
| A2 스킬 작성·설치 | 적용 완료 | 로컬 caveman·ponytail·i-have-adhd SKILL.md 읽음. git-master·programming도 적용 | 새 설치 없음. 전체 스킬 설치 감사는 미확인 |
| A3 모델 목록 확인 | 지정값 기록 완료 | 사용자 지시 | CLI 실행, 모델 gpt-6.1-sol, effort xhigh(클로드 프로젝트 지정) |
| A4 인계 기록 | 완료 | 이 REPORT, `handoff/STATE.md`, `handoff/usage-log.md` | 현재 상태·다음 행동·검증 근거 기록 |
| A5 Claude 도구·시험 호출 | 해당 없음 | 이번 API 0회 | API 금지 준수. 기존 장부 변경 없음 |
| B1 첫 push | 해당 없음 | 이번 push 없음 | 네트워크·push 금지 준수 |
| B2 기반 모듈 | 기존 테스트 재검증 완료 | 최종 185건 로그 | 기존 QC 테스트 포함 통과. src/plating_qc 변경 없음 |
| B3 probe | 기존 테스트 재검증 완료 | 같은 로그 | FFmpeg PATH 변경 없이 통과. 실제 클립 실행 없음 |
| B4 convert | 기존 테스트 재검증 완료 | 같은 로그 | 합성 변환 통과. 새 QC 위임 convert는 가짜 dry-run만 검증 |
| B5 compare | 기존 테스트 재검증 완료 | 같은 로그 | head2·tail11·other_clip 등 기존 시나리오 통과 |
| B6 tiles·split·Blender | 일부 재검증 | 같은 로그 | 기존 tiles·split 통과. 실제 Blender 실행 없음 |
| B7 샘플·PR | 해당 없음 | `tools/plating/README.md` 사용법 갱신 | PR 조회·변경·push 없음. 실제 미디어 산출물 커밋 없음 |
| C 워크플로우 감사·템플릿 | 미착수 | 해당 없음 | 이번 범위 밖 |
| D sangsang-voice | 미착수 | 해당 없음 | 이번 범위 밖 |
| E CMMI | 미착수 | 해당 없음 | 이번 범위 밖 |

A3는 지정 문구다. 런타임 모델·effort 독립 확인과 Astra 목록은 미확인이다.

## 3. 결과물 목록

| 종류 | 경로·값 | 비고 |
| --- | --- | --- |
| 1단계 커밋 | `7612db8` Implement P1 stage 1 reference checks and thumbnails | refs 코드·테스트·로그, 지연 import, P0 정적 검사 범위 구분 |
| 2단계 커밋 | `b8755fc` Implement P1 stage 2 blockout version checks | versions 코드·테스트·로그, W04 문서 키 등록 |
| 3단계 커밋 | `cbe3519` Implement P1 stage 3 isolated QC subprocess delegation | QC 코드·테스트·로그 |
| 4단계 커밋 | `a259cf0` Verify P1 stage 4 P0 isolation and repository test writes | P0 격리 검사·테스트 tempfile 범위·사용법·로그 |
| 인계 | `handoff/REPORT_2256_P1.md`, `handoff/STATE.md`, `handoff/usage-log.md` | 별도 기록 커밋 |
| 설계 근거 | `design/plating-tools.draft.md` 2.6~2.8, 4.5~4.7, 4.9 / 12번 D1 / 16번 지시 | 초안 본문 변경 없음 |
| 사용법 | `tools/plating/README.md` | refs·versions·QC 명령·설정·검증 범위 |
| PR·원격 URL | 해당 없음 | 네트워크 조회 없음 |

### 테스트 명령·전체 로그

전체 테스트는 매번 정확히 `python -m unittest discover -s tests -v` 단독 명령이다. 대상 테스트도 `python -m unittest tests.test_xxx -v` 단독 명령만 사용했다. 앞에 PATH·환경 설정, 구분자, 파이프, 리다이렉트를 붙이지 않았다. 테스트 파일에 로그 저장 코드를 넣지 않았다. 도구 출력을 받은 뒤 별도 단계에서 로그를 저장했다. 파일명의 해시는 실행 당시 HEAD, 시각은 로그 저장 시각이다.

| 검증 | 총계 / 실패 / 오류 / skip | 시간 | 전체 로그 |
| --- | --- | --- | --- |
| 시작 기준선 | 140 / 0 / 0 / 0 | 18.202s | `handoff/logs/win_709d9de_20261107_224151_133.txt` |
| 1단계 HTTP 대상 | 6 / 0 / 0 / 0 | 0.054s | `handoff/logs/win_709d9de_20261107_224130_414.txt` |
| 1단계 전체 | 157 / 0 / 0 / 0 | 19.116s | `handoff/logs/win_709d9de_20261107_224134_053.txt` |
| 2단계 대상 | 12 / 0 / 0 / 0 | 0.132s | `handoff/logs/win_7612db8_20261107_224645_825.txt` |
| 2단계 전체 | 171 / 0 / 0 / 0 | 18.442s | `handoff/logs/win_7612db8_20261107_224646_859.txt` |
| 3단계 대상 | 11 / 0 / 0 / 0 | 0.203s | `handoff/logs/win_b8755fc_20261107_225141_953.txt` |
| 3단계 전체 | 184 / 0 / 0 / 0 | 16.005s | `handoff/logs/win_b8755fc_20261107_225142_962.txt` |
| 4단계 독립성 대상 | 4 / 0 / 0 / 0 | 1.748s | `handoff/logs/win_cbe3519_20261107_225604_162.txt` |
| 최종 전체 | 185 / 0 / 0 / 0 | 20.711s | `handoff/logs/win_cbe3519_20261107_225605_092.txt` |

최종 185건 = 시작 140 + refs 17 + versions 14 + QC 13 + 기본 tempfile 경계 1이다. 2·3단계 대상 검사 후 보강한 테스트는 해당 단계 전체 검사에서 통과했다. 최종 전체 검사는 a259cf0와 같은 코드·테스트 작업 트리를 커밋 전에 검증한 결과다. 이후 제품 코드·테스트 변경은 없다.

구현 전 실패 로그도 보존했다. refs 미구현 11오류: `handoff/logs/win_709d9de_20261107_224128_531.txt`. refs 중간 검사 2오류: `handoff/logs/win_709d9de_20261107_224129_455.txt`(하위 resolve 모듈과 문서 resolve 함수 이름 충돌, import 별칭으로 수정). versions 미구현 12오류: `handoff/logs/win_7612db8_20261107_224644_824.txt`. QC 미구현 11오류: `handoff/logs/win_b8755fc_20261107_225140_946.txt`. 모두 후속 전체 검사에서 해소했다. versions 첫 red 출력이 도구 출력 한도로 잘려, 동일한 단독 명령으로 완전 출력을 다시 받아 저장했다. 일부 기존 한국어 모의 오류 문자열은 도구 수신 시 깨진 상태이며 임의 복원하지 않았다.

## 4. 사용량

| 항목 | 값 | 확인 방법 |
| --- | --- | --- |
| 코덱스 주간 한도 | 미확인 | 네트워크 금지. 과거 값을 현재 값으로 사용하지 않음 |
| 이번 모델·effort | CLI 실행, 모델 gpt-6.1-sol, effort xhigh(클로드 프로젝트 지정) | 사용자 지정. 런타임 독립 확인 미확인 |
| 작업 수 | 1~4단계 각 1건 | usage-log.md |
| 초기화권 | 해당 없음 | 요청·사용 없음 |
| Claude API | 이번 0회·0토큰 | 기존 usage·balance 장부 변경 없음 |
| Console 잔액 | 미확인 | 조회하지 않음 |
| claude -p | 없음 | 실행하지 않음 |

## 5. 사용자 답이 필요한 것·설계 변경 제안

1. I14 실제 블록아웃 계열·폴더·README 형식·렌더 위치·v2i 의미: 미확인. 실제 설정과 실행은 답 이후 별도 작업이다. 이번 합성 검증은 완료했다.
2. I15 실제 pin 적용 범위: 미확인. 승인자 표기는 지시대로 ts다. 답 전에는 설계 기본값인 파일 명시 범위만 적용한다.

중간 질문 없음. **설계 변경 제안 0건.** 끝낸 단계는 1~4 전체이며, 못 끝낸 구현 단계는 없다. R16 실제 GET·실제 경로 실행·선택 Q7은 지시상 제외하거나 선택 항목으로 실행하지 않았다. 다음 첫 할 일은 클로드 프로젝트의 로컬 커밋 검수다.

## 6. 규칙 위반 자가 점검

- raw 아래 직접 쓰기 없음: 예. 기존 QC 테스트의 합성 raw fixture는 기존 동작이며 테스트 전용 임시 폴더다.
- 원본·기존 결과 덮어쓰기 없음: 예. 새 실행 폴더·배타적 파일 생성 사용. 기존 사용자 미추적 파일 보존.
- 핸드북·노션·workflow·specification 수정 없음: 예. W02·W04 등은 읽기 전용이다.
- API 키 조회·출력·저장 없음: 예.
- 유료 생성 API·실제 GET 없음: 예. 새 HTTP 검사는 가짜 opener·응답만 사용했다.
- 검수 없이 제품 설계 변경 없음: 예. 12번 D1·16번 범위만 구현했다.
- 네트워크·push·API·설치·전역 설정 변경 없음: 예. 새 테스트는 두 소켓 연결 경계를 막고 호출 0회를 단언했다. P0 사본 하위 프로세스도 별도로 단언했다.
- 저장소 밖 쓰기 없음: **예외 있음.** 기준선~3단계 전체 검사는 기존 테스트가 원래 쓰던 시스템 TEMP(`C:/Users/uicus/AppData/Local/Temp`)를 사용했다. 실행 전에 이 기본값을 확인하지 못했다. 해당 테스트는 자신이 만든 TemporaryDirectory를 정리하는 기존 동작이다. 4단계에서 `tests/__init__.py`의 테스트 초기화로 기본 tempfile 경로를 저장소 `out/pt-tests/tempfile`에 한정했고, 그 조건을 검사한 최종 185건이 통과했다. 새 P1 테스트와 직접 작성한 파일은 처음부터 저장소 안에만 뒀다. 시스템 TEMP 전체 정리·권한 변경은 하지 않았다.
- src/plating_qc 동결: 예. 시작 709d9de 대비 diff 없음. 루트 config.toml·기존 REPORT_1536·과거 미추적 로그를 변경·커밋하지 않았다.
- handoff/claude-usage.*·claude-balance.json 변경·커밋 없음: 예. 시작 HEAD 대비 보호 경로 diff 없음.
- 실제 F 출력·미디어·fixture 커밋 없음: 예. `git ls-files -- out` 결과 없음. 설계 초안 본문 diff 없음.
- 코드·테스트 diff 공백 검사: 통과. 새 제품 모듈은 모두 순수 코드 200행 이하다. 파일별 책임은 이미지 헤더/도구, HTTP, 후보, 레퍼런스 판정, 버전 모델/스캔/판정, CLI 경계, QC 프로세스 경계로 구분했다. 사용자 입력은 각 P1 로더에서 검사하고, 외부 동작은 승인된 추상 경계로 한정했다. 추가 패키지·미래용 추상화는 만들지 않았다.
