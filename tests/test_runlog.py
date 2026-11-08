import os
import shutil
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from plating_qc.core import QCError, analyze_timestamps, convert, frame_timestamps, probe
from plating_qc.review import compare, mixed_frame_hint, tiles, write_comparison
from plating_qc.split import split
from _synth import QCFixture


class RunlogIntegration(QCFixture):
    def test_command_log_records_versions_result_and_argv(self):
        import json
        source = self.make_video("log_source.mp4")
        target = self.scene / "run.json"
        env = dict(os.environ, PYTHONPATH=str(Path(__file__).resolve().parents[1] / "src"), PYTHONDONTWRITEBYTECODE="1", QC_TEST_SECRET="not-for-log")
        args = ["--log", str(target), "probe", str(source)]
        run = subprocess.run([sys.executable, "-m", "plating_qc", *args], env=env, capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(run.returncode, 0, run.stderr)
        record = json.loads(target.read_text(encoding="utf-8"))
        self.assertEqual(record["exit_code"], 0)
        self.assertEqual(record["argv"], args)
        self.assertEqual(record["result"], json.loads(run.stdout))
        self.assertTrue(record["tools"]["ffmpeg"].startswith("ffmpeg version"))
        self.assertTrue(record["tools"]["ffprobe"].startswith("ffprobe version"))
        self.assertEqual(len(record["source_sha256"]["core.py"]), 64)
        self.assertIn("started_utc", record)
        self.assertGreaterEqual(record["duration_s"], 0)
        self.assertNotIn("not-for-log", target.read_text(encoding="utf-8"))
        self.assertTrue(source.exists())

    def test_command_log_records_error_without_changing_input(self):
        import json
        target = self.scene / "failure.json"
        missing = self.raw / "missing.mp4"
        env = dict(os.environ, PYTHONPATH=str(Path(__file__).resolve().parents[1] / "src"), PYTHONDONTWRITEBYTECODE="1")
        run = subprocess.run([sys.executable, "-m", "plating_qc", "--log", str(target), "probe", str(missing)], env=env, capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(run.returncode, 2, run.stderr)
        record = json.loads(target.read_text(encoding="utf-8"))
        self.assertEqual(record["exit_code"], 2)
        self.assertIn("입력 파일이 없습니다", record["error"])
        self.assertFalse(missing.exists())

    def test_command_log_rejects_existing_raw_and_new_output_folder(self):
        source = self.make_video("log_guard.mp4")
        env = dict(os.environ, PYTHONPATH=str(Path(__file__).resolve().parents[1] / "src"), PYTHONDONTWRITEBYTECODE="1")
        existing = self.scene / "existing.json"
        existing.write_text("keep", encoding="utf-8")
        run = subprocess.run([sys.executable, "-m", "plating_qc", "--log", str(existing), "probe", str(source)], env=env, capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(run.returncode, 3, run.stderr)
        self.assertEqual(existing.read_text(encoding="utf-8"), "keep")
        in_raw = self.raw / "forbidden.json"
        run = subprocess.run([sys.executable, "-m", "plating_qc", "--log", str(in_raw), "probe", str(source)], env=env, capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(run.returncode, 2, run.stderr)
        self.assertFalse(in_raw.exists())
        output = self.scene / "new_review"
        run = subprocess.run([sys.executable, "-m", "plating_qc", "--log", str(output / "run.json"), "tiles", str(source), "--out", str(output)], env=env, capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(run.returncode, 2, run.stderr)
        self.assertFalse(output.exists())
        self.assertTrue(source.exists())
