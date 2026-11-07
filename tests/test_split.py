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


class SplitIntegration(QCFixture):
    def test_split_prores_verifies_all_frames_and_preserves_existing(self):
        source = self.make_video("split.mp4", "0.4")
        converted = Path(convert(source, None, {})["output"]["path"])
        size = converted.stat().st_size
        target = self.scene / "parts%03d"
        result = split(converted, target, {}, max_part_mb=size / (1024 * 1024) * .55)
        self.assertGreaterEqual(len(result["parts"]), 2)
        self.assertEqual(result["frames_verified"], 24)
        self.assertFalse(result["audio_boundary_verified"])
        self.assertTrue(result["warnings"])
        self.assertTrue(all(x["audio_timing_first_stream"] is not None for x in result["parts"]))
        self.assertEqual(sum(x["frames"] for x in result["parts"]), 24)
        def pcm(path):
            return subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-map", "0:a:0", "-f", "s16le", "-"], check=True, capture_output=True).stdout
        self.assertEqual(pcm(converted), b"".join(pcm(target / x["file"]) for x in result["parts"]))
        self.assertTrue(all((target / x["file"]).stat().st_size <= result["limit_bytes"] for x in result["parts"]))
        manifest = (target / "manifest.json").read_bytes()
        with self.assertRaises(QCError) as exc:
            split(converted, target, {})
        self.assertEqual(exc.exception.code, 3)
        self.assertEqual((target / "manifest.json").read_bytes(), manifest)
        self.assertTrue(converted.exists())

    def test_split_cli_warns_if_audio_boundary_unverified(self):
        source = self.make_video("warning.mp4", "0.4")
        converted = Path(convert(source, None, {})["output"]["path"])
        dest = self.scene / "warning_parts"
        env = dict(os.environ, PYTHONPATH=str(Path(__file__).resolve().parents[1] / "src"), PYTHONDONTWRITEBYTECODE="1")
        p = subprocess.run([sys.executable, "-m", "plating_qc", "split", str(converted), "--out", str(dest)], env=env, capture_output=True, text=True)
        self.assertEqual(p.returncode, 1, p.stderr)
        import json
        result = json.loads(p.stdout)
        self.assertFalse(result["audio_boundary_verified"])
        self.assertTrue(result["warnings"])
        self.assertTrue((dest / "manifest.json").is_file())

    def test_split_frame_mismatch_removes_partial_output(self):
        source = self.make_video("split_fail.mp4")
        converted = Path(convert(source, None, {})["output"]["path"])
        target = self.scene / "bad_parts"
        with patch("plating_qc.split.frame_hashes", return_value=["0" * 32]):
            with self.assertRaises(QCError) as exc:
                split(converted, target, {})
        self.assertEqual(exc.exception.code, 1)
        self.assertFalse(target.exists())
        self.assertTrue(converted.exists())

    def test_split_rejects_non_prores_and_raw_output(self):
        source = self.make_video("not_prores.mp4")
        target = self.scene / "parts"
        with self.assertRaises(QCError) as exc:
            split(source, target, {})
        self.assertEqual(exc.exception.code, 2)
        self.assertFalse(target.exists())
        converted = Path(convert(source, None, {})["output"]["path"])
        with self.assertRaises(QCError) as exc:
            split(converted, self.raw / "parts", {})
        self.assertEqual(exc.exception.code, 2)
        self.assertFalse((self.raw / "parts").exists())
