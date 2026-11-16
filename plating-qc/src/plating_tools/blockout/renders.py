"""명시된 자산·세 자리 버전·씬 토큰으로 렌더와 시트를 비교한다."""
import re
from collections.abc import Mapping
from pathlib import Path
from typing import Final

from ..model import Finding, Severity
from .model import Manifest, VERSION, version_number

SCENE: Final = re.compile(r"(?:^|[/_])(S#[0-9]{2})(?=$|[/_.])")
DATE_FOLDER: Final = re.compile(r"[0-9]{4}[-_]?[0-9]{2}[-_]?[0-9]{2}")
DATE_TOKEN: Final = re.compile(r"(?:^|_)[0-9]{4}[-_]?[0-9]{2}[-_]?[0-9]{2}(?=_|$)")


def check_renders(root: Path, manifests: Mapping[str, Manifest]) -> tuple[Finding, ...]:
    """씬을 추정하지 않는다. 씬 토큰이 없으면 manifest current와 비교한다."""
    findings: list[Finding] = []
    pending = [root]
    while pending:
        path = pending.pop()
        if path.is_symlink() or path.is_junction():
            findings.append(Finding("CONVENTION", Severity.ERROR, f"렌더 링크 금지: {path}"))
            continue
        if path.is_dir():
            if DATE_FOLDER.fullmatch(path.name) or (re.match(r"v[0-9]", path.name) and not VERSION.fullmatch(path.name)):
                findings.append(Finding("CONVENTION", Severity.ERROR, f"렌더 버전·날짜 폴더 규약 위반: {path}"))
            pending.extend(sorted(path.iterdir(), reverse=True))
            continue
        parts = (root.name, *path.relative_to(root).parts)
        relative = "/".join(parts)
        if DATE_TOKEN.search(path.stem):
            findings.append(Finding("CONVENTION", Severity.ERROR, f"렌더 파일명 날짜 금지: {path}"))
            continue
        candidates = [name for name in manifests if path.name.startswith(name + "_v")]
        asset = max(candidates, key=len) if candidates else ""
        pattern = re.fullmatch(re.escape(asset) + r"_(v[0-9]{3})_(.+)\.png", path.name)
        if not asset or pattern is None:
            findings.append(Finding("CONVENTION", Severity.ERROR, f"렌더 이름은 <asset>_vNNN_<view>[_<variant>].png: {path}"))
            continue
        manifest = manifests[asset]
        version = pattern[1]
        if version not in manifest.versions:
            findings.append(Finding("CONVENTION", Severity.ERROR, f"manifest에 없는 렌더 버전 {version}: {path}"))
            continue
        folders = [part for part in parts[:-1] if VERSION.fullmatch(part)]
        if any(part != version for part in folders):
            findings.append(Finding("CONVENTION", Severity.ERROR, f"렌더 폴더·파일 버전 불일치: {path}"))
            continue
        scenes = set(SCENE.findall(relative))
        if len(scenes) > 1:
            findings.append(Finding("CONVENTION", Severity.ERROR, f"렌더 씬 범위가 모호함: {path}"))
            continue
        scene = next(iter(scenes), "")
        pin = manifest.pins.get(scene)
        expected = pin.version if pin else manifest.current
        if not expected:
            findings.append(Finding("CONVENTION", Severity.ERROR, f"비교할 manifest current가 비어 있음: {path}"))
        elif version == expected:
            if pin:
                findings.append(Finding("PINNED", Severity.INFO,
                                        f"{path}: {scene} {version}, 승인자 {pin.approved_by}, {pin.date}, {pin.reason}"))
        elif pin or version_number(version) < version_number(expected):
            findings.append(Finding("STALE", Severity.WARN, f"{path}: {scene or 'current'} 기준 {expected}, 렌더 {version}"))
        else:
            findings.append(Finding("CONVENTION", Severity.ERROR, f"current로 선택하지 않은 새 렌더 {version}, 기준 {expected}: {path}"))
    return tuple(findings)
