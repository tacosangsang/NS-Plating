"""입출력 폴더 이름의 공통 검증."""

from dataclasses import dataclass
from pathlib import Path

from .errors import QCError


def checked_path(path: Path) -> Path:
    absolute = path.absolute()
    if len(str(absolute)) > 240:
        raise QCError(2, f"경로가 240자를 초과합니다: {absolute}")
    resolved = absolute.resolve()
    if len(str(resolved)) > 240:
        raise QCError(2, f"경로가 240자를 초과합니다: {resolved}")
    return resolved


@dataclass(frozen=True, slots=True)
class SceneLayout:
    raw: str
    prores: str

    @classmethod
    def from_config(cls, config: dict) -> "SceneLayout":
        layout = config.get("layout", {})
        if not isinstance(layout, dict):
            raise QCError(2, "설정의 layout은 TOML 테이블이어야 합니다")
        raw, prores = layout.get("raw", "raw"), layout.get("prores", "prores")

        def valid(name):
            return (isinstance(name, str) and name not in ("", ".", "..")
                    and name[-1] not in (" ", ".")
                    and not any(c in name for c in ("/", "\\", ":"))
                    and not any(ord(c) < 32 for c in name))

        if not valid(raw) or not valid(prores) or raw.casefold() == prores.casefold():
            raise QCError(2, "raw/prores 설정은 서로 다른 단일 폴더 이름이어야 합니다")
        return cls(raw, prores)

    def names(self) -> tuple[str, str]:
        return self.raw, self.prores
