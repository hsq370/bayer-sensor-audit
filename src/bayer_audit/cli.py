"""Command-line interface for Bayer Sensor Audit."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from .core import CFA_LAYOUTS, audit_frame, compare_repeat_frames
from .io import load_frame


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="bayer-audit", description="Summarize Bayer RAW arrays and repeat-frame noise.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    cfa_choices = tuple(CFA_LAYOUTS)

    inspect = subparsers.add_parser("inspect", help="Summarize one single-plane Bayer frame")
    inspect.add_argument("frame", type=Path)
    inspect.add_argument("--cfa", choices=cfa_choices, default="RGGB")
    inspect.add_argument("--black-level", type=float)
    inspect.add_argument("--saturation-level", type=float)
    inspect.add_argument("--key", help="Array name when loading a multi-array .npz file")
    inspect.add_argument("--output", type=Path, help="Write JSON to this path instead of stdout")

    noise = subparsers.add_parser("noise", help="Compare two registered repeat captures")
    noise.add_argument("first", type=Path)
    noise.add_argument("second", type=Path)
    noise.add_argument("--cfa", choices=cfa_choices, default="RGGB")
    noise.add_argument("--first-key", help="Array name for the first .npz file")
    noise.add_argument("--second-key", help="Array name for the second .npz file")
    noise.add_argument("--output", type=Path, help="Write JSON to this path instead of stdout")
    return parser


def _write(report: dict[str, Any], destination: Path | None) -> None:
    rendered = json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n"
    if destination is None:
        sys.stdout.write(rendered)
    else:
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(rendered, encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "inspect":
            frame = load_frame(args.frame, key=args.key)
            report = audit_frame(
                frame,
                cfa=args.cfa,
                black_level=args.black_level,
                saturation_level=args.saturation_level,
            )
        else:
            first = load_frame(args.first, key=args.first_key)
            second = load_frame(args.second, key=args.second_key)
            report = compare_repeat_frames(first, second, cfa=args.cfa)
        _write(report, args.output)
        return 0
    except (OSError, ValueError, RuntimeError) as exc:
        print(f"bayer-audit: error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
