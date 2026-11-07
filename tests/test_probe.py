import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from plating_qc.core import QCError, probe, run
from plating_qc.backend.ffmpeg import FfmpegBackend
from plating_qc.model import MediaInfo


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

        with patch("plating_qc.core.run", side_effect=error_result):
            with self.assertRaises(QCError) as caught:
                probe(self.source, {})
        self.assertEqual(caught.exception.code, 5)


if __name__ == "__main__":
    unittest.main()
