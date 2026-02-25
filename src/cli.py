import argparse
from pathlib import Path
import sys
from typing import Optional, Sequence

from rlangc import __version__, pipeline


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="rlangc")
    parser.add_argument("--version", action="version", version=f"rlangc {__version__}")
    subparsers = parser.add_subparsers(dest="command", required=True)
    check_parser = subparsers.add_parser("check", help="Check a .rl file")
    check_parser.add_argument("path", type=Path)
    return parser


def _run_check(path: Path) -> int:
    source = path.read_text(encoding="utf-8")
    pipeline.run(source)
    print(f"{path}: OK")
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    if args.command == "check":
        return _run_check(args.path)
    parser.error("No command provided")
    return 2


if __name__ == "__main__":
    sys.exit(main())
