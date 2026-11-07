# P0 진행 보고 (2026-11-07 21:28 KST)

## 1. 한 줄 상태

- 현재 단계: 12번 P0 1~6단계 구현·검증·단계 커밋 완료. 3단계의 실제 문법 차이 2항목은 승인 전 구현하지 않고 보류했다.
- 다음 행동: 클로드 프로젝트가 아래 설계 변경 제안 2건을 검수한다. dot는 push·네트워크·API·설치를 하지 않는다.
- 막힌 것: 환경 오류 없음. 시작 기준선 66건 통과로 tempfile 재개 조건을 확인했다. S#02 자동 인식과 추가 TC 형식만 설계 결정 대기다.
- 검증 기준 HEAD: `e57ccbe`. 이 REPORT와 마지막 로그를 넣는 후속 커밋은 인계 기록 전용이다.

## 2. 작업 체크리스트

### 12번 실행 범위

| 항목 | 상태 | 근거 커밋 | 검수 기준·충족 |
| --- | --- | --- | --- |
| 0 설계·결정표 | 기존 완료 | e9bfaee, 3892adf | 이전 커밋 보존, REPORT_1935 수정 없음 |
| 1 공통 + S1~S6 | 완료 | ced18a5 | 75건 통과. raw·junction·입력/읽기 전용 루트·충돌·격리·재실행 |
| 2 inventory | 완료 | 83a9dcf | 78건 통과. 실제 F, 15섹션, 색 유실 0 |
| 3 extract + C1~C22 | 부분 완료 | e8b7955 | 93건 통과. S#01·S#04 추출. S#02 자동 선택 및 초 단위 TC 확장은 설계 변경 제안으로 보류 |
| 4 prompt + P1~P12 | 완료 | 3385e9a | 104건 통과. 원문 앵커·골격·이미지 한도·검사. 추가 회귀 검증은 6단계 포함 |
| 5 gate + G1~G13 | 완료 | 6285232 | 116건 통과. 8개 응답·승인 SHA 결속·Decimal 비용 |
| 6 S7~S10 | 완료 | e57ccbe | 최종 124건 통과. P1 없는 사본에서 P0 실행·stdlib 검사·소켓 차단·문서 비실행 |

선택적으로 미룰 수 있던 cuts.csv, inventory.md, gate cost --out도 구현했다. P1 refs·versions·QC 실행은 구현하지 않았다. P1 인자와 종료 4 경계만 있다.

C3·C4의 S#02 span ID·주석·6열 구조는 읽기 전용 파서로 검증했다. S#02 자동 추출 성공을 확인한 것은 아니다. C6 셀 green은 12번 I5 결정대로 done이며 행 todo와 합치지 않는다. 초 단위 TC 미지원은 원문 유지·CT006 경고로 남기므로 테스트 실패와 구별한다.

### 05 형식의 기존 브리핑 항목

| 항목 | 상태 | 근거 | 검수 기준 | 충족 |
| --- | --- | --- | --- | --- |
| A1 세 저장소 클론 | 일부 확인 | 현재 저장소, NS-Plating 읽기 | 현재 저장소·NS-Plating HEAD 확인. 다른 두 저장소는 이번 범위 밖 | 일부 |
| A2 스킬 작성·설치 | 읽기 적용 완료, 설치 미수행 | caveman·ponytail, NS-Plating/.claude/skills/i-have-adhd/SKILL.md | 필수 3개 적용. programming·git-master 지침도 적용 | 일부: 전체 설치 감사는 미수행 |
| A3 모델 목록 확인 | 지정값 기록 완료 | 사용자 이번 지시 | CLI 실행, 모델 gpt-6.1-sol, effort xhigh(클로드 프로젝트 지정) | 지정 문구 기록. 런타임 독립 확인·Astra 목록 미확인 |
| A4 인계 기록 | 완료 | STATE.md, usage-log.md, 이 REPORT | 현재 상태·다음 행동·테스트 기록 | 예 |
| A5 Claude 도구·시험 호출 | 해당 없음 | 이번 API 0회 | 이번 API 금지 | 예 |
| B1 첫 push | 해당 없음 | 이번 push 없음 | 이번 push 금지 | 예 |
| B2 기존 기반 모듈 | 기존 테스트 재검증 완료 | 기준선 66건, 최종 전체 124건 로그 | src/plating_qc 변경 없이 회귀 통과 | 예 |
| B3 probe | 기존 테스트 재검증 완료 | 같은 로그 | 기존 테스트 통과 | 예 |
| B4 convert | 기존 테스트 재검증 완료 | 같은 로그 | 기존 테스트 통과. 실제 클립 재변환은 범위 밖 | 예 |
| B5 compare | 기존 테스트 재검증 완료 | 같은 로그 | 기존 시나리오 통과 | 예 |
| B6 tiles·split·Blender | 일부 재검증 | 같은 로그 | tiles·split 기존 테스트 통과, Blender는 이번 미실행 | 일부 |
| B7 샘플·PR | 해당 없음 | 기존 기록 보존 | PR 조회·수정·push 금지 | 해당 없음 |
| C 워크플로우 스킬화·감사·템플릿 | 미착수 | 해당 없음 | 이번 범위 밖 | 해당 없음 |
| D sangsang-voice | 미착수 | 해당 없음 | 이번 범위 밖 | 해당 없음 |
| E CMMI | 미착수 | 해당 없음 | 이번 범위 밖 | 해당 없음 |

### 실제 F inventory 관찰 원문

입력은 121,954 bytes, LF. 전체 15섹션 중 씬 14개와 비씬 녹음 대본 1개다. 다음은 inventory.json에서 읽은 메타데이터·열·색 집계 값이다. 실제 컷 본문을 fixture로 복사해 커밋하지 않았다.

```json
{
  "source_sha256": "cae22e2f0637d29ebfe1f6e5a7daa973ee8ea72a397373246ecdddf9cfe6dc37",
  "metadata": {
    "fetch": "Here is the result of \"fetch\" for the Page with URL https://app.notion.com/p/3eb339339b9b8007bf8afbdd52102e49 as of 2026-11-07T07:06:55.423Z:",
    "properties": "{\"title\":\"스토리보드/컷표\"}"
  },
  "headers": [
    [
      "컷",
      "TC",
      "길이",
      "대사",
      "영어 대사",
      "상황",
      "판정",
      "씬",
      "감정"
    ],
    [
      "컷",
      "TC",
      "길이",
      "샷 / 앵글",
      "화면",
      "대사 / 사운드"
    ],
    [
      "컷",
      "TC",
      "길이",
      "샷 / 앵글",
      "화면",
      "사운드"
    ],
    [
      "컷",
      "TC",
      "길이",
      "샷 / 앵글",
      "화면",
      "사운드",
      "대사"
    ]
  ],
  "colors": {
    "callout": {
      "gray_bg": 2
    },
    "tr": {
      "green_bg": 5,
      "red_bg": 79,
      "gray_bg": 2
    },
    "td": {
      "red_bg": 9,
      "green_bg": 155,
      "gray_bg": 6
    },
    "span": {
      "yellow_bg": 1
    }
  },
  "color_loss": 0,
  "span_attributes": []
}
```

| 제목 원문 텍스트 | 컨테이너 | F 행 |
| --- | --- | --- |
| S#01 오프닝(편집&사운드작업만 남음) | toggle_h3 | 22~386 |
| S#02 HOPE — 신념 | toggle_h3 | 388~923 |
| S#03 절도 | md_h3 | 925~1215 |
| S#04 수정 | md_h3 | 1216~1488 |
| S#05 수정 | md_h3 | 1489~1803 |
| S#06 수정 | md_h3 | 1804~2036 |
| S#07 수정 | md_h3 | 2037~2429 |
| S#08 수정 | md_h3 | 2430~2614 |
| S#09 수정 | md_h3 | 2615~2887 |
| S#10 완 | toggle_h3 | 2888~3141 |
| S#11 수정 | toggle_h3 | 3143~3456 |
| S#12 수정 | md_h3 | 3458~3890 |
| S#13 수정 | md_h3 | 3891~4365 |
| S#14 수정 | md_h3 | 4366~4880 |
| 녹음 대본 (인물별 대사) | md_h3 | 4881~5085 |

- A1: 혼합 경계 확인. 토글 S#01·02·10·11과 나머지 Markdown h3를 구분한다. 녹음 대본은 S#14의 끝 경계다.
- A2: colspan·rowspan 속성 0건.
- A3: color 속성은 tr·td·span·callout뿐이며 원문 집계와 파싱 집계 차이 0.
- A4: 씬 표의 첫 칸 컷·TC 열 구조 확인. 다만 S#02 F:391은 단순 `<table>`로 header-row 속성이 없다. 비씬 녹음 9열 표도 컷·TC로 시작하므로 씬 경계 검사가 필요하다.
- A5: S#04-C001 `00:00.0–02.0`은 0.0~2.0초로 해석한다. 문서에서 분 상속의 의미를 명시한 설명은 미확인이다. 설계 기본값을 쓴다. 이후 `02.0–03.5` 등은 지원 형식 밖이라 보존·경고한다.
- A10: 위 fetch 첫 줄과 properties 제목을 기록했다. fetch 시각은 2026-11-07T07:06:55.423Z다.
- A6~A8: W10 펜스, W02 번호 8줄, W07 행 패턴을 실제 원문으로 확인해 앵커 명세를 작성했다. W10 사람·SCENE 구획에는 여러 펜스가 있어 개수를 검증하고 원문 단위로 읽는다.
- A9·A11: P1 사항. 이번 확인하지 않았다.

### 실제 추출 결과

| 항목 | S#01 | S#04 수정 |
| --- | --- | --- |
| 선택 범위 | F:22~386 | F:1216~1488 |
| 대상 행 | 15 | 12 |
| 행 상태 | done 2, todo 4, unknown 9 | todo 5, unknown 7 |
| 소견 | CT006 5, CT007 1, CT011 1 | CT006 11 |
| 앞 문맥 | 첫 씬이라 없음 | S#03-C014 |
| 뒤 문맥 | CT003: S#02 header-row 속성 없음 | S#05-C001 |
| 종료 | 1, 결과 공개 | 1, 결과 공개 |

S#01-C001은 행 done, 대사 셀 red_bg→todo, 사운드는 색 상태 없음이다. TC는 0~4초, 길이 원문은 4s다. S#01-C003은 행 todo와 ID 셀 green_bg→done을 별도로 보존한다. S#04-C001은 행 unknown, 대사 / 사운드 열 present, 대사·사운드 개별 열 absent다. 길이 원문 2.0s를 유지했다. removed 행은 삭제하지 않으며 생성 제외 플래그를 남긴다.

S#01의 특수 TC `(대안)`, `00:56–α`, `+α`와 ID `(별도 제작)`은 임의 수정하지 않았다. S#04의 나머지 11행도 TC를 채워 넣지 않았다.

### 원문 대조로 확인한 미결 항목

| ID | 확인 결과·처리 |
| --- | --- |
| I2 | 이미지 3000자: W05:30, W02:42. 앵커에서 읽는다. 영상 상한 미확인 유지 |
| I3 | 최소 4초 W07:14. 허용 최소인지 과금 최소인지 미확인. 4초 미만 계산 보류. 최대 30초 W05:9, 정수 초 운영 규칙 W05:16·103 확인 |
| I4 | Topaz 5크레딧 W06:73(실제 §4 설정). 클립당/초당/작업당 적용 단위 미확인. 대안 금액은 Unknown |
| I5·I6 | 12번 결정 적용. 셀·span과 행 상태 독립. 색 있는 필드만 상태 표시 |
| I7 | W05:7의 앞뒤 씬 지시 확인. 번호 ±1이라는 명시는 미확인이라 설계 기본값 유지 |
| I8 | 씬 표의 열 이름은 대응표 안이다. 녹음 9열 표는 비씬. S#02 표 속성 결손은 제안 1로 분리 |
| I9·I10 | W02 승인 어휘를 읽고 인용문·위치·검수 주체·날짜·현재 프롬프트 SHA-256을 기록한다. 최종 승인 판단은 사람 |
| I11 | 사람의 plan.toml 분류 유지. 이름에서 인물 분류를 추정하지 않는다 |
| I12 | W05:16의 여유는 산술 정의 미확인. 해석 가능한 값에만 도구 계산으로 표시. 복수 컷의 개별 생성 길이는 임의 분배하지 않는다 |
| I13 | W05:3·13·70, W02:73에 3~5장 안전 권고. 하드 한도로 확정하지 않는다 |
| I14·I15 | P1 보류 |
| I16 | src/plating_qc/cli.py의 현재 인자와 진입점을 읽음. 동결 유지. QC 위임은 P1 보류 |
| H 대조 | handbook 설정이 비어 있어 직접 대조 미확인. 이번 읽은 W 원문을 근거로 사용 |

### 설계 변경 제안: 2건, 미구현

1. **S#02 header-row 속성 없는 표 선택 허용 여부.** F:391의 `<table>`은 첫 칸 컷·TC 열을 갖지만 설계 2.2의 `header-row="true"` 조건을 만족하지 않는다. 명시적인 --table-line 선택을 허용하거나 머리 내용으로 판단하도록 설계를 바꾸는 안을 제안한다. 현재 CT003을 유지한다. S#01 뒤 문맥과 S#03 앞 문맥의 S#02 연결도 이 결정 전에는 미확인이다.
2. **초 단위 양 끝 TC 형식 추가 여부.** F:1267~1486의 `02.0–03.5` 등은 설계의 M+:SS 시작 조건을 만족하지 않는다. 초 범위 SS(.f)–SS(.f)를 별도 형식으로 승인하는 안을 제안한다. 현재 11행 CT006, 원문·길이 값은 보존한다.

다음 첫 할 일은 제안 1의 판정 규칙을 클로드 프로젝트가 확정하는 것이다. 승인 전 두 항목을 구현하지 않는다.

## 3. 결과물 목록

| 종류 | 경로·값 | 비고 |
| --- | --- | --- |
| 저장소·브랜치 | C:/Users/uicus/Dev/plating-qc-workflows, design/plating-qc-request | 시작 3892adf |
| 구현 | src/plating_tools/ | P0만, stdlib |
| 설정·진입점 | plating.toml, pyproject.toml | plating 추가. 재설치 없음. 기존 config.toml 불변 |
| 실행 안내 | tools/plating/README.md | 소스 경로·명령·종료 코드·보류 항목 |
| 설계 | design/plating-tools.draft.md, design/plating-tools.review.md | 원문·결정표 불변 |
| 최신 인계 | handoff/STATE.md, handoff/usage-log.md | 새 상태 추가 |
| 기존 REPORT | handoff/REPORT_1935_P0.md | 수정하지 않음 |
| PR | 해당 없음 | 조회·생성·수정·push 없음 |

### 테스트 전체 로그

명령은 매번 정확히 `python -m unittest discover -s tests -v` 단독으로 실행했다. FFmpeg PATH를 추가하지 않았다. 로그는 명령 출력을 받은 뒤 별도 단계에서 저장했다. 아래는 각 단계 최종 통과 로그다. 건수 표기는 총계 / 실패·오류 / skip이다.

| 단계 | 건수 | 전체 로그 |
| --- | --- | --- |
| 재개 기준선 | 66 / 0 / 0 | `handoff/logs/win_3892adf_20261107_2049_baseline.txt` |
| 1단계 | 75 / 0 / 0 | `handoff/logs/win_ced18a5_20261107_2053_stage1.txt` |
| 2단계 | 78 / 0 / 0 | `handoff/logs/win_83a9dcf_20261107_205707_stage2.txt` |
| 3단계 | 93 / 0 / 0 | `handoff/logs/win_e8b7955_20261107_210301_stage3.txt` |
| 4단계 | 104 / 0 / 0 | `handoff/logs/win_3385e9a_20261107_211152_stage4.txt` |
| 5단계 | 116 / 0 / 0 | `handoff/logs/win_6285232_20261107_211753_stage5.txt` |
| 6단계 | 124 / 0 / 0 | `handoff/logs/win_e57ccbe_20261107_212832_stage6.txt` |

최종 전체 124건 = 기존 66건 + 새 P0 58건. 실패 0, 오류 0, skip 0, 15.889초. P0 테스트는 소켓 연결을 차단하고 연결 시도 0을 확인한다. 실제 F/W를 복사해 fixture로 커밋하지 않는다. T2 입력이 없거나 F 지문이 다르면 해당 테스트는 skip하도록 구현했다.

추가 단독 명령 `python -m unittest tests.test_pt_prompt -v`: 13건, 실패·오류·skip 0. 로그 `handoff/logs/win_e57ccbe_20261107_212832_prompt_targeted.txt`. 개발 중 미구현 기능의 red와 회귀 오류를 수정한 뒤 최종 통과한 결과다. 미해결 실패는 없다.

### 실제 CLI 수동 확인

전체 명령과 stdout/stderr, 종료 코드는 `handoff/logs/win_e57ccbe_20261107_212832_manual.txt`에 있다. PowerShell의 네이티브 종료 코드 4는 `exit $LASTEXITCODE`로 도구까지 전달해 확인했다. unittest 명령에는 이를 붙이지 않았다.

| 명령 | 종료 | 로컬 결과(커밋 제외) |
| --- | --- | --- |
| --help | 0 | 모든 P0·P1 그룹 도움말 |
| cuts inventory | 0 | out/20261107T122655-a38fad_cuts-inventory_F |
| cuts extract --scene S#01 | 1 | out/20261107T122656-8cf373_cuts-extract_S01 |
| cuts extract --scene S#04 | 1 | out/20261107T122657-634bc7_cuts-extract_S04 |
| prompt skeleton, S#04, 계획 없음 | 1 | out/20261107T122658-4fa32b_prompt-skeleton_unplanned |
| prompt check, 골격 본문 | 1 | out/20261107T122724-d4f7a6_prompt-check_unplanned |
| gate check, 빈 응답, --require-approval | 1 | out/20261107T122728-ec709b_gate-check_unplanned |
| gate cost, 4초 480p new | 0 | stdout: 4 × 20 = 80 Crons |
| gate cost, 1.5초 1080p edit | 0 | stdout: ceil(1.5) × 110 = 220 Crons |
| gate cost, 4초 1080p new | 1 | 요청 324 Crons, 대안 480p 80 Crons, Topaz 적용 단위 미확인 |
| refs check | 4 | P1 모듈 없음: plating_tools.refs |

게이트는 [점검 미완료]를 유지한다. 점검 완료·승인 기록 유무는 분리한다. 골격을 실제 전송본이나 생성 승인으로 취급하지 않는다. 1080p 대안과 요청 비용은 서로 합산하지 않으며 Crons와 Higgsfield 크레딧도 합산하지 않는다.

입력 workflow의 실제 Git HEAD는 `577c3d4cc607c823603fe1aa0e78fa02773a8e33`으로 읽어 확인했다. 도구 실행 기록의 declared_commit은 선언값이며 도구 자체가 Git을 실행해 검증한 값으로 표기하지 않는다.

## 4. 사용량

| 항목 | 값 | 확인 방법 |
| --- | --- | --- |
| 코덱스 주간 한도 | 이번 미측정 | 네트워크 금지. 과거 97%를 현재 값으로 사용하지 않음 |
| 이번 모델·effort | CLI 실행, 모델 gpt-6.1-sol, effort xhigh(클로드 프로젝트 지정) | 사용자 지정, usage-log.md 추가 |
| 초기화권 | 없음 | 요청·사용 없음 |
| Claude API | 이번 0회·0토큰 | API 실행 없음. 기존 사용 장부 불변 |
| Console 잔액 | 미확인 | 조회 금지 |
| claude -p | 없음 | 실행 없음 |

## 5. 사용자 답이 필요한 것

1. 설계 변경 제안 1·2는 클로드 프로젝트 검수 대기다. 이번 실행 중 질문하지 않았고 해당 확장만 보류했다.
2. Topaz 적용 단위, 최소 4초 의미, 여유의 공식 정의, 승인 증거·검수 주체의 최종 규칙은 원문으로 확정하지 못했다. 12번 기본값·미확인 처리를 유지한다.
3. P1 기능은 이번 범위 밖이다. 레퍼런스 GET·썸네일·버전 스캔·QC 위임을 실행하지 않았다.

## 6. 규칙 위반 자가 점검

- raw 아래 쓰기 없음: 예.
- 원본·기존 결과 덮어쓰기 없음: 예. 새 실행 폴더만 공개. 실패 시 자기 staging의 run.json 상태만 갱신한다.
- 핸드북·노션·workflow·specification 수정 없음: 예.
- API 키 조회·출력·저장 없음: 예.
- 유료 생성 API 호출 없음: 예.
- 검수 없이 설계 정책 변경 없음: 예. 위 2건은 제안만 남기고 미구현.
- 네트워크·push·API·설치·전역 설정 변경 없음: 예.
- 직접 쓰기와 추가 P0 테스트 쓰기는 저장소 안만: 예. out/pt-tests와 수동 샘플은 Git 제외. 기존 66건의 임시 파일 동작은 바꾸지 않고 사용자 허용 단독 unittest 명령으로 실행했다.
- src/plating_qc, config.toml, 기존 미추적 REPORT_1536, REPORT_1935 변경 없음: 예. `git diff 3892adf -- src/plating_qc handoff/REPORT_1935_P0.md config.toml handoff/REPORT_2026-11-07_1536.md` 출력 없음.
- 실제 F 출력·발췌 fixture 커밋 없음: 예. out/ 전체 Git 제외. REPORT에는 요청된 메타데이터·관찰 집계·요약만 기록.
- 기존 미추적 로그 삭제·변경 없음: 예. 해당 파일들은 그대로 미추적 상태다.
