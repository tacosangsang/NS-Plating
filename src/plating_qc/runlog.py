"""명시적으로 요청한 로컬 실행 로그. 기존 파일은 수정하지 않는다."""
import hashlib
import os
from pathlib import Path
import subprocess

from .core import QCError, executable, layout_names
from .layout import checked_path


def reserve_log(name, config, output_dir=None):
    path = checked_path(Path(name))
    raw, _ = layout_names(config)
    if path.suffix.lower() != ".json":
        raise QCError(2, "로그 파일은 .json 확장자를 사용하세요")
    if any(part.name.casefold() == raw.casefold() for part in (path, *path.parents)):
        raise QCError(2, "raw 폴더에는 로그를 쓸 수 없습니다")
    if output_dir:
        output = Path(output_dir).resolve()
        if path == output or output in path.parents:
            raise QCError(2, "새 출력 폴더 밖에 로그를 지정하세요")
    if not path.parent.is_dir():
        raise QCError(2, "로그 상위 폴더가 없습니다")
    try:
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0), 0o600)
        return os.fdopen(fd, "w", encoding="utf-8")
    except FileExistsError as exc:
        raise QCError(3, f"로그 파일이 이미 있습니다: {path}") from exc
    except OSError as exc:
        raise QCError(5, f"로그 파일 생성 실패: {exc}") from exc


def tool_versions(config):
    versions = {}
    for name in ("ffmpeg", "ffprobe"):
        try:
            path = executable(name, config)
            result = subprocess.run([path, "-version"], capture_output=True, text=True, errors="replace", timeout=5)
            versions[name] = result.stdout.splitlines()[0] if result.returncode == 0 and result.stdout else None
        except (QCError, OSError, subprocess.TimeoutExpired):
            versions[name] = None
    return versions


def source_hashes():
    result = {}
    for path in sorted(Path(__file__).resolve().parent.glob("*.py")):
        try:
            result[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
        except OSError:
            result[path.name] = None
    return result
