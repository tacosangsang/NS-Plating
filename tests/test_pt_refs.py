"""SYNTH: R1~R15. HTTP·이미지 도구는 가짜이며 소켓 연결을 금지한다."""
import importlib
import io
import json
import struct
import sys
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch
from uuid import uuid4

from tests._pt_support import NetworkBlockedCase

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))


class ReferenceTests(NetworkBlockedCase):
    def setUp(self):
        super().setUp()
        self.root = REPO / "out" / "pt-tests" / uuid4().hex
        self.inputs = self.root / "inputs"
        self.inputs.mkdir(parents=True)
        self.api = importlib.import_module("plating_tools.refs.check")
        self.model = importlib.import_module("plating_tools.model")
        self.images = importlib.import_module("plating_tools.refs.images")
        self.errors = importlib.import_module("plating_tools.errors")
        self.data = b"\x89PNG\r\n\x1a\n" + struct.pack(">I", 13) + b"IHDR" + struct.pack(">II", 32, 16) + b"SYNTH"
        self.local = self.inputs / "SYNTH.png"
        self.local.write_bytes(self.data)
        self.entry = self.model.RefEntry(1, "SYNTH 역할", str(self.local), "https://synth.invalid/image")

    def resolve(self, entry=None, response=None, allow=True):
        fetch = importlib.import_module("plating_tools.refs.fetch")
        class FakeFetcher(fetch.HttpFetcher):
            calls = 0
            def get(inner, url, **limits):
                inner.calls += 1
                return response or fetch.inspect_response(200, "image/png", self.data, url)
        fake = FakeFetcher()
        result = self.api.check_references((entry or self.entry,), fetcher=fake, allow_network=allow)
        return result, fake

    def test_R1_same_image_has_dimensions_size_hash_and_byte_match(self):
        result, fake = self.resolve()
        item = result[0]
        self.assertEqual((item.local.width, item.local.height, item.local.size), (32, 16, len(self.data)))
        self.assertEqual(item.local.sha256, item.remote.body_sha256)
        self.assertEqual(item.correspondence, "바이트 동일")
        self.assertEqual(fake.calls, 1)

    def test_R8_same_size_different_hash_is_mismatch(self):
        self.local.write_bytes(self.data[:-1] + b"X")
        result, _ = self.resolve()
        self.assertEqual(result[0].correspondence, "불일치")

    def test_R9_indices_and_prompt_tokens_are_checked(self):
        for indices in ((1, 2, 4), (1, 1)):
            entries = tuple(replace(self.entry, index=i) for i in indices)
            findings = self.api.check_numbers(entries, "REFERENCE ROLES\n@image1\nSTYLE\n@image5")
            self.assertTrue(any(f.severity == "error" for f in findings))
        findings = self.api.check_numbers((self.entry,), "REFERENCE ROLES\n@image1\nSTYLE\n@image1")
        self.assertEqual(findings, ())

    def test_R10_count_is_advice_not_hard_failure(self):
        findings = self.api.count_advice(6, (3, 5))
        self.assertTrue(findings)
        self.assertTrue(all(f.severity != "error" for f in findings))
        self.assertEqual(self.api.count_advice(5, (3, 5))[0].severity, "info")

    def test_R11_sheet_and_preview_are_preserved(self):
        result, _ = self.resolve()
        self.assertEqual(result[0].entry.sheet, "시트 없음/만들어야 함")
        self.assertEqual(result[0].entry.preview, "미검수")

    def test_R12_complete_candidates_basis_and_largest_are_required(self):
        larger = self.inputs / "SYNTH-large.png"
        larger.write_bytes(self.data[:16] + struct.pack(">II", 64, 32) + self.data[24:])
        complete = replace(self.entry, candidates=(str(self.local), str(larger)), candidates_complete=True, candidates_basis="SYNTH 전수")
        for entry, expected in ((self.entry, "최대 원본 미확인"), (complete, "최대 원본 미확인"), (replace(complete, local_path=str(larger)), "최대 원본 확인됨"), (replace(complete, local_path=str(larger), candidates_basis=""), "최대 원본 미확인")):
            result, _ = self.resolve(entry)
            self.assertEqual(result[0].best_original, expected)

    def test_R13_thumbnail_input_is_error(self):
        thumbs = self.inputs / "thumbs"
        thumbs.mkdir()
        tiny = thumbs / "SYNTH.png"
        tiny.write_bytes(self.data)
        result, fake = self.resolve(replace(self.entry, local_path=str(tiny)))
        self.assertTrue(any(f.code == "REF_THUMB_INPUT" and f.severity == "error" for f in result[0].findings))
        self.assertEqual(fake.calls, 0)

    def test_R15_default_network_block_makes_zero_get_calls(self):
        result, fake = self.resolve(allow=False)
        self.assertEqual(fake.calls, 0)
        self.assertEqual(result[0].remote.error.value, "not_attempted")
        self.assertEqual(result[0].correspondence, "미확인")

    def cli(self, *extra):
        cli = importlib.import_module("plating_tools.cli")
        cfg = self.root / "plating.toml"
        workflow = self.root / "workflow"
        workflow.mkdir(exist_ok=True)
        profile = importlib.import_module("plating_tools.profile_plating")
        items = "\n".join(f"{n}. SYNTH 점검 {n}" + (" (안전선 3~5장)" if n == 2 else "") for n in range(1, 9))
        (workflow / profile.DOC_FILES["W02"]).write_text(f"# {profile.DOC_TITLES['W02']}\n\n## 4. 크레딧 쓰기 전 점검 8줄\n\n{items}\n", encoding="utf-8")
        cfg.write_text(f"[paths]\nwrite_root='.'\noutput_root='out'\nworkflow_dir='{workflow.as_posix()}'\n", encoding="utf-8")
        refs = self.inputs / "refs.toml"
        refs.write_text(f"[[reference]]\nindex=1\nrole='SYNTH 역할'\nlocal_path='{self.local}'\nurl='https://synth.invalid/image'\n", encoding="utf-8")
        stdout = io.StringIO()
        with patch("sys.stdout", stdout), patch("sys.stderr", io.StringIO()):
            code = cli.main(["--config", str(cfg), "refs", "check", "--list", str(refs), *extra])
        return code, stdout.getvalue()

    def test_R14_fake_thumbnails_contact_and_conflict(self):
        images = self.images
        class FakeImageTool(images.ImageTool):
            def available(inner): return True
            def decode_check(inner, path): return True
            def thumbnail(inner, src, dst, max_side):
                with dst.open("xb") as stream: stream.write(b"SYNTH thumbnail")
        out = self.root / "result"
        with patch("plating_tools.refs.FFmpegImageTool", return_value=FakeImageTool()):
            code, _ = self.cli("--thumbs", "--out", str(out))
            self.assertEqual(code, 1)
            contact = (out / "contact.html").read_text(encoding="utf-8")
            self.assertIn("SYNTH.png", contact)
            self.assertIn("SYNTH 역할", contact)
            self.assertIn("@image1", contact)
            self.assertEqual(json.loads((out / "refs.json").read_text(encoding="utf-8"))["results"][0]["local"]["decode"], "디코딩 확인")
            code, _ = self.cli("--thumbs", "--out", str(out))
            self.assertEqual(code, 3)

    def test_R14_missing_ffmpeg_returns_four_without_result(self):
        out = self.root / "absent"
        with patch("plating_tools.refs.FFmpegImageTool.available", return_value=False):
            code, _ = self.cli("--thumbs", "--out", str(out))
        self.assertEqual(code, 4)
        self.assertFalse(out.exists())

    def test_R15_cli_without_network_publishes_unknown_and_exit_one(self):
        code, stdout = self.cli()
        self.assertEqual(code, 1)
        output = Path(json.loads(stdout)["output"])
        self.assertEqual(json.loads((output / "refs.json").read_text(encoding="utf-8"))["results"][0]["remote"]["error"], "not_attempted")
