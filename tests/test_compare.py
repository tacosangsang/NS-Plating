import sys
import json
import os
import random
import shutil
import subprocess
import tempfile
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from plating_qc.review import compare, normalized_distance


class CompareTests(unittest.TestCase):
    def test_brightness_and_contrast_are_normalized(self):
        original = bytes((10, 30, 50, 70, 90, 110))
        candidate = bytes((50, 60, 70, 80, 90, 100))
        self.assertLess(normalized_distance(original, candidate), 0.000001)

    def test_different_frames_remain_different(self):
        self.assertGreater(normalized_distance(bytes((0, 40, 80, 120)), bytes((120, 80, 40, 0))), 0.15)


class CompareScenarios(unittest.TestCase):
    def setUp(self):
        if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
            self.skipTest("ffmpeg와 ffprobe가 필요합니다")
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.frames = [random.Random(i).randbytes(64 * 36) for i in range(48)]
        self.source = self.video("source", self.frames)

    def video(self, name, frames):
        path = self.root / (name + ".mkv")
        subprocess.run(["ffmpeg", "-v", "error", "-f", "rawvideo", "-pix_fmt", "gray",
                        "-s", "64x36", "-r", "24", "-i", "-", "-c:v", "ffv1",
                        "-pix_fmt", "gray", str(path)], input=b"".join(frames),
                       check=True, capture_output=True)
        return path

    def test_head2(self):
        candidate = self.video("head2", self.frames[2:])
        report = compare(self.source, candidate, {}, search=12)
        self.assertEqual(report["alignment"]["estimated_missing_head"], 2)

    def test_tail11(self):
        candidate = self.video("tail11", self.frames[:-11])
        report = compare(self.source, candidate, {}, search=12)
        self.assertEqual(report["alignment"]["estimated_missing_tail"], 11)

    def test_other_clip(self):
        other = self.video("other_clip", [random.Random(i + 1000).randbytes(64 * 36) for i in range(48)])
        env = os.environ.copy()
        env["PYTHONPATH"] = str(Path(__file__).resolve().parents[1] / "src")
        result = subprocess.run([sys.executable, "-m", "plating_qc", "compare", str(self.source),
                                 str(other)], env=env, capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        report = json.loads(result.stdout)
        self.assertIsNone(report["alignment"]["estimated_missing_head"])
        self.assertIsNone(report["alignment"]["estimated_missing_tail"])


if __name__ == "__main__":
    unittest.main()
