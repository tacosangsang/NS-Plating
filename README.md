# PLATING QC

로컬 영상의 디코딩 프레임 수와 형식을 확인하고 ProRes 422 HQ로 변환합니다. 현재 `probe`, `convert`, `compare`, `tiles`, `split`을 구현했습니다. 네트워크나 API 키는 사용하지 않습니다. Python 3.12 이상과 FFmpeg·ffprobe가 필요합니다.

## 실행

저장소 폴더에서 패키지 설치 없이:

```bash
PYTHONPATH=src python -m plating_qc probe "경로/영상.mp4" --json
PYTHONPATH=src python -m plating_qc convert "경로/씬/raw/영상.mp4" --dry-run
PYTHONPATH=src python -m plating_qc convert "경로/씬/raw/영상.mp4"
```

Windows PowerShell에서는 먼저 `$env:PYTHONPATH = "src"`를 실행하고 같은 `python -m plating_qc ...` 명령을 사용합니다. `--scene`으로 씬 폴더를 지정할 수 있습니다. 설정 예시는 `plating-qc.toml.example`이며 `plating-qc.toml`로 복사해 프로그램 경로를 지정합니다. `--config`는 하위 명령 앞에 둡니다. 출력은 `씬/prores/원본명_prores422hq.mov`이며 기존 출력은 덮어쓰지 않습니다. `--suffix _2`로 다른 이름을 지정할 수 있습니다.

성공은 0, 경고 또는 검증 실패 1, 잘못된 입력 2, 출력 충돌 3, 실행 파일 없음 4, 디코딩 또는 저장 실패 5입니다. 출력은 JSON입니다. 임시 파일과 최종 파일을 같은 폴더에 두며, 원자적인 하드링크 생성이 불가능한 파일 시스템에서는 안전하게 실패합니다. Windows 및 동기화 드라이브에서는 아직 검증하지 않았습니다.

변환 결과는 디코딩 프레임 수·크기·평균 fps·ProRes HQ·픽셀 형식·BT.709 태그 및 오디오 길이를 확인합니다. 다른 색 태그가 명시된 입력은 변환하지 않습니다. 가변 속도 탐지는 제한적이며, 실제 재생 타이밍과 색의 시각적 일치는 별도 확인해야 합니다. `compare`는 64×36 회색 프레임의 차이로 정렬 후보를 찾습니다. 반복 장면이나 프레임 속도 차이 등으로 불확실한 경우 누락 수치를 표시하지 않습니다. 제시된 오프셋과 차이 구간은 검수 힌트이며 확정 판정이 아닙니다. 긴 영상은 메모리 보호를 위해 비교를 거부할 수 있습니다. `tiles`는 새 출력 폴더가 필요하며 `raw/` 아래에 쓰지 않습니다. 타일에 프레임 번호·시간 표시는 아직 없고, 컷 이미지 파일명에 0부터 시작하는 원본 프레임 범위를 적습니다. 장면 전환 후보 자동 감지, 비교 보고서 파일·원본 크기 비교 이미지, Blender 폴백은 아직 없습니다.

```bash
PYTHONPATH=src python -m plating_qc compare "씬/raw/원본.mp4" "업스케일.mp4" --json
PYTHONPATH=src python -m plating_qc tiles "씬/raw/원본.mp4" --out "씬/검수_새폴더" --cuts 48,120 --around 3
PYTHONPATH=src python -m plating_qc split "씬/prores/영상.mov" --out "씬/분할_새폴더" --max-part-mb 400
```

`--search`는 ±프레임 탐색 범위이며 기본 30, `--threshold`는 차이 임계값이며 기본 0.02입니다. 결과가 불확실하거나 차이를 발견하면 종료 코드 1을 반환합니다.

## 테스트

```bash
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s tests -v
```

FFmpeg로 임시 합성 영상을 만들고 시험 후 삭제합니다. 원본 프로젝트 파일이나 유료 API를 사용하지 않습니다.

`split`은 ProRes 영상만 재인코딩 없이 나눕니다. 각 파일의 크기와 전체 영상 프레임의 디코딩 해시를 검사해 모두 통과할 때만 새 출력 폴더에 저장합니다. 크기 추정이 맞지 않아 한도 초과가 나면 결과를 남기지 않으며 더 작은 `--max-part-mb`로 재시도해야 합니다. 오디오가 있으면 패킷 경계 때문에 조각별 오디오 시작 시각과 길이가 영상 경계와 다를 수 있어 무음 없는 이음새를 보장하지 않습니다. JSON과 `manifest.json`에 첫 오디오 스트림의 시작·길이를 기록하고 경고와 종료 코드 1을 반환합니다. 출력은 정상 저장된 상태입니다. 원본 오디오를 편집에서 연속 트랙으로 사용하는 방안을 검토하고 재생을 별도로 확인하세요. 가변 프레임 속도 의심 영상은 거부합니다.
