# PLATING QC

로컬 영상의 디코딩 프레임 수와 형식을 확인하고 ProRes 422 HQ로 변환합니다. 현재 `probe`와 `convert`만 구현했습니다. 네트워크나 API 키는 사용하지 않습니다. Python 3.12 이상과 FFmpeg·ffprobe가 필요합니다.

## 실행

저장소 폴더에서 패키지 설치 없이:

```bash
PYTHONPATH=src python -m plating_qc probe "경로/영상.mp4" --json
PYTHONPATH=src python -m plating_qc convert "경로/씬/raw/영상.mp4" --dry-run
PYTHONPATH=src python -m plating_qc convert "경로/씬/raw/영상.mp4"
```

Windows PowerShell에서는 먼저 `$env:PYTHONPATH = "src"`를 실행하고 같은 `python -m plating_qc ...` 명령을 사용합니다. `--scene`으로 씬 폴더를 지정할 수 있습니다. 설정 예시는 `plating-qc.toml.example`이며 `plating-qc.toml`로 복사해 프로그램 경로를 지정합니다. `--config`는 하위 명령 앞에 둡니다. 출력은 `씬/prores/원본명_prores422hq.mov`이며 기존 출력은 덮어쓰지 않습니다. `--suffix _2`로 다른 이름을 지정할 수 있습니다.

성공은 0, 경고 또는 검증 실패 1, 잘못된 입력 2, 출력 충돌 3, 실행 파일 없음 4, 디코딩 또는 저장 실패 5입니다. 출력은 JSON입니다. 임시 파일과 최종 파일을 같은 폴더에 두며, 원자적인 하드링크 생성이 불가능한 파일 시스템에서는 안전하게 실패합니다. Windows 및 동기화 드라이브에서는 아직 검증하지 않았습니다.

변환 결과는 디코딩 프레임 수·크기·평균 fps·ProRes HQ·픽셀 형식·BT.709 태그 및 오디오 길이를 확인합니다. 다른 색 태그가 명시된 입력은 변환하지 않습니다. 가변 속도 탐지는 제한적이며, 실제 재생 타이밍과 색의 시각적 일치는 별도 확인해야 합니다. `compare`, `tiles`, `split`, Blender 폴백은 아직 없습니다.

## 테스트

```bash
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s tests -v
```

FFmpeg로 임시 합성 영상을 만들고 시험 후 삭제합니다. 원본 프로젝트 파일이나 유료 API를 사용하지 않습니다.
