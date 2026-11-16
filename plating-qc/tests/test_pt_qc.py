"""SYNTH: Q1~Q6. 실제 QC 대신 하위 프로세스 경계에 가짜를 주입한다."""
import ast
import importlib
import io
import json
import os
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch
from uuid import uuid4

from tests._pt_support import NetworkBlockedCase

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))


class QcTests(NetworkBlockedCase):
    def setUp(self):
        super().setUp()
        self.api = importlib.import_module("plating_tools.qc")
        self.errors = importlib.import_module("plating_tools.errors")
        self.root = REPO / "out" / "pt-tests" / uuid4().hex
        self.inputs = self.root / "inputs"
        self.inputs.mkdir(parents=True)
        self.input = self.inputs / "SYNTH input.mov"
        self.input.write_bytes(b"SYNTH")
        self.work = self.root / "work"

    def runner(self):
        return self.api.SubprocessQcRunner(sys.executable)

    def test_Q1_array_shell_false_absolute_inputs_and_no_import(self):
        with patch("plating_tools.qc.subprocess.run", return_value=subprocess.CompletedProcess([], 0, b"[]", b"")) as process:
            result = self.runner().run("probe", [str(self.input), "--json"], work_dir=self.work, timeout_s=10)
        argv = process.call_args.args[0]
        self.assertIsInstance(argv, list)
        self.assertEqual(argv[:3], [sys.executable, "-m", "plating_qc"])
        self.assertIs(process.call_args.kwargs["shell"], False)
        self.assertIn(str(self.input.resolve()), argv)
        self.assertEqual(result.exit_code, 0)
        for path in (REPO / "src" / "plating_tools").rglob("*.py"):
            for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
                names = [a.name for a in node.names] if isinstance(node, ast.Import) else [node.module or ""] if isinstance(node, ast.ImportFrom) else []
                self.assertFalse(any(n == "plating_qc" or n.startswith("plating_qc.") for n in names), path)

    def test_Q2_logs_cwd_and_only_two_environment_overrides(self):
        with patch("plating_tools.qc.subprocess.run", return_value=subprocess.CompletedProcess([], 0, b"[]", b"")) as process:
            result = self.runner().run("probe", [str(self.input)], work_dir=self.work, timeout_s=10)
        argv = process.call_args.args[0]
        environment = process.call_args.kwargs["env"]
        self.assertTrue(Path(argv[argv.index("--log") + 1]).is_relative_to(self.work))
        self.assertTrue(Path(environment["PLATING_QC_LOG_DIR"]).is_relative_to(self.work))
        self.assertEqual(process.call_args.kwargs["cwd"], self.work)
        self.assertEqual(environment, {**os.environ, "PLATING_QC_LOG_DIR": str(self.work / "log"), "PYTHONIOENCODING": "utf-8"})
        self.assertEqual(set(result.env_set), {"PLATING_QC_LOG_DIR", "PYTHONIOENCODING"})

    def fake_process(self, code=1, stdout=b'{"uncertain":true}', stderr=b"SYNTH\xff"):
        def run(argv, **kwargs):
            work = Path(kwargs["cwd"])
            out = work / "out"
            out.mkdir()
            (out / "SYNTH.txt").write_bytes(b"SYNTH result")
            (work / "log" / "qc.log").write_bytes(b"SYNTH log")
            return subprocess.CompletedProcess(argv, code, stdout, stderr)
        return run

    def test_Q3_exit_one_bytes_and_artifacts_are_preserved(self):
        with patch("plating_tools.qc.subprocess.run", side_effect=self.fake_process()):
            result = self.runner().run("compare", [str(self.input), str(self.input)], work_dir=self.work, timeout_s=10)
        self.assertEqual(result.exit_code, 1)
        self.assertEqual(Path(result.stdout_path).read_bytes(), b'{"uncertain":true}')
        self.assertEqual(Path(result.stderr_path).read_bytes(), b"SYNTH\xff")
        self.assertTrue(result.stdout_is_json)
        self.assertIn("out/SYNTH.txt", {p for p, size, digest in result.produced})
        self.assertEqual(result.input_dir_changes, ())

    def test_Q4_exit_four_and_five_meanings(self):
        for code in (4, 5):
            with patch("plating_tools.qc.subprocess.run", return_value=subprocess.CompletedProcess([], code, b"", b"SYNTH")):
                result = self.runner().run("probe", [str(self.input)], work_dir=self.root / str(code), timeout_s=10)
            self.assertEqual(result.exit_code, code)
            self.assertEqual(result.exit_meaning, self.api.EXIT_MEANINGS[code])

    def test_Q4_timeout_keeps_partial_bytes_and_maps_to_five(self):
        with patch("plating_tools.qc.subprocess.run", side_effect=subprocess.TimeoutExpired([], 1, output=b"SYNTH partial", stderr=b"SYNTH error")):
            result = self.runner().run("probe", [str(self.input)], work_dir=self.work, timeout_s=1)
        self.assertIsNone(result.exit_code)
        self.assertEqual(Path(result.stdout_path).read_bytes(), b"SYNTH partial")
        self.assertEqual(self.api.result_code(result), 5)

    def test_Q5_convert_without_dry_run_is_rejected_before_spawn(self):
        with patch("plating_tools.qc.subprocess.run") as process, self.assertRaises(self.errors.InputError):
            self.runner().run("convert", [str(self.input)], work_dir=self.work, timeout_s=10)
        process.assert_not_called()
        self.assertFalse(self.work.exists())

    def test_Q5_convert_with_dry_run_has_no_output_argument(self):
        with patch("plating_tools.qc.subprocess.run", return_value=subprocess.CompletedProcess([], 0, b"{}", b"")) as process:
            self.runner().run("convert", [str(self.input), "--dry-run"], work_dir=self.work, timeout_s=10)
        argv = process.call_args.args[0]
        self.assertIn("--dry-run", argv)
        self.assertNotIn("--out", argv)

    def test_Q6_child_output_config_and_log_options_are_rejected(self):
        for flag in ("--out", "--out=x", "--log", "--log=x", "--config", "--config=x"):
            with patch("plating_tools.qc.subprocess.run") as process, self.assertRaises(self.errors.InputError):
                self.runner().run("probe", [str(self.input), flag], work_dir=self.work, timeout_s=10)
            process.assert_not_called()

    def cli(self, *extra):
        cfg = self.root / "plating.toml"
        cfg.write_text("[paths]\nwrite_root='.'\noutput_root='out'\n", encoding="utf-8")
        cli = importlib.import_module("plating_tools.cli")
        stdout = io.StringIO()
        with patch("sys.stdout", stdout), patch("sys.stderr", io.StringIO()):
            code = cli.main(["--config", str(cfg), "qc", "probe", str(self.input), *extra])
        return code, stdout.getvalue()

    def test_cli_exit_one_publishes_child_result_unchanged(self):
        with patch("plating_tools.qc.subprocess.run", side_effect=self.fake_process()):
            code, stdout = self.cli()
        self.assertEqual(code, 1)
        output = Path(json.loads(stdout)["output"])
        data = json.loads((output / "qc.json").read_text(encoding="utf-8"))
        self.assertEqual(data["exit_code"], 1)
        self.assertEqual((output / data["stdout_path"]).read_bytes(), b'{"uncertain":true}')
        self.assertTrue(all((output / p).is_file() for p in data["log_paths"]))
        self.assertTrue(all((output / p).is_file() for p, size, digest in data["produced"]))

    def test_cli_exit_four_five_and_timeout_are_quarantined(self):
        for effect, code in ((self.fake_process(4), 4), (self.fake_process(5), 5), (subprocess.TimeoutExpired([], 1), 5)):
            with patch("plating_tools.qc.subprocess.run", side_effect=effect):
                status, stdout = self.cli()
            self.assertEqual(status, code)
            self.assertEqual(stdout, "")
        failed = list((self.root / "out" / "_failed").glob("*/qc.json"))
        self.assertEqual(len(failed), 3)

    def test_input_directory_change_is_reported(self):
        def mutate(argv, **kwargs):
            (self.inputs / "SYNTH unexpected.txt").write_bytes(b"SYNTH")
            return subprocess.CompletedProcess(argv, 0, b"{}", b"")
        with patch("plating_tools.qc.subprocess.run", side_effect=mutate):
            result = self.runner().run("probe", [str(self.input)], work_dir=self.work, timeout_s=10)
        self.assertEqual(len(result.input_dir_changes), 1)

    def test_missing_child_module_is_four_with_native_exit_one_recorded(self):
        with patch("plating_tools.qc.subprocess.run", return_value=subprocess.CompletedProcess([], 1, b"", b"python: No module named plating_qc\n")):
            result = self.runner().run("probe", [str(self.input)], work_dir=self.work, timeout_s=10)
        self.assertEqual(result.exit_code, 1)
        self.assertEqual(self.api.result_code(result), 4)

    def test_child_config_precedes_command_and_is_not_a_user_argument(self):
        config = self.root / "SYNTH-qc.toml"
        config.write_text("backend='SYNTH'\n", encoding="utf-8")
        runner = self.api.SubprocessQcRunner(sys.executable, config)
        with patch("plating_tools.qc.subprocess.run", return_value=subprocess.CompletedProcess([], 0, b"[]", b"")) as process:
            runner.run("probe", [str(self.input)], work_dir=self.work, timeout_s=10)
        argv = process.call_args.args[0]
        self.assertEqual(argv[3:5], ["--config", str(config)])
        self.assertLess(argv.index("--config"), argv.index("probe"))
