import sys
from pathlib import Path
import unittest
import os
import shutil
import subprocess
import tempfile
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from plating_qc.backend.base import MediaBackend
from plating_qc.errors import QCError
from plating_qc.layout import SceneLayout, checked_path
from plating_qc.core import QCError, analyze_timestamps, convert, frame_timestamps, probe
from plating_qc.review import compare, mixed_frame_hint, tiles, write_comparison
from plating_qc.split import split
from _synth import QCFixture


class LayoutTests(unittest.TestCase):
    def test_default_names(self):
        self.assertEqual(SceneLayout.from_config({}).names(), ("raw", "prores"))

    def test_rejects_same_raw_and_prores(self):
        with self.assertRaises(QCError) as caught:
            SceneLayout.from_config({"layout": {"raw": "raw", "prores": "RAW"}})
        self.assertEqual(caught.exception.code, 2)

    def test_unsupported_backend_method_is_exit_four(self):
        with self.assertRaises(QCError) as caught:
            MediaBackend().probe(Path("video.mp4"))
        self.assertEqual(caught.exception.code, 4)

    def test_long_path_is_usage_error(self):
        with self.assertRaises(QCError) as caught:
            checked_path(Path("a" * 241))
        self.assertEqual(caught.exception.code, 2)






class LayoutIntegration(QCFixture):
    def test_layout_must_be_table(self):
        source = self.make_video("config.mp4")
        with self.assertRaises(QCError) as exc:
            convert(source, None, {"layout": "raw"})
        self.assertEqual(exc.exception.code, 2)
        self.assertFalse((self.scene / "prores").exists())
        config = self.scene / "bad.toml"
        config.write_text('layout = "raw"\n', encoding="utf-8")
        env = dict(os.environ, PYTHONPATH=str(Path(__file__).resolve().parents[1] / "src"), PYTHONDONTWRITEBYTECODE="1")
        result = subprocess.run([sys.executable, "-m", "plating_qc", "--config", str(config), "convert", str(source)], env=env, capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertNotIn("Traceback", result.stderr)
