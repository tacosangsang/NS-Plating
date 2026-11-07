"""TOML 설정 탐색과 읽기."""

from pathlib import Path
import tomllib

from .errors import QCError


def load_config(path=None):
    if path:
        candidates = [Path(path)]
    else:
        candidates = [p / "plating-qc.toml" for p in (Path.cwd(), *Path.cwd().parents)]
    for candidate in candidates:
        if candidate.is_file():
            try:
                with candidate.open("rb") as stream:
                    return tomllib.load(stream)
            except (OSError, tomllib.TOMLDecodeError) as exc:
                raise QCError(2, f"설정 오류: {exc}") from exc
    if path:
        raise QCError(2, f"설정 파일이 없습니다: {path}")
    return {}
