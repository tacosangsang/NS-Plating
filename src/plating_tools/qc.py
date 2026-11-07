"""QC를 별도 프로세스로 실행한다. 내부 패키지 import·원본 변환은 금지한다."""
import json
import math
import os
import shutil
import subprocess
import sys
import tomllib
from abc import ABC, abstractmethod
from argparse import Namespace
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, replace
from hashlib import sha256
from pathlib import Path
from typing import Final

from . import __version__
from .config import Config
from .errors import InputError, ToolError, Unavailable
from .output import RunDir, new_target, now
from .textio import read_document

EXIT_MEANINGS: Final = {0: "성공", 1: "경고/검증 실패", 2: "입력 불량", 3: "출력 충돌", 4: "실행 파일 없음/미지원", 5: "디코딩/저장 실패"}


@dataclass(frozen=True, slots=True)
class QcResult:
    argv: tuple[str, ...]
    cwd: str
    env_set: Mapping[str, str]
    exit_code: int | None
    exit_meaning: str
    stdout_path: str
    stderr_path: str
    stdout_is_json: bool
    log_paths: tuple[str, ...]
    produced: tuple[tuple[str, int, str], ...]
    input_dir_changes: tuple[str, ...]
    started: str
    ended: str


class QcRunner(ABC):
    @abstractmethod
    def run(self, cmd: str, args: Sequence[str], *, work_dir: Path, timeout_s: float) -> QcResult: ...


def source_paths(cmd: str, args: Sequence[str]) -> tuple[Path, ...]:
    count = {"probe": len(args), "compare": 2, "tiles": 1, "split": 1, "convert": 1}.get(cmd)
    if count is None:
        raise InputError(f"QC 허용 명령 아님: {cmd}")
    paths = []
    for arg in args[:count]:
        if arg.startswith("--"):
            break
        paths.append(Path(arg).resolve())
    if not paths or (cmd == "compare" and len(paths) != 2):
        raise InputError("QC 입력 파일 필요")
    return tuple(paths)


def snapshot(directories: tuple[Path, ...]) -> dict[str, tuple[int, int]]:
    result = {}
    for directory in directories:
        for path in directory.iterdir():
            stat = path.stat()
            result[str(path)] = (stat.st_size, stat.st_mtime_ns)
    return result


def result_code(result: QcResult) -> int:
    if result.exit_code is None:
        return 5
    if result.exit_meaning == EXIT_MEANINGS[4]:
        return 4
    return result.exit_code


class SubprocessQcRunner(QcRunner):
    def __init__(self, python: str = sys.executable, config: Path | None = None):
        self.python = python
        self.config = config

    def run(self, cmd: str, args: Sequence[str], *, work_dir: Path, timeout_s: float) -> QcResult:
        if any(arg.split("=", 1)[0] in {"--out", "--log", "--config"} for arg in args):
            raise InputError("QC 인자 --out/--log/--config 직접 전달 금지")
        if cmd == "convert" and "--dry-run" not in args:
            raise InputError("QC convert는 --dry-run 필수")
        sources = source_paths(cmd, args)
        directories = tuple(dict.fromkeys(p.parent for p in sources))
        before = snapshot(directories)
        work_dir = work_dir.resolve()
        work_dir.mkdir(parents=True, exist_ok=False)
        log = work_dir / "log"
        log.mkdir()
        argv = [self.python, "-m", "plating_qc"]
        if self.config:
            argv += ["--config", str(self.config)]
        argv += ["--log", str(log / "qc.log"), cmd, *(str(p) for p in sources), *args[len(sources):]]
        if cmd in {"compare", "tiles", "split"}:
            argv += ["--out", str(work_dir / "out")]
        overrides = {"PLATING_QC_LOG_DIR": str(log), "PYTHONIOENCODING": "utf-8"}
        started = now()
        try:
            process = subprocess.run(argv, cwd=work_dir, env={**os.environ, **overrides}, shell=False, capture_output=True, timeout=timeout_s, check=False)
            code, stdout, stderr = process.returncode, process.stdout, process.stderr
        except subprocess.TimeoutExpired as exc:
            code, stdout, stderr = None, exc.output or b"", exc.stderr or b""
        except FileNotFoundError as exc:
            raise Unavailable(f"QC Python 실행 불가: {self.python}") from exc
        stdout_path, stderr_path = work_dir / "stdout.bin", work_dir / "stderr.bin"
        with stdout_path.open("xb") as stream:
            stream.write(stdout)
        with stderr_path.open("xb") as stream:
            stream.write(stderr)
        try:
            json.loads(stdout)
            is_json = True
        except (ValueError, UnicodeDecodeError):
            is_json = False
        after = snapshot(directories)
        changes = tuple(sorted(p for p in before.keys() | after.keys() if before.get(p) != after.get(p)))
        produced = []
        for path in sorted(work_dir.rglob("*")):
            if path.is_file():
                data = path.read_bytes()
                produced.append((path.relative_to(work_dir).as_posix(), len(data), sha256(data).hexdigest()))
        meaning = "시간 초과(종료 5)" if code is None else EXIT_MEANINGS.get(code, f"하위 프로세스 종료 {code}")
        if code == 1 and b"No module named plating_qc" in stderr:
            meaning = EXIT_MEANINGS[4]
        return QcResult(tuple(argv), str(work_dir), overrides, code, meaning, str(stdout_path), str(stderr_path), is_json,
                        tuple(p.relative_to(work_dir).as_posix() for p in sorted(log.rglob("*")) if p.is_file()), tuple(produced), changes, started, now())


class QcFailure(ToolError):
    def __init__(self, result: QcResult):
        self.exit_code = result_code(result)
        super().__init__(f"QC {result.exit_meaning}; 원출력·기록은 _failed/ 참조")


def execute(args: Namespace, argv: list[str], cfg: Config):
    if args.command == "convert" and not args.dry_run:
        raise InputError("QC convert는 --dry-run 필수")
    settings = tomllib.loads(read_document(cfg.path, "config").text).get("qc", {})
    if not isinstance(settings, dict):
        raise InputError("qc는 TOML 표여야 함")
    python = settings.get("python", "") or sys.executable
    config_path = settings.get("config", "")
    timeout = settings.get("timeout_s", 1800)
    if not isinstance(python, str) or not isinstance(config_path, str) or type(timeout) not in (int, float) or not math.isfinite(timeout) or timeout <= 0:
        raise InputError("qc: python/config 문자열, 양의 유한 timeout_s 필요")
    if Path(python).parent != Path(".") and not Path(python).is_absolute():
        python = str((cfg.path.parent / python).resolve())
    if not shutil.which(python):
        raise Unavailable(f"QC Python 실행 파일 없음: {python}")
    child_config = (cfg.path.parent / config_path).resolve() if config_path else None
    if child_config and not child_config.is_file():
        raise InputError(f"QC config 파일 없음: {child_config}")
    fields = {"probe": ("files",), "compare": ("original", "candidate"), "tiles": ("input",), "split": ("input",), "convert": ("input",)}[args.command]
    inputs = tuple(Path(p).resolve() for field in fields for p in (getattr(args, field) if field == "files" else [getattr(args, field)]))
    child_args = [str(p) for p in inputs]
    for field in ("json", "search", "threshold", "fps", "width", "grid", "cuts", "around", "scene_threshold", "max_part_mb", "verify", "dry_run", "scene", "suffix", "profile"):
        value = getattr(args, field, None)
        if value is not None and value is not False:
            child_args.append("--" + field.replace("_", "-"))
            if value is not True:
                child_args.append(str(value))
    runner = SubprocessQcRunner(python, child_config)
    target = args.out or new_target(cfg.output_root, f"qc-{args.command}", "review")
    with RunDir(target, cfg.policy(inputs)) as run:
        result = runner.run(args.command, child_args, work_dir=run.stage / "qc" / "1", timeout_s=timeout)
        result = replace(result, stdout_path="qc/1/stdout.bin", stderr_path="qc/1/stderr.bin",
                         log_paths=tuple("qc/1/" + p for p in result.log_paths),
                         produced=tuple(("qc/1/" + p, size, digest) for p, size, digest in result.produced))
        run.write_json("qc.json", result)
        code = result_code(result)
        metadata = {"tool_version": __version__, "argv": argv, "config_sha256": cfg.sha256, "exit_code": code, "status": "검수 대기", "qc": result}
        if code not in {0, 1}:
            run.write_json("run.json", {**metadata, "status": "failed"})
            raise QcFailure(result)
        run.finish(metadata)
    return {"command": f"qc {args.command}", "exit_code": code, "status": "검수 대기", "output": str(target.resolve()), "produced": len(result.produced)}
