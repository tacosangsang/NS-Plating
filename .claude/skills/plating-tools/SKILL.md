---
name: plating-tools
description: PLATING의 로컬 컷표 추출, 프롬프트 골격·검사, 비용·점검, 레퍼런스·버전·영상 QC가 필요할 때 사용한다.
---

# plating-tools

저장소 `C:\Users\uicus\Dev\plating-qc-workflows`의 실제 CLI를 사용한다.
생성·edit·업스케일 API를 실행하는 도구가 아니다. 판단과 생성 승인은 사람이 한다.
근거: 저장소 `tools/plating/README.md`, `src/plating_tools/cli.py`, `profile_plating.py`.
절차별 선택은 NS-Plating `01 docs/automation/automation_map.md`를 참고한다.

## 실행·경로

Python 3.12 이상. 설치하지 않는다. 아래 설정은 실행 프로세스에만 적용한다.

```powershell
Set-Location -LiteralPath 'C:\Users\uicus\Dev\plating-qc-workflows'
$env:PYTHONPATH = (Resolve-Path -LiteralPath 'src').Path
python -m plating_tools --help
```

전역 `--config plating.toml`은 그룹 앞에 둔다. 기본값은 작업 폴더의 `plating.toml`이다.
설정의 `[paths] write_root/output_root/workflow_dir/read_only`, `[cuts] input`을 확인한다.
설정 상대 경로는 설정 폴더, CLI 상대 경로는 작업 폴더 기준이다.
입력은 `inputs/` 같은 별도 폴더, 출력은 허용된 새 실행 폴더로 분리한다.
`--out`에 기존 폴더를 주면 종료 3이다. 생략하면 설정 출력 루트에 새 폴더를 만든다.
이하 경로·씬·클립은 형식 예다. 반환된 실제 출력 경로를 다음 단계 입력으로 쓴다.

## 명령 선택

| 작업 | 명령 |
| --- | --- |
| 컷표 구조·색 집계 | `python -m plating_tools cuts inventory --input inputs/cuts.md` |
| 씬·문맥 추출 | `python -m plating_tools cuts extract --input inputs/cuts.md --scene 'S#04'` |
| 영상 골격 | `python -m plating_tools prompt skeleton --cuts-json inputs/cuts.json --kind video --plan inputs/plan.toml --clip A` |
| 완성 전문 검사 | `python -m plating_tools prompt check --prompt inputs/prompt.txt --kind video --plan inputs/plan.toml --clip A` |
| 이미지 전문 검사 | `python -m plating_tools prompt check --prompt inputs/image.txt --kind image` |
| 문서 기준 비용 | `python -m plating_tools gate cost --plan inputs/plan.toml --clip A` |
| 8항목·승인 증거 대조 | `python -m plating_tools gate check --gate inputs/gate.toml --prompt inputs/prompt.txt --plan inputs/plan.toml --clip A --cuts-json inputs/cuts.json --check-json inputs/check.json --refs-json inputs/refs.json --require-approval` |
| 레퍼런스·보기용 목록 | `python -m plating_tools refs check --list inputs/refs.toml --thumbs --prompt inputs/prompt.txt` |
| 기존 파일명·README 버전 | `python -m plating_tools versions check --spec inputs/versions.toml --pins inputs/pins.toml` |
| 영상 메타 확인 | `python -m plating_tools qc probe inputs/raw.mp4 inputs/result.mov --json` |
| 프레임 정렬·누락 비교 | `python -m plating_tools qc compare inputs/raw.mp4 inputs/result.mp4 --json` |
| 검수 타일 | `python -m plating_tools qc tiles inputs/raw.mp4 --fps 1 --width 320 --grid 5x2` |
| 용량 분할 | `python -m plating_tools qc split inputs/master.mov --max-part-mb 400 --verify` |
| 변환 계획만 확인 | `python -m plating_tools qc convert inputs/raw.mp4 --profile hq --dry-run --json` |

컷 선택은 `--cuts 'S#04-C001,S#04-C002'`, 모호한 원문 선택은 `--section-line`·`--table-line`이다.
골격은 영상만 지원한다. 영어 액팅·길이 배분을 만들지 않는다. 이미지 skeleton은 실행하지 않는다.
이미지는 문서의 3000자 기준을 검사한다. 영상 글자 상한은 미확인이며 무제한으로 단정하지 않는다.
SCENE_D는 문서 충돌 때문에 미결이다. 블록을 임의로 고쳐 통과시키지 않는다.

## 입력 파일

`plan.toml`: `[[clip]]` 중 하나를 `--clip`으로 고른다. 빈 값은 미결, 인물 분류·길이는 사람이 적는다.

```toml
[[clip]]
id = "A"
kind = "video" # video 또는 image
cuts = ["S#04-C001"]
segment = ""
gen_seconds = ""
mode = "new" # new / edit / code
model = "Seedance 2.5"
resolution = "480p"
edit_input_seconds = ""
people = "" # 있음 / 없음
scene_module = "" # SCENE_LOW, SCENE_A~G, LAYOUT_TRUCK 등 실제 블록 키
props = []
[clip.staging]
seated = "" # bool 또는 미결 빈 문자열
procession = ""
[[clip.character]]
name = ""
group = "" # 하층민·아이·요리사·도둑·공물·진우·흰토끼·상류층 등 명시
face = "" # close / far / none
basis = ""
[[clip.reference]]
index = 1
role = ""
local_path = ''
url = ''
file_id = ''
sheet = "시트 없음/만들어야 함"
preview = "미검수"
candidates = []
candidates_complete = false
candidates_basis = ""
```

`gen_seconds`는 새 생성 길이, `edit_input_seconds`는 실제 edit 입력 길이다. 섞지 않는다.
ts 확인(2026-11-08): 새 생성(Seedance) 최소 4초. AICRON edit은 4초 미만 입력도 동작하지만, 뒤쪽 여유분은 마지막 프레임에서 멈춘 채로 나온다.
새 생성은 정수 초·최대 30초 규칙을 따른다. edit 비용은 입력 초 올림이다. 현재 요금·잔액은 별도 확인한다.
Topaz 출력 크기는 비디오(Higgsfield) 원본/1k/2k/4k, 이미지(AICRON) x2다. 과금 단위와 구분한다.

`gate.toml`: `[[item]]`을 `no=1`~`8`로 각각 둔다. `answer`는 예/아니오/해당 없음 또는 미입력이다.
예는 `evidence` 문자열 배열과 `reviewer`, 아니오는 `reason`·`alternative`, 해당 없음은 `reason`이 필요하다.
골격이 만든 gate.toml 양식을 사용한다. 사람 응답·승인 인용을 자동으로 채우지 않는다.
`[approval]`의 문자열 필드는 `quote`, `where`, `by`, `at`, `prompt_sha256`이다. 실제 승인 전문에 결속한다.
`refs.toml`: plan의 `[[clip.reference]]`와 같은 필드를 최상위 `[[reference]]`로 반복한다.
refs의 로컬·후보 상대 경로는 refs.toml 폴더 기준이다. plan의 경로 문자열도 혼동 없게 절대 경로를 권장한다.
번호는 1부터 연속이다. 육안 확인 후에만 `preview="검수 완료"`, `preview_by`, `preview_at`을 기록한다.
최대 원본 확정은 후보 전수·근거·최대 픽셀 조건이 모두 필요하다. 파일 크기만으로 동일성을 확정하지 않는다.
`versions.toml`: 비어 있지 않은 `[[family]]`(name, root, blend_glob, script_glob, readme_glob)와 `[[render]]`(family, path)를 둔다.
render는 선택 문자열 `scene`, `version_from="접두사"` 또는 `"README"`를 받는다. 실제 렌더 파일이 있어야 한다.
family의 선택값은 `readme_version_pattern`(첫 캡처 또는 version 캡처), `exclude_dirs`, `explicit_order`다.
`pins.toml`: 선택 `[[pin]]`의 family/version/scope 배열/basis_doc/basis_line 정수/basis_contains/approved_by를 적는다.
현 도구는 승인자 `ts`와 문서 근거 행을 요구한다. 실제 승인 문장이 없으면 pin 파일을 만들지 않는다.
이 pins 형식은 blockout 초안 manifest의 `[pins]`와 다르다. manifest current·불변 해시 검사 명령은 아직 없다.

## 안전·종료 코드

네트워크 기본 차단. `--allow-network`는 별도 허용이 있을 때만 쓰며 이번 인계 작업에서는 금지다.
URL을 검사하지 않은 refs 종료 1은 예상된다. 성공시키려고 네트워크를 켜거나 후보 전수를 허위 선언하지 않는다.
입력·raw·읽기 전용 루트·외부 저장소를 수정하지 않는다. 입력 부모로 출력하지 않고 덮어쓰기·강제 옵션을 쓰지 않는다.
원본·생성 전문·출처 지문을 보존한다. 썸네일은 보기용이며 생성 입력으로 쓰지 않는다.
승인은 사람의 명시 문장으로 확인한다. 게이트 종료 0도 생성 승인이 아니다.
승인 판정(ts 확정 2026-11-08, plating-qc-workflows #3에서 수정): 인용문이 W02 §2 어휘("생성해", "돌려", "씬 하나 다 만들어 둬")로 끝나고 부정어(안, 말고, 하지 마)가 없어야 승인이다. "돌려줘"는 미승인이다.
생성 승인을 물을 때는 매번 정확한 문장을 함께 알려 준다. 예: "'S#02 A 클립 돌려'라고 말하면 생성할게요." 게이트 결과의 `how_to_approve`가 같은 안내를 준다.
`--thumbs`는 `[tools] ffmpeg_path` 또는 PATH의 FFmpeg가 필요하다. 없으면 종료 4를 보고하며 설치하지 않는다.
QC는 `[qc] python/config/timeout_s`를 읽고 `python -m plating_qc`로 위임한다. PYTHONPATH는 절대 경로여야 한다.
QC 래퍼의 `--out`은 새 실행 폴더다. 하위 QC의 --out/--log/--config를 직접 주입하지 않는다.
convert는 `--dry-run` 필수다. split은 용량 분할이며 정확한 숏 자르기가 아니다. compare 결과의 불확실성을 유지한다.

| 종료 | 의미·대응 |
| --- | --- |
| 0 | 검사 성공. 결과를 검토한다. 사람 판단·생성 승인을 대체하지 않는다. |
| 1 | 경고·미결·검증 실패. 생성물을 보존하고 소견을 보고한다. |
| 2 | 입력·설정·선택·경로 불량 또는 미지원 요청. 원인을 바로잡는다. |
| 3 | 기존 출력과 충돌. 기존 결과는 두고 허용된 새 경로를 사용한다. |
| 4 | 실행 파일·기능 모듈 없음/미지원. 필요한 경로·환경 해결안을 보고한다. |
| 5 | I/O·디코딩·저장 실패 또는 QC 시간 초과. 오류와 실패 기록을 보고한다. |

실행 폴더를 만든 뒤 실패하면 `_failed/` 기록을 확인한다. 설정 누락 때문에 반복할 상황이면 중단하고 해결안을 제시한다.
