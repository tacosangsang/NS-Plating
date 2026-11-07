# PLATING 자동화 툴킷 설계 답변 [검수 대기]

이 문서는 설계 답변입니다. 구현, 실행, 테스트, 외부 저장은 하지 않았습니다. F와 W 문서의 행 번호와 수치는 요청서에 적힌 값을 인용했으며, 원문을 다시 읽어 확인하지 않았습니다. 아래 JSON과 표 예시는 형식 예이고 실행 결과가 아닙니다.

## 0. 설계 요지

- **계층 구조**: 공통 기반(경로, 출력, 문서 읽기) → 기능 모듈(cuts, prompt, gate / refs, versions, qc) → `cli.py` 순으로 의존합니다.
- **PLATING 고유 정보의 위치**: PLATING 고유의 형식과 판정 규칙은 `profile_plating.py` 한 파일에만 둡니다. 수치와 블록 본문은 이 프로필에도 복사하지 않습니다. 프로필에는 "어느 문서의 어느 제목 아래에서 어떤 형식으로 읽는가"(앵커 명세)만 두고, 값은 실행할 때마다 W 문서에서 읽습니다.
- **추상 경계는 6개뿐**: `CutTableSource`, `DocStore`, `HttpFetcher`, `ImageTool`, `ReferenceResolver`, `QcRunner`. 나머지는 함수와 frozen dataclass로 처리합니다.
- **기능 간 연결은 JSON 파일 계약**: 모듈끼리 import로 묶지 않습니다. 그래서 P0(cuts, prompt, gate)는 P1(refs, versions, qc)이 없어도 시작하고 실행됩니다.
- **종료 코드**: plating-qc와 같은 0~5 체계를 씁니다.
- **출력 방식**: 모든 출력은 staging 폴더에 만든 뒤 한 번에 공개합니다. 덮어쓰기는 하지 않습니다. raw, 입력 루트, 읽기 전용 루트에 대한 쓰기는 경로를 해석한 뒤 다시 검사해 거부합니다.
- **네트워크**: `--allow-network`가 있을 때만 사용합니다. 테스트에서는 소켓을 차단하고 가짜 구현만 주입합니다.

---

## 1. 모듈 구조와 데이터 흐름

### 1.1 파일 트리와 책임

```text
src/plating_tools/
  __init__.py          버전 문자열만. 하위 모듈 import 없음
  __main__.py          from .cli import main; raise SystemExit(main())
  cli.py               argparse 전체 정의(P1 인자 포함), 명령 실행 시점에만 처리 모듈 import, 종료 코드 매핑
  errors.py            ToolError(exit_code): InputError 2, OutputConflict 3, Unavailable 4, IoFailure 5
  config.py            plating.toml 읽기(tomllib), 경로 해석
  model.py             공통 dataclass: SourceRef, Finding, Unknown, DocFingerprint, RefEntry(공유 스키마)
  textio.py            UTF-8/BOM/CRLF 읽기, 줄 번호 보존, 글자 수 계산
  paths.py             경로 해석(junction/링크 포함)과 쓰기 허용 검사
  output.py            RunDir: staging→공개, 실패 격리, run.json, json/md/csv 쓰기
  docs.py              DocStore ABC + WorkflowDir, Markdown 부분 문법(제목·코드 펜스·번호 목록·파이프 표), 앵커 해석, 표기 분류
  profile_plating.py   PLATING 예외 데이터(1.3). 로직 없음
  cuts/
    source.py          CutTableSource ABC + NotionMdFile
    sections.py        토글 h3 / ### 섹션 분할, 제목 span 연결
    table.py           html.parser 기반 표 파서(행·셀·span·색·주석·원문 슬라이스)
    extract.py         씬 후보 선택, 열 대응, TC·길이 해석, 대상·문맥 조립, 검사
    report.py          cuts.json/md/csv, inventory
  prompt/
    rules.py           W05·W10·W11·W02에서 섹션 순서, 블록 카탈로그, 점검 8줄, 한도 읽기
    plan.py            plan.toml 로드·검증
    select.py          블록 선택 규칙(데이터) 평가
    assemble.py        골격 조립, 자리표시, 길이 표
    check.py           완성 프롬프트 검사(원문 동일성, 글자 수, @imageN, 옛 표기)
  gate/
    checklist.py       gate.toml 응답 검사, 기계 소견 결합, 승인 증거 판독
    cost.py            W07 §1·W06 §2 비용표 읽기와 계산
  refs/                (P1)
    fetch.py           HttpFetcher ABC + UrllibFetcher
    image.py           헤더 판독(표준 라이브러리), ImageTool ABC + FfmpegImageTool
    resolve.py         ReferenceResolver ABC + ListResolver
    check.py           대응, 번호·역할 대조, 썸네일, contact.html
  versions/            (P1)
    check.py           버전 태그 해석, 계열 스캔, 고정 예외 대조
  qc.py                (P1 끝) QcRunner ABC + SubprocessQcRunner
```

### 1.2 데이터 흐름

```text
F(md) ──cuts extract──> cuts.json
W02/W05/W10/W11 + cuts.json + plan.toml(사용자, 선택) ──prompt skeleton──> skeleton.md/json, gate.toml(빈 양식)
사용자가 새로 만든 prompt.txt + plan + W 문서 ──prompt check──> check.json/md
gate.toml(사용자 응답) + prompt.txt + W02/W06/W07 + cuts.json + check.json [+ refs.json]
    ──gate check──> gate.md(8줄을 프롬프트 바로 위에 배치) / gate.json / cost.json
refs.toml [--allow-network] ──refs check──> refs.json/md, thumbs/, contact.html       (P1)
versions.toml + pins.toml + W04 ──versions check──> versions.json/md                  (P1)
plating qc <cmd> ──python -m plating_qc 하위 프로세스──> qc/<n>/...                    (P1 끝)
```

gate는 refs 결과를 파일(`refs.json`)로만 읽습니다. 스키마는 P0의 `model.py`에 있으므로 refs 패키지를 import하지 않습니다.

### 1.3 일반 로직과 PLATING 예외의 위치

| 위치 | 내용 |
| --- | --- |
| 일반 모듈 | 섹션·표 파싱 장치, 앵커 해석, 글자 수 계산, 점검 완료 판정, 비용 산술, URL 검사, 버전 태그 비교, 경로 안전, 출력 공개 |
| `profile_plating.py` (값은 문서에서 읽음) | W01~W11 파일명과 키, 파일 단위 예외 파일 W07·W10·W11(근거 README 5~13행, W01 §1~2) |
| | 컷표 형식: 씬 ID `S#NN`, 수정본 표기 `S#NN 수정`, 컷 ID 형식, 열 이름→표준 필드 대응, 색→상태 규칙(사용자 확정 2026-11-07, W06 19행보다 우선) |
| | 앵커 명세: W05 §2 섹션 순서와 16행 길이 표 열, W10 블록 위치, W11 설정, W02 §2 승인 어휘, W02 §4 점검 8줄, W07 §1 비용, W06 §2 Topaz, 이미지 한도 위치, 레퍼런스 장수 권고 위치, `@imageN` 형식(W02 43, W07 31), Drive uc 형식(W07 24) |
| | 블록 선택 규칙(W10 44~110 근거 행 포함) |
| | 알려진 충돌 기록(H 542, H 120, W10 144~146 대 W11 49) |
| | 프로필 작성 기준 지문(각 W 파일 SHA-256, NS-Plating HEAD 577c3d4). 실행 시 지문이 다르면 경고 |
| 사용자 파일(코드 밖) | 블록아웃 고정 예외(pins). W04 §10의 v58, S#10 v50, v13, v2i는 코드나 프로필에 넣지 않습니다 |

### 1.4 모듈별 원전

| 모듈 | 구분 | 원전 |
| --- | --- | --- |
| cuts/sections, table | 일반(F 문법 한정) | 요청서 2절 F 확인 문법, W01 §1, W07 §6 74행 |
| cuts/extract | 일반 + 프로필 | W05 §1 1·12단계, W09 §7 1단계, H §5-13 1단계, 사용자 확정 색 규칙 |
| prompt/rules, assemble | 일반 | W05 §1 2~9단계, §2 27~51(34~41 순서), §5, 16행 |
| prompt/select | 프로필 | W10 44~110 |
| prompt/check | 일반 + 프로필 | W02 43, W07 31, H 542(옛 표기), 이미지 한도 문구(위치 미확인) |
| gate/checklist | 일반 + 프로필 | W02 §2 24~28, §3 53~66, §4 68~81, H §0-1 |
| gate/cost | 계산은 일반, 앵커는 프로필 | W07 §1 5~19(14~15), W06 §1~2, H 70·120 |
| refs | 일반 + 프로필 | W03 §2 19~24, W05 §4 63~80, W07 §2 23~25·§7, W09 §7 3단계, W08 24·38 |
| versions | 일반 | W01 §5 49~51, W04 §1~3 7~26, §10 130~137(pins 근거로만), W08 21·84, H §3-1 |
| qc | 일반 | W06 §4~5 79~98, W09 §7 5단계·§8, 요청서 5절 cli 계약 |
| paths, output | 일반 | W01 §4~6, 요청서 6절 |

### 1.5 P1 없이 P0가 실행되는 구조

- **인자 정의는 `cli.py`에만**: P1 명령의 인자 정의도 여기 있습니다. 처리 모듈은 명령을 실행하는 시점에만 import하므로, P1 패키지가 없어도 `--help`가 동작합니다.
- **P1 모듈이 없을 때**: P1 명령을 호출하면 종료 4(`P1 모듈 없음: plating_tools.refs`)를 내고, 다른 명령에는 영향이 없습니다.
- **import 금지 범위**: P0 모듈(공통, cuts, prompt, gate)은 refs, versions, qc와 서드파티 라이브러리를 import하지 않습니다. 이는 테스트 S7, S8로 강제합니다.
- **선택 의존성**: ffmpeg(썸네일과 디코딩 확인)과 네트워크는 P1에서만 씁니다. 둘 다 없어도 P0는 표준 라이브러리만으로 끝납니다.
- **설정 파일**: `config.py`는 `[qc]`, `[network]`, `[tools]` 섹션이 없어도 P0 명령에 필요한 키만 검사합니다.

### 1.6 QC 위임 경계

| 항목 | 계약 |
| --- | --- |
| 호출 | `[python, "-m", "plating_qc", ("--config", cfg)?, "--log", <work>/log/qc.log, <cmd>, ...]`, `shell=False`, argv 배열만 사용 |
| python | `[qc] python` 설정값, 비어 있으면 `sys.executable` |
| cwd | `<work>`(실행 폴더 오염 방지). 입력 경로는 미리 절대 경로로 해석해서 전달 |
| env | 부모 환경 복사 + `PLATING_QC_LOG_DIR=<work>/log`, `PYTHONIOENCODING=utf-8`. 이 둘 외에는 변경 없음 |
| 허용 명령 | `probe`, `compare`, `tiles`, `split`(`--out`은 `<work>/out`으로 도구가 지정). `convert`는 `--dry-run`만 허용(출력 위치를 우리가 통제할 수 없음) |
| 사용자 인자 제한 | 사용자가 `--out`, `--log`, `--config`를 주면 거부(도구가 지정함) |
| 보존 | stdout/stderr 원바이트, 종료 코드 그대로, 생성물 목록(경로·크기·SHA-256), 입력 파일 부모 폴더의 실행 전후 목록 차이 |
| 해석 | stdout이 JSON이면 요약만 읽습니다. 판정 문구는 바꾸지 않습니다(compare의 불확실 판정을 확정으로 바꾸지 않음) |
| 금지 | `plating_qc` 내부 모듈 import, shell 문자열 조립, plating-qc 파일 변경 |

---

## 2. 인터페이스 정의와 데이터 모델

시그니처는 설계 수준입니다. 모든 dataclass는 `frozen=True`입니다.

### 2.1 공통

```python
class Severity(StrEnum): INFO = "info"; WARN = "warn"; ERROR = "error"

class Mark(StrEnum):              # 문서에 실제로 적힌 표기만 판독
    UNMARKED = "무표기"; EXCEPTION = "예외"; EXAMPLE = "예(PLATING)"; FILE_EXCEPTION = "파일 단위 예외"

@dataclass(frozen=True)
class Unknown:
    reason: str                   # "열 없음", "해석 실패: ...", "문서에 없음", "사람 확인 필요" 등

@dataclass(frozen=True)
class DocFingerprint:
    key: str                      # "F", "W02", "README", "H"
    path: str; size: int; sha256: str
    authored_sha256: str | None   # 프로필 작성 기준값. 실행 값과 다르면 WARN
    declared_commit: str | None   # plating.toml 선언값. 도구는 검증하지 않음

@dataclass(frozen=True)
class SourceRef:
    doc: str
    line_start: int; line_end: int        # 1부터, 양끝 포함
    heading_path: tuple[str, ...] = ()
    mark: Mark | None = None; mark_reason: str | None = None
    excerpt_sha256: str | None = None     # 사용한 범위(LF 정규화 텍스트)의 해시

@dataclass(frozen=True)
class Finding:
    code: str; severity: Severity; message: str; where: SourceRef | None
```

미확인은 `Unknown(reason)` 한 가지로 표현합니다. JSON에서는 `{"unknown": "사유"}`, md에서는 `미확인(사유)`로 씁니다. 상태 필드의 기본값을 긍정 값으로 두지 않습니다.

**문서 지문을 남기는 최소 방법**은 다음 두 가지입니다.
- `run.json`의 `docs`에 사용한 모든 문서의 `DocFingerprint`를 기록합니다.
- 결과의 각 요소에 `SourceRef`(제목 경로, 행 범위, 발췌 SHA-256, 표기 분류)를 붙입니다.

git 명령은 실행하지 않고, 커밋은 선언값으로만 기록합니다.

### 2.2 컷표 추출

**입력 경계**

```python
class CutTableSource(ABC):
    @abstractmethod
    def fingerprint(self) -> DocFingerprint: ...
    @abstractmethod
    def lines(self) -> tuple[str, ...]: ...     # 개행을 제거한 원문 줄. 인덱스 0 = 1행

class NotionMdFile(CutTableSource): ...          # 로컬 fetch md 읽기. 나중에 노션 API 구현이 같은 경계를 씀
# 실패: 파일 없음, UTF-8 디코딩 실패(바이트 위치 표시) → InputError(2)
```

**데이터 모델**

```python
class RowState(StrEnum):
    TODO = "todo"; DONE = "done"; REMOVED = "removed"; REVISE = "revise"; UNKNOWN = "unknown"

@dataclass(frozen=True)
class ColorMark:
    element: Literal["row", "cell", "span", "title", "other"]
    raw: str                      # 원문 값 그대로, 예 "red_bg"
    state: RowState               # 이 요소의 상태(아래 색 규칙 표)
    rule: str                     # "사용자 확정 2026-11-07" | "미정의 색" | "요소 의미 미확정"
    line: int; col: int

@dataclass(frozen=True)
class Annotation:                 # discussion-urls 등 색 외 속성을 가진 인라인 요소
    tag: str; attrs: tuple[tuple[str, str], ...]; text: str; line: int; col: int

@dataclass(frozen=True)
class Cell:
    column_raw: str               # 머리 행 원문 텍스트
    field: str                    # 표준 필드 또는 "extra"
    raw_html: str                 # td 안 원문(태그·속성 보존)
    text: str                     # 인라인 태그 제거·연결, <br />→"\n", 문자 참조 해석
    colors: tuple[ColorMark, ...] # td 자신의 색과 내부 span 색을 각각 별도로
    annotations: tuple[Annotation, ...]
    line: int

@dataclass(frozen=True)
class FieldValue:
    kind: Literal["present", "empty", "absent"]   # absent = 이 표에 그 열이 없음
    cell: Cell | None

@dataclass(frozen=True)
class TcValue:
    raw: str
    start_s: Decimal | Unknown; end_s: Decimal | Unknown
    form: str | None              # "mm:ss–mm:ss" | "mm:ss.f–ss.f" 등

@dataclass(frozen=True)
class LengthValue:
    raw: str; seconds: Decimal | Unknown

@dataclass(frozen=True)
class CutRow:
    order: int                    # 선택된 표 안의 원문 순서. 재정렬 없음
    cut_id: str | Unknown         # 셀 텍스트를 연결한 값
    row_color: ColorMark | None
    row_state: RowState           # tr 색만으로 결정
    fields: Mapping[str, FieldValue]   # 모든 표준 필드를 키로 가짐(absent 포함)
    extra: tuple[Cell, ...]       # 모르는 열. 원문 순서 유지
    tc: TcValue | Unknown; length: LengthValue | Unknown
    excluded_from_generation: bool     # row_state == REMOVED일 때만 True
    where: SourceRef

@dataclass(frozen=True)
class TableRef:
    line_start: int; line_end: int
    header: tuple[str, ...] | Unknown
    is_cut_table: bool; nested: bool   # nested = 섹션 안의 중첩 토글이나 하위 제목 아래

@dataclass(frozen=True)
class SceneSection:
    scene_id: str | None          # "S#04". 씬 형식이 아니면 None(녹음 대본 등)
    title_raw: str; title_text: str
    container: Literal["toggle_h3", "md_h3"]
    is_revision: bool
    title_colors: tuple[ColorMark, ...]; title_annotations: tuple[Annotation, ...]
    tables: tuple[TableRef, ...]
    notes: tuple[SourceRef, ...]  # 러닝타임 문단 등 표 밖 텍스트의 위치(컷이 아님)
    where: SourceRef

@dataclass(frozen=True)
class ContextCut:
    role: Literal["prev_scene_last", "next_scene_first", "prev_in_scene", "next_in_scene"]
    row: CutRow | None
    note: str                     # "첫 씬이라 없음", "S#05 섹션 없음", "마지막 행이 removed" 등

@dataclass(frozen=True)
class SceneExtract:
    source: DocFingerprint
    scene_id: str
    selected: SceneSection
    rejected: tuple[tuple[SceneSection, str], ...]   # 위치와 제외 사유만(본문 없음)
    header_map: tuple[tuple[str, str], ...]          # (원문 열 이름, 표준 필드)
    targets: tuple[CutRow, ...]
    context: tuple[ContextCut, ...]                  # 생성 대상 아님
    findings: tuple[Finding, ...]
```

**함수와 실패 조건**

```python
def parse_sections(src: CutTableSource) -> list[SceneSection]
    # InputError: 토글 짝 불일치, 표 미종결로 섹션 경계를 정할 수 없음
def extract_scene(src: CutTableSource, scene_id: str, *, cut_ids: Sequence[str] | None = None,
                  section_line: int | None = None, table_line: int | None = None) -> SceneExtract
    # InputError: 씬 섹션 없음, 수정본 후보 2개 이상(section_line 없음), 컷표 후보 0개 또는 2개 이상,
    #             지정 컷 ID 없음, 요약 표기(~)를 단일 ID로 지정
def inventory(src: CutTableSource) -> Inventory      # 전 섹션·표·열 이름·색 집계(구현 초기 확인용)
```

**씬과 표 선택 규칙**

1. **섹션 경계**: 섹션은 다음 둘 중 하나입니다.
   - 최상위 `<toggle heading="h3">`부터 짝이 맞는 `</toggle>`까지
   - 최상위 `### `부터 다음 h1~h3 제목, 최상위 h1~h3 토글, 또는 EOF 직전까지

   토글 제목은 여는 태그 다음의 첫 비어 있지 않은 줄이고, `###` 제목은 기호 뒤의 텍스트입니다.
2. **제목 텍스트**: 인라인 태그를 제거하고 텍스트를 연결한 뒤 공백을 정규화합니다. 비교용 키에만 NFC를 적용하고, 원문은 그대로 둡니다. 예: `S#<span ...>12 수정</span>` → `S#12 수정`.
3. **씬 ID**: 정규식 `^S#(\d{2})(\s|$)`로 판별합니다. 맞지 않는 h3(`### 녹음 대본 (인물별 대사)` 등)는 비씬 섹션으로, 직전 씬의 끝 경계 역할만 하며 추출에 섞지 않습니다.
4. **수정본 판정**: 제목 텍스트가 정확히 `S#NN 수정`일 때만 수정본입니다. 다른 형태로 `수정`을 포함하면 CT016 경고를 내고 수정본으로 취급하지 않습니다.
5. **후보 선택**:
   - 수정본이 1개면 그것을 선택합니다.
   - 수정본이 0개이고 같은 ID의 섹션이 1개면 그것을 선택합니다.
   - 그 외에는 InputError를 내고 후보 줄과 제목을 보고합니다. `--section-line`으로 명시 선택할 수 있고, 그 선택은 `run.json`에 기록합니다.
6. **컷표 판별**: 선택된 섹션의 최상위(중첩 토글 밖)에 있는 `<table header-row="true">` 중, 머리 첫 칸이 `컷`이고 `TC` 열이 있는 표입니다. 1개가 아니면 InputError를 내고 `--table-line`으로 지정하게 합니다. 중첩 위치의 표는 쓰지 않고 CT015로 보고합니다.
7. **문맥 컷**:
   - 씬 번호 ±1의 씬에 같은 규칙을 적용해, 앞 씬의 마지막 행과 뒤 씬의 첫 행을 문맥으로 냅니다. 그 행이 removed이면 그 행을 그대로 내고, 마지막(또는 첫) 비제거 행을 note와 함께 추가로 냅니다.
   - `--cuts`를 지정하면 같은 씬 안의 바로 앞과 뒤 행도 문맥에 넣습니다.
   - 문맥 컷은 `targets`에 넣지 않습니다.

**원문 열 이름 → 표준 필드 대응표**

비교는 공백 정규화 후 정확 일치로 합니다(PLATING 예외).

| 원문 열 이름 | 표준 필드 | 처리 | 확인 위치 |
| --- | --- | --- | --- |
| `컷` | `cut_id` | span을 연결한 텍스트로 식별. 원문 HTML과 주석은 보존 | F 37~59, 400~419, 1227~1246 |
| `TC` | `tc` | 원문 + 지원 형식만 해석 | 같음 |
| `길이` | `length` | 원문 + `<수>s` 해석 | 같음 |
| `샷 / 앵글` | `shot_angle` | 한 필드. 분리하지 않음 | 같음 |
| `화면` | `picture` | 화면·액팅 서술 원문. 액팅을 따로 추출하지 않음 | 같음 |
| `사운드` | `sound` | S#01, S#02 | F 37~59, 400~419 |
| `대사` | `dialogue` | S#01 | F 37~59 |
| `대사 / 사운드` | `dialogue_sound` | 합쳐진 원문을 한 필드로 보존. 이 표에서 `dialogue`, `sound`는 absent | F 1227~1246 |
| 그 밖 | `extra["원문 이름"]` | 원문 열 이름과 값을 그대로 보존. CT010 경고 | 미관찰. inventory로 확인 |

같은 표 안에 같은 열 이름이 두 번 있으면 깨진 표(CT004)로 봅니다. `샷/앵글`처럼 띄어쓰기가 다른 변형은 extra로 보존하고 경고합니다.

**색 규칙**

행 색과 셀·span 색은 항상 별도로 출력하고 합치지 않습니다.

| 위치 | 원문 색 | 내보내는 상태 | 근거 |
| --- | --- | --- | --- |
| tr | red_bg / green_bg / gray_bg / yellow_bg | row_state todo / done / removed / revise | 사용자 확정 2026-11-07 |
| tr | 없음 | row_state unknown | 같음(추정 금지) |
| tr | 그 밖의 색 | row_state unknown + CT009 | 미정의 |
| td | red_bg | 그 필드만 todo. row_state 불변 | 사용자 확정 |
| td, span, title | yellow_bg | 그 요소 revise. row_state 불변 | 사용자 확정(S#10 제목 span 2889 포함) |
| td, span | green_bg, gray_bg / span의 red_bg | 원문 보존, 요소 상태 unknown(`요소 의미 미확정`) | 규칙 미지정. 질문 I5 |
| callout 등 그 밖의 요소 | 모든 색 | 원문 보존, 상태 없음 | |

removed 행은 출력에 남기고 `excluded_from_generation=true`로 표시합니다. 상태 추출은 생성 승인과 무관합니다.

**TC·길이 지원 형식**

| 형식 | 예 | 해석 |
| --- | --- | --- |
| `M+:SS(.f)?–M+:SS(.f)?` | `00:04–00:08`(F 88) | 그대로 |
| `M+:SS(.f)?–SS(.f)?` | `00:00.0–02.0`(F 1252) | 끝값은 분이 생략된 것으로 보고 시작의 분을 상속. 상속 결과 끝이 시작보다 작으면 실패 |
| 그 밖(ASCII 하이픈, em dash, 시:분:초, 구분자 주변 공백 등) | | 해석 실패(CT006), 원문 유지 |
| 길이 `^\d+(\.\d+)?s$` | `4s`(F 68), `2.0s`(F 1255) | Decimal 초. 그 밖은 CT007 |

구분자는 확인된 en dash(U+2013)만 지원합니다. TC 구간과 길이가 다르면 CT014 경고를 내고, 어느 쪽도 고치지 않습니다.

**소견 코드**

| 코드 | 내용 | 종료 영향 |
| --- | --- | --- |
| CT001 | 씬 섹션 없음 | 2 |
| CT002 | 수정본 후보 중복 | 2 |
| CT003 | 컷표 후보 표 0개 또는 2개 이상 | 2 |
| CT004 | 깨진 표 | 1 |
| CT005 | 중복 컷 ID | 1 |
| CT006 | TC 해석 실패 | 1 |
| CT007 | 길이 해석 실패 | 1 |
| CT008 | 색 유실(섹션 원문의 `color="…"` 수 ≠ 파싱된 ColorMark 수) | 1 |
| CT009 | 미정의 색 | 1 |
| CT010 | 모르는 열 | 1 |
| CT011 | 컷 ID 형식 미확인(`^S#\d{2}-C\d{3}(-\d+[A-Z]?)?$` 외) | 1 |
| CT012 | 머리 행 없음 | 2 |
| CT013 | 요약 표기 ID(`~` 포함) | 1 |
| CT014 | TC·길이 불일치 | 1 |
| CT015 | 중첩 위치 표 | 1 |
| CT016 | 수정 표기 변형 | 1 |
| CT017 | 컷 ID의 씬과 섹션의 씬 불일치 | 1 |

**출력 형식 예 (S#01-C001, 실행 결과 아님)**

```json
{
  "order": 0, "cut_id": "S#01-C001",
  "row_color": {"element": "row", "raw": "green_bg", "state": "done", "rule": "사용자 확정 2026-11-07"},
  "row_state": "done",
  "fields": {
    "tc": {"kind": "present", "text": "00:00–00:04"},
    "length": {"kind": "present", "text": "4s"},
    "shot_angle": {"kind": "present", "text": "BLACK"},
    "picture": {"kind": "present", "text": "완전한 암전. …"},
    "sound": {"kind": "present", "text": "브라운관이 켜지는 …", "colors": []},
    "dialogue": {"kind": "present", "text": "앵커(TV): …",
                 "colors": [{"element": "cell", "raw": "red_bg", "state": "todo", "rule": "사용자 확정 2026-11-07"}]},
    "dialogue_sound": {"kind": "absent"}
  },
  "field_states": {"dialogue": "todo"},
  "tc_parsed": {"start_s": "0", "end_s": "4", "form": "mm:ss–mm:ss"},
  "length_parsed": {"seconds": "4"},
  "excluded_from_generation": false,
  "where": {"doc": "F", "line_start": 60, "line_end": 82}
}
```

색은 대사 셀에만 있으므로 `sound`에는 상태를 붙이지 않습니다. 요청서의 "대사·사운드 새 작업" 설명과의 관계는 질문 I6에 남깁니다. S#04-C001은 `row_state: "unknown"`, `dialogue_sound: present`, `dialogue`·`sound: absent`로 출력합니다.

### 2.3 규칙 문서와 앵커

```python
class DocStore(ABC):
    @abstractmethod
    def load(self, key: str) -> Doc: ...        # 없거나 디코딩 실패 → InputError

@dataclass(frozen=True)
class Doc:
    fingerprint: DocFingerprint
    lines: tuple[str, ...]

@dataclass(frozen=True)
class Anchor:
    doc: str
    heading: tuple[str, ...]          # 제목 경로. 각 요소는 공백 정규화 후 정확 일치
    take: Literal["fence", "fences", "numbered", "table_rows", "lines"]
    count: int | None                 # 기대 개수(점검 8줄 = 8). 다르면 실패
    pattern: str | None               # 이름 있는 그룹으로 값을 추출. 값은 문서에서만 옴
    fixed: Mapping[str, str]          # 반드시 이 문자열이어야 하는 그룹(예: 단위 "Crons")
    hint_lines: tuple[int, int] | None  # 작성 시점의 행 범위. 이동하면 경고만

@dataclass(frozen=True)
class Extract:
    text: str; where: SourceRef; groups: Mapping[str, str]

def resolve(doc: Doc, a: Anchor) -> list[Extract]
    # InputError(2): 제목 0개 또는 2개 이상, 개수 불일치, 패턴 불일치, fixed 불일치, 펜스 미종결.
    # 메시지에 문서 키, 행, 찾은 후보 제목을 포함. 비슷한 제목으로 대체하지 않음
def classify(doc: Doc, where: SourceRef) -> tuple[Mark, str | None]
    # [예외: 이유], 예(PLATING), 파일 단위 예외(W07·W10·W11)를 원문에서 판독. 없으면 UNMARKED
```

- **지원하는 Markdown 부분 문법**: 펜스 밖의 ATX 제목, ``` 또는 ~~~ 펜스(길이 일치), `N.` 번호 목록, 파이프 표 행. CommonMark 전체를 처리하지 않습니다.
- **펜스 본문**: 펜스 사이의 줄을 LF로 연결하고 끝 개행은 넣지 않습니다.
- **무표기 항목**: `무표기`로만 기록합니다. 일반 규칙이라고 확정하지 않고 md에 `[확인 필요]`로 표시합니다.
- **RuleBook**: 앵커 결과를 묶는 객체입니다. 명령은 필요한 부분만 읽습니다. skeleton은 W07이 깨져 있어도 동작하고, gate는 W07이 필요합니다.

### 2.4 프롬프트 골격과 글자 수

```python
@dataclass(frozen=True)
class Block:
    key: str                  # 프로필이 정한 키, 예 "STYLE", "AVOID", "FACE_RULE", "EYES_CHILD", "SCENE_<모듈>"
    text: str; sha256: str; where: SourceRef

@dataclass(frozen=True)
class CharacterMeta:
    name: str
    group: str | Unknown      # 계획 파일에 사람이 적은 값만 사용. 이름으로 추론하지 않음
    face: Literal["close", "far", "none"] | Unknown
    basis: str | None

@dataclass(frozen=True)
class RefEntry:               # model.py. plan·gate·refs 공용
    index: int; role: str
    local_path: str | None; url: str | None; file_id: str | None
    sheet: Literal["있음", "시트 없음/만들어야 함"]
    preview: Literal["미검수", "검수함"]; preview_by: str | None; preview_at: str | None
    candidates: tuple[str, ...]; candidates_complete: bool; candidates_basis: str | None

@dataclass(frozen=True)
class ClipPlan:
    clip_id: str; kind: Literal["video", "image"]
    cuts: tuple[str, ...]
    segment: str | Unknown
    gen_seconds: Decimal | Unknown
    mode: Literal["new", "edit", "code"] | Unknown
    model: str | Unknown; resolution: str | Unknown
    edit_input_seconds: Decimal | Unknown
    people: Literal["있음", "없음"] | Unknown
    characters: tuple[CharacterMeta, ...]
    staging: Mapping[str, bool | Unknown]     # seated, procession 등 프로필이 정한 키
    scene_module: str | None | Unknown
    props: tuple[str, ...] | Unknown
    references: tuple[RefEntry, ...]

class Decision(StrEnum): INCLUDE = "포함"; EXCLUDE = "제외"; UNDECIDED = "미결"

@dataclass(frozen=True)
class BlockRule:              # 프로필 데이터. W10 44~110 근거 행 포함
    block_key: str
    requires: Mapping[str, object]            # 예 {"people": "있음", "face": "close"}
    forbid_names: tuple[str, ...]; forbid_groups: tuple[str, ...]
    basis: SourceRef

@dataclass(frozen=True)
class BlockDecision:
    block_key: str; decision: Decision; reason: str
    inputs: Mapping[str, str]; basis: SourceRef

def select_blocks(clip: ClipPlan, catalog: Mapping[str, Block],
                  rules: Sequence[BlockRule]) -> list[BlockDecision]
    # 필요한 메타데이터가 Unknown이면 UNDECIDED. "자동 적용 완료"라는 상태는 없음
```

블록 선택 규칙의 예입니다.
- 사람이 없거나 얼굴이 먼 컷이면 FACE RULE과 EYES를 제외합니다.
- 진우, 흰토끼, 상류층(forbid)에는 하층민 블록을 제외합니다.
- 아이 EYES, 인물별 의상, STAGING 예외는 W10 44~110의 해당 행을 근거로 프로필에 기록합니다.

```python
@dataclass(frozen=True)
class Slot:
    section: str
    kind: Literal["fixed", "placeholder"]
    text: str
    block_keys: tuple[str, ...]
    needs: tuple[str, ...]        # 비어 있는 항목: 컷표 문장, Camera, Sound, Subtext, End state, 마지막 상태

@dataclass(frozen=True)
class LengthRow:                  # 컷 / 구간 / 생성 길이 / 컷표 길이 / 여유
    cut_id: str; segment: str | Unknown
    gen_seconds: Decimal | Unknown; cut_length: LengthValue | Unknown
    slack: Decimal | Unknown      # 정의 확인 전에는 "생성 길이 − 컷표 길이 합"을 도구 계산으로 표시(I12)

@dataclass(frozen=True)
class LengthCount:
    codepoints: int; utf16_units: int; utf8_bytes: int; non_nfc: bool

@dataclass(frozen=True)
class Limit:
    value: int; unit: str; where: SourceRef      # 문서에서 읽은 값

@dataclass(frozen=True)
class LengthReport:
    total: LengthCount
    per_block: Mapping[str, LengthCount]; per_section: Mapping[str, LengthCount]
    placeholders: int
    limit: Limit | Unknown        # 영상은 Unknown("상한 미확인")
    verdict: Literal["within", "over", "over_by_utf16_only", "not_final", "no_limit"]

@dataclass(frozen=True)
class Skeleton:
    clip: ClipPlan | Unknown
    order: tuple[str, ...]; order_basis: SourceRef    # W05 34~41
    slots: tuple[Slot, ...]
    decisions: tuple[BlockDecision, ...]
    length_table: tuple[LengthRow, ...]
    checklist: tuple[ChecklistLine, ...]               # W02 §4 원문. 응답 비어 있음
    conflicts: tuple[Finding, ...]
    decided_by_tool: tuple[str, ...]                   # md "내가 정한 것"
    needs_user: tuple[str, ...]                        # md "사용자 답이 필요한 것"
    lengths: LengthReport
    cuts_source: DocFingerprint                        # 컷표 최신성 대조용

def build_skeleton(cuts: SceneExtract, plan: ClipPlan | None, rules: RuleBook) -> Skeleton
    # InputError: 계획 컷 ID가 targets에 없음, 문맥 컷을 대상으로 지정,
    #             정본 블록 안에 자리표시 표지 "{{" 존재(충돌)
    # Finding: removed 행 포함(ERROR), done 행 포함(WARN), 컷 순서가 원문과 다름(WARN)
def check_prompt(text: str, plan: ClipPlan | None, rules: RuleBook) -> PromptCheck
```

**골격 조립 규칙**

- 섹션 순서는 W05 34~41에서 읽습니다. 8개 이름이 기대와 다르면 실패합니다.
- 고정 블록은 W10 펜스의 원문을 그대로 넣습니다. 비고정 섹션에는 `{{미결: <섹션> — <필요 항목>}}`만 넣습니다.
- 섹션 라벨 줄을 도구가 지어 넣지 않습니다. W10 블록에 `AVOID:`처럼 라벨이 이미 들어 있으면 그것만 남습니다.
- 섹션 사이는 빈 줄 하나(`\n\n`)로 연결하고, 글자 수에 포함합니다.
- TIMELINE에는 컷마다 자리표시를 둡니다. 컷표 한국어 원문은 md의 검수 패널에만 싣고, 프롬프트 본문에는 넣지 않습니다. 영어 문장, 액팅, 길이 배분은 만들지 않습니다.
- 충돌이 기록된 SCENE 모듈(W10 144~146 대 W11 49)을 선택하면 conflicts에 올리고, 해당 슬롯을 미결로 둡니다. 원문을 치환하거나 정본을 수정하지 않습니다.
- 충돌 기록의 근거 행에 기록된 수치 문자열이 더 이상 없으면 `충돌 기록 재확인 필요`로 보고합니다.

**글자 수 계산**

1. 계산 대상은 실제 완성 문자열입니다. CRLF와 CR을 LF로 바꾼 뒤, 끝 개행은 포함하지 않고 셉니다.
2. 주 기준은 Python `len`(코드 포인트)입니다. UTF-16 코드 단위와 UTF-8 바이트를 함께 기록합니다.
3. 원문은 NFC로 정규화하지 않습니다. NFC가 아니면 경고합니다.
4. 이미지는 문서에서 읽은 한도(3000)로 검사합니다.
   - 코드 포인트가 한도를 넘으면 `over`(종료 1)입니다.
   - 코드 포인트는 한도 이내지만 UTF-16 단위가 넘으면 `over_by_utf16_only`(종료 1, 계산 방식 차이 경고)입니다.
5. 고정 블록은 어떤 경우에도 자르지 않습니다.
6. 자리표시가 남아 있으면 `not_final`로 판정합니다. 이때는 고정 블록 합계와 남은 예산만 보고합니다.
7. 영상은 길이만 기록하고 `상한 미확인`으로 둡니다.
8. 서비스의 실제 계산과 일치한다고 표시하지 않습니다.

**PromptCheck** 결과에는 다음이 들어갑니다.
- 포함하기로 결정된 블록마다 원문의 정확한 부분 문자열이 있는지. 첫 줄만 일치하면 `변형 의심`으로 표시합니다.
- 남은 자리표시 수
- 옛 표기 `@[이미지 N](image_N)` 검출(H 542). 검출되면 오류입니다.
- `@imageN` 집합과 계획 레퍼런스 번호의 대조: 누락, 미사용, 비연속, 중복
- 글자 수 보고

### 2.5 점검 게이트와 비용

```python
class Answer(StrEnum): YES = "예"; NO = "아니오"; NA = "해당 없음"

@dataclass(frozen=True)
class ChecklistLine:
    no: int; text: str; where: SourceRef          # W02 §4 원문

@dataclass(frozen=True)
class ItemInput:
    no: int; answer: Answer | None
    reason: str; alternative: str
    evidence: tuple[str, ...]; reviewer: str

class ItemStatus(StrEnum):
    COMPLETE = "완료"; INCOMPLETE = "미완료"; CONTRADICTED = "기계 소견과 충돌"

@dataclass(frozen=True)
class ItemResult:
    line: ChecklistLine; given: ItemInput | None
    machine: tuple[Finding, ...]
    human_required: tuple[str, ...]
    status: ItemStatus; problems: tuple[str, ...]

@dataclass(frozen=True)
class ApprovalEvidence:
    quote: str; where: str; by: str; at: str; prompt_sha256: str

@dataclass(frozen=True)
class ApprovalResult:
    status: Literal["승인 기록 있음", "승인 기록 없음", "승인 기록 불일치", "어휘 불명확"]
    vocabulary_hits: tuple[str, ...]              # W02 §2 어휘와 일치한 원문 낱말
    bound_to_prompt: bool                         # 증거의 SHA-256 = 현재 prompt 파일의 SHA-256

@dataclass(frozen=True)
class GateResult:
    items: tuple[ItemResult, ...]                 # 정확히 8개
    checklist_complete: bool
    approval: ApprovalResult
    cost: CostSummary
    cuts_fresh: bool | Unknown                    # cuts.json의 F 지문 = 현재 F 지문
    label: str                                    # 아래 라벨 중 하나

def evaluate_gate(lines: Sequence[ChecklistLine], inputs: Sequence[ItemInput],
                  context: GateContext, approval: ApprovalEvidence | None) -> GateResult
```

**항목 완료 조건**
- 응답이 없거나 빈 문자열, `미확인`이면 미완료입니다.
- `예`는 근거가 1개 이상 있어야 합니다. 사람 검수 항목이면 reviewer도 필요합니다.
- `아니오`는 reason과 alternative가 모두 있어야 합니다.
- `해당 없음`은 reason이 있어야 합니다.
- ERROR 수준의 기계 소견이 있으면 응답과 관계없이 CONTRADICTED입니다.
- 기계 검사가 통과해도 응답을 자동으로 채우지 않습니다.

**라벨**
- `[점검 미완료]`
- `[점검 완료·승인 기록 없음]`
- `[점검 완료·승인 기록 있음]`

"전송 가능", "생성 가능"이라는 라벨은 없습니다. 이 툴킷은 생성 API를 호출하지 않습니다.

**승인 판정**
- 프롬프트 준비 지시를 인용한 경우처럼 W02 §2 어휘와 맞지 않으면 `어휘 불명확`입니다.
- 증거의 SHA-256이 현재 프롬프트와 다르면 `승인 기록 불일치`입니다.
- 최종 판단은 사람이 합니다.

```python
@dataclass(frozen=True)
class Rate:                      # W07 §1의 한 행에서 읽은 값
    model: str; mode: Literal["new", "edit"]; resolution: str
    per_second: Decimal; min_seconds: Decimal | None
    billing: Literal["seconds_as_given", "ceil_input_seconds"]
    unit: str                    # 문서 표기 그대로
    where: SourceRef

@dataclass(frozen=True)
class FlatFee:                   # W06 §2 Topaz
    service: str; amount: Decimal; unit: str; per: str | Unknown; where: SourceRef

@dataclass(frozen=True)
class CostLine:
    label: str                   # "요청안", "대안: 480p 새 생성", "대안: 업스케일"
    amount: Decimal | Unknown; unit: str
    formula: str                 # "4 × 20 = 80"
    inputs: Mapping[str, str]; where: SourceRef | None

@dataclass(frozen=True)
class CostSummary:
    lines: tuple[CostLine, ...]
    totals: Mapping[str, Decimal]       # 단위별 합계. Crons와 Higgsfield 크레딧은 합산하지 않음
    doc_versions: tuple[DocFingerprint, ...]
    not_checked: tuple[str, ...]        # "실제 잔여 Crons", "결제 가능 여부", "현재 서비스 요금"

def cost_for(clip: ClipPlan, table: CostTable) -> CostSummary
```

**계산 규칙**

모든 계산은 Decimal로 합니다.

| 경우 | 처리 |
| --- | --- |
| 새 생성 | `gen_seconds × per_second` |
| 새 생성, 정수가 아닌 길이 | 계산하지 않음. ERROR 소견 |
| 새 생성, 최소 4초 미만 | 계산하지 않음. "허용 최소인지 과금 최소인지 미확인"(I3) |
| edit | `ceil(edit_input_seconds) × per_second`. 생성 길이와 섞지 않음 |
| 문서에 없는 모델, 해상도, 모드(예: edit 480p) | `Unknown("문서에 없음")` |
| 1080p 새 생성 요청 | 요청안 옆에 480p 새 생성 행과 Topaz 업스케일 행을 추가. 단위 합계는 별도 |
| Topaz 적용 단위(`per`)가 미확인 | 문서 문구만 표시하고 금액은 Unknown |

계산 예:
- 4초 480p 새 생성 → `4 × 20 = 80 Crons`
- 1.5초 1080p edit → `ceil(1.5) × 110 = 220 Crons`
- 4초 1080p 새 생성 → `4 × 81 = 324 Crons`, 대안 480p `80 Crons` + Topaz(W06 §2 값, Higgsfield 크레딧)

8번째 칸에는 식, 단위, 모델, 문서 SHA-256과 선언 커밋을 남깁니다.

### 2.6 레퍼런스 (P1)

```python
@dataclass(frozen=True)
class ImageInfo:
    format: Literal["png", "jpeg", "webp"] | Unknown
    width: int | Unknown; height: int | Unknown
    decode: Literal["헤더만 확인", "디코딩 확인", "디코딩 실패", "확인 안 함"]
    size: int; sha256: str

class FetchError(StrEnum):
    NONE = "none"; NOT_ATTEMPTED = "not_attempted"; NON_HTTPS = "non_https"; TIMEOUT = "timeout"
    TOO_MANY_REDIRECTS = "too_many_redirects"; HTTP_STATUS = "http_status"; HTML_PAGE = "html_page"
    NOT_IMAGE = "not_image"; TOO_LARGE = "too_large"; NETWORK = "network"

@dataclass(frozen=True)
class Hop:
    url: str; status: int; location: str | None

@dataclass(frozen=True)
class FetchResult:
    error: FetchError; detail: str
    hops: tuple[Hop, ...]
    final_url: str | None; status: int | None; content_type: str | None
    body_size: int | None; body_sha256: str | None
    image: ImageInfo | None

class HttpFetcher(ABC):
    @abstractmethod
    def get(self, url: str, *, timeout_s: float, max_redirects: int, max_bytes: int) -> FetchResult: ...
    # 예외를 던지지 않고 error 값으로 구분

class ImageTool(ABC):
    @abstractmethod
    def available(self) -> bool: ...
    @abstractmethod
    def decode_check(self, path: Path) -> bool: ...
    @abstractmethod
    def thumbnail(self, src: Path, dst: Path, max_side: int) -> None: ...   # dst가 있으면 OutputConflict

class ReferenceResolver(ABC):
    @abstractmethod
    def candidates(self, entry: RefEntry) -> CandidateSet: ...

@dataclass(frozen=True)
class CandidateSet:
    entry_index: int; items: tuple[Path, ...]; complete: bool; basis: str | None

@dataclass(frozen=True)
class RefResult:
    entry: RefEntry
    local: ImageInfo | Unknown
    remote: FetchResult
    correspondence: Literal["바이트 동일", "불일치", "미확인"]
    largest_among_given: str | Unknown
    best_original: Literal["최대 원본 확인됨", "최대 원본 미확인"]
    findings: tuple[Finding, ...]
```

**UrllibFetcher**
- 자동 리디렉트를 끄고 매 hop을 직접 처리합니다. 모든 hop에서 HTTPS가 아니면 `NON_HTTPS`로 끝냅니다.
- 쿠키와 인증 헤더를 보내지 않습니다.
- 본문을 청크로 읽어 `max_bytes + 1`에서 멈추고, 단조 시계로 전체 마감 시간을 검사합니다.

**성공 판정**: 최종 상태 200, Content-Type이 `image/*`, 본문 매직 바이트가 PNG, JPEG, WebP 중 하나로 해석될 것. 셋을 모두 만족해야 합니다. HTML 로그인·다운로드 확인 페이지, 403, 404, timeout은 성공이 아닙니다.

**대응 판정**: 로컬 파일과 응답 본문의 SHA-256이 같을 때만 `바이트 동일`입니다. 크기만 같은 경우는 `불일치` 또는 `미확인`입니다.

**최대 원본**: `최대 원본 확인됨`은 다음 셋을 모두 만족할 때만 표시합니다.
- 사람이 후보 전수(`candidates_complete`)와 근거를 선언함
- 선택된 로컬 파일이 그 후보들 가운데 최대 픽셀 수임
- 근거가 남아 있음

그 외에는 `제공된 후보 N개 중 최대`만 보고합니다.

**보기용 축소본 감지**: 로컬 경로가 이전 `plating` 출력의 `thumbs/` 안을 가리키면 ERROR를 냅니다(W08 24).

**이미지 처리 도구 검토**
- 표준 라이브러리에는 이미지 디코더가 없습니다. `imghdr`는 3.12에서 폐기 예정이므로 쓰지 않습니다.
- 크기와 형식은 `struct`로 PNG IHDR, JPEG SOF, WebP VP8/VP8L/VP8X 헤더를 읽어 얻습니다(`헤더만 확인`).
- 디코딩 확인과 썸네일은 기존 FFmpeg를 argv로 호출합니다.
  - 디코딩 확인: `ffmpeg -v error -i SRC -f null -`
  - 썸네일: `ffmpeg -n -v error -i SRC -vf scale=…:force_original_aspect_ratio=decrease -frames:v 1 DST`
- 애니메이션 WebP와 일부 형식은 FFmpeg 빌드에 따라 실패할 수 있으며, 실패는 그대로 보고합니다.
- 새 이미지 라이브러리는 필요하지 않습니다. FFmpeg를 직접 호출하는 것에 대한 허용 여부는 D1입니다.

**contact.html**: 번호, 파일명, 역할, 시트 상태, 검수 상태를 HTML 텍스트로 표시합니다. 한글이 그림에 박히지 않으므로 글꼴 문제가 없습니다. 상단에 "보기용, 생성 입력 아님"을 표기합니다.

**번호와 장수 검사**
- 첨부 순서와 `@image1`부터의 번호, REFERENCE ROLES 안의 번호 토큰, 본문 참조를 대조합니다.
- 역할 문구가 일치하는지는 사람이 검수합니다.
- 장수는 문서 문구에서 읽은 범위(3~5장 안전 권고)로 표시하고, 6장 이상이면 분할 검토 사유를 표시합니다. 하드 한도로 다루지 않습니다.

### 2.7 블록아웃 버전 (P1)

```python
@dataclass(frozen=True)
class VersionTag:
    raw: str; number: int; suffix: str            # "v2i" → 2, "i"

@dataclass(frozen=True)
class FamilySpec:
    name: str; root: Path
    blend_glob: str; script_glob: str; readme_glob: str
    readme_version_pattern: str | None
    exclude_dirs: tuple[str, ...]
    explicit_order: tuple[str, ...] | None        # 접미사 판의 순서를 사람이 정한 경우만

@dataclass(frozen=True)
class Pin:
    family: str; version: str; scope: tuple[str, ...]          # 예 ("S#10",)
    basis_doc: str; basis_line: int; basis_contains: str       # 근거 행에 이 문자열이 있어야 함
    approved_by: str

@dataclass(frozen=True)
class FamilyState:
    family: str
    blend: VersionTag | Unknown; script: VersionTag | Unknown; readme: VersionTag | Unknown
    latest: VersionTag | Unknown              # 세 출처가 일치할 때만 확정
    order_unknown: tuple[str, ...]
    files: tuple[tuple[str, str], ...]

class Verdict(StrEnum):
    LATEST = "최신 일치"; STALE = "옛 판"; PINNED = "고정 예외 일치"; PIN_MISMATCH = "고정 예외 불일치"
    NO_VERSION = "판 없음"; ORDER_UNKNOWN = "순서 불명"; CONFLICT = "출처 충돌"
    FAMILY_UNKNOWN = "계열 미지정"

@dataclass(frozen=True)
class RenderCheck:
    path: str; scene: str | None
    version: VersionTag | Unknown; version_from: Literal["접두사", "README"] | None
    verdict: Verdict; compared_to: str | None; diff: int | None
    not_verified: tuple[str, ...] = ("형상 동일성", "실제 치수")
```

**버전 판정 규칙**
- **판 읽기**: 접두사 `^v(\d+)([a-z]*)_`로 읽고, 숫자 부분을 정수로 비교합니다(v10 > v9).
- **접미사가 있는 판**: `explicit_order`가 없으면 다른 판과 비교하지 않고 `순서 불명`으로 둡니다.
- **계열 범위**: 계열은 사용자가 지정한 spec으로만 정합니다. 다른 공간, 낮/밤, 백업 폴더를 합치지 않습니다.
- **판 근거**: 수정 시각은 쓰지 않습니다.
- **출처 충돌**: .blend, 스크립트, README의 최대 판이 서로 다르면 `출처 충돌`입니다.
- **고정 예외(pin) 검증**: 근거 행에 `basis_contains` 문자열이 없거나 근거가 비어 있으면 그 pin을 거부합니다. pin의 scope 밖의 렌더는 최신 판과 비교합니다.
- **읽기 범위**: `os.scandir`, `stat`, README 텍스트 읽기만 합니다. .blend를 열지 않고 Blender도 실행하지 않습니다.

### 2.8 QC 위임 (P1 끝)

```python
class QcRunner(ABC):
    @abstractmethod
    def run(self, cmd: str, args: Sequence[str], *, work_dir: Path, timeout_s: float) -> QcResult: ...

@dataclass(frozen=True)
class QcResult:
    argv: tuple[str, ...]; cwd: str; env_set: Mapping[str, str]
    exit_code: int | None                     # None = 시간 초과
    exit_meaning: str                         # plating-qc 0~5 의미표
    stdout_path: str; stderr_path: str; stdout_is_json: bool
    log_paths: tuple[str, ...]
    produced: tuple[tuple[str, int, str], ...]     # 경로, 크기, SHA-256
    input_dir_changes: tuple[str, ...]
    started: str; ended: str
```

`plating qc` 하위 명령의 인자는 요청서 5절에 기재된 plating-qc 서명을 그대로 따라 `cli.py`에 정의합니다. 이렇게 해야 입력 경로 위치를 알고 절대 경로로 바꿀 수 있습니다.

---

## 3. CLI와 입출력

### 3.1 명령

전역 인자는 하위 명령 앞에 둡니다: `plating [--config PATH] <group> <cmd> ...`

| 명령 | 필수 | 선택 | 단계 | 생성물 |
| --- | --- | --- | --- | --- |
| `cuts inventory` | (설정의 F 또는 `--input`) | `--out` | P0 | inventory.json/md |
| `cuts extract` | `--scene S#NN` | `--cuts ID,...`, `--section-line`, `--table-line`, `--input`, `--out` | P0 | cuts.json/md/csv |
| `prompt skeleton` | `--cuts-json`, `--kind video\|image` | `--plan`, `--clip`, `--out` | P0 | skeleton.md/json, lengths.json, gate.toml(빈 양식) |
| `prompt check` | `--prompt`, `--kind` | `--plan`, `--clip`, `--out` | P0 | check.json/md |
| `gate check` | `--gate`, `--prompt` | `--plan`, `--clip`, `--cuts-json`, `--check-json`, `--refs-json`, `--require-approval`, `--out` | P0 | gate.md/json, cost.json |
| `gate cost` | `--model --mode --resolution --seconds` 또는 `--plan --clip` | `--out` | P0 | 기본은 stdout JSON만(파일 쓰기 없음) |
| `refs check` | `--list` | `--allow-network`, `--thumbs`, `--prompt`, `--out` | P1 | refs.json/md, thumbs/, contact.html |
| `versions check` | `--spec` | `--pins`, `--out` | P1 | versions.json/md |
| `qc probe\|compare\|tiles\|split\|convert` | plating-qc 인자 | `--out` | P1 끝 | qc/<n>/… |

- `--scene`은 `S#04`와 `04`를 받습니다.
- stdout에는 JSON 한 개(명령, 종료 코드, 상태, 결과 폴더, 요약 수치, 소견 수)를 `ensure_ascii=False`, UTF-8로 냅니다. 출력 전에 `sys.stdout.reconfigure(encoding="utf-8")`를 호출합니다.
- 오류는 stderr에 한국어로, 소견 코드를 포함해 냅니다.

**진입점**: `python -m plating_tools`는 항상 동작합니다. `plating` 콘솔 스크립트를 쓰려면 `pyproject.toml`의 `[project.scripts]`에 `plating = "plating_tools.cli:main"`을 추가하고 재설치해야 합니다. 기존 `plating-qc` 항목은 그대로 둡니다. 이 추가와 재설치의 허용 여부는 D3입니다.

### 3.2 최소 `plating.toml`

```toml
# 저장소 루트. 이 파일 안의 상대 경로는 이 파일이 있는 폴더 기준
[paths]
write_root   = '.'                       # 출력은 이 안에서만
output_root  = 'out'                     # write_root 안이어야 함
workflow_dir = 'C:\Users\uicus\Dev\NS-Plating\workflow'
readme       = 'C:\Users\uicus\Dev\NS-Plating\README.md'
handbook     = ''                        # 선택. 비우면 H 대조는 미확인으로 표시
read_only    = ['C:\Users\uicus\Dev\NS-Plating', 'C:\Users\uicus\Dev\dot-handoff', 'D:\', 'G:\']

[docs]
declared_commit = '577c3d4cc607c823603fe1aa0e78fa02773a8e33'   # 선언값, 미검증

[cuts]
input = 'C:\Users\uicus\Dev\dot-handoff\notion_컷표_fetch_2026-11-07T0706Z.md'
expected_sha256 = 'cae22e2f0637d29ebfe1f6e5a7daa973ee8ea72a397373246ecdddf9cfe6dc37'   # 다르면 경고

[qc]            # P1
python = ''     # 비우면 현재 인터프리터
config = ''     # plating-qc --config. 비우면 전달하지 않음
timeout_s = 1800

[network]       # P1. 실제 GET은 --allow-network일 때만
timeout_s = 20
max_redirects = 5
max_bytes = 52428800

[tools]         # P1
ffmpeg = ''     # 비우면 PATH 탐색
```

- TOML 리터럴 문자열(작은따옴표)을 써서 Windows 백슬래시가 이스케이프되지 않게 합니다.
- 규칙 본문과 단가는 넣지 않습니다.
- 기존 `config.toml`과 `plating-qc.toml.example`은 건드리지 않습니다.

### 3.3 사용자 입력 파일

모든 입력 파일에서 빈 문자열은 미결을 뜻합니다. 숫자는 문자열과 TOML 숫자를 모두 받되, 부동소수는 `repr`를 거쳐 Decimal로 바꿉니다.

```toml
# plan.toml
scene = "S#04"
[[clip]]
id = "A"
kind = "video"
cuts = ["S#04-C001"]
segment = ""
gen_seconds = ""
mode = ""                 # new | edit | code
model = ""
resolution = ""           # 480p | 1080p
edit_input_seconds = ""
people = ""               # 있음 | 없음
scene_module = ""
props = []
[clip.staging]
seated = ""
procession = ""
[[clip.character]]
name = ""
group = ""
face = ""                 # close | far | none
basis = ""
[[clip.reference]]
index = 1
role = ""
local_path = ''
url = ''
file_id = ''
sheet = "있음"
preview = "미검수"
candidates = []
candidates_complete = false
candidates_basis = ""
```

```toml
# gate.toml (prompt skeleton이 빈 양식을 만듦. no 1~8)
[[item]]
no = 1
answer = ""               # 예 | 아니오 | 해당 없음
reason = ""
alternative = ""
evidence = []
reviewer = ""
[approval]
quote = ""
where = ""
by = ""
at = ""
prompt_sha256 = ""
```

```toml
# versions.toml / pins.toml (P1)
[[family]]
name = ""
root = ''
blend_glob = "v*_*.blend"
script_glob = "v*_*.py"
readme_glob = "v*_README*"
readme_version_pattern = ""
exclude_dirs = []
explicit_order = []
[[render]]
family = ""
path = ''
scene = ""
version_from = "접두사"   # 접두사 | README
[[pin]]
family = ""
version = ""
scope = []
basis_doc = "W04"
basis_line = 0
basis_contains = ""
approved_by = ""
```

refs check는 plan의 `[[clip.reference]]`와 같은 스키마인 `[[reference]]` 목록을 받습니다.

### 3.4 생성물

| 생성물 | 형식과 내용 |
| --- | --- |
| 실행 폴더 | `<output_root>/<YYYYMMDDTHHMMSS>-<6hex>_<명령>_<라벨>/`. 라벨의 `S#04`는 `S04`로 바꿉니다 |
| `run.json` | 도구 버전, argv, 설정 파일 SHA-256, 입력 지문, 문서 지문(작성 기준 대비 차이 경고), 명시 선택(`--section-line` 등), 시작·종료 시각, 종료 코드, 상태 라벨 |
| md 제목 | `# [검수 대기] S#04 컷표 추출`, `# [검수 대기] S#04 클립 A 프롬프트 골격 (전송본 아님)`, `# [점검 미완료] …` |
| md 공통 끝 섹션 | `## 내가 정한 것`, `## 사용자 답이 필요한 것`, `## 근거`(문서, 행, 표기 분류) |
| cuts.md | 대상 표(순서, 컷, 행 상태, 행 색 원문, 셀 색(필드: 원문→상태), TC, 길이, 필드…), 별도 `## 연결 문맥(생성 대상 아님)`, 제외 후보 위치, 소견 |
| cuts.csv | `utf-8-sig`. 셀 줄바꿈은 따옴표 안의 `\n` |
| skeleton.md | 점검 8줄(원문, 응답 미입력) → 프롬프트 골격 코드 블록 → 길이 표 → 컷표 원문 검수 패널 → 글자 수 → 블록 선택 결정 → 공통 끝 섹션 |
| gate.md | 8줄과 응답·근거·검수 주체 → 그 바로 아래 프롬프트 전문 → 비용(식·단위·모델·문서 판) → 승인 상태 |
| 기타 텍스트 출력 | JSON과 md는 UTF-8(BOM 없음), LF |

### 3.5 종료 코드

plating-qc와 같은 체계입니다.

| 코드 | 의미 | 예 | 결과 공개 |
| --- | --- | --- | --- |
| 0 | 성공 | 소견 없음 또는 INFO만 | 공개 |
| 1 | 경고/검증 실패 | 소견 있음, 점검 미완료, URL 미검사, `--require-approval`인데 승인 없음 | 공개(상태 라벨 포함) |
| 2 | 입력 불량 | 설정·입력 파일 오류, 정본 구조 해석 불가, 선택 모호, 쓰기 금지 경로 지정, convert 실행 요청 | 비공개 |
| 3 | 출력 충돌 | 대상 폴더나 파일이 이미 있음 | 비공개, 기존 내용 불변 |
| 4 | 실행 파일/모듈 없음 | ffmpeg 없음(`--thumbs`), plating-qc 실행 불가, P1 모듈 없음 | 비공개 |
| 5 | 읽기·쓰기·디코딩 실패 | QC 시간 초과 포함 | 비공개, `_failed/`에 기록 |

`plating qc`는 plating-qc의 종료 코드를 그대로 전달합니다. 종료 1을 성공으로 바꾸지 않으며, 그때의 생성물도 보존하고 보고합니다. 우리 쪽 실패(경로 거부, 시간 초과)는 우리 코드로 냅니다.

### 3.6 충돌·중간 실패·재실행

1. **실행 전 검사**: 출력 경로를 해석하고 쓰기 허용 여부를 검사합니다(3.8). 최종 폴더가 이미 있으면 종료 3입니다. `--force`는 없습니다.
2. **staging**: 최종 폴더와 같은 부모 아래에 `.staging-<run_id>`를 만들고, 그 안에만 씁니다.
3. **공개**: 완료되면 `os.rename(staging, final)`로 공개합니다. Windows에서는 대상이 있으면 실패하므로 경합 중의 덮어쓰기도 막힙니다. 공개 직전에 다시 한 번 존재 여부를 검사합니다.
4. **실패 격리**: 실패하면 `<output_root>/_failed/<run_id>_<명령>/`로 옮기고 `run.json`에 `status: failed`와 오류를 기록합니다. 최종 이름으로는 절대 공개하지 않습니다.
5. **실행 폴더 생성 전 실패**(설정 오류 등): stderr에만 출력하고 파일을 만들지 않습니다.
6. **재실행**: 항상 새 폴더를 만듭니다. 이전 결과를 읽어 갱신하지 않습니다.
7. **원본 불변**: 입력 파일은 `rb`로만 엽니다. 노션 컷표, 기존 프롬프트, W 문서, H는 수정하지 않습니다.

### 3.7 자동 검사와 사람 확인

| 기능 | 자동 검사 | 사람 확인 |
| --- | --- | --- |
| 컷표 | 섹션·표 선택, 열 대응, 색 원문과 상태 매핑, ID·TC·길이 형식, 중복·결손, 색 유실 집계 | 수정본 후보 선택이 모호할 때의 선택, 대상 컷 범위, 문맥의 연출 의미 |
| 골격 | 섹션 순서, 고정 블록 원문 삽입과 동일성, 근거가 있는 블록 선택, 길이 표 산술, 글자 수, `@imageN` 대조, 옛 표기, 충돌 표시 | 클립 분할·생성 길이, 영어 문장, Subtext, End state, 미결 블록 선택, 인물 분류 |
| 점검 8줄 | 아래 표 참조. 응답은 자동으로 채우지 않음 | 8개 응답, 근거, 검수 주체 |
| 승인 | 증거 필드 존재, W02 §2 어휘 일치, 프롬프트 SHA-256 결속 | 승인이 실제로 생성 승인인지 |
| 비용 | 문서 단가로 계산, 대안 표시, 단위 분리 | 해상도 선택, 실제 잔액과 요금 |
| 레퍼런스 | HTTPS 응답, Content-Type, 매직 바이트, 해시 대응, 번호 연속성, 장수 권고, 시트 없음 표시 | 역할 적합성, 썸네일 육안 검수, 후보 전수 선언, 최대 원본 판단 |
| 버전 | 판 해석, 계열 내 최댓값, 출처 충돌, pin 근거 행 검증 | 계열 정의, 접미사 순서, pin 승인, 치수·형상 |
| QC | 실행 기록, 종료 코드, 생성물, 경로 격리 | 비교 결과 해석 |

점검 8항목별 분담:

| 항목 | 기계 소견 | 사람 판단 |
| --- | --- | --- |
| 1 edit/새 생성/코드 합성 | plan `mode` 값의 존재·허용값, 비용표에 해당 모드가 있는지 | 판단 자체 |
| 2 분할 필요 | 레퍼런스 6장 이상, 컷 수, (문서에 허용 길이가 있을 때) 길이 범위 | 분할 결정 |
| 3 중요 소품 시트 | plan `props` 대비 시트 역할 레퍼런스 존재, `시트 없음/만들어야 함` | 시트 적합성 |
| 4 컷표 문장 일치 | 계획 컷 ID가 추출본에 존재, removed 행 미포함, cuts.json의 F 지문과 현재 F 지문 일치(W08 21·84) | 문장 대응 |
| 5 원인 다음 반응 | TIMELINE 슬롯 순서가 원문 컷 순서와 같은지 | 인과 순서(W08 47~49) |
| 6 앞뒤 연결 | 문맥 컷 추출 존재 | 연결 판단 |
| 7 가장 큰 원본 | refs.json의 해상도·크기·해시 기록, `최대 원본 미확인` 여부. refs.json이 없으면 "레퍼런스 검사 결과 없음" | 원본 확인 |
| 8 해상도·비용 | 비용 계산 전부, 1080p 대안 | 결정 |

### 3.8 경로와 인코딩

**경로 해석**
- CLI 인자의 상대 경로는 현재 작업 폴더 기준이고, 설정 파일 안의 상대 경로는 설정 파일 폴더 기준입니다.
- 모든 경로는 `Path.resolve()`로 해석합니다(Windows에서 symlink와 junction 해석).
- 아직 없는 출력 경로는 가장 가까운 기존 상위 폴더를 해석한 뒤 나머지를 붙입니다.
- 비교는 `os.path.normcase` 후 `is_relative_to`로 합니다.
- staging 폴더를 만든 직후 다시 해석해 검사합니다(경합 방지).

**쓰기 허용 조건**: 해석된 출력 경로가 다음을 모두 만족해야 합니다.
- `write_root` 안에 있음
- `read_only` 루트, 이번 실행의 모든 입력 파일의 부모 폴더, `.git`의 안이 아님
- 경로 구성요소 중 대소문자 무시로 정확히 `raw`인 폴더가 없음

위반하면 종료 2입니다. 로그, 캐시, 실패 임시 파일, QC 위임 출력도 같은 규칙을 따릅니다.

**인코딩과 줄**
- 텍스트는 `utf-8-sig`로 읽습니다. 줄 분리는 `\n` 기준으로만 하고 끝의 `\r`을 제거합니다. `splitlines`는 U+2028 등에서도 나뉘어 행 번호가 어긋나므로 쓰지 않습니다.
- 원문의 개행 방식(CRLF/LF)은 지문과 함께 기록합니다.

**긴 경로**: 260자를 넘는 경로는 시스템 설정을 바꾸지 않습니다. 오류가 나면 종료 5와 함께 경로 길이를 안내합니다.

---

## 4. 테스트 계획과 구현 순서

### 4.1 fixture 구분

| 등급 | 내용 | 저장소 커밋 |
| --- | --- | --- |
| T1 합성 | F와 W의 문법만 흉내 낸 중립 내용(예 "가짜 화면 1"). 파일 머리에 `SYNTH` 표기 | 함 |
| T2 실제 참조 | 테스트가 환경 변수 `PLATING_TOOLS_F`, `PLATING_TOOLS_WORKFLOW_DIR`의 원본을 읽기 전용으로 열어 필요한 행만 잘라 사용. F는 SHA-256 `cae22e2f…`가 일치할 때만 실행하고, 없거나 다르면 skip 사유 기록. 복사 없음 | 하지 않음 |
| T3 실제 발췌 커밋 | 사용자가 승인한 경우에만 | 사용자 결정(I18) |

**공통 테스트 장치**
- 모든 테스트의 기반 클래스에서 `socket.create_connection`과 `socket.socket.connect`를 실패하도록 패치합니다.
- ffmpeg와 plating-qc는 가짜 `ImageTool`과 `QcRunner`로 대체합니다. 유료 API는 호출하지 않습니다.
- 테스트 파일은 `tests/test_pt_*.py`이며 `unittest`로 실행합니다. 기존 plating-qc 테스트와 섞이지 않습니다.
- 실제 S#01 샘플은 이후 구현 시 T2로 실행합니다. 이번에는 실행하지 않았습니다.

### 4.2 P0 (11/8): 컷표 추출

| ID | 검사 | 등급 | 합격 조건 |
| --- | --- | --- | --- |
| C1 | 토글/h3 혼재 | T2 | S#01(22), S#02(388), S#10(2888), S#11(3143)이 toggle_h3이고, S#03~09, S#12~14가 md_h3. 4881의 녹음 대본은 비씬 |
| C2 | span 제목 | T2(2615, 3458) + T1 | `S#09 수정`, `S#12 수정`으로 식별. discussion-urls 원문과 행·열 보존 |
| C3 | span 컷 ID | T2(722) | `S#02-C016-1` 식별, 주석 보존 |
| C4 | 7열/6열/합쳐진 열 | T2(37~59, 400~419, 1227~1246) | header_map이 2.2 대응표와 일치. S#02 dialogue는 absent, S#04 dialogue_sound는 present이고 dialogue와 sound는 absent |
| C5 | S#01-C001 | T2(22~82) | TC `00:00–00:04`, 길이 원문 `4s`, 행 done, 대사 셀 red_bg→대사 필드 todo, 행 done 유지, 사운드와 대사 별도 |
| C6 | S#01-C003 | T2(102~124) | 행 red→todo, 컷 ID 셀 green_bg 원문 보존(요소 상태 unknown), 행 상태 불변 |
| C7 | S#04-C001 | T2(1216~1266) | TC `00:00.0–02.0` → 0.0~2.0, 길이 `2.0s`, 행 unknown |
| C8 | 색 집계와 유실 | T2 inventory | tr: green 5, red 79, gray 2 / td: green 155, red 9, gray 6 / callout: gray 2 / span: yellow 1(2889). 원문 정규식 집계와 파싱 집계의 차이 0 |
| C9 | 제목 yellow | T2(2889) | S#10 title_colors가 revise이고, S#10 행 상태 집계는 변하지 않음 |
| C10 | 분할 ID | T2(171, 194, 722, 742, 762, 862) | ID 문자열과 원문 순서 유지. `S#02-C016-1~3`을 지정하면 종료 2(확장하지 않음) |
| C11 | 녹음 대본 제외 | T2(4881, 4922~) | S#14 추출에 9열 표가 없고, inventory에는 비씬 표로만 나옴 |
| C12 | 문맥 | T2 | S#04 추출에서 S#03 마지막 행과 S#05 첫 행이 context이며 targets에 없음. S#01의 prev는 "첫 씬이라 없음" |
| C13 | 수정본 우선 | T1 | `S#05`와 `S#05 수정`이 공존하면 수정본 선택, 원본은 rejected에 위치만 |
| C14 | 후보 중복 | T1 | `S#05 수정`이 토글과 h3에 하나씩 있으면 종료 2, 후보 줄 보고, 결과 폴더 없음 |
| C15 | 중첩 표 | T1 | 중첩 토글 안의 표는 쓰지 않고 CT015 |
| C16 | 중복 컷 ID | T1 | CT005, 종료 1, 순서 유지 |
| C17 | 깨진 표 | T1 | `</table>` 누락, 셀 수 불일치, 열 이름 중복 → CT004 또는 종료 2 |
| C18 | 모르는 열, 빈 셀, br | T1 | extra 원문 보존, empty와 absent 구분, `<br />`→`\n`, raw_html 유지 |
| C19 | TC·길이 실패 | T1 | 하이픈, 시:분:초, 상속 후 끝<시작, `4초` → CT006/CT007, 원문 유지 |
| C20 | 미정의 색, 무색 행 | T1 | blue_bg는 unknown + CT009, 무색 행은 unknown |
| C21 | removed 행 | T1 + T2(inventory의 gray tr 2개) | 출력에 남고 `excluded_from_generation=true`. 계획에 넣으면 skeleton ERROR |
| C22 | Windows 입력 | T1 | 공백과 한글이 든 경로, CRLF·LF·BOM에서 같은 결과와 같은 행 번호 |

C1~C12는 실제 관찰을 근거로 한 테스트이고, C13~C20의 중첩, 중복, 결손은 합성 실패 사례입니다. inventory에서 F에 같은 사례가 발견되면 T2 테스트를 추가합니다.

### 4.3 P0 (11/8): 프롬프트 골격과 글자 수

| ID | 검사 | 등급 | 합격 조건 |
| --- | --- | --- | --- |
| P1 | 블록 원문 | T2 W10 | AVOID가 W10 35행 문자열과 바이트 단위로 동일. 근거로 W10 §4·35행, 파일 단위 예외, SHA-256 기록 |
| P2 | 구조 변경 | T1 합성 W | 제목 변경, 같은 제목 2개, 펜스 개수 변화, 펜스 미종결 → 종료 2, 문서와 행 표시, 대체 없음 |
| P3 | 섹션 순서 | T2 W05 | 34~41의 8개 섹션 순서와 일치 |
| P4 | 계획 없음 | T1 | 길이 표 전부 미확인, 균등 배분 없음, 영어 문장 없음(자리표시만) |
| P5 | 계획 있음 | T1 | 모든 값이 해석된 경우만 여유 계산. 컷표 길이와 생성 길이가 각각 보존됨 |
| P6 | 블록 선택 | T1 | 사람 없음 또는 얼굴이 멀면 FACE RULE·EYES 제외. 진우·흰토끼·상류층에는 하층민 블록 제외. 메타데이터 없음이면 미결이고 "적용 완료" 표시 없음 |
| P7 | 충돌 모듈 | T2 W10 144~146 + W11 49 | 해당 SCENE 모듈 선택 시 충돌 보고, 원문 유지, 슬롯 미결 |
| P8 | 이미지 경계 | T1 | 3000은 within, 3001은 over(종료 1), 고정 블록은 잘리지 않음. CRLF 입력을 LF로 계산. BMP 밖 문자로 UTF-16만 초과하면 over_by_utf16_only |
| P9 | 영상 상한 | T1 | `상한 미확인`, 길이만 기록 |
| P10 | 완성본 검사 | T1 | 블록 한 글자 변형 → 원문 불일치. 자리표시 남음 → not_final. `@[이미지 1](image_1)` → 오류. 미등록 `@image3` → 오류 |
| P11 | 자리표시 충돌 | T1 | 정본 블록에 `{{`가 있으면 종료 2 |
| P12 | 상태 표시 | T1 | 제목에 `[검수 대기]`와 `(전송본 아님)`. `내가 정한 것`과 `사용자 답이 필요한 것`이 분리됨 |

### 4.4 P0 (11/8): 게이트와 비용

| ID | 검사 | 등급 | 합격 조건 |
| --- | --- | --- | --- |
| G1 | 8줄 원문 | T2 W02 | 8개를 원문 그대로, 프롬프트 바로 위에 배치 |
| G2 | 개수 변경 | T1 | 7개 또는 9개면 종료 2 |
| G3 | 미입력·미확인 | T1 | 미완료, 종료 1 |
| G4 | 사유 요건 | T1 | 대안 없는 아니오, 이유 없는 해당 없음은 미완료 |
| G5 | 기계 통과 ≠ 예 | T1 | 기계 소견 없음 + 응답 없음 → 미완료. 자동 `예` 없음 |
| G6 | 소견 충돌 | T1 | 계획에 removed 컷이 있는데 4번이 `예`면 CONTRADICTED |
| G7 | 승인 분리 | T1 | 증거 없음, 다른 SHA-256, "프롬프트 준비" 인용 → 각각 없음, 불일치, 어휘 불명확. 점검 완료 라벨과 승인 라벨은 별개 |
| G8 | 4초 480p 새 생성 | T2 W07 | 80 Crons. 식, 단위, 모델, 문서 SHA-256 기록 |
| G9 | 1.5초 1080p edit | T2 W07 | 220 Crons(입력 길이를 올림. 생성 길이 규칙을 쓰지 않음) |
| G10 | 1080p 새 생성 | T2 W07·W06 | 요청안 324 Crons, 대안 480p 80 Crons, Topaz는 Higgsfield 크레딧 합계로 별도 |
| G11 | 모름 | T1 | 미지 모델, edit 480p, 3초 새 생성, 4.5초 새 생성 → 숫자 없음, 미확인 + 소견 |
| G12 | 비용표 구조 변경 | T1 | 행 패턴 불일치나 단위 문자열 변경 → 종료 2 |
| G13 | 컷표 최신성 | T1 | cuts.json의 F 지문이 현재 F와 다르면 4번에 ERROR 소견 |

### 4.5 P1 (11/9): 레퍼런스와 썸네일

모두 가짜 `HttpFetcher`와 `ImageTool`을 씁니다(R16 제외).

| ID | 검사 | 합격 조건 |
| --- | --- | --- |
| R1 | 정상 | 200, image/jpeg, 유효한 헤더 → 성공, 크기와 SHA-256. 로컬과 같은 바이트면 `바이트 동일` |
| R2 | 확인 페이지 | 200, text/html → HTML_PAGE |
| R3 | 403, 404 | HTTP_STATUS |
| R4 | timeout | TIMEOUT |
| R5 | redirect | 한도 이내 성공, 한도+1 → TOO_MANY_REDIRECTS, https→http → NON_HTTPS |
| R6 | 거짓 Content-Type | image/png인데 본문이 HTML → NOT_IMAGE |
| R7 | 크기 한도 | 한도+1 바이트 → TOO_LARGE, 대응 미확인 |
| R8 | 크기 같고 해시 다름 | `불일치`. 동일성을 확정하지 않음 |
| R9 | 번호 | 1, 2, 4 / 중복 / 프롬프트의 `@image5` → 오류 |
| R10 | 장수 | 5장은 안전 권고, 6장은 분할 검토 사유(하드 실패 아님) |
| R11 | 시트·검수 | `시트 없음/만들어야 함`, `미검수` 표시 유지 |
| R12 | 최대 원본 | 전수 선언이 없으면 미확인. 선언, 근거, 최대 조건을 모두 만족하면 확인됨 |
| R13 | 축소본 입력 | 로컬 경로가 thumbs/ 출력 안이면 ERROR(W08 24) |
| R14 | 썸네일 | contact.html에 번호, 파일명, 역할. 기존 파일 덮어쓰기 없음. ffmpeg 없이 `--thumbs` → 종료 4, 결과 없음 |
| R15 | 네트워크 기본 차단 | `--allow-network`가 없으면 GET 0회, URL 미확인, 종료 1 |
| R16 | 실제 GET | 사용자 PC에서 수동으로만 수행. 샌드박스와 자동 테스트에서는 하지 않음 |

### 4.6 P1 (11/9): 블록아웃 버전

임시 폴더에 합성 파일 이름을 만들어 테스트합니다.

| ID | 검사 | 합격 조건 |
| --- | --- | --- |
| V1 | v9/v10 | v10이 최신(문자열 정렬이 아님) |
| V2 | 판 없음 | 접두사도 README 기준도 없으면 NO_VERSION, 통과 아님 |
| V3 | 옛 판 | v57 렌더 대 v58 → STALE, 차이 1 |
| V4 | S#10 예외 | pin(v50, S#10, W04 135 근거) → S#10 렌더 v50은 PINNED, S#11 렌더 v50은 STALE |
| V5 | 근거 없는 pin | 근거가 비었거나 근거 행에 문자열이 없으면 pin 거부 |
| V6 | v2i | v2와 v2i → ORDER_UNKNOWN. explicit_order가 있으면 그 순서 |
| V7 | 계열 분리 | 낮/밤, 백업 폴더를 합치지 않음 |
| V8 | 출처 충돌 | .blend v58, README v57 → CONFLICT |
| V9 | 읽기 전용 | 스캔 전후의 목록과 mtime이 같음 |
| V10 | 미검증 표시 | 모든 결과에 "형상 동일성, 실제 치수 미검증" |

### 4.7 QC 위임과 공통 안전

| ID | 검사 | 합격 조건 |
| --- | --- | --- |
| Q1 | argv | 리스트 형태, `shell=False`, `-m plating_qc`. `plating_qc` import 없음(AST 검사) |
| Q2 | 로그 위치 | `--log`와 `PLATING_QC_LOG_DIR`가 작업 폴더 안 |
| Q3 | 종료 1 보존 | 가짜 종료 1 + 생성물 → 종료 1 그대로, 생성물 목록 보고 |
| Q4 | 종료 4·5, 시간 초과 | 의미표대로 기록. 시간 초과는 종료 5 |
| Q5 | convert | `--dry-run`이 없으면 종료 2 |
| Q6 | 출력 인자 | 사용자가 `--out`, `--log`, `--config`를 주면 거부 |
| Q7 | 수동 통합(선택) | 사용자 PC에서 실제 `probe` 1회. 자동 테스트 아님 |
| S1 | raw 거부 | `…\raw\…` 출력 → 종료 2 |
| S2 | junction | Windows에서 `_winapi.CreateJunction`으로 입력 루트를 가리키는 경로를 만들면 거부. 다른 OS는 skip |
| S3 | 덮어쓰기 | 기존 폴더 → 종료 3, 내용 불변 |
| S4 | 중간 실패 | 쓰기 중 예외 주입 → 최종 이름의 폴더 없음, `_failed/`에 기록 |
| S5 | 재실행 | 같은 입력으로 2회 실행하면 서로 다른 새 폴더 |
| S6 | 읽기 전용 루트 | dot-handoff, NS-Plating, D:, G:로의 출력 거부 |
| S7 | P0 독립 | 임시 사본에서 refs/, versions/, qc.py를 삭제한 뒤 `python -m plating_tools --help`와 cuts·prompt·gate 정상 실행. refs는 종료 4 |
| S8 | import 정적 검사 | P0 모듈에 refs, versions, qc, 서드파티 import 없음 |
| S9 | 네트워크 0회 | 전체 테스트에서 소켓 연결 시도 0 |
| S10 | 문서는 데이터 | 합성 W에 명령문과 경로를 넣어도 subprocess 호출 0, 파일 열기 0 |

### 4.8 W08 실패 사례와 테스트 대응

| W08 | 방지 조건 | 테스트 |
| --- | --- | --- |
| 24 보기용 축소본 입력 | thumbs/ 경로 입력 거부, 썸네일은 보기용 표기 | R13, R14 |
| 47~49 컷표 문장 미확인, 인과 역순 | 4·5번 사람 검수 필수, 슬롯 순서 대조 | G5, G6, P4 |
| 38 이미지 과다 | 6장 이상이면 분할 검토 사유 | R10 |
| 21, 84 이름만 믿은 자료, 옛 버전, 상태 표시 누락 | 해시 대응, 버전 판정, 컷표 지문, 제목 상태 라벨 | R8, V1~V8, G13, P12 |

### 4.9 구현 순서

**P0 (11/8)**
1. 공통 모듈(errors, textio, paths, output, config, model)과 S1~S6
2. `cuts inventory`. 사용자 PC에서 F로 실행해 열 이름 목록, 제목 형식, 색 집계를 C8 기대값과 대조합니다. 결과에 따라 I7, I8에 답을 받습니다.
3. `cuts extract`와 C1~C22
4. 원문을 읽고 앵커 명세를 작성합니다(W10, W05, W02). 이어서 `prompt skeleton`, `prompt check`, P1~P12
5. W07, W06 앵커를 작성하고 `gate check`, `gate cost`, G1~G13
6. S7~S10
7. 시간이 부족할 때 미룰 수 있는 것: cuts.csv, inventory.md, `gate cost`의 `--out`

**P1 (11/9)**
1. refs: fetch(가짜) → 헤더 판독 → resolve → check → 썸네일(D1 결정 후). R1~R15
2. versions와 V1~V10(실제 폴더 경로는 I14 답 이후)
3. qc 위임과 Q1~Q6. 시간이 부족하면 보류하고 plating-qc를 직접 실행하는 것으로 대체할 수 있습니다.

---

## 5. 미결 질문과 가정

### 5.1 설계 확정 전에 필요한 답 (답에 따라 구조가 바뀜)

| ID | 질문 | 답이 없을 때의 진행 |
| --- | --- | --- |
| D1 | 썸네일과 디코딩 확인을 위해 `plating_tools`가 ffmpeg 실행 파일을 plating-qc를 거치지 않고 직접 argv로 호출해도 되는가. 불가하면 (a) plating-qc의 tiles나 probe가 정지 이미지를 받는지 확인(구조 동결로 추가 불가), (b) 이미지 라이브러리 설치 승인, (c) 썸네일 없이 헤더 판독만 중 하나를 택해야 함 | 직접 호출로 설계, ffmpeg가 없으면 종료 4 |
| D2 | 이미지 프롬프트도 P0 골격 생성 대상인가. 대상이라면 이미지 프롬프트 섹션 순서의 정본 위치(W03? H §5-3~5-6?) | 이미지는 `prompt check`(원문 동일성, 3000자, @imageN)만. 골격은 영상만 |
| D3 | `plating` 콘솔 스크립트를 위해 `pyproject.toml`에 진입점을 추가하고 재설치하는 것을 이번에 허용하는가. 빌드 백엔드와 패키지 탐색 설정(현재 발췌에 없음)도 필요 | `python -m plating_tools`를 공식 진입점으로. 설치 방식에 따라 `PYTHONPATH=src` 안내 |

### 5.2 구현 전에 필요한 답

| ID | 질문 |
| --- | --- |
| I1 | 원문 범위. 구현자가 NS-Plating HEAD 577c3d4를 직접 읽을 수 있으면 불필요합니다: W02 §2 24~28, 43, §4 68~81 / W05 16, 34~41, §4 63~80, §5 82~103 / W06 §2, 19 / W07 §1 5~19, 24, 31 / W10 전문 / W11 전문 / W04 §1~3, §10 130~137 / README 5~13. 앵커 명세는 이 원문으로만 작성합니다 |
| I2 | 이미지 3000자 문구가 있는 정확한 문서와 행 |
| I3 | W07의 "최소 4초"가 허용 최소인지 과금 최소인지. 새 생성의 최대 길이와 정수 초 요구의 문서 근거 행 |
| I4 | Topaz 5 Higgsfield 크레딧의 적용 단위(클립당, 초당, 작업당). 없으면 대안 행은 "단위 미확인" |
| I5 | 셀·span의 green_bg(셀 155), gray_bg(셀 6), span의 red_bg가 요소 상태로 무엇을 뜻하는가. 답이 오기 전에는 원문을 보존하고 요소 상태는 unknown |
| I6 | 요청서가 S#01-C001을 "대사·사운드 새 작업"으로 설명한 것이 사운드 필드에도 todo를 붙이라는 뜻인가. 현재 설계는 색이 있는 대사 필드에만 todo |
| I7 | 문맥의 "앞 씬/뒤 씬" 기준이 씬 번호 ±1인지 문서 순서인지. 앞 씬의 마지막 행이 removed일 때 마지막 비제거 행을 함께 내는 처리로 충분한지 |
| I8 | inventory에서 `S#NN 수정` 이외의 수정 표기나 대응표에 없는 열 이름(편집 메모 등)이 나오면 그 처리와 표준 필드 지정 |
| I9 | W02 §2 어휘 중 생성 승인으로 인정하는 것, 승인 증거 형식(인용문, 위치, 날짜), 프롬프트 SHA-256 결속의 수용 여부 |
| I10 | 사람 검수 주체의 표기 기준(이름, 역할) |
| I11 | 블록 선택에 쓸 인물 분류(진우, 흰토끼, 상류층, 하층민, 아이)의 정본 위치. 아니면 계획 파일에 사람이 적는 방식 유지 |
| I12 | W05 16행 "여유"의 정의 |
| I13 | 레퍼런스 3~5장 권고 문구의 정본 위치(W03 §2와 W05 §4 중 어디인지) |
| I14 | 블록아웃 대상 계열의 실제 폴더, 낮/밤·백업 구분 규칙, README의 버전 표기 형식, 렌더와 시트 위치, v2i의 의미(v2의 후속인지 별도 계열인지) |
| I15 | W04 §10 고정 예외를 pins 파일로 옮길 때의 승인자와 적용 범위(S#10 v50이 S#10 렌더 전체에 적용되는지) |
| I16 | plating-qc의 현재 실행 방식(어느 python인지), `--config` 필요 여부, `convert`의 출력 위치 규칙, probe의 정지 이미지 지원 여부 |
| I17 | 출력 루트 `out/`을 `.gitignore`에 추가하는 변경의 허용 여부. 출력에 F 원문 일부가 들어감 |
| I18 | 실제 F 발췌 fixture의 커밋 여부. 답 전에는 커밋하지 않고 T2(읽기 전용 참조)만 사용 |
| I19 | HTTP 기본 한도(timeout 20초, redirect 5회, 응답 50MB)의 수용 여부. Drive 원본이 50MB를 넘을 수 있는지 |

### 5.3 보류 가능한 질문

| ID | 질문 |
| --- | --- |
| L1 | 노션 API를 직접 읽는 `CutTableSource` 구현 시기 |
| L2 | Drive 검색 결과를 `ReferenceResolver`로 받을 형식 |
| L3 | 사용자 확정 색 규칙을 워크플로우 문서에 기록할지(이 툴킷은 문서를 고치지 않음) |
| L4 | 서비스의 실제 글자 수 계산 방식(grapheme 등)과 영상 프롬프트 상한 |
| L5 | CSV의 BOM 포함 여부 |
| L6 | 파일 ID만 있을 때 W07 24행 형식으로 URL을 파생할지(현재는 파생하지 않음) |
| L7 | QC 위임 명령을 실제로 쓸지, plating-qc 직접 실행으로 충분한지 |
| L8 | 비고정 섹션의 라벨 줄 형식과 섹션 구분자(현재는 라벨을 넣지 않고 빈 줄 하나) |

### 5.4 이 설계가 둔 가정 (근거 없음, inventory나 원문으로 확인할 것)

| ID | 가정 |
| --- | --- |
| A1 | F의 씬 섹션 경계는 2.2의 규칙(최상위 토글 짝, 다음 h1~h3 직전)으로 정해진다 |
| A2 | F의 표에는 colspan과 rowspan이 없다 |
| A3 | 색 속성은 tr, td, span, callout의 `color="…"` 형식뿐이다 |
| A4 | 컷표는 머리 첫 칸 `컷`과 `TC` 열로 판별할 수 있다 |
| A5 | TC 끝값의 분 생략은 시작의 분을 상속한다는 뜻이다 |
| A6 | W10의 각 블록은 독립된 코드 펜스 안에 있고, 제목 경로로 유일하게 찾을 수 있다 |
| A7 | W02 §4의 8줄은 번호 목록이나 8개의 구분 가능한 줄이다 |
| A8 | W07 §1의 비용은 모델, 해상도, 단가를 행 단위 패턴으로 추출할 수 있다 |
| A9 | 사용자 PC에 정지 WebP 디코딩을 지원하는 ffmpeg가 있다(plating-qc의 ffmpeg 백엔드 존재로부터의 추정) |
| A10 | F의 머리(1~10행)에서 제목과 fetch 시각을 읽을 수 있다. 못 읽으면 기록을 생략한다 |
| A11 | 블록아웃의 README도 `vNN_` 접두사로 판이 매겨져 있다(W04 18~19행 문구로부터의 추정) |

### 5.5 이 답변에서 내가 정한 것 (변경 가능)

- **종료 코드와 수치**: plating-qc의 0~5 종료 코드를 재사용합니다. 계산은 Decimal로 합니다.
- **글자 수**: LF 정규화 후 코드 포인트를 주 기준으로 하고 UTF-16과 UTF-8을 병기합니다. 자리표시는 `{{미결: …}}`입니다.
- **네트워크**: 기본으로 끄고 `--allow-network`일 때만 씁니다.
- **출력**: staging 후 rename으로 공개하고, 실패는 `_failed/`로 격리합니다. 실행 폴더 이름은 `<시각>-<hex>_<명령>_<라벨>` 형식입니다.
- **인코딩**: 출력은 UTF-8(BOM 없음)과 LF를 쓰고, CSV만 `utf-8-sig`입니다.
- **색**: 셀·span의 green과 gray는 요소 상태 unknown이 기본입니다.
- **레퍼런스**: URL을 파생하지 않습니다.
- **승인**: 승인 증거를 프롬프트 SHA-256과 결속합니다.
- **QC 위임**: `convert`는 dry-run만 허용합니다.
- **fixture**: T1·T2·T3 3등급으로 운용합니다.
- **프롬프트 본문**: 컷표 한국어 원문은 검수 패널에만 두고 본문에는 넣지 않습니다.

이 답변 이후의 외부 저장, API 호출, push, 구현은 자동으로 이어 가지 않습니다.