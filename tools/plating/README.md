# plating-tools P0·P1

공식 진입점은 `python -m plating_tools`다. Python 3.12 이상, 표준 라이브러리만 사용한다. 기존 `plating-qc`는 별도 도구다.

이 작업은 설치를 하지 않았다. 저장소 루트 PowerShell에서 명령을 실행할 프로세스에만 소스 경로를 지정한다.

```powershell
$env:PYTHONPATH = (Resolve-Path 'src').Path
python -m plating_tools --help
```

`plating.toml`의 상대 경로는 설정 파일 폴더 기준이다. CLI의 상대 경로는 작업 폴더 기준이다. 기존 `config.toml`은 사용하지 않는다.

```powershell
python -m plating_tools cuts inventory
python -m plating_tools cuts extract --scene 'S#04'
python -m plating_tools prompt skeleton --cuts-json 'out/<추출 폴더>/cuts.json' --kind video
python -m plating_tools prompt check --prompt 'inputs/prompt.txt' --kind image
python -m plating_tools gate cost --model 'Seedance 2.5' --mode new --resolution 480p --seconds 4
python -m plating_tools gate check --gate 'inputs/gate.toml' --prompt 'inputs/prompt.txt' --require-approval
```

골격·검사·게이트에는 `--plan inputs/plan.toml --clip A`를 추가할 수 있다. 계획 형식은 `design/plating-tools.draft.md` 3.3절을 따른다. 빈 값은 미결이다. 인물 분류·클립 분할·생성 길이·승인 증거는 사람이 적는다. `scene_module`에는 `SCENE_LOW`, `SCENE_A`~`SCENE_G`, `LAYOUT_TRUCK` 등 문서 블록 키를 지정한다. `SCENE_D`는 원문 충돌 때문에 미결로 남는다.

모든 파일 출력은 새 실행 폴더에 저장한다. `--out`으로 기존 폴더를 주면 종료 3이다. 입력 파일의 부모 폴더에도 출력할 수 없으므로 입력은 `inputs/`처럼 출력과 별도 폴더에 둔다. `gate cost`는 `--out`이 없으면 stdout만 출력한다.

- 종료 0: 검사를 통과했다. 생성 승인으로 해석하지 않는다.
- 종료 1: 경고·미결·검증 실패. 결과는 공개한다.
- 종료 2/3/4/5: 입력 불량/출력 충돌/실행 파일·모듈 없음/I/O 실패.
- P1 패키지가 없는 사본에서도 P0는 동작하며, 해당 P1 명령만 종료 4다.

컷표는 씬 안 첫 두 머리 칸 `컷`, `TC`로 선택한다. `header-row`가 없으면 정보 소견만 남긴다. 초 단위 TC는 같은 표의 바로 앞 행에서 해석한 끝 분을 이어받는다. 앞 행 해석 실패·역행·역전에서는 원문과 CT006을 유지한다.

```powershell
python -m plating_tools refs check --list 'inputs/refs.toml'
python -m plating_tools refs check --list 'inputs/refs.toml' --thumbs
python -m plating_tools versions check --spec 'inputs/versions.toml' --pins 'inputs/pins.toml'
python -m plating_tools qc probe 'inputs/SYNTH.mov' --json
python -m plating_tools qc convert 'inputs/SYNTH.mov' --dry-run
```

`refs`의 기본값은 네트워크 차단이다. URL 미확인으로 종료 1을 낸다. 실제 GET에는 `--allow-network`가 필요하며, 이번 구현 검증에서는 사용하지 않았다. `--thumbs`는 `[tools] ffmpeg_path`의 FFmpeg를 직접 argv로 호출한다. 값은 실행 파일 또는 폴더이며, 비우면 PATH에서 찾는다. FFmpeg가 없으면 종료 4, 결과 폴더 없음이다. 썸네일은 보기용이며 생성 입력으로 쓰지 않는다. 시트 상태·미검수 표시는 자동으로 승인되지 않는다.

`versions`의 계열·렌더 경로는 spec에서만 읽는다. 실제 블록아웃 경로는 I14 답 전까지 설정하지 않는다. README 본문 판은 `readme_version_pattern`의 첫 캡처 또는 `version` 이름 캡처로 지정한다. 숫자 판은 정수로 비교하고, 접미사 판은 명시한 `explicit_order` 없이는 순서를 정하지 않는다. pin은 승인자 `ts`, 문서·행·문자열 근거·씬 범위가 필요하다. I15의 실제 적용 범위는 미확인이며, 파일에 적은 범위만 적용한다. 형상 동일성, 실제 치수는 미검증이다.

`qc`는 `[qc] python`(빈 값은 현재 Python), `config`(선택), `timeout_s`(기본 1800)를 읽는다. `python -m plating_qc`만 실행하며 입력 경로는 절대 경로로 전달한다. 작업 폴더는 새 실행 폴더의 `qc/1/`이고 로그·stdout/stderr 원바이트·생성물 해시를 보존한다. QC의 Python에서 기존 `plating_qc`를 찾을 수 있어야 한다. 부모 환경에서 설정한 PYTHONPATH는 절대 경로여야 하며, 위임 시 환경은 로그 위치와 출력 인코딩만 바꾼다.

QC 하위 인자의 `--out`, `--log`, `--config`는 거부한다. CLI의 `--out`은 툴킷 실행 폴더만 지정하며, 하위 QC 출력은 도구가 `qc/1/out`으로 통제한다. `convert`는 `--dry-run` 필수다. 종료 1도 생성물과 함께 공개하고, 종료 2~5·시간 초과는 `_failed/`에 격리한다. `qc.json`의 생성물·로그·stdout/stderr 경로는 실행 폴더 기준이며, argv·cwd·환경에는 실행 당시 staging 경로를 그대로 기록한다.

전체 테스트는 다음 **단독 명령**을 쓴다. PATH 설정·세미콜론·파이프·리다이렉트를 붙이지 않는다. 결과 로그는 실행 후 별도 단계에서 저장한다.

```powershell
python -m unittest discover -s tests -v
```

테스트의 합성 파일과 기본 tempfile 경로는 저장소 `out/pt-tests/` 안으로 한정한다. 기존 QC 테스트는 자신이 만든 tempfile만 정리한다. P0·P1 산출물은 보존한다. 실제 F와 W는 읽기 전용으로 참조하며, 없거나 F 지문이 다르면 해당 실제 참조 테스트를 skip한다. `out/`은 Git 제외다.

## blockout: manifest를 정본으로 관리

다음 프로젝트용 규약 도구다. 기존 추론형 `versions check`와 독립적이며 실제 PLATING 폴더에는 적용하지 않았다. 새 블록아웃은 **Blender에서 현재 장면을 저장해 만든다**. build.py는 필수가 아니다.

`--root`는 자산들의 부모 폴더다. 아래는 저장소 안 예시이며, 실제 프로젝트에서는 설정 `[paths] write_root`와 `read_only`를 먼저 맞춘다. 쓰기 제한은 기존 도구와 같다. `--config`는 `blockout` 앞에 지정한다.

```powershell
python -m plating_tools blockout init tower_hall --root 'out/blockout-demo'
```

초기 구조는 `<root>/tower_hall/{manifest.toml,versions/,renders/,archive/}`다. 이미 있는 자산에는 종료 2를 반환한다. manifest의 current는 첫 생성 때 비어 있으며, 새 버전을 만들 때 `--set-current`를 명시해야 바뀐다.

Blender Python Console에서 저장 스크립트의 `main`을 호출한다. `--python`은 Blender 실행 파일이 아닌 외부 Python 3.12 이상 실행 파일이다. 아래 경로와 자산 이름·변경 내용을 자신의 작업에 맞춘다.

```python
import runpy
save_next = runpy.run_path(r"C:\Users\uicus\Dev\pqw-bo\tools\blender\save_next_version.py")["main"]
save_next([
    "tower_hall",
    "--root", r"C:\Users\uicus\Dev\pqw-bo\out\blockout-demo",
    "--change", "링 보 재질 변경",
    "--by", "ts",
    "--python", r"C:\Users\uicus\AppData\Local\Programs\Python\Python312\python.exe",
    "--set-current",
])
```

이 스크립트는 `copy=True`로 저장소 `out/blockout-save/<uuid>/<asset>.blend`에 임시 저장한 뒤 CLI를 argv·`shell=False`로 호출한다. 상대 경로를 임시 폴더 기준으로 바꾸지 않도록 `relative_remap=False`를 사용한다. 기본 설정은 이 저장소 `plating.toml`이며 `--config`로 바꿀 수 있다. 성공하면 자신의 임시 파일·빈 폴더만 정리하고 실패하면 사본을 보존한다. 자식 프로세스에만 소스 경로를 전달하므로 패키지 재설치는 필요 없다. **Blender 실제 저장 실행은 미검증이다.**

이미 저장해 둔 파일을 등록할 때는 CLI를 직접 쓴다. `--from` 뒤에 여러 파일을 주거나 옵션을 반복할 수 있다.

```powershell
python -m plating_tools blockout new-version tower_hall --root 'out/blockout-demo' --from 'inputs/tower_hall.blend' --change '링 보 재질 변경' --by ts --set-current
python -m plating_tools blockout check --root 'out/blockout-demo'
python -m plating_tools blockout check --root 'out/blockout-demo' --renders 'inputs/sheets'
python -m plating_tools blockout pin tower_hall --root 'out/blockout-demo' --scene 'S#10' --version v001 --reason '사용자 승인 문장을 그대로 인용' --by ts --date '2026-11-08'
```

버전은 숫자 최댓값 다음의 `v001`~`v999`이며 접미사를 허용하지 않는다. 파일을 staging에 복사하고 NOTES.md 틀과 모든 파일의 SHA-256을 만든 뒤 새 버전 폴더로 공개한다. `--set-current`가 없으면 current를 유지한다. 같은 파일명·NOTES.md 입력 충돌과 기존 버전 덮어쓰기는 거부한다. NOTES.md도 해시에 포함되므로 공개 후 수정하지 않는다. 변경은 새 버전에 담는다.

검사는 `versions/`와 `archive/`의 파일 목록·SHA-256을 manifest와 비교한다. 렌더·시트 이름은 `<asset>_vNNN_<view>[_<variant>].png`이고 날짜를 넣지 않는다. 낮·밤 등의 변형은 .blend 안 Scene·컬렉션 또는 manifest variants로 표현한다. 렌더는 `renders/vNNN/<view>/` 아래에 둔다.

| 판정 | 의미 | 종료 |
| --- | --- | --- |
| STALE | current보다 옛 렌더, 또는 해당 씬 pin과 다른 렌더 | 1 |
| PINNED | 승인 기록이 있는 씬과 pin 버전 일치 | 0, 다른 위반이 없을 때 |
| CONVENTION | 미등록 버전·접미사·날짜·중복 정본·렌더 이름/폴더 불일치 | 1 |
| IMMUTABLE | 버전 폴더·파일 누락, 파일 추가, SHA-256 변경 | 1 |

pin의 씬은 파일명 또는 렌더 루트부터의 경로에 명시한 정확한 `S#NN` 토큰으로 식별한다. 예: `renders/v001/S#10/tower_hall_v001_front.png`, `tower_hall_v001_S#10_front.png`. 씬을 명시하지 않은 렌더는 current와 비교하며 씬을 추정하지 않는다. `--renders`는 기본 자산별 renders 대신 지정한 폴더를 검사한다. current보다 새롭지만 아직 선택하지 않은 렌더도 규약 위반이다.

결과 `blockout.json`, `blockout.md`, `run.json`은 설정 `output_root`의 새 실행 폴더에 저장하고 stdout에 경로를 반환한다. 검사는 입력 파일·mtime을 바꾸지 않는다. pin은 비어 있지 않은 승인 인용문·승인자·유효 날짜와 manifest에 있는 버전이 필요하며 current를 바꾸지 않는다. 승인 여부 자체는 사람이 기록한다.

입력 불량 2·출력/자산 잠금 충돌 3·모듈 없음 4·I/O 실패 5의 기존 의미를 유지한다. 복사 실패의 staging, manifest 저장 실패 뒤 미등록 버전은 진단용으로 보존하며 자동 삭제·덮어쓰기로 복구하지 않는다. 자산의 `.blockout.lock`이 남으면 다른 쓰기 작업이 끝났는지 확인한 뒤 처리한다. archive 이동·렌더 정리·Drive 동기화는 이 명령들이 수행하지 않는다.
