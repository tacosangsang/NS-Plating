import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch
import os

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from plating_qc.core import QCError, probe, run
from plating_qc.backend.ffmpeg import FfmpegBackend
from plating_qc.model import MediaInfo
from plating_qc.core import QCError, analyze_timestamps, convert, frame_timestamps, probe
from plating_qc.review import compare, mixed_frame_hint, tiles, write_comparison
from plating_qc.split import split
from _synth import QCFixture


class ProbeTests(unittest.TestCase):
    def setUp(self):
        if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
            self.skipTest("ffmpeg와 ffprobe가 필요합니다")
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.source = Path(self.directory.name) / "sample.mp4"
        subprocess.run(["ffmpeg", "-v", "error", "-f", "lavfi", "-i",
                        "testsrc2=size=160x90:rate=24:duration=1", "-c:v", "mpeg4", str(self.source)],
                       check=True, capture_output=True)

    def test_reports_packet_count(self):
        info = probe(self.source, {})
        self.assertEqual(info["video"]["nb_read_packets"], 24)

    def test_backend_returns_media_info(self):
        info = FfmpegBackend({}).probe(self.source)
        self.assertIsInstance(info, MediaInfo)
        self.assertEqual(info.video.nb_frames_decoded, 24)

    def test_decode_error_is_exit_five(self):
        def error_result(args):
            result = run(args)
            result.stderr = "error decoding frame"
            return result

        with patch("plating_qc.backend.ffmpeg.run", side_effect=error_result):
            with self.assertRaises(QCError) as caught:
                probe(self.source, {})
        self.assertEqual(caught.exception.code, 5)






class ProbeIntegration(QCFixture):
    def test_timestamp_analysis_detects_vfr_even_if_rates_match(self):
        source = self.raw / "synthetic_pts"
        with patch("plating_qc.backend.ffmpeg_helpers.frame_timestamps", return_value=[0, .04, .08, .18, .22]):
            result = analyze_timestamps(source, "ffprobe", 5, "25/1", "25/1")
        self.assertEqual(result["status"], "observed")
        self.assertTrue(result["vfr_suspect"])
        self.assertFalse(result["rates_differ"])
        self.assertGreater(result["interval_stddev_s"], .002)

    def test_timestamp_missing_recovery_is_never_claimed_original(self):
        source = self.raw / "synthetic_pts"
        with patch("plating_qc.backend.ffmpeg_helpers.frame_timestamps", side_effect=[[None, None], [0, .04]]) as reader:
            result = analyze_timestamps(source, "ffprobe", 2, "25/1", "25/1")
        self.assertEqual(result["status"], "generated")
        self.assertEqual(result["missing_count"], 2)
        self.assertIsNone(result["vfr_suspect"])
        self.assertTrue(reader.call_args_list[1].kwargs["generated"])
        with patch("plating_qc.backend.ffmpeg_helpers.frame_timestamps", side_effect=[[None, None], [None, None]]):
            result = analyze_timestamps(source, "ffprobe", 2, "25/1", "25/1")
        self.assertEqual(result["status"], "unavailable")
        self.assertIsNone(result["vfr_suspect"])

    def test_timestamp_absent_h264_refuses_unsafe_convert(self):
        encoders = subprocess.run(["ffmpeg", "-hide_banner", "-encoders"], capture_output=True, text=True, check=True).stdout
        if "libx264" not in encoders:
            self.skipTest("합성 H.264 인코더가 없습니다")
        source = self.raw / "missing_pts.h264"
        subprocess.run(["ffmpeg", "-v", "error", "-f", "lavfi", "-i", "testsrc2=size=160x90:rate=24:duration=1", "-c:v", "libx264", "-f", "h264", str(source)], check=True)
        result = probe(source, {})
        self.assertEqual(result["timestamp_analysis"]["status"], "unavailable")
        self.assertEqual(result["timestamp_analysis"]["missing_count"], 24)
        self.assertTrue(result["warnings"])
        with self.assertRaises(QCError) as exc:
            convert(source, None, {})
        self.assertEqual(exc.exception.code, 2)
        self.assertFalse((self.scene / "prores").exists())
        self.assertTrue(source.is_file())
        with self.assertRaises(QCError) as exc:
            tiles(source, self.scene / "no_pts_review", {})
        self.assertEqual(exc.exception.code, 2)
        self.assertFalse((self.scene / "no_pts_review").exists())
        comparison = compare(source, source, {}, search=2)
        self.assertTrue(comparison["alignment"]["uncertain"])
        self.assertIsNone(comparison["alignment"]["estimated_missing_head"])
