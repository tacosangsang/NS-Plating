"""공식 CLI. 기능 모듈은 해당 명령 실행 시점에만 import한다."""
import argparse
import sys
from pathlib import Path

from . import __version__
from .config import load_config
from .errors import InputError, ToolError, Unavailable
from .model import json_text
from .output import RunDir, new_target


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(prog="plating")
    root.add_argument("--config", type=Path, default=Path("plating.toml"))
    groups = root.add_subparsers(dest="group", required=True)
    cuts = groups.add_parser("cuts").add_subparsers(dest="command", required=True)
    inv = cuts.add_parser("inventory")
    inv.add_argument("--input", type=Path)
    inv.add_argument("--out", type=Path)
    ext = cuts.add_parser("extract")
    ext.add_argument("--scene", required=True)
    ext.add_argument("--cuts")
    ext.add_argument("--section-line", type=int)
    ext.add_argument("--table-line", type=int)
    ext.add_argument("--input", type=Path)
    ext.add_argument("--out", type=Path)
    return root


def execute(args, argv: list[str]):
    cfg = load_config(args.config)
    if args.group == "cuts" and args.command == "extract":
        from .cuts.extract import extract_scene
        from .cuts.report import cuts_md, cuts_csv
        from .cuts.source import NotionMdFile
        source_path = args.input or cfg.cuts_input
        if source_path is None:
            raise InputError("컷표 --input 또는 cuts.input 필요")
        source = NotionMdFile(source_path)
        result = extract_scene(source, args.scene, cut_ids=tuple(args.cuts.split(",")) if args.cuts else None,
                               section_line=args.section_line, table_line=args.table_line)
        code = int(bool(result.findings))
        target = args.out or new_target(cfg.output_root, "cuts-extract", result.scene_id)
        with RunDir(target, cfg.policy((source_path,))) as run:
            run.write_json("cuts.json", result)
            run.write_text("cuts.md", cuts_md(result))
            run.write_text("cuts.csv", cuts_csv(result), "utf-8-sig")
            run.finish({"tool_version": __version__, "argv": argv, "config_sha256": cfg.sha256,
                        "docs": [source.fingerprint()], "exit_code": code, "status": "검수 대기",
                        "section_line": args.section_line, "table_line": args.table_line})
        return {"command": "cuts extract", "exit_code": code, "status": "검수 대기", "output": str(target.resolve()), "targets": len(result.targets), "findings": len(result.findings)}
    if args.group == "cuts" and args.command == "inventory":
        from .cuts.report import inventory, inventory_md
        from .cuts.source import NotionMdFile
        source_path = args.input or cfg.cuts_input
        if source_path is None:
            raise InputError("컷표 --input 또는 cuts.input 필요")
        source = NotionMdFile(source_path)
        result = inventory(source)
        changed = bool(cfg.cuts_expected_sha256 and source.fingerprint().sha256 != cfg.cuts_expected_sha256)
        code = int(bool(result["color_loss"]) or changed)
        target = args.out or new_target(cfg.output_root, "cuts-inventory", "F")
        with RunDir(target, cfg.policy((source_path,))) as run:
            run.write_json("inventory.json", result)
            run.write_text("inventory.md", inventory_md(result))
            run.finish({"tool_version": __version__, "argv": argv, "config_sha256": cfg.sha256,
                        "docs": [source.fingerprint()], "exit_code": code, "status": "검수 대기",
                        "expected_source_changed": changed})
        return {"command": "cuts inventory", "exit_code": code, "status": "검수 대기", "output": str(target.resolve()), "sections": len(result["sections"]), "color_loss": result["color_loss"]}
    raise Unavailable("아직 구현되지 않은 명령")


def main(argv: list[str] | None = None) -> int:
    actual = list(sys.argv[1:] if argv is None else argv)
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    try:
        args = parser().parse_args(actual)
        result = execute(args, actual)
        print(json_text(result), end="")
        return result["exit_code"]
    except ToolError as exc:
        print(str(exc), file=sys.stderr)
        return exc.exit_code
    except OSError as exc:
        print(f"I/O 실패(경로 길이도 확인): {exc}", file=sys.stderr)
        return 5
