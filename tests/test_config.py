import io
import json
import os
import sys
import tempfile
from pathlib import Path
import unittest
from contextlib import chdir, redirect_stdout
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from plating_qc import cli
from plating_qc.core import executable


class ConfigTests(unittest.TestCase):
    def test_compare_search_uses_toml_and_creates_default_log(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config = root / "config.toml"
            config.write_text("[compare]\nsearch = 7\n", encoding="utf-8")
            with chdir(root), patch("plating_qc.cli.compare", return_value={"warnings": []}) as call, redirect_stdout(io.StringIO()):
                result = cli.main(["--config", str(config), "compare", "a", "b"])
            self.assertEqual(result, 0)
            self.assertEqual(call.call_args.args[3], 7)
            logs = list((root / "plating-qc-logs").glob("*.json"))
            self.assertEqual(len(logs), 1)
            self.assertEqual(json.loads(logs[0].read_text(encoding="utf-8"))["exit_code"], 0)

    def test_unsupported_backend_returns_four(self):
        with tempfile.TemporaryDirectory() as directory:
            with chdir(directory):
                self.assertEqual(cli.main(["--backend", "blender", "probe", "input.mp4"]), 4)

    def test_auto_log_uses_environment_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            logs = root / "test-logs"
            with chdir(root), patch.dict(os.environ, {"PLATING_QC_LOG_DIR": str(logs)}), patch("plating_qc.cli.compare", return_value={"warnings": []}), redirect_stdout(io.StringIO()):
                result = cli.main(["compare", "a", "b"])
            self.assertEqual(result, 0)
            self.assertEqual(len(list(logs.glob("*.json"))), 1)
            self.assertFalse((root / "plating-qc-logs").exists())

    def test_split_limit_uses_toml(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config = root / "config.toml"
            config.write_text("max_part_mb = 125\n", encoding="utf-8")
            with chdir(root), patch("plating_qc.cli.split", return_value={"warnings": []}) as call, redirect_stdout(io.StringIO()):
                result = cli.main(["--config", str(config), "split", "a.mov", "--out", "parts"])
            self.assertEqual(result, 0)
            self.assertEqual(call.call_args.args[3], 125)

    def test_ffmpeg_directory_supplies_ffprobe(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            suffix = ".exe" if os.name == "nt" else ""
            for name in ("ffmpeg", "ffprobe"):
                (root / (name + suffix)).touch()
            self.assertEqual(Path(executable("ffmpeg", {"ffmpeg_path": str(root)})), root / ("ffmpeg" + suffix))
            self.assertEqual(Path(executable("ffprobe", {"ffmpeg_path": str(root)})), root / ("ffprobe" + suffix))


if __name__ == "__main__":
    unittest.main()
