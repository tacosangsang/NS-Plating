"""SYNTH: 네 판정·승인 pin·검사 읽기 전용 회귀."""
import hashlib
import importlib
import io
import json
import shutil
import sys
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from uuid import uuid4

from tests._pt_support import NetworkBlockedCase

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))


class BlockoutCheckTests(NetworkBlockedCase):
    def setUp(self):
        super().setUp()
        self.workspace = REPO / "out" / "pt-tests" / uuid4().hex
        self.workspace.mkdir(parents=True)
        self.root = self.workspace / "blockout"
        self.asset = self.root / "tower_hall"
        self.config = self.workspace / "plating.toml"
        self.config.write_text('[paths]\nwrite_root="."\noutput_root="out"\n', encoding="utf-8")
        self.inputs = self.workspace / "inputs"
        self.inputs.mkdir()
        self.blend = self.inputs / "tower_hall.blend"
        self.blend.write_bytes(b"SYNTH 1")
        self.cli = importlib.import_module("plating_tools.cli")
        self.assertEqual(self.call("init", "tower_hall", "--root", self.root)[0], 0)
        self.assertEqual(self.new_version()[0], 0)
        self.blend.write_bytes(b"SYNTH 2")
        self.assertEqual(self.new_version()[0], 0)

    def call(self, *args):
        stdout, stderr = io.StringIO(), io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            code = self.cli.main(["--config", str(self.config), "blockout", *map(str, args)])
        return code, json.loads(stdout.getvalue()) if stdout.getvalue() else None, stderr.getvalue()

    def new_version(self):
        return self.call("new-version", "tower_hall", "--root", self.root, "--from", self.blend,
                         "--change", "SYNTH", "--by", "ts", "--set-current")

    def pin(self, version="v001", scene="S#10", reason='ts: "이 버전 유지"', by="ts", day="2026-11-08"):
        return self.call("pin", "tower_hall", "--root", self.root, "--scene", scene, "--version", version,
                         "--reason", reason, "--by", by, "--date", day)

    def render(self, version, scene=None, name=None, root=None):
        directory = (root if root else self.asset / "renders") / version
        if scene:
            directory /= scene
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / (name or f"tower_hall_{version}_front.png")
        path.write_bytes(b"SYNTH render, not a real image")
        return path

    def check(self, *extra):
        code, result, error = self.call("check", "--root", self.root, *extra)
        self.assertIsNotNone(result, error)
        output = Path(result["output"])
        self.assertTrue((output / "blockout.md").is_file())
        return code, json.loads((output / "blockout.json").read_text(encoding="utf-8")), output

    def codes(self, report):
        return {f["code"] for f in report["findings"]}

    def test_current_render_passes_and_emits_json_markdown_and_run_metadata(self):
        self.render("v002")
        code, report, output = self.check()
        self.assertEqual(code, 0)
        self.assertEqual(report["findings"], [])
        self.assertEqual(json.loads((output / "run.json").read_text(encoding="utf-8"))["exit_code"], 0)

    def test_older_render_is_stale(self):
        self.render("v001")
        code, report, _ = self.check()
        self.assertEqual(code, 1)
        self.assertEqual(self.codes(report), {"STALE"})

    def test_pin_approval_is_stored_and_matching_scene_is_pinned(self):
        self.assertEqual(self.pin()[0], 0)
        self.render("v001", "S#10")
        code, report, output = self.check()
        self.assertEqual(code, 0)
        self.assertEqual(self.codes(report), {"PINNED"})
        text = (self.asset / "manifest.toml").read_text(encoding="utf-8")
        self.assertIn('approved_by = "ts"', text)
        self.assertIn("PINNED", (output / "blockout.md").read_text(encoding="utf-8"))

    def test_pin_mismatch_is_stale_and_other_scene_uses_current(self):
        self.assertEqual(self.pin()[0], 0)
        wrong_pin = self.render("v002", "S#10")
        other_scene = self.render("v001", "S#11")
        code, report, _ = self.check()
        self.assertEqual(code, 1)
        self.assertEqual(self.codes(report), {"STALE"})
        messages = "\n".join(f["message"] for f in report["findings"])
        self.assertIn(str(wrong_pin), messages)
        self.assertIn(str(other_scene), messages)

    def test_pin_rejects_empty_approval_unknown_version_invalid_scene_by_and_date(self):
        before = (self.asset / "manifest.toml").read_bytes()
        for kwargs in ({"reason": " "}, {"version": "v999"}, {"version": "v1"}, {"scene": "S10"},
                       {"by": " "}, {"day": "2026-02-30"}):
            with self.subTest(kwargs=kwargs):
                self.assertEqual(self.pin(**kwargs)[0], 2)
                self.assertEqual((self.asset / "manifest.toml").read_bytes(), before)

    def test_one_byte_mutation_is_immutable_violation(self):
        path = self.asset / "versions" / "v001" / self.blend.name
        original = path.read_bytes()
        path.write_bytes(bytes([original[0] ^ 1]) + original[1:])
        code, report, _ = self.check()
        self.assertEqual(code, 1)
        self.assertEqual(self.codes(report), {"IMMUTABLE"})
        self.assertIn(self.blend.name, report["findings"][0]["message"])

    def test_added_deleted_files_and_missing_version_are_immutable_violations(self):
        version = self.asset / "versions" / "v001"
        (version / "NOTES.md").unlink()
        (version / "extra.txt").write_text("SYNTH", encoding="utf-8")
        code, report, _ = self.check()
        self.assertEqual(code, 1)
        self.assertEqual(self.codes(report), {"IMMUTABLE"})
        for path in version.iterdir():
            path.unlink()
        version.rmdir()
        self.assertEqual(self.codes(self.check()[1]), {"IMMUTABLE"})

    def test_unrecorded_suffix_and_date_folders_are_convention_violations(self):
        for name in ("v003", "v002i", "v032_seats", "2026-11-08"):
            (self.asset / "versions" / name).mkdir()
        code, report, _ = self.check()
        self.assertEqual(code, 1)
        self.assertEqual(self.codes(report), {"CONVENTION"})
        self.assertEqual(len(report["findings"]), 4)

    def test_archived_version_is_checked_without_reusing_its_number(self):
        source = self.asset / "versions" / "v002"
        source.rename(self.asset / "archive" / "v002")
        self.assertEqual(self.check()[0], 0)
        self.assertEqual(self.new_version()[1]["version"], "v003")

    def test_duplicate_version_locations_are_not_silently_selected(self):
        shutil.copytree(self.asset / "versions" / "v001", self.asset / "archive" / "v001")
        self.assertIn("CONVENTION", self.codes(self.check()[1]))

    def test_external_renders_and_explicit_scene_in_filename_use_pin(self):
        self.assertEqual(self.pin()[0], 0)
        external = self.workspace / "sheets"
        self.render("v001", name="tower_hall_v001_S#10_front.png", root=external)
        code, report, _ = self.check("--renders", external)
        self.assertEqual(code, 0)
        self.assertEqual(self.codes(report), {"PINNED"})

    def test_unknown_asset_version_and_render_folder_name_mismatch_do_not_pass(self):
        self.render("v002", name="unknown_v002_front.png")
        self.render("v999")
        self.render("v002", name="tower_hall_v001_front.png")
        code, report, _ = self.check()
        self.assertEqual(code, 1)
        self.assertIn("CONVENTION", self.codes(report))

    def test_newer_unselected_render_and_suffix_or_date_names_are_convention_violations(self):
        # v003을 만들되 current는 v002로 유지한다.
        self.assertEqual(self.call("new-version", "tower_hall", "--root", self.root, "--from", self.blend,
                                   "--change", "SYNTH", "--by", "ts")[0], 0)
        self.render("v003")
        self.render("v002", name="tower_hall_v002i_front.png")
        self.render("2026-11-08", name="tower_hall_v002_front.png")
        code, report, _ = self.check()
        self.assertEqual(code, 1)
        self.assertEqual(self.codes(report), {"CONVENTION"})

    def test_malformed_manifest_and_missing_layout_are_reported(self):
        before = (self.asset / "manifest.toml").read_bytes()
        (self.asset / "manifest.toml").write_text('asset = [', encoding="utf-8")
        code, report, _ = self.check()
        self.assertEqual(code, 1)
        self.assertIn("CONVENTION", self.codes(report))
        (self.asset / "manifest.toml").write_bytes(before)
        (self.asset / "renders").rmdir()
        self.assertIn("CONVENTION", self.codes(self.check()[1]))

    def test_pin_quote_control_character_round_trip(self):
        self.assertEqual(self.pin(reason='ts: "이 판 유지"\x7f')[0], 0)
        self.render("v001", "S#10")
        self.assertEqual(self.codes(self.check()[1]), {"PINNED"})

    def test_missing_root_and_explicit_missing_renders_are_input_errors(self):
        self.assertEqual(self.call("check", "--root", self.workspace / "missing")[0], 2)
        self.assertEqual(self.call("check", "--root", self.root, "--renders", self.workspace / "missing")[0], 2)

    def test_check_does_not_change_manifest_versions_or_render_bytes_and_mtimes(self):
        self.render("v002")
        def snapshot():
            return {p.relative_to(self.root).as_posix(): (hashlib.sha256(p.read_bytes()).hexdigest(), p.stat().st_mtime_ns)
                    for p in self.root.rglob("*") if p.is_file()}
        before = snapshot()
        self.assertEqual(self.check()[0], 0)
        self.assertEqual(snapshot(), before)

    def test_blank_current_with_a_render_is_not_reported_as_current(self):
        text = (self.asset / "manifest.toml").read_text(encoding="utf-8")
        (self.asset / "manifest.toml").write_text(text.replace('current = "v002"', 'current = ""'), encoding="utf-8")
        self.render("v002")
        self.assertEqual(self.check()[0], 1)
