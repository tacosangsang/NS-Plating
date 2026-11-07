import argparse
import json
import sys
from .core import QCError, convert, load_config, probe
from .review import compare, tiles
from .split import split


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
    comp = subs.add_parser("compare")
    comp.add_argument("original")
    comp.add_argument("candidate")
    comp.add_argument("--search", type=int, default=30)
    comp.add_argument("--threshold", type=float, default=.02)
    comp.add_argument("--json", action="store_true")
    tile = subs.add_parser("tiles")
    tile.add_argument("input")
    tile.add_argument("--out", required=True)
    tile.add_argument("--fps", type=float, default=1)
    tile.add_argument("--width", type=int, default=320)
    tile.add_argument("--grid", default="5x2")
    tile.add_argument("--cuts", default="")
    tile.add_argument("--around", type=int, default=3)
    part = subs.add_parser("split")
    part.add_argument("input")
    part.add_argument("--out", required=True)
    part.add_argument("--max-part-mb", type=float, default=400)
    part.add_argument("--verify", action="store_true", help="호환 옵션: 프레임 검증은 항상 실행")
    args = parser.parse_args(argv)
    try:
        config = load_config(args.config)
        if args.command == "probe":
            result = [probe(path, config) for path in args.files]
            warnings = any(item["warnings"] for item in result)
        elif args.command == "compare":
            result = compare(args.original, args.candidate, config, args.search, args.threshold)
            warnings = bool(result["warnings"])
        elif args.command == "tiles":
            try:
                columns, rows = map(int, args.grid.lower().split("x"))
                cuts = [int(c) for c in args.cuts.split(",")] if args.cuts else []
            except ValueError as exc:
                raise QCError(2, "grid 또는 cuts 형식이 올바르지 않습니다") from exc
            result = tiles(args.input, args.out, config, args.fps, args.width, columns, rows, cuts, args.around)
            warnings = bool(result["warnings"][:-1])
        elif args.command == "split":
            result = split(args.input, args.out, config, args.max_part_mb)
            warnings = bool(result["warnings"])
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
