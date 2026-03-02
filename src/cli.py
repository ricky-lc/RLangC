import argparse
from pathlib import Path
import subprocess
import sys
import tempfile
from typing import Optional, Sequence

from rlangc.backends import generate_c
from rlangc import __version__, pipeline


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="rlangc")
    parser.add_argument("--version", action="version", version=f"rlangc {__version__}")
    subparsers = parser.add_subparsers(dest="command", required=True)
    check_parser = subparsers.add_parser("check", help="Check a .rl file")
    check_parser.add_argument("path", type=Path)
    compile_parser = subparsers.add_parser("compile", help="Compile a .rl file to a native executable")
    compile_parser.add_argument("path", type=Path)
    compile_parser.add_argument("-o", "--output", type=Path, required=True)
    compile_parser.add_argument("--cc", default="cc")
    return parser


def _run_check(path: Path) -> int:
    source = path.read_text(encoding="utf-8")
    pipeline.run(source)
    print(f"{path}: OK")
    return 0


def _run_compile(path: Path, output: Path, cc: str) -> int:
    source = path.read_text(encoding="utf-8")
    module = pipeline.run(source)
    c_source = generate_c(module)
    with tempfile.NamedTemporaryFile("w", suffix=".c", encoding="utf-8", delete=False) as c_file:
        c_file.write(c_source)
        c_path = Path(c_file.name)
    try:
        subprocess.run([cc, str(c_path), "-O2", "-o", str(output)], check=True)
    finally:
        c_path.unlink(missing_ok=True)
    print(f"Built native executable: {output}")
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    if args.command == "check":
        return _run_check(args.path)
    if args.command == "compile":
        return _run_compile(args.path, args.output, args.cc)
    raise RuntimeError(f"Unsupported command: {args.command}")


if __name__ == "__main__":
    sys.exit(main())
