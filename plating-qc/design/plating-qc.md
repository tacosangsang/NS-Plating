# 설계 답변: PLATING 검수·변환 오프라인 CLI (2026-11-07)

요청서 `claude_plating_design_request.md` 1판·2판(Codex dot 작성, 2판은 저장소·Notion 접근만 갱신)에 대한 답. 작성: 클로드 프로젝트(검수 역할). 이 답은 Claude API 크레딧을 쓰지 않고 썼다. 다음 설계 요청부터는 브리핑 3장의 `tools/claude_design.py` 경로로 보내 크레딧을 쓴다.

근거로 읽은 것: NS-Plating `workflow/06`(업스케일·ProRes 규약, 11-06 실측), `workflow/05` 8절, `workflow/08` 환경 표, PC `D:\Plating\prores\*.py` 5개(Blender 내장 FFmpeg로 만든 기존 도구), 핸드북 md 11-07판.

## 0. 요청서의 전제 중 바로잡을 것

| 요청서 | 사실 | 설계에 미치는 영향 |
| --- | --- | --- |
| Linux 환경에 ffmpeg 7.1.5가 있으니 그걸로 설계 | 11/11 제출 작업은 사용자 PC(Windows)에서 한다. **PC PATH에 ffmpeg가 없다**(workflow/06 5절). 기존 도구 5개는 전부 `blender -b -P`로 Blender 내장 FFmpeg를 돌린다. Blender 경로는 출력이 더 크고(963MB vs 661MB) 색 태그·apad를 제어할 수 없다 | 백엔드를 인터페이스로 분리하되, **PC에 ffmpeg 정적 빌드를 두는 것을 사용자에게 요청**한다. 이게 거부되면 compare·tiles는 PC에서 못 돌고 convert만 Blender 폴백으로 된다 |
| Notion 404(1판) | 2판에서 학교 계정으로 읽힘. 어차피 이 도구 범위의 규칙은 전부 저장소 `workflow/06`에 있다 | Notion 의존 없음 |
| 새 저장소 생성 권한 미확인(1판) | 2판에서 해결: `tacosangsang/plating-qc-workflows` 비공개 생성됨 | 그 저장소에서 개발 |
| 프레임 수 비교 + 원본 크기로 줄여 같은 프레임끼리 | 맞다. 다만 실측 사례(끝 11프레임 잘림, 컷 최대 4프레임 앞당김)는 "같은 번호끼리"만 비교하면 못 잡는다 | 오프셋 탐색(±N 프레임)으로 머리·꼬리 누락을 찾고, 그 뒤 정렬된 쌍끼리 차이를 본다 |
| "큰 출력 분할"은 경험적 한도 | 맞다. 400MB는 공유 폴더 첨부 제한이지 포맷 제한이 아니다 | `split`은 선택 명령, 한도는 설정값 `max_part_mb`(기본 400) |

## 1. 범위와 비범위

- 범위: `probe`, `compare`, `tiles`, `convert`, `split`(선택). 모두 로컬 파일만. 네트워크·유료 API 없음.
- 비범위(경계만 둔다): 컷표 파서, 프롬프트 골격, 점검 게이트, 레퍼런스 URL 검사, 블록아웃 버전 검사, 기존 `join/xfade/match_frames` 이식. 4장 "확장 경계" 참고.
- 핸드북 수치·블록을 코드에 복사하지 않는다. 이 도구가 고정하는 값은 포맷 사실(ProRes 프로파일 3 = HQ, bt709)뿐이고, 경로 규약(`raw/`, `prores/`, 접미사)과 한도는 `plating-qc.toml`에서 읽는다.

## 2. CLI 계약

```
plating-qc probe   <file>...                       [--json]
plating-qc compare <original> <candidate>          [--search 30] [--size 64x36] [--threshold 0.02] [--json] [--out DIR]
plating-qc tiles   <file>                          [--fps 1] [--width 320] [--grid 5x2] [--cuts 48,120] [--around 3] [--out DIR]
plating-qc convert <input>                         [--scene DIR] [--profile hq] [--dry-run] [--json]
plating-qc split   <prores.mov>                    [--max-part-mb 400] [--verify] [--out DIR]
```

공통: `--config plating-qc.toml`(기본: 현재 폴더 → 상위 탐색), `--log FILE`(기본 `<out>/plating-qc.log`), `--backend ffmpeg|blender`(기본 자동: ffmpeg 있으면 ffmpeg).

### 종료 코드 (모든 명령 공통)
| 코드 | 뜻 |
| --- | --- |
| 0 | 완료, 지적 없음 |
| 1 | 완료, **검수 지적 있음**(프레임 수 불일치, 누락 의심, 태그 불일치). 보고서에 상세 |
| 2 | 사용법·입력 오류(파일 없음, 인자 오류) |
| 3 | 출력 충돌(같은 이름 존재). 절대 덮어쓰지 않는다 |
| 4 | 백엔드 없음(ffmpeg/ffprobe/blender 못 찾음) |
| 5 | 디코딩 실패(손상 파일, 스트림 없음) |

### 입력·출력 계약

**probe**: 입력 1개 이상. 출력 `MediaInfo` JSON(아래). 프레임 수는 `nb_read_frames`(실제 디코딩 카운트, `-count_frames`)를 정본으로 하고 `nb_frames`(컨테이너 메타)·`nb_read_packets`를 함께 적어 셋이 다르면 `warnings`에 기록.

```json
{"path":"...","video":{"codec":"hevc","width":2048,"height":1152,"pix_fmt":"yuv420p10le",
 "r_frame_rate":"24/1","avg_frame_rate":"24/1","nb_frames_meta":356,"nb_frames_decoded":356,
 "duration_s":14.833,"vfr_suspect":false,"color":{"primaries":"unknown","transfer":"unknown","space":"unknown"},
 "profile":null},
 "audio":{"codec":"aac","sample_rate":48000,"channels":2,"duration_s":14.80} ,
 "warnings":[]}
```

**compare**: 입력 = 원본(480p raw), 후보(업스케일·변환·분할 결과). 출력 = `compare_<후보이름>.json` + 같은 내용 텍스트 표 + 선택 `--out`에 차이 큰 쌍의 나란히 PNG.
- 판정 항목: 해상도 비율(후보/원본 정수배인지), fps 동일, 프레임 수 차이, **정렬 오프셋**(후보가 원본의 몇 프레임째부터 시작하나), 머리 누락 n, 꼬리 누락 n, 정렬 후 프레임별 차이 중 임계 초과 구간 목록.
- 원본이 없으면 명령 자체가 2로 끝난다. "누락"은 원본 대비로만 말한다(workflow/06 4절 2).
- 프레임 수가 같아도 내용 차이는 따로 본다(요청 1). 둘 다 보고서에 분리 표기.

**tiles**: 입력 1개. 출력 `tiles_<이름>_<NN>.png`(1초 간격, 10장/장, 긴 영상은 여러 장), `cut_<프레임>.png`(지정 컷 ±around 프레임을 원본 해상도로 가로 이어 붙임), `scene_candidates.txt`(ffmpeg `select=gt(scene,T)` 결과, **힌트일 뿐** 판정은 사람). 프레임 번호와 타임코드를 각 칸에 drawtext로 찍는다(글꼴 없으면 파일명에만).

**convert**: 입력 1개(HEVC mp4 등). 출력 `<scene>/prores/<원래이름>_prores422hq.mov`.
- `<scene>`은 `--scene` 또는 입력 경로에서 `raw/`의 부모를 찾아 정한다. 못 찾으면 2.
- 출력이 있으면 3. 사용자가 다른 판을 원하면 `--suffix _2`로 명시한다. `--force` 없음.
- 같은 폴더에 `.<이름>.partial.mov`로 쓰고 끝나면 이름 바꿈. 실패하면 partial 삭제.
- 변환 뒤 자동 `probe`로 검증: profile == "HQ"(prores profile 3), pix_fmt `yuv422p10le`, color 세 태그 bt709, 프레임 수·해상도·fps가 입력과 같음, 오디오가 있으면 길이 ≥ 영상 길이. 하나라도 틀리면 1.
- `--dry-run`은 실행할 ffmpeg 명령과 출력 경로만 찍는다.

**split**: ProRes 인트라라 `-c copy`로 자른다. part1 `-t`, part2는 출력쪽 `-ss`. `--verify`면 경계 두 프레임의 framemd5를 원본 같은 프레임과 대조. 한도는 설정값.

## 3. 파일 트리와 데이터 흐름

```
plating-qc/
  pyproject.toml            # python>=3.12, 의존성 없음(stdlib만). 콘솔 스크립트 plating-qc
  plating-qc.toml.example   # layout.raw="raw", layout.prores="prores", suffix="_prores422hq", max_part_mb=400, compare.search=30
  src/plating_qc/
    __main__.py / cli.py    # argparse, 서브커맨드 등록, 종료 코드 매핑
    config.py               # toml 읽기(tomllib), 기본값, 상위 폴더 탐색
    model.py                # dataclass: MediaInfo, CompareReport, ConvertReport, Finding(level, code, message)
    backend/base.py         # MediaBackend(ABC): probe(path)->MediaInfo, decode_gray(path, size, start, count)->Iterator[bytes],
                            #   extract_frames(path, frames, out)->list[Path], encode_prores(spec)->Path, cut_copy(...)->Path, framemd5(path, frames)
    backend/ffmpeg.py       # FfmpegBackend: ffprobe/ffmpeg 서브프로세스. 전 기능
    backend/blender.py      # BlenderBackend: encode_prores만(기존 to_prores.py 이식). 나머지는 NotImplementedError → 종료 4
    probe.py                # MediaInfo 조립, VFR 의심·메타 불일치 warnings
    compare.py              # 오프셋 탐색 + 정렬 + 차이 구간
    tiles.py                # 타일·컷 경계·scene 힌트
    convert.py              # 경로 규약, partial 쓰기, 사후 검증
    split.py
    layout.py               # SceneLayout: raw/prores 해석, 접미사, 충돌 검사
    report.py               # JSON + 텍스트 표, 로그
  tests/
    conftest.py             # 합성 입력 생성(아래 5장), ffmpeg 없으면 skip
    test_probe.py test_compare.py test_tiles.py test_convert.py test_split.py test_layout.py
  samples/README.md         # 샘플 실행 로그(합성 입력으로 재현)
```

흐름: `cli` → `config` → `backend 선택` → 명령 모듈 → `report`(JSON·표·로그) → 종료 코드. 명령 모듈은 `MediaBackend`만 알고 ffmpeg 문자열을 모른다. ffmpeg 인자 조립은 `backend/ffmpeg.py` 한 곳.

왜 stdlib만: PC에서 `pip install` 없이 `python -m plating_qc`로 바로 돌리기 위해. 프레임 비교는 ffmpeg가 `scale=64:36,format=gray -f rawvideo`로 뱉은 바이트를 파이썬으로 평균 절대차 계산. 64×36×프레임 수라 numpy 없이도 15초 클립은 1초 안.

## 4. 검증 방법과 한계

### 프레임 수
- 정본은 디코딩 카운트(`ffprobe -count_frames`, `nb_read_frames`). 메타 `nb_frames`와 다르면 경고만, 판정은 디코딩 값으로.
- 가변 프레임 속도: `r_frame_rate != avg_frame_rate` 또는 패킷 pts 간격의 표준편차가 1/fps의 5%를 넘으면 `vfr_suspect=true`. 이때 "n초 = n×fps 프레임" 식 계산을 쓰지 않고 디코딩 수만 보고한다. 변환은 `-vsync passthrough`(ffmpeg 7: `-fps_mode passthrough`)로 프레임을 보존한다. 1080 생성·Topaz 결과는 실측상 CFR 24였다(workflow/06). 한계: VFR 입력을 ProRes로 passthrough하면 프리미어가 CFR로 해석해 타이밍이 어긋날 수 있다. 경고 후 사용자 판단.
- 타임스탬프 없음: pts 없는 패킷은 `-fflags +genpts`로 생성해 카운트. 보고서에 "genpts 적용" 표기.
- 손상 파일: ffprobe 실패 → 5. 부분 디코딩 가능한 파일은 디코딩 수를 적고 `decode_errors` 경고(ffmpeg stderr의 `error`·`corrupt` 줄 수).

### 정렬과 누락(compare)
- 두 파일을 같은 크기(64×36, 회색)로 디코딩. 후보의 처음 k프레임(k=5)을 원본 [0, search] 구간에서 평균 절대차 최소인 위치로 찾는다 → `head_offset`. 끝도 같은 방법 → `tail_offset`. 머리 누락 = head_offset, 꼬리 누락 = (원본 수 − head_offset) − 후보 수 (음수면 후보가 더 김).
- 정렬 뒤 쌍별 차이가 `threshold`(기본 0.02, 0~1 정규화) 초과인 연속 구간을 목록화. 업스케일은 전체적으로 차이가 작고 컷 자리에서 치솟는 것이 정상. 컷 자리 ±4프레임에서 원본보다 차이가 큰 쌍은 "섞인 프레임 의심"으로 표기(최종 판정은 사람).
- 한계: 같은 내용이 아닌 두 파일(다른 클립)을 넣으면 오프셋이 의미 없다. 전체 평균 차이가 0.15를 넘으면 "같은 소스가 아닐 수 있음"으로 1을 반환하고 누락 수치를 적지 않는다. 밝기만 다른 경우(색 태그 해석 차이)는 각 프레임을 평균 0·분산 1로 정규화한 뒤 비교해 흡수한다.

### 오디오
- 없음: `probe.audio=null`. convert는 `-an` 없이 비디오만 인코딩하고 보고서에 "무음성" 표기.
- 짧음: `-af apad=whole_dur=<영상 길이 초>`로 영상 길이까지 무음 채움. `-shortest`를 쓰지 않는다(끝 프레임을 자른 실측, workflow/06). 변환 뒤 오디오 길이 ≥ 영상 길이 검증.
- 긺: 그대로 둔다(프리미어에서 잘림). 보고서 경고.

### 색 태그
- `-color_primaries bt709 -color_trc bt709 -colorspace bt709`는 태그만 쓰고 화소를 바꾸지 않는다. 입력이 unknown이면 그대로 적용. 입력이 bt2020 등 다른 값이면 변환하지 않고 1 + 경고(사용자가 정한다). ProRes는 `-vendor apl0`, `-profile:v 3`, `-pix_fmt yuv422p10le`. 검증은 ffprobe `profile`(HQ) + 세 태그.

### Blender 폴백의 한계
- 색 태그·apad·passthrough를 제어하지 못한다. 결과 파일이 크다. compare·tiles 불가. 그래서 폴백은 "ffmpeg가 정말 없을 때 convert만".

## 5. 임시 파일·실패·충돌·경로

- 임시: 출력 폴더 안 `.<이름>.partial.<ext>`. 다른 드라이브 `%TEMP%`를 쓰지 않는다(G: 동기화 폴더와 D: 사이 이동이 느리고 실패 시 잔해가 숨는다).
- 실패: partial 삭제, 로그에 ffmpeg stderr 마지막 40줄, 종료 코드 5 또는 4. 절반 쓰인 파일이 `prores/`에 남지 않는다.
- 충돌: 출력 존재 → 3, 아무것도 쓰지 않음. `--suffix`로만 다른 이름. `raw/` 아래에는 어떤 명령도 쓰지 않는다(layout에서 거부).
- 경로: 입력 경로는 `Path.resolve()`로 절대화. Windows 한글 경로·공백·`G:\내 드라이브`는 서브프로세스 인자 리스트로 넘긴다(셸 문자열 조립 금지). 파일명은 원래 이름 유지, 접미사만 추가. 길이 240자 넘으면 2.
- 로그: 명령·인자·백엔드 버전·입력 probe·출력 probe·소요 시간을 `plating-qc.log`에 append. 샘플 로그는 `samples/`에 복사.

## 6. 자동 테스트 (합성 입력, 실키 없음)

conftest에서 ffmpeg `lavfi`로 만든다. ffmpeg 없으면 전부 skip(4와 같은 조건).

| 이름 | 생성 | 쓰는 테스트 | 검증 조건 |
| --- | --- | --- | --- |
| `base_480.mp4` | `testsrc2=854x480:r=24:d=3` + `sine=440:d=3`, h264, 프레임 번호가 화면에 찍힘(testsrc2 기본) | 전부 | probe: 72프레임, 24/1, 오디오 3.0s |
| `base_noaudio.mp4` | 위에서 `-an` | probe, convert | audio null; convert 결과 오디오 없음, 72프레임, 종료 0 |
| `base_shortaudio.mp4` | sine `d=2` | convert | 결과 오디오 길이 ≥ 3.0s, 72프레임 |
| `up_2k_full.mp4` | base_480을 `scale=2048:1152`, hevc, 색 태그 없음 | compare, convert | compare: 오프셋 0, 누락 0, 종료 0. convert: HQ·bt709·72프레임·422p10 |
| `up_2k_tail11.mp4` | 위에서 `-frames:v 61` | compare | 꼬리 누락 11, 종료 1 |
| `up_2k_head2.mp4` | 위에서 `-ss 2/24`(입력쪽, 정확 seek은 `-accurate_seek`) | compare | 머리 누락 2, 종료 1 |
| `other_clip.mp4` | `testsrc=...`(다른 패턴) | compare | "같은 소스 아님" 판정, 누락 수치 없음, 종료 1 |
| `cut_at_36.mp4` | 두 testsrc 패턴을 36프레임 경계로 concat | tiles, compare | tiles: `cut_36.png` 생성, scene 힌트에 36 포함. compare(자기 자신과 섞인 1프레임 삽입판): 섞임 의심 표기 |
| `vfr.mp4` | `setpts='PTS+if(mod(N,7),0,0.02/TB)'` + `-fps_mode vfr` | probe, convert | vfr_suspect true; convert는 passthrough로 프레임 수 보존, 경고 1건 |
| `corrupt.mp4` | base_480 뒤쪽 30% 바이트 잘라 냄 | probe, convert | 종료 5 또는 디코딩 수 < 72 + 경고. 둘 중 하나로 고정해 두고 실측으로 확정 |
| 충돌 | convert를 두 번 | convert | 두 번째 종료 3, 첫 결과 mtime 불변 |
| 분할 | up_2k_full → prores → split `--max-part-mb 1` | split | part 2개 이상, 프레임 합 = 72, `--verify` 경계 md5 일치 |
| layout | `x/raw/a.mp4` → `x/prores/a_prores422hq.mov`; `raw/` 출력 시도 | layout | 경로 해석, raw 쓰기 거부(2) |

재현 로그: `samples/README.md`에 위 입력으로 각 명령 1회씩 돌린 출력과 종료 코드를 붙인다.

## 7. 확장 경계 (지금 만들지 않는 것과 붙는 자리)

| 나중 모듈 | 붙는 자리 | 계약 |
| --- | --- | --- |
| 점검 게이트(8줄) | `cli`의 새 서브커맨드 `gate`. `Finding` 모델 재사용 | 점검 파일(md 표) 경로를 받아 빈 칸이면 종료 1. 8줄 본문은 `workflow/02` 4절에서 파싱, 코드에 복사 안 함 |
| 컷표 파서·프롬프트 골격 | 별도 패키지 `plating_prompt`가 `plating_qc.report`·`model`만 import | 공유 모델은 `model.py`에만 둔다. 반대 방향 의존 금지 |
| 레퍼런스 URL 검사 | `backend`와 무관한 새 모듈. 네트워크는 이 모듈에만 | 이 도구의 "오프라인" 원칙을 지키려고 기본 설치에서 분리(`extras`) |
| 블록아웃 버전 검사 | `layout.py`에 `BlockoutLayout` 추가 | 파일명 `vNN_` 접두사 규칙은 `plating-qc.toml`에서 읽음 |
| 기존 `join/xfade/match_frames` | `backend.base`에 `concat`, `xfade` 추가 후 ffmpeg 구현 | Blender 판은 폐기 후보. 사용자 결정 |
| 섞인 프레임 판정(check_mix) | `compare --mix A ia B ib` 옵션 | 합성 가중 w 추정은 선택 기능 |

## 8. 불확실한 점 (사용자 답 필요)

1. **PC에 ffmpeg 정적 빌드 설치 허용 여부.** 예: `D:\Plating\tools\ffmpeg\bin\`에 두고 `plating-qc.toml`의 `ffmpeg_path`로 지정(관리자 권한·PATH 변경 불필요). 거부하면 PC에서는 convert만 Blender 폴백으로 되고 compare·tiles는 클라우드(Linux)에서만 된다. 11/11 제출 작업은 PC에서 하므로 이 답이 가장 먼저 필요하다.
2. (해결, 요청서 2판) 저장소는 `tacosangsang/plating-qc-workflows`(비공개)로 생성됨. 3장 파일 트리의 루트 이름을 이 저장소 이름으로 바꾼다. dot의 실행 환경 gh CLI는 미로그인이므로 push는 Codex의 GitHub 연결로 한다. 안 되면 사용자에게 보고.
3. (해결, 요청서 2판) Notion은 학교 계정 연결로 읽힌다. 이 작업에는 그래도 필요 없다. 핸드북 11-07판과 Drive 사본의 일치는 바이트 비교 대신 "노션 맨 위 첨부가 정본"으로 간주한다(workflow/01 2절).
4. **Claude API 비용 상한.** 모델 ID는 `claude-opus-5-5`, 크레딧 만료 2026-11-16 UTC(사용자 확인). 상한은 "$100 전부를 설계·검토 호출에 써도 된다"로 두는 것을 추천. 호출당 상한은 두지 않고 `claude-usage.md` 누적으로만 본다.

## 9. dot에게: 구현 순서

1. `backend/base.py`, `model.py`, `layout.py`, `config.py` 먼저(인터페이스·계약). 테스트 `test_layout.py`.
2. `probe` + `FfmpegBackend.probe` + conftest 합성 입력 + `test_probe.py`.
3. `convert`(partial·충돌·사후 검증) + `test_convert.py`. 여기까지가 11/11 제출에 직접 쓰이는 최소.
4. `compare`(오프셋 탐색) + `test_compare.py`.
5. `tiles`, `split`, `BlenderBackend.encode_prores`(기존 `to_prores.py` 이식).
6. `samples/README.md` 로그, PR.

모델: 1~2는 Sol Extra High, 3~5는 Sol Extra High, 테스트 루프는 Luna. 각 단계 끝에 STATE.md 갱신.
