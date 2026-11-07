import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from plating_qc.core import probe
from plating_qc.review import tiles


class TileFallbackTests(unittest.TestCase):
    def test_font_failure_keeps_frame_numbers_in_manifest(self):
        if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
            self.skipTest("ffmpeg와 ffprobe가 필요합니다")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source.mp4"
            subprocess.run(["ffmpeg", "-v", "error", "-f", "lavfi", "-i",
                            "testsrc2=size=160x90:rate=24:duration=1",
                            "-c:v", "mpeg4", str(source)], check=True, capture_output=True)
            info = probe(source, {})
            real_run = subprocess.run
            failed = False

            def fail_font_once(args, **kwargs):
                nonlocal failed
                if not failed and any("drawtext=" in str(arg) for arg in args):
                    failed = True
                    return subprocess.CompletedProcess(args, 1, "", "Cannot find a valid font")
                return real_run(args, **kwargs)

            with patch("plating_qc.review.probe", return_value=info), patch("plating_qc.review.subprocess.run", side_effect=fail_font_once):
                report = tiles(source, root / "output", {}, cuts=[3])
            self.assertTrue(failed)
            self.assertEqual(report["label_mode"], "manifest")
            self.assertEqual(report["samples"][0]["frame"], 0)
            self.assertTrue((root / "output" / "manifest.json").is_file())


if __name__ == "__main__":
    unittest.main()
