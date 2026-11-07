# 합성 영상으로 다섯 명령 재현

이 예제는 새 시스템 임시 폴더에서 2초짜리 합성 영상만 만들고 `probe`, `convert`, `compare`, `tiles`, `split`을 각각 실행합니다. 명령마다 JSON 실행 로그를 별도로 남깁니다. 실제 프로젝트 영상은 사용하지 않습니다. Python 3.12 이상과 FFmpeg·ffprobe가 필요하며, 타일에는 FFmpeg `drawtext`와 글꼴이 필요합니다. 설치 과정은 없습니다.

저장소 루트에서 실행하세요.

```text
python samples/reproduce.py
```

FFmpeg가 PATH에 없다면 FFmpeg·ffprobe 경로가 들어 있는 기존 설정 파일을 지정합니다. 이 예제는 합성 입력에 기본 `layout.raw = "raw"`를 사용하므로 설정에서 다른 raw 폴더명을 지정했다면 기본값을 쓰는 별도 설정이 필요합니다.

```text
python samples/reproduce.py --config <설정파일경로>
```

출력된 `임시 결과 폴더` 안에서 `probe.json`, `convert.json`, `compare.json`, `tiles.json`, `split.json`과 `comparison`, `tiles`, `parts` 폴더를 확인합니다. `compare`는 파이프라인 예시를 위해 같은 합성 파일을 양쪽에 넣고 탐색 범위를 0으로 제한합니다. 이 예시만으로 다른 영상의 정렬 정확도를 증명하지 않습니다. 확인 후 해당 임시 폴더는 직접 삭제할 수 있습니다.

## 실제 실행 예

### Windows 재실행 (09 구조 수정)

2026-11-07 Windows, Python 3.12.10, `D:\Plating\tools\ffmpeg\bin`을 PATH에 추가해 실행했다. 다섯 명령 모두 종료 0. 원본과 변환본은 각각 48프레임이며, 비교 이미지 1장, 타일 프레임 0·24, 분할 23·22·3프레임, 검증 48프레임이다. 전체 콘솔 로그는 `handoff/logs/win_09_synthetic_reproduce.txt`, 다섯 JSON 로그는 `handoff/logs/synthetic_09/`에 있다. 아래 Linux 예는 이전 실행이다.

Linux, Python 3.12.14, FFmpeg·ffprobe 7.1.5의 합성 테스트 결과입니다. 임시 경로는 `<임시폴더>`로 바꿔 적었습니다. FFmpeg 버전과 인코더에 따라 용량·분할 위치는 달라질 수 있습니다.

```text
임시 결과 폴더: <임시폴더>
probe: 종료 0; 로그 <임시폴더>/probe.json
convert: 종료 0; 로그 <임시폴더>/convert.json
compare: 종료 0; 로그 <임시폴더>/compare.json
tiles: 종료 0; 로그 <임시폴더>/tiles.json
split: 종료 0; 로그 <임시폴더>/split.json
원본 48프레임, 변환 48프레임, 비교 이미지 1장
타일 프레임 [0, 24], 분할 [23, 22, 3]프레임, 검증 48프레임
```

실행 로그는 작업 디렉터리, 명령 인자와 파일 경로, 결과·오류, 종료 코드, 소요 시간, FFmpeg·ffprobe 버전, 도구 소스 해시를 포함합니다. 환경 변수 값은 기록하지 않습니다. 경로에 개인 정보가 있을 수 있으니 로그를 공유하기 전에 내용을 확인하세요. 로그 파일은 기존 파일을 덮어쓰지 않으며 `raw`와 새 결과 폴더 바깥에 지정해야 합니다.
