import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch
import os

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from plating_qc.core import probe
from plating_qc.review import tiles
from plating_qc.core import QCError, analyze_timestamps, convert, frame_timestamps, probe
from plating_qc.review import compare, mixed_frame_hint, tiles, write_comparison
from plating_qc.split import split
from _synth import QCFixture


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






class TilesIntegration(QCFixture):
    def test_tiles_report_original_frame_indices_and_pts(self):
        import json
        from fractions import Fraction
        source = self.raw / "timed.mp4"
        subprocess.run(["ffmpeg", "-v", "error", "-f", "lavfi", "-i", "testsrc2=size=320x180:rate=4:duration=2.5", "-vf", "setpts=PTS+2/TB", "-c:v", "mpeg4", str(source)], check=True)
        dest = self.scene / "timed_review"
        result = tiles(source, dest, {}, fps=1, width=320, columns=2, rows=1, cuts=[4], around=1)
        raw = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_frames", "-show_entries", "frame=best_effort_timestamp_time", "-of", "json", str(source)], check=True, capture_output=True, text=True)
        source_frames = json.loads(raw.stdout)["frames"]
        self.assertEqual([x["frame"] for x in result["samples"]], [0, 4, 8])
        for sample in result["samples"]:
            timestamp = float(source_frames[sample["frame"]]["best_effort_timestamp_time"])
            self.assertAlmostEqual(sample["seconds"], timestamp, places=5)
            self.assertAlmostEqual(float(sample["pts"] * Fraction(sample["time_base"])), timestamp, places=5)
        self.assertEqual(result["samples"][2]["tile"], "tiles_002.png")
        self.assertEqual(result["samples"][2]["cell"], 0)
        self.assertEqual([x["frame"] for x in result["cut_frames"]["4"]], [3, 4, 5])
        self.assertAlmostEqual(result["cut_frames"]["4"][1]["seconds"], 3.0, places=5)
        self.assertEqual(json.loads((dest / "manifest.json").read_text(encoding="utf-8"))["samples"], result["samples"])
        self.assertTrue((dest / "cut_000004_000003-000005.png").exists())

    def test_tiles_variable_timestamps_match_source_frames(self):
        import json
        source = self.raw / "vfr.mkv"
        subprocess.run(["ffmpeg", "-v", "error", "-f", "lavfi", "-i", "testsrc2=size=320x180:rate=4:duration=2.5", "-vf", "setpts=PTS+if(gte(N\\,4)\\,0.25/TB\\,0)", "-fps_mode", "vfr", "-c:v", "ffv1", str(source)], check=True)
        result = tiles(source, self.scene / "vfr_review", {}, fps=1, width=320, columns=3, rows=1)
        raw = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_frames", "-show_entries", "frame=best_effort_timestamp_time", "-of", "json", str(source)], check=True, capture_output=True, text=True)
        frames = json.loads(raw.stdout)["frames"]
        self.assertEqual([x["frame"] for x in result["samples"]], [0, 4, 8])
        for sample in result["samples"]:
            self.assertAlmostEqual(sample["seconds"], float(frames[sample["frame"]]["best_effort_timestamp_time"]), places=5)

    def test_tiles_scene_candidate_with_exact_frame_and_timestamp(self):
        import json
        source = self.raw / "scene.mkv"
        subprocess.run(["ffmpeg", "-v", "error", "-f", "lavfi", "-i", "color=black:s=160x90:r=24:d=0.5", "-f", "lavfi", "-i", "color=white:s=160x90:r=24:d=0.5", "-filter_complex", "[0:v][1:v]concat=n=2:v=1:a=0[out]", "-map", "[out]", "-c:v", "ffv1", str(source)], check=True)
        target = self.scene / "scene_review"
        result = tiles(source, target, {})
        self.assertEqual([x["frame"] for x in result["scene_candidates"]], [12])
        self.assertAlmostEqual(result["scene_candidates"][0]["seconds"], .5, places=3)
        self.assertIn("직접 확인", (target / "scene_candidates.txt").read_text(encoding="utf-8"))
        saved = json.loads((target / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(saved["scene_candidates"], result["scene_candidates"])
        high_threshold = tiles(source, self.scene / "strict_review", {}, scene_threshold=1.0)
        self.assertEqual(high_threshold["scene_candidates"], [])
        self.assertTrue(source.is_file())

    def test_tiles_create_cut_and_do_not_overwrite(self):
        source = self.make_video("tile.mp4")
        dest = self.scene / "review"
        result = tiles(source, dest, {}, cuts=[12], around=1)
        self.assertIn("cut_000012_000011-000013.png", result["files"])
        self.assertTrue((dest / "tiles_001.png").is_file())
        self.assertTrue((dest / "manifest.json").is_file())
        before = (dest / "manifest.json").read_bytes()
        with self.assertRaises(QCError) as exc:
            tiles(source, dest, {})
        self.assertEqual(exc.exception.code, 3)
        self.assertEqual((dest / "manifest.json").read_bytes(), before)
        with self.assertRaises(QCError) as exc:
            tiles(source, self.raw / "review", {})
        self.assertEqual(exc.exception.code, 2)

    def test_tiles_rejects_invalid_raw_config(self):
        source = self.make_video("invalid_layout.mp4")
        target = self.raw / "review"
        with self.assertRaises(QCError) as exc:
            tiles(source, target, {"layout": {"raw": "raw/"}})
        self.assertEqual(exc.exception.code, 2)
        self.assertFalse(target.exists())
        config = self.scene / "invalid_layout.toml"
        config.write_text('[layout]\nraw = "raw/"\n', encoding="utf-8")
        env = dict(os.environ, PYTHONPATH=str(Path(__file__).resolve().parents[1] / "src"), PYTHONDONTWRITEBYTECODE="1")
        result = subprocess.run([sys.executable, "-m", "plating_qc", "--config", str(config), "tiles", str(source), "--out", str(target)], env=env, capture_output=True, text=True)
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertFalse(target.exists())

    def test_tiles_percent_sign_in_output_path(self):
        source = self.make_video("percent.mp4")
        target = self.scene / "review%03d"
        sibling = self.scene / "review001"
        sibling.mkdir()
        sentinel = sibling / "keep.txt"
        sentinel.write_text("기존 파일", encoding="utf-8")
        result = tiles(source, target, {}, cuts=[12], around=1)
        self.assertTrue((target / "tiles_001.png").is_file())
        self.assertTrue((target / "cut_000012_000011-000013.png").is_file())
        self.assertIn("tiles_001.png", result["files"])
        self.assertEqual(list(sibling.iterdir()), [sentinel])
        self.assertEqual(sentinel.read_text(encoding="utf-8"), "기존 파일")

    def test_tiles_encoder_failure_cleans_partial_output(self):
        source = self.make_video("encoder.mp4")
        target = self.scene / "failed%03d"
        source_info = probe(source, {})
        def fail_after_writing(args, cwd, **kwargs):
            (Path(cwd) / "tiles_001.png").write_bytes(b"partial")
            return subprocess.CompletedProcess(args, 1, "", "인코더 실패")
        with patch("plating_qc.review.probe", return_value=source_info), patch("plating_qc.review.subprocess.run", side_effect=fail_after_writing):
            with self.assertRaises(QCError) as exc:
                tiles(source, target, {})
        self.assertEqual(exc.exception.code, 5)
        self.assertFalse(target.exists())
        self.assertFalse((self.scene / "failed001").exists())
        self.assertTrue(source.exists())

    def test_tiles_missing_timestamps_do_not_publish(self):
        source = self.make_video("missing_pts.mp4")
        target = self.scene / "missing_pts_review"
        source_info = probe(source, {})
        def no_timestamps(args, cwd, **kwargs):
            (Path(cwd) / "tiles_001.png").write_bytes(b"fake")
            return subprocess.CompletedProcess(args, 0, "", "[showinfo@source] config in time_base: 1/24\n[showinfo@source] n: 0 pts: NOPTS pts_time:NOPTS\n")
        with patch("plating_qc.review.probe", return_value=source_info), patch("plating_qc.review.subprocess.run", side_effect=no_timestamps):
            with self.assertRaises(QCError) as exc:
                tiles(source, target, {})
        self.assertEqual(exc.exception.code, 5)
        self.assertFalse(target.exists())
        self.assertTrue(source.exists())

    def test_scene_detection_failure_cleans_all_temporary_output(self):
        source = self.make_video("scene_fail.mp4")
        target = self.scene / "scene_failure"
        source_info = probe(source, {})
        def fail_on_scene(args, cwd, **kwargs):
            if "showinfo@scene" in " ".join(args):
                return subprocess.CompletedProcess(args, 1, "", "scene error")
            (Path(cwd) / "tiles_001.png").write_bytes(b"partial")
            logs = ["[showinfo@source] config in time_base: 1/24"]
            logs += [f"[showinfo@source] n: {i} pts: {i} pts_time:" for i in range(24)]
            logs += ["[showinfo@selected] n: 0 pts: 0 pts_time:"]
            return subprocess.CompletedProcess(args, 0, "", "\n".join(logs))
        with patch("plating_qc.review.probe", return_value=source_info), patch("plating_qc.review.subprocess.run", side_effect=fail_on_scene):
            with self.assertRaises(QCError) as exc:
                tiles(source, target, {})
        self.assertEqual(exc.exception.code, 5)
        self.assertFalse(target.exists())
        self.assertTrue(source.is_file())

    def test_tiles_invalid_frame_does_not_create_folder(self):
        source = self.make_video("tile_bad.mp4")
        dest = self.scene / "review"
        with self.assertRaises(QCError) as exc:
            tiles(source, dest, {}, cuts=[24])
        self.assertEqual(exc.exception.code, 2)
        self.assertFalse(dest.exists())
