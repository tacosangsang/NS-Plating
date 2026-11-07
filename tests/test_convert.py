import sys
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch
import os
import shutil
import subprocess

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from plating_qc.errors import QCError
from plating_qc.publish import publish
from plating_qc.core import QCError, analyze_timestamps, convert, frame_timestamps, probe
from plating_qc.review import compare, mixed_frame_hint, tiles, write_comparison
from plating_qc.split import split
from _synth import QCFixture


class PublishTests(unittest.TestCase):
    def test_existing_target_is_not_replaced(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "source"
            target = Path(directory) / "target"
            source.write_text("new")
            target.write_text("old")
            with self.assertRaises(QCError) as caught:
                publish(source, target)
            self.assertEqual(caught.exception.code, 3)
            self.assertEqual(target.read_text(), "old")

    @unittest.skipUnless(sys.platform == "win32", "Windows rename fallback")
    def test_windows_falls_back_when_hardlink_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "source"
            target = Path(directory) / "target"
            source.write_text("data")
            with patch("plating_qc.publish.os.link", side_effect=OSError("unsupported")):
                publish(source, target)
            self.assertEqual(target.read_text(), "data")

    @unittest.skipUnless(sys.platform == "win32", "Windows rename fallback")
    def test_windows_fallback_keeps_existing_target(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "source"
            target = Path(directory) / "target"
            source.write_text("new")
            target.write_text("old")
            with patch("plating_qc.publish.os.link", side_effect=OSError("unsupported")):
                with self.assertRaises(QCError) as caught:
                    publish(source, target)
            self.assertEqual(caught.exception.code, 3)
            self.assertEqual(target.read_text(), "old")






class ConvertIntegration(QCFixture):
    def test_probe_and_convert_without_audio_and_collision(self):
        source = self.make_video("원본.mp4")
        self.assertEqual(probe(source, {})["video"]["nb_frames_decoded"], 24)
        output = convert(source, None, {})["output"]
        self.assertEqual(output["video"]["nb_frames_decoded"], 24)
        self.assertEqual(output["video"]["profile"], "HQ")
        self.assertEqual(output["video"]["color"], {"primaries": "bt709", "transfer": "bt709", "space": "bt709"})
        self.assertIsNone(output["audio"])
        out = Path(output["path"])
        before = out.read_bytes()
        with self.assertRaises(QCError) as exc:
            convert(source, None, {})
        self.assertEqual(exc.exception.code, 3)
        self.assertEqual(out.read_bytes(), before)
        self.assertFalse(list(out.parent.glob("*.partial.mov")))

    def test_short_audio_is_padded(self):
        source = self.make_video("short.mp4", "0.4")
        output = convert(source, None, {})["output"]
        self.assertEqual(output["video"]["nb_frames_decoded"], 24)
        self.assertGreaterEqual(float(output["audio"]["duration_s"]), .999)

    def test_raw_output_and_invalid_suffix_rejected(self):
        source = self.make_video("test.mp4")
        for scene, config, suffix in [(self.raw, {}, ""), (None, {}, "_../oops"), (None, {"layout": {"prores": "raw"}}, "")]:
            with self.assertRaises(QCError) as exc:
                convert(source, scene, config, suffix)
            self.assertEqual(exc.exception.code, 2)

    def test_corrupt_file_fails_without_output(self):
        source = self.raw / "broken.mp4"
        source.write_bytes(b"not a media file")
        with self.assertRaises(QCError) as exc:
            convert(source, None, {})
        self.assertEqual(exc.exception.code, 5)
        self.assertFalse((self.scene / "prores").exists())

    def test_prores_path_is_file_returns_storage_error(self):
        source = self.make_video("blocked.mp4")
        (self.scene / "prores").write_text("기존 파일", encoding="utf-8")
        with self.assertRaises(QCError) as exc:
            convert(source, None, {})
        self.assertEqual(exc.exception.code, 5)
        self.assertEqual((self.scene / "prores").read_text(encoding="utf-8"), "기존 파일")
        env = dict(os.environ, PYTHONPATH=str(Path(__file__).resolve().parents[1] / "src"), PYTHONDONTWRITEBYTECODE="1")
        result = subprocess.run([sys.executable, "-m", "plating_qc", "convert", str(source)], env=env, capture_output=True, text=True)
        self.assertEqual(result.returncode, 5, result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_generated_pts_convert_uses_genpts_option(self):
        source = self.make_video("genpts_option.mp4")
        info = probe(source, {})
        info["timestamp_analysis"]["status"] = "generated"
        with patch("plating_qc.core.probe", return_value=info):
            result = convert(source, None, {}, dry_run=True)
        self.assertIn("-fflags", result["command"])
        self.assertIn("+genpts", result["command"])

    def test_convert_reports_absolute_start_shift(self):
        source = self.raw / "offset_start.mp4"
        subprocess.run(["ffmpeg", "-v", "error", "-f", "lavfi", "-i", "testsrc2=size=160x90:rate=24:duration=1", "-vf", "setpts=PTS+2/TB", "-c:v", "mpeg4", str(source)], check=True)
        output = convert(source, None, {})
        self.assertAlmostEqual(float(output["input"]["video"]["start_time_s"]), 2.0, places=3)
        self.assertAlmostEqual(float(output["output"]["video"]["start_time_s"]), 0.0, places=3)
        self.assertTrue(any("절대 시작 시각" in x for x in output["warnings"]))
        self.assertEqual(output["output"]["video"]["nb_frames_decoded"], 24)

    def test_convert_warns_on_audio_start_offset_change(self):
        source = self.make_video("audio_start.mp4", "1")
        from plating_qc import core
        real_probe = core.probe
        calls = 0
        def shift_output_audio(path, config):
            nonlocal calls
            info = real_probe(path, config)
            calls += 1
            if calls == 2:
                info["audio"]["start_time_s"] = str(float(info["audio"]["start_time_s"]) + .1)
            return info
        with patch("plating_qc.core.probe", side_effect=shift_output_audio):
            result = convert(source, None, {})
        self.assertTrue(any("상대 시작 시각이 달라졌습니다" in x for x in result["warnings"]))
        self.assertTrue(Path(result["output"]["path"]).exists())

    def test_convert_checks_relative_pts_and_cleans_mismatch(self):
        source = self.make_video("pts_compare.mp4")
        target_dir = self.scene / "prores"
        from plating_qc import core
        real = core.frame_timestamps
        def alter_only_final(path, ffprobe, generated=False):
            values = real(path, ffprobe, generated)
            if str(path).endswith(".partial.mov") and len(values) > 2:
                values[-1] += .1
            return values
        with patch("plating_qc.backend.ffmpeg.frame_timestamps", side_effect=alter_only_final):
            with self.assertRaises(QCError) as exc:
                convert(source, None, {})
        self.assertEqual(exc.exception.code, 1)
        self.assertIn("PTS", str(exc.exception))
        self.assertFalse(list(target_dir.glob("*.mov")))
        self.assertTrue(source.exists())

    def test_missing_input_and_dry_run(self):
        with self.assertRaises(QCError) as exc:
            probe(self.raw / "missing.mp4", {})
        self.assertEqual(exc.exception.code, 2)
        source = self.make_video("dry.mp4")
        result = convert(source, None, {}, dry_run=True)
        self.assertFalse(Path(result["output"]).exists())
        self.assertFalse((self.scene / "prores").exists())
