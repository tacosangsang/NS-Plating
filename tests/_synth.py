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


class QCFixture(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
            raise unittest.SkipTest("ffmpeg와 ffprobe가 필요합니다")

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.log_env = patch.dict(os.environ, {"PLATING_QC_LOG_DIR": str(Path(self.tmp.name) / "logs")})
        self.log_env.start()
        self.scene = Path(self.tmp.name) / "씬 공백"
        self.raw = self.scene / "raw"
        self.raw.mkdir(parents=True)

    def tearDown(self):
        self.log_env.stop()
        self.tmp.cleanup()

    def make_video(self, name, audio=None):
        path = self.raw / name
        cmd = ["ffmpeg", "-v", "error", "-f", "lavfi", "-i", "testsrc2=size=160x90:rate=24:duration=1"]
        if audio:
            cmd += ["-f", "lavfi", "-i", f"sine=frequency=440:duration={audio}"]
        cmd += ["-c:v", "mpeg4", "-q:v", "4", "-pix_fmt", "yuv420p"]
        if audio:
            cmd += ["-c:a", "aac"]
        subprocess.run(cmd + [str(path)], check=True)
        return path
