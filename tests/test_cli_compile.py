import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import cli


class CliCompileTests(unittest.TestCase):
    def test_parser_supports_compile_command(self) -> None:
        parser = cli._build_parser()
        args = parser.parse_args(["compile", "program.rl", "-o", "program"])
        self.assertEqual(args.command, "compile")
        self.assertEqual(args.path, Path("program.rl"))
        self.assertEqual(args.output, Path("program"))
        self.assertEqual(args.cc, "cc")

    @patch("cli.subprocess.run")
    def test_run_compile_invokes_c_compiler(self, mock_run) -> None:
        with tempfile.TemporaryDirectory() as td:
            source_path = Path(td) / "program.rl"
            source_path.write_text("let x = 1", encoding="utf-8")
            output_path = Path(td) / "program"
            exit_code = cli._run_compile(source_path, output_path, "cc")
        self.assertEqual(exit_code, 0)
        mock_run.assert_called_once()
        command = mock_run.call_args[0][0]
        self.assertEqual(command[0], "cc")
        self.assertEqual(command[-3:], ["-O2", "-o", str(output_path)])


if __name__ == "__main__":
    unittest.main()
