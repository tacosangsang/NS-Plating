"""plating.toml 경계. 기존 plating-qc config.toml과 독립적이다."""
import tomllib
from dataclasses import dataclass
from pathlib import Path

from .errors import InputError
from .paths import WritePolicy
from .textio import read_document


@dataclass(frozen=True, slots=True)
class Config:
    path: Path
    sha256: str
    write_root: Path
    output_root: Path
    workflow_dir: Path
    read_only: tuple[Path, ...]
    cuts_input: Path | None
    cuts_expected_sha256: str | None
    declared_commit: str | None
    readme: Path | None
    handbook: Path | None

    def policy(self, inputs: tuple[Path, ...] = ()) -> WritePolicy:
        return WritePolicy(self.write_root, self.read_only, tuple(path.resolve().parent for path in inputs))


def load_config(path: Path) -> Config:
    doc = read_document(path, "config")
    try:
        data = tomllib.loads(doc.text)
    except tomllib.TOMLDecodeError as exc:
        raise InputError(f"설정 TOML 오류: {path}: {exc}") from exc
    base = path.resolve().parent
    paths = data.get("paths", {})
    cuts = data.get("cuts", {})
    docs = data.get("docs", {})
    if not all(isinstance(section, dict) for section in (paths, cuts, docs)):
        raise InputError("설정 paths/cuts/docs는 TOML 표여야 함")

    def resolve(value: str) -> Path:
        if not isinstance(value, str):
            raise InputError("설정 경로는 문자열이어야 함")
        candidate = Path(value)
        return (candidate if candidate.is_absolute() else base / candidate).resolve()

    readonly = paths.get("read_only", [])
    if not isinstance(readonly, list):
        raise InputError("read_only는 경로 목록이어야 함")
    cfg = Config(path.resolve(), doc.fingerprint.sha256,
                 resolve(paths.get("write_root", ".")), resolve(paths.get("output_root", "out")),
                 resolve(paths.get("workflow_dir", "workflow")), tuple(resolve(p) for p in readonly),
                 resolve(cuts["input"]) if cuts.get("input") else None,
                 cuts.get("expected_sha256"), docs.get("declared_commit"),
                 resolve(paths["readme"]) if paths.get("readme") else None,
                 resolve(paths["handbook"]) if paths.get("handbook") else None)
    cfg.policy().check(cfg.output_root)
    return cfg
