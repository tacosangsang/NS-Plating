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
    prompt = groups.add_parser("prompt").add_subparsers(dest="command", required=True)
    for name in ("skeleton", "check"):
        command = prompt.add_parser(name)
        command.add_argument("--kind", required=True, choices=("video", "image"))
        command.add_argument("--plan", type=Path)
        command.add_argument("--clip")
        command.add_argument("--out", type=Path)
        command.add_argument("--cuts-json" if name == "skeleton" else "--prompt", type=Path, required=True)
    gate = groups.add_parser("gate").add_subparsers(dest="command", required=True)
    cost = gate.add_parser("cost")
    for name in ("model", "mode", "resolution", "seconds"):
        cost.add_argument("--" + name)
    cost.add_argument("--out", type=Path)
    check = gate.add_parser("check")
    check.add_argument("--gate", type=Path, required=True)
    check.add_argument("--prompt", type=Path, required=True)
    check.add_argument("--require-approval", action="store_true")
    check.add_argument("--out", type=Path)
    for name in ("cuts-json", "check-json", "refs-json"):
        check.add_argument("--" + name, type=Path)
    for command in (cost, check):
        command.add_argument("--plan", type=Path)
        command.add_argument("--clip")
    refs = groups.add_parser("refs").add_subparsers(dest="command", required=True).add_parser("check")
    refs.add_argument("--list", type=Path, required=True)
    refs.add_argument("--allow-network", action="store_true")
    refs.add_argument("--thumbs", action="store_true")
    refs.add_argument("--prompt", type=Path)
    refs.add_argument("--out", type=Path)
    versions = groups.add_parser("versions").add_subparsers(dest="command", required=True).add_parser("check")
    versions.add_argument("--spec", type=Path, required=True)
    versions.add_argument("--pins", type=Path)
    versions.add_argument("--out", type=Path)
    qc = groups.add_parser("qc").add_subparsers(dest="command", required=True)
    for name, fields in (("probe", ("files",)), ("compare", ("original", "candidate")), ("tiles", ("input",)), ("split", ("input",)), ("convert", ("input",))):
        command = qc.add_parser(name)
        for field in fields:
            command.add_argument(field, nargs="+" if field == "files" else None)
        command.add_argument("--out", type=Path)
        command.add_argument("--json", action="store_true")
        if name == "compare":
            command.add_argument("--search", type=int)
            command.add_argument("--threshold", type=float)
        if name == "tiles":
            for field, kind in (("fps", float), ("width", int), ("grid", str), ("cuts", str), ("around", int), ("scene-threshold", float)):
                command.add_argument("--" + field, type=kind)
        if name == "split":
            command.add_argument("--max-part-mb", type=float)
            command.add_argument("--verify", action="store_true")
        if name == "convert":
            command.add_argument("--dry-run", action="store_true")
            for field in ("scene", "suffix", "profile"):
                command.add_argument("--" + field)
    return root


def execute(args, argv: list[str]):
    if args.group in {"refs", "versions", "qc"}:
        raise Unavailable(f"P1 모듈 없음: plating_tools.{args.group}")
    cfg = load_config(args.config)
    if args.group == "gate":
        from .docs import WorkflowDir
        from .gate.cost import cost_for, read_cost_table
        from .prompt.plan import ClipPlan, load_plan, number
        from .textio import read_document, read_json
        from .model import Unknown
        store = WorkflowDir(cfg.workflow_dir, cfg.declared_commit)
        table = read_cost_table(store)
        plan = load_plan(args.plan, args.clip)
        if args.command == "cost":
            if plan is not None and any(getattr(args, field) is not None for field in ("model", "mode", "resolution", "seconds")):
                raise InputError("계획과 직접 비용 인자를 함께 지정할 수 없음")
            if plan is None:
                if not all((args.model, args.mode, args.resolution, args.seconds)) or args.mode not in {"new", "edit", "code"}:
                    raise InputError("--model --mode --resolution --seconds 또는 --plan 필요")
                unknown = Unknown("직접 비용 인자에 없음")
                seconds = number(args.seconds, "seconds")
                plan = ClipPlan("cost", "video", (), unknown, seconds if args.mode == "new" else unknown, args.mode,
                                args.model, args.resolution, seconds if args.mode == "edit" else unknown, unknown, (), {}, unknown, unknown, ())
            result = cost_for(plan, table)
            code = int(bool(result.findings))
            target = None
            if args.out:
                inputs = tuple(Path(d.fingerprint.path) for d in store.used.values()) + ((args.plan,) if args.plan else ())
                with RunDir(args.out, cfg.policy(inputs)) as run:
                    run.write_json("cost.json", result)
                    run.finish({"tool_version": __version__, "argv": argv, "config_sha256": cfg.sha256, "docs": table.doc_versions,
                                "inputs": [read_document(args.plan, "plan").fingerprint] if args.plan else [], "exit_code": code, "status": "검수 대기"})
                target = str(args.out.resolve())
            return {"command": "gate cost", "exit_code": code, "status": "검수 대기", "output": target, "cost": result}
        from .gate.checklist import GateContext, evaluate_gate, gate_md, load_gate, machine_findings, read_gate_rules
        rules = read_gate_rules(store)
        prompt = read_document(args.prompt, "prompt")
        inputs, approval = load_gate(args.gate)
        cuts = read_json(args.cuts_json) if args.cuts_json else None
        check = read_json(args.check_json) if args.check_json else None
        refs = read_json(args.refs_json) if args.refs_json else None
        current = read_document(cfg.cuts_input, "F") if cfg.cuts_input else None
        machine, fresh = machine_findings(plan, cuts, check, refs, current.fingerprint.sha256 if current else None, prompt.fingerprint.sha256, max_seconds=rules.max_seconds)
        cost = cost_for(plan, table) if plan else None
        if cost is not None:
            machine[8] = (*machine.get(8, ()), *cost.findings)
        context = GateContext(prompt.fingerprint.sha256, rules.approval_words, machine, cost, fresh)
        result = evaluate_gate(rules.lines, inputs, context, approval)
        code = int(not result.checklist_complete or any(machine.values()) or (args.require_approval and result.approval.status != "승인 기록 있음"))
        target = args.out or new_target(cfg.output_root, "gate-check", args.clip or "unplanned")
        paths = tuple(p for p in (args.gate, args.prompt, args.plan, args.cuts_json, args.check_json, args.refs_json, cfg.cuts_input) if p)
        paths += tuple(Path(d.fingerprint.path) for d in store.used.values())
        with RunDir(target, cfg.policy(paths)) as run:
            run.write_json("gate.json", result)
            run.write_text("gate.md", gate_md(result, prompt.text))
            run.write_json("cost.json", cost if cost else Unknown("계획 없음"))
            run.finish({"tool_version": __version__, "argv": argv, "config_sha256": cfg.sha256, "docs": [d.fingerprint for d in store.used.values()],
                        "inputs": [read_document(p, "input").fingerprint for p in paths if p not in tuple(Path(d.fingerprint.path) for d in store.used.values())], "exit_code": code, "status": result.label})
        return {"command": "gate check", "exit_code": code, "status": result.label, "output": str(target.resolve())}
    if args.group == "prompt":
        from .docs import WorkflowDir
        from .prompt.rules import read_rules
        from .prompt.plan import load_plan
        from .textio import read_document, read_json
        store = WorkflowDir(cfg.workflow_dir, cfg.declared_commit)
        rules = read_rules(store)
        plan = load_plan(args.plan, args.clip)
        if plan is not None and plan.kind != args.kind:
            raise InputError("--kind와 계획 kind 불일치")
        inputs = tuple(Path(doc.path) for doc in rules.fingerprints) + ((args.plan,) if args.plan else ())
        target = args.out or new_target(cfg.output_root, f"prompt-{args.command}", args.clip or "unplanned")
        if args.command == "skeleton":
            if args.kind != "video":
                raise InputError("이미지는 prompt check만 지원")
            from .prompt.assemble import build_skeleton, skeleton_md, gate_template
            data = read_json(args.cuts_json)
            if not all(key in data for key in ("source", "targets", "scene_id")):
                raise InputError("cuts.json 계약 필드 누락")
            result = build_skeleton(data, plan, rules)
            code = 1 if result.lengths.placeholders or result.conflicts else 0
            with RunDir(target, cfg.policy((*inputs, args.cuts_json))) as run:
                run.write_json("skeleton.json", result)
                run.write_text("skeleton.md", skeleton_md(result))
                run.write_json("lengths.json", result.lengths)
                run.write_text("gate.toml", gate_template())
                run.finish({"tool_version": __version__, "argv": argv, "config_sha256": cfg.sha256,
                            "docs": rules.fingerprints, "inputs": [read_document(p, "input").fingerprint for p in (args.cuts_json, args.plan) if p], "exit_code": code, "status": "검수 대기(전송본 아님)"})
        else:
            from .prompt.check import check_prompt
            prompt_doc = read_document(args.prompt, "prompt")
            result = check_prompt(prompt_doc.text, plan, rules, args.kind)
            code = int(bool(result.findings))
            with RunDir(target, cfg.policy((*inputs, args.prompt))) as run:
                run.write_json("check.json", {"prompt_sha256": prompt_doc.fingerprint.sha256, "result": result})
                run.write_text("check.md", "# [검수 대기] 프롬프트 검사\n\n```json\n" + json_text(result) + "```\n\n## 내가 정한 것\n실제 문자열 검사.\n\n## 사용자 답이 필요한 것\n원문 대응과 레퍼런스 역할 검수.\n\n## 근거\nrun.json 문서 지문 참조.\n")
                run.finish({"tool_version": __version__, "argv": argv, "config_sha256": cfg.sha256,
                            "docs": rules.fingerprints, "inputs": [prompt_doc.fingerprint, *([read_document(args.plan, "plan").fingerprint] if args.plan else [])], "exit_code": code, "status": "검수 대기"})
        return {"command": f"prompt {args.command}", "exit_code": code, "status": "검수 대기", "output": str(target.resolve())}
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
        if cfg.cuts_expected_sha256 and source.fingerprint().sha256 != cfg.cuts_expected_sha256:
            from dataclasses import replace
            from .model import Finding, Severity
            result = replace(result, findings=(*result.findings, Finding("DOC_CHANGED", Severity.WARN, "F의 설정 기준 지문 변경")))
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
