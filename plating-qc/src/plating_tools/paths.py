"""해석된 경로에 대해 모든 쓰기를 제한한다."""
import os
from dataclasses import dataclass
from pathlib import Path

from .errors import InputError


def within(path: Path, root: Path) -> bool:
    return Path(os.path.normcase(str(path))).is_relative_to(Path(os.path.normcase(str(root))))


@dataclass(frozen=True, slots=True)
class WritePolicy:
    write_root: Path
    read_only: tuple[Path, ...] = ()
    input_dirs: tuple[Path, ...] = ()

    def check(self, path: Path) -> Path:
        resolved = path.resolve()
        roots = (self.write_root / ".git", *self.read_only, *self.input_dirs)
        if (not within(resolved, self.write_root.resolve())
                or any(within(resolved, root.resolve()) for root in roots)
                or any(part.casefold() in {"raw", ".git"} for part in (*path.parts, *resolved.parts))):
            raise InputError(f"쓰기 금지 경로: {path} → {resolved}")
        return resolved
