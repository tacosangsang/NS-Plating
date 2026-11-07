import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from plating_qc.core import QCError, convert, probe
from plating_qc.review import compare, tiles, write_comparison
from plating_qc.split import split


class QCIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import shutil
        if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
            raise unittest.SkipTest("ffmpeg와 ffprobe가 필요합니다")

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.scene = Path(self.tmp.name) / "씬 공백"
        self.raw = self.scene / "raw"
        self.raw.mkdir(parents=True)

    def tearDown(self):
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

    def test_layout_must_be_table(self):
        source = self.make_video("config.mp4")
        with self.assertRaises(QCError) as exc:
            convert(source, None, {"layout": "raw"})
        self.assertEqual(exc.exception.code, 2)
        self.assertFalse((self.scene / "prores").exists())
        config = self.scene / "bad.toml"
        config.write_text('layout = "raw"\n', encoding="utf-8")
        env = dict(os.environ, PYTHONPATH=str(Path(__file__).resolve().parents[1] / "src"), PYTHONDONTWRITEBYTECODE="1")
        result = subprocess.run([sys.executable, "-m", "plating_qc", "--config", str(config), "convert", str(source)], env=env, capture_output=True, text=True)
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_compare_identical_and_missing_input(self):
        source = self.make_video("compare.mp4")
        result = compare(source, source, {}, search=2)
        self.assertEqual(result["original"]["video"]["nb_frames_decoded"], 24)
        self.assertEqual(result["alignment"]["score"], 0)
        self.assertEqual(result["difference_ranges_candidate_frames"], [])
        with self.assertRaises(QCError) as exc:
            compare(source, self.raw / "absent.mp4", {})
        self.assertEqual(exc.exception.code, 2)

    def test_compare_detects_head_and_tail_loss(self):
        source = self.raw / "pattern.mkv"
        head = self.raw / "head.mkv"
        tail = self.raw / "tail.mkv"
        subprocess.run(["ffmpeg", "-v", "error", "-f", "lavfi", "-i", "nullsrc=s=64x36:r=24:d=1,geq=lum='mod(N*71+X*Y,256)':cb=128:cr=128", "-c:v", "ffv1", str(source)], check=True)
        for target, filt in ((head, "trim=start_frame=2,setpts=PTS-STARTPTS"), (tail, "trim=end_frame=20,setpts=PTS-STARTPTS")):
            subprocess.run(["ffmpeg", "-v", "error", "-i", str(source), "-vf", filt, "-c:v", "ffv1", str(target)], check=True)
        a = compare(source, head, {}, search=5)
        b = compare(source, tail, {}, search=5)
        self.assertFalse(a["alignment"]["uncertain"])
        self.assertEqual(a["alignment"]["estimated_missing_head"], 2)
        self.assertFalse(b["alignment"]["uncertain"])
        self.assertEqual(b["alignment"]["estimated_missing_tail"], 4)

    def test_compare_repeated_frames_is_uncertain(self):
        source = self.raw / "static.mp4"
        subprocess.run(["ffmpeg", "-v", "error", "-f", "lavfi", "-i", "color=black:size=160x90:rate=24:duration=1", "-c:v", "mpeg4", str(source)], check=True)
        result = compare(source, source, {}, search=2)
        self.assertTrue(result["alignment"]["uncertain"])
        self.assertIsNone(result["alignment"]["estimated_missing_head"])

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

    def test_compare_report_and_aligned_images(self):
        import json
        source, candidate = self.raw / "pattern.mkv", self.raw / "head.mkv"
        subprocess.run(["ffmpeg", "-v", "error", "-f", "lavfi", "-i", "nullsrc=s=64x36:r=24:d=1,geq=lum='mod(N*71+X*Y,256)':cb=128:cr=128", "-c:v", "ffv1", str(source)], check=True)
        subprocess.run(["ffmpeg", "-v", "error", "-i", str(source), "-vf", "trim=start_frame=2,setpts=PTS-STARTPTS", "-c:v", "ffv1", str(candidate)], check=True)
        target = self.scene / "report%03d"
        result = write_comparison(compare(source, candidate, {}, search=5), target, {})
        self.assertEqual(result["alignment"]["offset_candidate_to_original"], 2)
        image = result["comparison_images"][0]
        self.assertEqual((image["original_frame"], image["candidate_frame"]), (2, 0))
        import struct
        png = (target / image["file"]).read_bytes()
        self.assertEqual(struct.unpack(">II", png[16:24]), (128, 36))
        rgb = subprocess.run(["ffmpeg", "-v", "error", "-f", "image2pipe", "-i", "-", "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], input=png, capture_output=True, check=True).stdout
        for y in range(36):
            row = rgb[y * 128 * 3:(y + 1) * 128 * 3]
            self.assertEqual(row[:64 * 3], row[64 * 3:])
        saved = json.loads((target / "report.json").read_text(encoding="utf-8"))
        self.assertEqual(saved["comparison_images"], result["comparison_images"])
        self.assertIn("왼쪽 원본", (target / "report.txt").read_text(encoding="utf-8"))
        before = (target / "report.json").read_bytes()
        with self.assertRaises(QCError) as exc:
            write_comparison(result, target, {})
        self.assertEqual(exc.exception.code, 3)
        self.assertEqual((target / "report.json").read_bytes(), before)
        env = dict(os.environ, PYTHONPATH=str(Path(__file__).resolve().parents[1] / "src"), PYTHONDONTWRITEBYTECODE="1")
        cli_target = self.scene / "cli_report"
        cli = subprocess.run([sys.executable, "-m", "plating_qc", "compare", str(source), str(candidate), "--search", "5", "--out", str(cli_target)], env=env, capture_output=True, text=True)
        self.assertEqual(cli.returncode, 1, cli.stderr)
        self.assertTrue((cli_target / "report.json").exists())
        self.assertTrue(list(cli_target.glob("pair_*.png")))
        with self.assertRaises(QCError) as exc:
            write_comparison(result, self.raw / "unsafe", {})
        self.assertEqual(exc.exception.code, 2)

    def test_comparison_image_failure_cleans_output(self):
        source = self.raw / "failure_pattern.mkv"
        subprocess.run(["ffmpeg", "-v", "error", "-f", "lavfi", "-i", "nullsrc=s=64x36:r=24:d=1,geq=lum='mod(N*71+X*Y,256)':cb=128:cr=128", "-c:v", "ffv1", str(source)], check=True)
        result = compare(source, source, {}, search=5)
        target = self.scene / "failed_compare"
        def fail_after_writing(args, cwd, **kwargs):
            (Path(cwd) / args[-1]).write_bytes(b"partial")
            return subprocess.CompletedProcess(args, 1, "", "encoder error")
        with patch("plating_qc.review.subprocess.run", side_effect=fail_after_writing):
            with self.assertRaises(QCError) as exc:
                write_comparison(result, target, {})
        self.assertEqual(exc.exception.code, 5)
        self.assertFalse(target.exists())
        self.assertTrue(source.exists())

    def test_uncertain_comparison_saves_no_misleading_images(self):
        source = self.raw / "static_report.mp4"
        subprocess.run(["ffmpeg", "-v", "error", "-f", "lavfi", "-i", "color=black:size=160x90:rate=24:duration=1", "-c:v", "mpeg4", str(source)], check=True)
        target = self.scene / "uncertain"
        result = write_comparison(compare(source, source, {}, search=2), target, {})
        self.assertTrue(result["alignment"]["uncertain"])
        self.assertEqual(result["comparison_images"], [])
        self.assertFalse(list(target.glob("pair_*.png")))
        self.assertTrue((target / "report.json").exists())

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

    def test_tiles_invalid_frame_does_not_create_folder(self):
        source = self.make_video("tile_bad.mp4")
        dest = self.scene / "review"
        with self.assertRaises(QCError) as exc:
            tiles(source, dest, {}, cuts=[24])
        self.assertEqual(exc.exception.code, 2)
        self.assertFalse(dest.exists())

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

    def test_missing_input_and_dry_run(self):
        with self.assertRaises(QCError) as exc:
            probe(self.raw / "missing.mp4", {})
        self.assertEqual(exc.exception.code, 2)
        source = self.make_video("dry.mp4")
        result = convert(source, None, {}, dry_run=True)
        self.assertFalse(Path(result["output"]).exists())
        self.assertFalse((self.scene / "prores").exists())


if __name__ == "__main__":
    unittest.main()
