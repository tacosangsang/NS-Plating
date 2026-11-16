"""파일시스템을 변경하지 않는 manifest 정본 검사."""
from dataclasses import dataclass
from pathlib import Path

from ..errors import InputError
from ..model import Finding, Severity
from .manifest import ManifestStore
from .model import Manifest, version_number
from .renders import check_renders
from .storage import VersionStore


@dataclass(frozen=True, slots=True)
class CheckReport:
    root: str
    assets: int
    findings: tuple[Finding, ...]


def check(root: Path, manifests: ManifestStore, versions: VersionStore, renders: Path | None = None) -> CheckReport:
    """규약·불변 위반과 렌더의 current/pin 상태를 근거와 함께 모은다."""
    root = root.resolve()
    if not root.is_dir() or (renders is not None and not renders.is_dir()):
        raise InputError("존재하는 blockout --root와 선택적 --renders 폴더 필요")
    entries = sorted(root.iterdir())
    if not entries:
        raise InputError(f"검사할 자산 폴더 없음: {root}")
    findings: list[Finding] = []
    loaded: dict[str, Manifest] = {}
    for directory in entries:
        manifest_path = directory / "manifest.toml"
        if (directory.is_symlink() or directory.is_junction() or not directory.is_dir()
                or not manifest_path.is_file() or manifest_path.is_symlink()):
            findings.append(Finding("CONVENTION", Severity.ERROR, f"자산 폴더·일반 manifest.toml 필요: {directory}"))
            continue
        try:
            manifest = manifests.read(manifest_path)
        except InputError as exc:
            findings.append(Finding("CONVENTION", Severity.ERROR, str(exc)))
            continue
        if manifest.asset != directory.name:
            findings.append(Finding("CONVENTION", Severity.ERROR, f"manifest asset·폴더 이름 불일치: {directory}"))
            continue
        loaded[manifest.asset] = manifest
        containers = [directory / name for name in ("versions", "renders", "archive")]
        if any(not path.is_dir() or path.is_symlink() or path.is_junction() for path in containers):
            findings.append(Finding("CONVENTION", Severity.ERROR, f"일반 versions/renders/archive 폴더 필요: {directory}"))
            continue
        locations: dict[str, list[Path]] = {}
        for path in versions.list(directory):
            try:
                version_number(path.name)
            except InputError:
                findings.append(Finding("CONVENTION", Severity.ERROR, f"버전 폴더 이름 규약 위반: {path}"))
                continue
            if not path.is_dir() or path.is_symlink() or path.is_junction():
                findings.append(Finding("CONVENTION", Severity.ERROR, f"일반 버전 폴더 필요: {path}"))
                continue
            if path.name not in manifest.versions:
                findings.append(Finding("CONVENTION", Severity.ERROR, f"manifest에 없는 버전 폴더: {path}"))
            locations.setdefault(path.name, []).append(path)
        for name, record in manifest.versions.items():
            paths = locations.get(name, [])
            if not paths:
                findings.append(Finding("IMMUTABLE", Severity.ERROR, f"기록된 버전 폴더가 없음: {directory}/{name}"))
                continue
            if len(paths) > 1:
                findings.append(Finding("CONVENTION", Severity.ERROR, f"버전 정본이 여러 위치에 있음: {paths}"))
            for path in paths:
                try:
                    actual = versions.hashes(path)
                except InputError as exc:
                    findings.append(Finding("IMMUTABLE", Severity.ERROR, str(exc)))
                    continue
                missing = sorted(record.files.keys() - actual.keys())
                extra = sorted(actual.keys() - record.files.keys())
                changed = sorted(key for key in record.files.keys() & actual.keys() if record.files[key] != actual[key])
                if missing or extra or changed:
                    findings.append(Finding("IMMUTABLE", Severity.ERROR,
                                            f"{path}: 누락 {missing}, 추가 {extra}, SHA-256 변경 {changed}"))
        if renders is None:
            findings.extend(check_renders(directory / "renders", {manifest.asset: manifest}))
    if renders is not None:
        findings.extend(check_renders(renders, loaded))
    return CheckReport(str(root), len(loaded), tuple(findings))


def report_md(report: CheckReport) -> str:
    lines = ["# 블록아웃 규약 검사", "", f"입력: {report.root}", f"자산: {report.assets}", "",
             "| 판정 | 심각도 | 근거 |", "| --- | --- | --- |"]
    for finding in report.findings:
        message = finding.message.replace("|", "\\|").replace("\n", " ")
        lines.append(f"| {finding.code} | {finding.severity} | {message} |")
    if not report.findings:
        lines.extend(("", "위반 없음."))
    return "\n".join(lines) + "\n"
