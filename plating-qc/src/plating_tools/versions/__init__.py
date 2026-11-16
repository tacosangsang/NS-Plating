"""versions check 입력·출력 경계. 실제 경로 기본값은 두지 않는다."""
import tomllib
from argparse import Namespace
from dataclasses import replace
from pathlib import Path

from .. import __version__
from ..config import Config
from ..docs import WorkflowDir
from ..errors import InputError
from ..model import json_text
from ..output import RunDir, new_target
from ..textio import read_document
from .check import check_render, validate_pins
from .model import FamilySpec, Pin, RenderSpec, Verdict, VersionTag
from .scan import parse_version, scan_family


def load_spec(path: Path) -> tuple[tuple[FamilySpec, ...], tuple[RenderSpec, ...]]:
    try:
        data = tomllib.loads(read_document(path, "versions").text)
    except tomllib.TOMLDecodeError as exc:
        raise InputError(f"versions TOML 오류: {exc}") from exc
    for key in ("family", "render"):
        if not isinstance(data.get(key), list) or not data[key] or any(not isinstance(row, dict) for row in data[key]):
            raise InputError(f"비어 있지 않은 [[{key}]] 목록 필요")
    families = []
    for row in data["family"]:
        if any(not isinstance(row.get(key, ""), str) for key in ("name", "root", "blend_glob", "script_glob", "readme_glob", "readme_version_pattern")) or not row.get("name") or not row.get("root"):
            raise InputError("family: name/root와 문자열 설정 필요")
        for key in ("exclude_dirs", "explicit_order"):
            if not isinstance(row.get(key, []), list) or any(not isinstance(v, str) or not v for v in row.get(key, [])):
                raise InputError(f"family.{key}: 문자열 목록 필요")
        explicit = tuple(row.get("explicit_order", [])) or None
        if explicit and (len(set(explicit)) != len(explicit) or any(not isinstance(parse_version(v, prefix=False), VersionTag) for v in explicit)):
            raise InputError("explicit_order: 중복 없는 vNN 판 목록 필요")
        for key in ("blend_glob", "script_glob", "readme_glob"):
            pattern = row.get(key, "")
            if key in row and not pattern:
                raise InputError(f"{key}: 빈 glob은 미확인, 명시 필요")
            if pattern and (Path(pattern).is_absolute() or ".." in Path(pattern).parts):
                raise InputError(f"{key}: 계열 안 상대 glob 필요")
        families.append(FamilySpec(row["name"], (path.resolve().parent / row["root"]).resolve(), row.get("blend_glob", "v*_*.blend"), row.get("script_glob", "v*_*.py"), row.get("readme_glob", "v*_README*"), row.get("readme_version_pattern") or None, tuple(row.get("exclude_dirs", [])), explicit))
    if len({f.name for f in families}) != len(families):
        raise InputError("family.name 중복")
    renders = []
    for row in data["render"]:
        if any(not isinstance(row.get(key, ""), str) for key in ("family", "path", "scene", "version_from")) or not row.get("path") or row.get("version_from", "접두사") not in {"접두사", "README"}:
            raise InputError("render: path·문자열 필드·접두사/README 기준 필요")
        render_path = (path.resolve().parent / row["path"]).resolve()
        if not render_path.is_file():
            raise InputError(f"render 파일 없음: {render_path}")
        renders.append(RenderSpec(row.get("family", ""), render_path, row.get("scene") or None, row.get("version_from", "접두사")))
    return tuple(families), tuple(renders)


def load_pins(path: Path | None) -> tuple[Pin, ...]:
    if path is None:
        return ()
    try:
        data = tomllib.loads(read_document(path, "pins").text)
    except tomllib.TOMLDecodeError as exc:
        raise InputError(f"pins TOML 오류: {exc}") from exc
    rows = data.get("pin", [])
    if not isinstance(rows, list):
        raise InputError("[[pin]] 목록 필요")
    pins = []
    for row in rows:
        if not isinstance(row, dict) or any(not isinstance(row.get(key, ""), str) for key in ("family", "version", "basis_doc", "basis_contains", "approved_by")):
            raise InputError("pin 문자열 필드 필요")
        if type(row.get("basis_line")) is not int or not isinstance(row.get("scope"), list) or any(not isinstance(s, str) or not s for s in row["scope"]):
            raise InputError("pin: basis_line 정수와 scope 문자열 목록 필요")
        pins.append(Pin(row.get("family", ""), row.get("version", ""), tuple(row["scope"]), row.get("basis_doc", ""), row["basis_line"], row.get("basis_contains", ""), row.get("approved_by", "")))
    return tuple(pins)


def execute(args: Namespace, argv: list[str], cfg: Config):
    families, renders = load_spec(args.spec)
    pins = load_pins(args.pins)
    store = WorkflowDir(cfg.workflow_dir, cfg.declared_commit)
    validate_pins(pins, store)
    if any(p.family not in {f.name for f in families} for p in pins):
        raise InputError("pin의 family가 spec에 없음")
    states = {f.name: scan_family(f) for f in families}
    specs = {f.name: f for f in families}
    checks = tuple(check_render(r, specs.get(r.family), states.get(r.family), pins) for r in renders)
    code = int(any(r.verdict not in {Verdict.LATEST, Verdict.PINNED} for r in checks))
    target = args.out or new_target(cfg.output_root, "versions-check", "families")
    inputs = (args.spec, *((args.pins,) if args.pins else ()), *(r.path for r in renders), *(Path(d.fingerprint.path) for d in store.used.values()))
    policy = cfg.policy(inputs)
    policy = replace(policy, input_dirs=(*policy.input_dirs, *(f.root for f in families)))
    report = {"families": tuple(states.values()), "renders": checks, "pins": pins, "pin_scope_confirmation": "미확인(I15), 파일에 명시한 범위만 적용"}
    with RunDir(target, policy) as run:
        run.write_json("versions.json", report)
        run.write_text("versions.md", "# [검수 대기] 블록아웃 버전 검사\n\n모든 결과: 형상 동일성, 실제 치수 미검증.\n\n```json\n" + json_text(report) + "```\n\n## 내가 정한 것\n파일 접두사·README 명시 판만 비교. mtime 미사용.\n\n## 사용자 답이 필요한 것\nI14 실제 계열·경로, I15 pin 적용 범위 미확인. 승인자 ts.\n\n## 근거\npins 근거 문서·행, run.json 지문.\n")
        run.finish({"tool_version": __version__, "argv": argv, "config_sha256": cfg.sha256, "inputs": [read_document(p, "spec").fingerprint for p in (args.spec, args.pins) if p], "docs": [d.fingerprint for d in store.used.values()], "exit_code": code, "status": "검수 대기"})
    return {"command": "versions check", "exit_code": code, "status": "검수 대기", "output": str(target.resolve()), "renders": len(checks)}
