"""SYNTH: blockout CLI 생성·충돌·원본 불변 계약."""
import hashlib
import importlib
import io
import json
import sys
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch
from uuid import uuid4

from tests._pt_support import NetworkBlockedCase

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))


class BlockoutCommandTests(NetworkBlockedCase):
    def setUp(self):
        super().setUp()
        self.workspace = REPO / "out" / "pt-tests" / uuid4().hex
        self.workspace.mkdir(parents=True)
        self.root = self.workspace / "blockout"
        self.asset = self.root / "tower_hall"
        self.inputs = self.workspace / "inputs"
        self.inputs.mkdir()
        self.blend = self.inputs / "tower_hall.blend"
        self.blend.write_bytes(b"SYNTH blend 1")
        self.config = self.workspace / "plating.toml"
        self.config.write_text('[paths]\nwrite_root="."\noutput_root="out"\n', encoding="utf-8")
        self.cli = importlib.import_module("plating_tools.cli")
        self.store = importlib.import_module("plating_tools.blockout.manifest").FileManifestStore(
            importlib.import_module("plating_tools.paths").WritePolicy(self.workspace))

    def call(self, *args):
        stdout, stderr = io.StringIO(), io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            code = self.cli.main(["--config", str(self.config), "blockout", *map(str, args)])
        return code, json.loads(stdout.getvalue()) if stdout.getvalue() else None, stderr.getvalue()

    def init_asset(self):
        self.assertEqual(self.call("init", "tower_hall", "--root", self.root)[0], 0)

    def new_version(self, *extra):
        return self.call("new-version", "tower_hall", "--root", self.root, "--from", self.blend,
                         "--change", '보 "흰색" 변경', "--by", "ts", *extra)

    def read_manifest(self):
        return self.store.read(self.asset / "manifest.toml")

    def test_init_creates_empty_manifest_and_required_directories(self):
        self.init_asset()
        self.assertEqual({p.name for p in self.asset.iterdir()}, {"manifest.toml", "versions", "renders", "archive"})
        manifest = self.read_manifest()
        self.assertEqual(manifest.asset, "tower_hall")
        self.assertEqual((manifest.current, manifest.versions, manifest.pins), ("", {}, {}))

    def test_init_existing_asset_is_two_and_preserves_all_bytes(self):
        self.init_asset()
        path = self.asset / "manifest.toml"
        before = path.read_bytes()
        self.assertEqual(self.call("init", "tower_hall", "--root", self.root)[0], 2)
        self.assertEqual(path.read_bytes(), before)

    def test_new_version_copies_sources_notes_and_hashes_without_changing_current(self):
        self.init_asset()
        script = self.inputs / "build.py"
        script.write_text("# SYNTH optional source\n", encoding="utf-8")
        before = self.blend.read_bytes(), self.blend.stat().st_mtime_ns
        code, result, _ = self.new_version("--from", script)
        self.assertEqual(code, 0)
        self.assertEqual(result["version"], "v001")
        manifest = self.read_manifest()
        version = manifest.versions["v001"]
        directory = self.asset / "versions" / "v001"
        self.assertEqual(manifest.current, "")
        self.assertEqual(set(version.files), {"tower_hall.blend", "build.py", "NOTES.md"})
        for name, digest in version.files.items():
            self.assertEqual(hashlib.sha256((directory / name).read_bytes()).hexdigest(), digest)
        self.assertIn('보 "흰색" 변경', (directory / "NOTES.md").read_text(encoding="utf-8"))
        self.assertEqual((self.blend.read_bytes(), self.blend.stat().st_mtime_ns), before)

    def test_numbering_and_current_are_explicit_and_previous_version_is_immutable(self):
        self.init_asset()
        self.assertEqual(self.new_version("--set-current")[0], 0)
        first = self.asset / "versions" / "v001"
        before = {p.name: (p.read_bytes(), p.stat().st_mtime_ns) for p in first.iterdir()}
        self.blend.write_bytes(b"SYNTH blend 2")
        self.assertEqual(self.new_version()[1]["version"], "v002")
        self.assertEqual(self.read_manifest().current, "v001")
        self.assertEqual(self.new_version("--set-current")[1]["version"], "v003")
        self.assertEqual(self.read_manifest().current, "v003")
        self.assertEqual({p.name: (p.read_bytes(), p.stat().st_mtime_ns) for p in first.iterdir()}, before)

    def test_missing_input_and_uninitialized_asset_are_two_without_publication(self):
        self.assertEqual(self.new_version()[0], 2)
        self.init_asset()
        before = (self.asset / "manifest.toml").read_bytes()
        self.blend.unlink()
        self.assertEqual(self.new_version()[0], 2)
        self.assertEqual(list((self.asset / "versions").iterdir()), [])
        self.assertEqual((self.asset / "manifest.toml").read_bytes(), before)

    def test_duplicate_basenames_and_generated_notes_are_rejected(self):
        self.init_asset()
        other = self.inputs / "other"
        other.mkdir()
        duplicate = other / "TOWER_HALL.blend"
        duplicate.write_bytes(b"SYNTH")
        notes = self.inputs / "NOTES.md"
        notes.write_text("SYNTH", encoding="utf-8")
        for source in (duplicate, notes):
            with self.subTest(source=source):
                self.assertEqual(self.new_version("--from", source)[0], 2)
        self.assertFalse(list((self.asset / "versions").iterdir()))

    def test_unsafe_asset_and_root_are_rejected_before_write(self):
        for name in ("../escape", "raw", "CON", "com1"):
            with self.subTest(name=name):
                self.assertEqual(self.call("init", name, "--root", self.root)[0], 2)
        self.assertEqual(self.call("init", "tower_hall", "--root", self.workspace.parent)[0], 2)
        self.assertFalse(self.root.exists())

    def test_existing_version_collision_does_not_overwrite(self):
        self.init_asset()
        self.assertEqual(self.new_version()[0], 0)
        version_store = importlib.import_module("plating_tools.blockout.storage")
        errors = importlib.import_module("plating_tools.errors")
        fs = version_store.FileVersionStore(importlib.import_module("plating_tools.paths").WritePolicy(self.workspace))
        before = (self.asset / "versions" / "v001" / self.blend.name).read_bytes()
        with self.assertRaises(errors.OutputConflict):
            fs.create(self.asset / "versions" / "v001", (self.blend,), "SYNTH", "ts")
        self.assertEqual((self.asset / "versions" / "v001" / self.blend.name).read_bytes(), before)

    def test_copy_failure_preserves_manifest_and_has_no_published_version(self):
        self.init_asset()
        before = (self.asset / "manifest.toml").read_bytes()
        with patch("plating_tools.blockout.storage.shutil.copy2", side_effect=OSError("SYNTH copy failed")):
            self.assertEqual(self.new_version()[0], 5)
        self.assertFalse((self.asset / "versions" / "v001").exists())
        self.assertEqual((self.asset / "manifest.toml").read_bytes(), before)

    def test_asset_lock_prevents_concurrent_manifest_mutation(self):
        self.init_asset()
        lock = self.asset / ".blockout.lock"
        lock.write_text("SYNTH another writer", encoding="utf-8")
        self.assertEqual(self.new_version()[0], 3)
        self.assertEqual(lock.read_text(encoding="utf-8"), "SYNTH another writer")
        self.assertEqual(self.read_manifest().versions, {})

    def test_manifest_failure_keeps_published_version_for_diagnosis(self):
        self.init_asset()
        before = (self.asset / "manifest.toml").read_bytes()
        with patch("plating_tools.blockout.manifest.os.replace", side_effect=OSError("SYNTH manifest failed")):
            self.assertEqual(self.new_version()[0], 5)
        self.assertTrue((self.asset / "versions" / "v001" / self.blend.name).is_file())
        self.assertEqual((self.asset / "manifest.toml").read_bytes(), before)
        self.assertFalse((self.asset / ".blockout.lock").exists())
