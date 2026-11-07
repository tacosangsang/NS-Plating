"""SYNTH: P0 공통 경로·출력 계약. 산출물은 저장소 out/에만 남긴다."""
import importlib
import json
import sys
import unittest
from tests._pt_support import NetworkBlockedCase
from pathlib import Path
from unittest.mock import patch
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))


class SafetyTests(NetworkBlockedCase):
    def setUp(self):
        super().setUp()
        self.root = Path(__file__).resolve().parents[1] / "out" / "pt-tests" / uuid4().hex
        self.root.mkdir(parents=True)
        self.paths = importlib.import_module("plating_tools.paths")
        self.errors = importlib.import_module("plating_tools.errors")
        self.output = importlib.import_module("plating_tools.output")

    def policy(self, **kwargs):
        return self.paths.WritePolicy(self.root, **kwargs)

    def test_S1_raw_component_is_rejected(self):
        with self.assertRaises(self.errors.InputError):
            self.policy().check(self.root / "RaW" / "result")

    @unittest.skipUnless(sys.platform == "win32", "Windows junction 검사")
    def test_S2_junction_to_input_is_rejected(self):
        import _winapi
        source = self.root / "input"
        source.mkdir()
        link = self.root / "alias"
        _winapi.CreateJunction(str(source), str(link))
        with self.assertRaises(self.errors.InputError):
            self.policy(input_dirs=(source,)).check(link / "new")

    def test_S3_existing_output_is_unchanged(self):
        target = self.root / "existing"
        target.mkdir()
        marker = target / "marker.txt"
        marker.write_text("SYNTH", encoding="utf-8")
        with self.assertRaises(self.errors.OutputConflict):
            with self.output.RunDir(target, self.policy()):
                self.fail("기존 결과에 진입하면 안 됨")
        self.assertEqual(marker.read_text(encoding="utf-8"), "SYNTH")

    def test_S4_partial_failure_is_quarantined(self):
        target = self.root / "result"
        with self.assertRaises(OSError):
            with self.output.RunDir(target, self.policy()) as run:
                run.write_text("partial.txt", "SYNTH")
                raise OSError("SYNTH 쓰기 실패")
        self.assertFalse(target.exists())
        failed = list((self.root / "_failed").glob("*/run.json"))
        self.assertEqual(len(failed), 1)
        self.assertEqual(json.loads(failed[0].read_text(encoding="utf-8"))["status"], "failed")

    def test_S5_repeated_runs_publish_new_directories(self):
        targets = [self.output.new_target(self.root, "cuts", "S#01") for _ in range(2)]
        for target in targets:
            with self.output.RunDir(target, self.policy()) as run:
                run.write_text("sample.txt", "SYNTH")
                run.finish({"exit_code": 0})
        self.assertNotEqual(*targets)
        self.assertTrue(all((p / "run.json").is_file() for p in targets))

    def test_S4_publish_failure_marks_run_as_failed(self):
        import os
        actual = os.rename
        calls = []
        def rename(source, destination):
            calls.append(destination)
            if len(calls) == 1:
                raise OSError("SYNTH 공개 실패")
            return actual(source, destination)
        target = self.root / "result"
        with self.assertRaises(OSError), patch("plating_tools.output.os.rename", side_effect=rename):
            with self.output.RunDir(target, self.policy()) as run:
                run.finish({"status": "검수 대기", "exit_code": 0})
        failed = next((self.root / "_failed").glob("*/run.json"))
        self.assertEqual(json.loads(failed.read_text(encoding="utf-8"))["status"], "failed")

    def test_S6_read_only_and_input_and_git_are_rejected(self):
        readonly = self.root / "NS-Plating"
        inputs = self.root / "dot-handoff"
        policy = self.policy(read_only=(readonly,), input_dirs=(inputs,))
        for path in (readonly / "out", inputs / "out", self.root / ".git" / "log", self.root.parent / "outside"):
            with self.subTest(path=path), self.assertRaises(self.errors.InputError):
                policy.check(path)

    def test_utf8_bom_crlf_and_unicode_line_numbers(self):
        textio = importlib.import_module("plating_tools.textio")
        source = self.root / "한글 입력.md"
        source.write_bytes(b"\xef\xbb\xbf" + "a\u2028b\r\nc\r\n".encode("utf-8"))
        doc = textio.read_document(source, "F")
        self.assertEqual(doc.lines, ("a\u2028b", "c", ""))
        self.assertEqual(doc.newline, "CRLF")

    def test_invalid_utf8_is_input_error_with_offset(self):
        textio = importlib.import_module("plating_tools.textio")
        source = self.root / "bad.md"
        source.write_bytes(b"a\xff")
        with self.assertRaisesRegex(self.errors.InputError, "1"):
            textio.read_document(source, "F")

    def test_config_relative_paths_use_config_parent(self):
        config = importlib.import_module("plating_tools.config")
        source = self.root / "plating.toml"
        source.write_text("[paths]\nwrite_root='.'\noutput_root='out'\nworkflow_dir='workflow'\n", encoding="utf-8")
        cfg = config.load_config(source)
        self.assertEqual(cfg.output_root, self.root / "out")
        self.assertEqual(cfg.workflow_dir, self.root / "workflow")
