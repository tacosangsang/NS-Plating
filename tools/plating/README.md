# plating-tools P0

공식 진입점은 `python -m plating_tools`다. Python 3.12 이상, 표준 라이브러리만 사용한다. 기존 `plating-qc`는 별도 도구다.

이 작업은 설치를 하지 않았다. 저장소 루트 PowerShell에서 명령을 실행할 프로세스에만 소스 경로를 지정한다.

```powershell
$env:PYTHONPATH = 'src'
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
- 종료 2/3/4/5: 입력 불량/출력 충돌/P1 모듈 없음/I/O 실패.
- `refs`, `versions`, `qc`는 P1이며 이번 구현에는 없다. 호출하면 종료 4다.

실제 F의 S#02 표는 `header-row="true"`가 없어 자동 추출에서 제외한다. S#04의 초 단위 TC(`02.0–03.5`)도 현재 지원 형식 밖이다. 두 항목은 REPORT의 설계 변경 제안에 남겼다. 원문은 고치지 않는다.

전체 테스트는 다음 **단독 명령**을 쓴다. PATH 설정·세미콜론·파이프·리다이렉트를 붙이지 않는다. 결과 로그는 실행 후 별도 단계에서 저장한다.

```powershell
python -m unittest discover -s tests -v
```

P0 테스트의 쓰기는 저장소 `out/pt-tests/` 안으로 한정한다. 정리는 수행하지 않는다. 실제 F와 W는 읽기 전용으로 참조하며, 없거나 F 지문이 다르면 해당 실제 참조 테스트를 skip한다. `out/`은 Git 제외다.
