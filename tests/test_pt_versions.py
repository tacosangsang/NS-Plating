"""SYNTH: V1~V10. 합성 이름과 README만 저장소 out/pt-tests 안에서 읽는다."""
import importlib
import io
import json
import sys
from pathlib import Path
from unittest.mock import patch
from uuid import uuid4

from tests._pt_support import NetworkBlockedCase

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))


class VersionTests(NetworkBlockedCase):
    def setUp(self):
        super().setUp()
        self.root = REPO / "out" / "pt-tests" / uuid4().hex
        self.root.mkdir(parents=True)
        self.scan = importlib.import_module("plating_tools.versions.scan")
        self.check = importlib.import_module("plating_tools.versions.check")
        self.model = importlib.import_module("plating_tools.versions.model")
        self.errors = importlib.import_module("plating_tools.errors")
        self.family = self.model.FamilySpec("SYNTH-day", self.root, "**/v*_*.blend", "**/v*_*.py", "**/v*_README*", None, ("backup",), None)

    def add_version(self, version, folder=None):
        root = folder or self.root
        root.mkdir(parents=True, exist_ok=True)
        for suffix in ("scene.blend", "script.py", "README.md"):
            (root / f"{version}_{suffix}").write_text("SYNTH", encoding="utf-8")

    def render(self, version, scene="S#01"):
        path = self.root / f"{version}_render.png"
        path.write_bytes(b"SYNTH")
        return self.model.RenderSpec(self.family.name, path, scene, "접두사")

    def evaluate(self, render, pins=()):
        state = self.scan.scan_family(self.family)
        return self.check.check_render(render, self.family, state, pins)

    def test_V1_numeric_order_v10_over_v9(self):
        self.add_version("v9")
        self.add_version("v10")
        result = self.evaluate(self.render("v10"))
        self.assertEqual(result.verdict, self.model.Verdict.LATEST)
        self.assertEqual(result.compared_to, "v10")

    def test_V2_missing_prefix_does_not_pass(self):
        self.add_version("v10")
        result = self.evaluate(self.render("SYNTH"))
        self.assertEqual(result.verdict, self.model.Verdict.NO_VERSION)

    def test_V3_stale_has_numeric_difference(self):
        self.add_version("v58")
        result = self.evaluate(self.render("v57"))
        self.assertEqual((result.verdict, result.diff), (self.model.Verdict.STALE, 1))

    def test_V4_pin_only_applies_inside_scope(self):
        self.add_version("v58")
        pin = self.model.Pin(self.family.name, "v50", ("S#98",), "W04", 2, "S#98은 v50 유지", "ts")
        self.assertEqual(self.evaluate(self.render("v50", "S#98"), (pin,)).verdict, self.model.Verdict.PINNED)
        self.assertEqual(self.evaluate(self.render("v50", "S#99"), (pin,)).verdict, self.model.Verdict.STALE)
        self.assertEqual(self.evaluate(self.render("v49", "S#98"), (pin,)).verdict, self.model.Verdict.PIN_MISMATCH)

    def test_V5_pin_basis_is_required_and_must_match_line(self):
        docs = importlib.import_module("plating_tools.docs")
        textio = importlib.import_module("plating_tools.textio")
        path = self.root / "SYNTH-W04.md"
        path.write_text("SYNTH\nS#98은 v50 유지\n", encoding="utf-8")
        class FakeStore(docs.DocStore):
            def load(inner, key): return textio.read_document(path, key)
        for basis in ("", "SYNTH 없는 근거"):
            pin = self.model.Pin(self.family.name, "v50", ("S#98",), "W04", 2, basis, "ts")
            with self.assertRaises(self.errors.InputError):
                self.check.validate_pins((pin,), FakeStore())
        pin = self.model.Pin(self.family.name, "v50", ("S#98",), "W04", 2, "S#98은 v50 유지", "ts")
        self.check.validate_pins((pin,), FakeStore())

    def test_V6_suffix_order_requires_explicit_order(self):
        from dataclasses import replace
        self.add_version("v2")
        self.add_version("v2i")
        render = self.render("v2i")
        self.assertEqual(self.evaluate(render).verdict, self.model.Verdict.ORDER_UNKNOWN)
        self.family = replace(self.family, explicit_order=("v2", "v2i"))
        self.assertEqual(self.evaluate(render).verdict, self.model.Verdict.LATEST)

    def test_V7_separate_families_and_excluded_backup(self):
        from dataclasses import replace
        self.add_version("v10")
        self.add_version("v99", self.root / "backup")
        night = self.root.parent / (self.root.name + "_night")
        self.add_version("v50", night)
        day = self.scan.scan_family(self.family)
        other = self.scan.scan_family(replace(self.family, name="SYNTH-night", root=night))
        self.assertEqual((day.latest.raw, other.latest.raw), ("v10", "v50"))

    def test_incomplete_explicit_order_is_not_guessed(self):
        from dataclasses import replace
        self.add_version("v8")
        self.add_version("v10")
        self.family = replace(self.family, explicit_order=("v9", "v10"))
        self.assertEqual(self.evaluate(self.render("v10")).verdict, self.model.Verdict.ORDER_UNKNOWN)

    def test_missing_source_is_not_confirmed_latest(self):
        (self.root / "v10_scene.blend").write_bytes(b"SYNTH")
        self.assertEqual(self.evaluate(self.render("v10")).verdict, self.model.Verdict.NO_VERSION)

    def test_V8_conflicting_sources_are_not_latest(self):
        (self.root / "v58_scene.blend").write_bytes(b"SYNTH")
        (self.root / "v58_script.py").write_bytes(b"SYNTH")
        (self.root / "v57_README.md").write_text("SYNTH", encoding="utf-8")
        self.assertEqual(self.evaluate(self.render("v58")).verdict, self.model.Verdict.CONFLICT)

    def test_V9_scan_does_not_change_files_or_mtime(self):
        self.add_version("v10")
        before = {str(p): (p.stat().st_size, p.stat().st_mtime_ns) for p in self.root.rglob("*")}
        with patch("subprocess.run", side_effect=AssertionError("Blender 실행 금지")):
            self.scan.scan_family(self.family)
        after = {str(p): (p.stat().st_size, p.stat().st_mtime_ns) for p in self.root.rglob("*")}
        self.assertEqual(before, after)

    def test_V10_every_result_retains_unverified_dimensions_and_geometry(self):
        self.add_version("v10")
        self.assertEqual(self.evaluate(self.render("v10")).not_verified, ("형상 동일성", "실제 치수"))

    def test_readme_render_version_requires_explicit_pattern(self):
        from dataclasses import replace
        self.add_version("v10")
        readme = self.root / "README.md"
        readme.write_text("기준 버전: v10\n", encoding="utf-8")
        self.family = replace(self.family, readme_glob="**/*README*", readme_version_pattern=r"기준 버전: (v\d+)")
        (self.root / "v10_README.md").write_text("기준 버전: v10\n", encoding="utf-8")
        render = replace(self.render("SYNTH"), version_from="README")
        self.assertEqual(self.evaluate(render).verdict, self.model.Verdict.LATEST)

    def test_cli_publishes_versions_and_pins_with_ts(self):
        from dataclasses import replace
        workspace = self.root
        self.root = workspace / "family"
        self.root.mkdir()
        self.family = replace(self.family, root=self.root)
        self.add_version("v58")
        render = self.render("v50", "S#98")
        cfg = workspace / "plating.toml"
        inputs = workspace / "inputs"
        inputs.mkdir()
        workflow = workspace / "workflow"
        workflow.mkdir()
        profile = importlib.import_module("plating_tools.profile_plating")
        (workflow / profile.DOC_FILES["W04"]).write_text("SYNTH\nS#98은 v50 유지\n", encoding="utf-8")
        cfg.write_text(f"[paths]\nwrite_root='.'\noutput_root='out'\nworkflow_dir='{workflow}'\n", encoding="utf-8")
        spec = inputs / "versions.toml"
        spec.write_text(f"[[family]]\nname='SYNTH-day'\nroot='{self.root}'\n[[render]]\nfamily='SYNTH-day'\npath='{render.path}'\nscene='S#98'\n", encoding="utf-8")
        pins = inputs / "pins.toml"
        pins.write_text("[[pin]]\nfamily='SYNTH-day'\nversion='v50'\nscope=['S#98']\nbasis_doc='W04'\nbasis_line=2\nbasis_contains='S#98은 v50 유지'\napproved_by='ts'\n", encoding="utf-8")
        cli = importlib.import_module("plating_tools.cli")
        stdout = io.StringIO()
        with patch("sys.stdout", stdout):
            code = cli.main(["--config", str(cfg), "versions", "check", "--spec", str(spec), "--pins", str(pins)])
        self.assertEqual(code, 0)
        output = Path(json.loads(stdout.getvalue())["output"])
        data = json.loads((output / "versions.json").read_text(encoding="utf-8"))
        self.assertEqual(data["renders"][0]["verdict"], "고정 예외 일치")
        self.assertEqual(data["pins"][0]["approved_by"], "ts")
