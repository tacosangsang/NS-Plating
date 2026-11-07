import argparse
import json
import sys
from .core import QCError, convert, load_config, probe


def main(argv=None):
    parser = argparse.ArgumentParser(prog="plating-qc")
    parser.add_argument("--config")
    subs = parser.add_subparsers(dest="command", required=True)
    p = subs.add_parser("probe")
    p.add_argument("files", nargs="+")
    p.add_argument("--json", action="store_true")
    c = subs.add_parser("convert")
    c.add_argument("input")
    c.add_argument("--scene")
    c.add_argument("--suffix", default="")
    c.add_argument("--dry-run", action="store_true")
    c.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        config = load_config(args.config)
        if args.command == "probe":
            result = [probe(path, config) for path in args.files]
            warnings = any(item["warnings"] for item in result)
        else:
            result = convert(args.input, args.scene, config, args.suffix, args.dry_run)
            warnings = bool(result.get("warnings"))
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 1 if warnings else 0
    except QCError as exc:
        print(str(exc), file=sys.stderr)
        return exc.code


if __name__ == "__main__":
    raise SystemExit(main())
