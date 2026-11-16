import sys
import json
import os
import random
import shutil
import subprocess
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from plating_qc.review import compare, normalized_distance
from plating_qc.core import QCError, analyze_timestamps, convert, frame_timestamps, probe
from plating_qc.review import compare, mixed_frame_hint, tiles, write_comparison
from plating_qc.split import split
from _synth import QCFixture


class CompareTests(unittest.TestCase):
    def test_brightness_and_contrast_are_normalized(self):
        original = bytes((10, 30, 50, 70, 90, 110))
        candidate = bytes((50, 60, 70, 80, 90, 100))
        self.assertLess(normalized_distance(original, candidate), 0.000001)

    def test_different_frames_remain_different(self):
        self.assertGreater(normalized_distance(bytes((0, 40, 80, 120)), bytes((120, 80, 40, 0))), 0.15)

    def test_flat_frames_use_original_brightness_distance(self):
        self.assertAlmostEqual(normalized_distance(bytes([4] * 4), bytes([8] * 4)), 4 / 255)


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
        env["PLATING_QC_LOG_DIR"] = str(self.root / "logs")
        result = subprocess.run([sys.executable, "-m", "plating_qc", "compare", str(self.source),
                                 str(other)], env=env, capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, 1)
        report = json.loads(result.stdout)
        self.assertIsNone(report["alignment"]["estimated_missing_head"])
        self.assertIsNone(report["alignment"]["estimated_missing_tail"])






class CompareIntegration(QCFixture):
    def test_vfr_probe_and_compare_do_not_claim_alignment(self):
        source = self.raw / "vfr_for_probe.mkv"
        subprocess.run(["ffmpeg", "-v", "error", "-f", "lavfi", "-i", "testsrc2=size=160x90:rate=4:duration=2.5", "-vf", "setpts=PTS+if(gte(N\\,4)\\,0.25/TB\\,0)", "-fps_mode", "vfr", "-c:v", "ffv1", str(source)], check=True)
        result = probe(source, {})
        self.assertEqual(result.timestamp_analysis.status, "observed")
        self.assertTrue(result.timestamp_analysis.vfr_suspect)
        comparison = compare(source, source, {}, search=2)
        self.assertTrue(comparison["alignment"]["uncertain"])
        self.assertIsNone(comparison["alignment"]["estimated_missing_head"])
        self.assertEqual(comparison["mixed_frame_suspects"], [])
        output = convert(source, None, {})
        self.assertEqual(output["output"].video.nb_frames_decoded, 10)
        self.assertTrue(output["warnings"])
        ffprobe = shutil.which("ffprobe")
        before = frame_timestamps(source, ffprobe)
        after = frame_timestamps(Path(output["output"].path), ffprobe)
        self.assertTrue(all(abs((a-before[0])-(b-after[0])) <= .001 for a,b in zip(before,after)))
        with self.assertRaises(QCError) as exc:
            split(Path(output["output"].path), self.scene / "vfr_parts", {})
        self.assertEqual(exc.exception.code, 2)
        self.assertFalse((self.scene / "vfr_parts").exists())

    def test_detects_synthetic_mixed_frame_as_suspicion(self):
        import random
        original = [random.Random(i).randbytes(64*36) for i in range(24)]
        candidate = original.copy()
        candidate[12] = bytes((a+b)//2 for a,b in zip(original[11], original[12]))
        source, other = self.raw / "mix_source.mkv", self.raw / "mix_candidate.mkv"
        for path, frames in ((source, original), (other, candidate)):
            subprocess.run(["ffmpeg", "-v", "error", "-f", "rawvideo", "-pix_fmt", "gray", "-s", "64x36", "-r", "24", "-i", "-", "-c:v", "ffv1", "-pix_fmt", "gray", str(path)], input=b"".join(frames), check=True, capture_output=True)
        result = compare(source, other, {}, search=3)
        self.assertFalse(result["alignment"]["uncertain"])
        self.assertTrue(any(x["candidate_frame"] == 12 and x["source_frames"] == [11, 12] for x in result["mixed_frame_suspects"]))
        self.assertTrue(result["warnings"])
        self.assertIsNone(mixed_frame_hint(original[11], original[12], original[12]))

    def test_compare_identical_and_missing_input(self):
        source = self.make_video("compare.mp4")
        result = compare(source, source, {}, search=2)
        self.assertEqual(result["original"].video.nb_frames_decoded, 24)
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
        cli = subprocess.run([sys.executable, "-m", "plating_qc", "compare", str(source), str(candidate), "--search", "5", "--out", str(cli_target)], env=env, capture_output=True, text=True, encoding="utf-8")
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
        with patch("plating_qc.backend.ffmpeg.subprocess.run", side_effect=fail_after_writing):
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
