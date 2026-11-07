"""명시한 계열의 파일 이름·README만 읽는다. Blender·mtime은 쓰지 않는다."""
import os
import re
from pathlib import Path

from ..errors import InputError
from ..model import Unknown
from ..paths import within
from ..textio import read_document
from .model import FamilySpec, FamilyState, VersionTag


def parse_version(text: str, *, prefix: bool = True) -> VersionTag | Unknown:
    match = re.match(r"^v(\d+)([a-z]*)_" if prefix else r"^v(\d+)([a-z]*)$", text)
    if match is None:
        return Unknown("vNN_ 접두사 또는 README 기준 판 없음")
    return VersionTag("v" + match[1] + match[2], int(match[1]), match[2])


def readme_version(path: Path, spec: FamilySpec) -> VersionTag | Unknown:
    prefix = parse_version(path.name)
    if spec.readme_version_pattern:
        try:
            matches = list(re.finditer(spec.readme_version_pattern, read_document(path, "README").text))
        except re.error as exc:
            raise InputError(f"README 판 정규식 오류: {exc}") from exc
        values = {m.groupdict().get("version") or (m[1] if m.lastindex else m[0]) for m in matches}
        if len(values) != 1:
            raise InputError(f"README 기준 판은 하나여야 함: {path}, {values}")
        value = parse_version(values.pop(), prefix=False)
        if isinstance(value, Unknown):
            raise InputError(f"README 기준 판 형식 오류: {path}")
        if isinstance(prefix, VersionTag) and prefix != value:
            raise InputError(f"README 이름·본문 기준 판 충돌: {path}")
        return value
    return prefix


def family_files(spec: FamilySpec) -> tuple[Path, ...]:
    if not spec.root.is_dir():
        raise InputError(f"계열 root 폴더 없음: {spec.root}")
    files = []
    pending = [spec.root]
    while pending:
        parent = pending.pop()
        with os.scandir(parent) as entries:
            for entry in entries:
                path = Path(entry.path)
                relative = path.relative_to(spec.root)
                if any(part.casefold() in {p.casefold() for p in spec.exclude_dirs} for part in relative.parts) or relative.as_posix() in spec.exclude_dirs:
                    continue
                if not within(path.resolve(), spec.root.resolve()) or entry.is_symlink() or path.is_junction():
                    continue
                if entry.is_dir(follow_symlinks=False):
                    pending.append(path)
                elif entry.is_file(follow_symlinks=False):
                    files.append(path)
    return tuple(sorted(files))


def order_unknown(tags: tuple[VersionTag, ...], spec: FamilySpec) -> tuple[str, ...]:
    if spec.explicit_order and any(tag.raw not in spec.explicit_order for tag in tags):
        return tuple(sorted({tag.raw for tag in tags}))
    if any(tag.suffix for tag in tags):
        if not spec.explicit_order or any(tag.raw not in spec.explicit_order for tag in tags):
            return tuple(sorted({tag.raw for tag in tags}))
    return ()


def version_key(tag: VersionTag, spec: FamilySpec) -> int:
    return spec.explicit_order.index(tag.raw) if spec.explicit_order and tag.raw in spec.explicit_order else tag.number


def scan_family(spec: FamilySpec) -> FamilyState:
    sources: dict[str, list[VersionTag]] = {"blend": [], "script": [], "readme": []}
    evidence = []
    for path in family_files(spec):
        relative = path.relative_to(spec.root)
        for kind, pattern in (("blend", spec.blend_glob), ("script", spec.script_glob), ("readme", spec.readme_glob)):
            if not (relative.match(pattern) or (pattern.startswith("**/") and relative.match(pattern[3:]))):
                continue
            tag = readme_version(path, spec) if kind == "readme" else parse_version(path.name)
            if isinstance(tag, VersionTag):
                sources[kind].append(tag)
                evidence.append((str(path), tag.raw))
    all_tags = tuple(tag for values in sources.values() for tag in values)
    unknown_order = order_unknown(all_tags, spec)
    maximum = {kind: max(tags, key=lambda t: version_key(t, spec)) if tags and not unknown_order else Unknown("순서 또는 출처 미확인") for kind, tags in sources.items()}
    values = tuple(maximum.values())
    latest: VersionTag | Unknown = Unknown("순서 불명" if unknown_order else "출처 누락")
    if not unknown_order and all(isinstance(t, VersionTag) for t in values):
        latest = values[0] if len({t.raw for t in values}) == 1 else Unknown("출처 충돌")
    return FamilyState(spec.name, maximum["blend"], maximum["script"], maximum["readme"], latest, unknown_order, tuple(evidence))
