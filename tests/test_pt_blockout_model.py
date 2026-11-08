"""SYNTH: 정본 모델·TOML·세 자리 버전 계약."""
import importlib
import sys
from pathlib import Path
from uuid import uuid4

from tests._pt_support import NetworkBlockedCase

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))


class BlockoutModelTests(NetworkBlockedCase):
    def setUp(self):
        super().setUp()
        self.root = REPO / "out" / "pt-tests" / uuid4().hex
        self.root.mkdir(parents=True)
        self.model = importlib.import_module("plating_tools.blockout.model")
        self.manifest = importlib.import_module("plating_tools.blockout.manifest")
        self.errors = importlib.import_module("plating_tools.errors")
        policy = importlib.import_module("plating_tools.paths").WritePolicy(self.root)
        self.store = self.manifest.FileManifestStore(policy)

    def test_version_number_requires_three_digits_without_suffix(self):
        for value in ("v000", "v1", "v01", "v1000", "v002i", "v032_seats", "V001"):
            with self.subTest(value=value), self.assertRaises(self.errors.InputError):
                self.model.version_number(value)
        self.assertEqual(self.model.version_number("v099"), 99)

    def test_next_version_uses_numeric_max_and_rejects_overflow(self):
        self.assertEqual(self.model.next_version(()), "v001")
        self.assertEqual(self.model.next_version(("v009", "v002")), "v010")
        with self.assertRaises(self.errors.InputError):
            self.model.next_version(("v999",))

    def test_manifest_round_trip_preserves_unicode_quotes_hashes_and_pins(self):
        version = self.model.Version("2026-11-07", '보 "흰색" \\ 변경', "ts", {"장면.blend": "a" * 64})
        pin = self.model.Pin("v001", '사용자: "이 판 유지"', "ts", "2026-11-07")
        expected = self.model.Manifest("tower_hall", "v001", ("낮", "night"), {"v001": version}, {"S#10": pin})
        path = self.root / "manifest.toml"
        self.store.write(path, expected)
        self.assertEqual(self.store.read(path), expected)
        self.assertIn("[versions.v001.files]", path.read_text(encoding="utf-8"))

    def test_empty_manifest_round_trip(self):
        path = self.root / "manifest.toml"
        expected = self.model.Manifest("tower_hall")
        self.store.write(path, expected)
        self.assertEqual(self.store.read(path), expected)

    def test_invalid_manifest_references_types_and_hashes_are_input_errors(self):
        for text in ('asset="tower"\ncurrent="v001"', 'asset="tower"\nvariants="day"',
                     'asset="tower"\n[versions.v001]\ndate="bad"\nchange="x"\nby="ts"',
                     'asset="tower"\n[versions.v001]\ndate="2026-11-07"\nchange="x"\nby="ts"\n[versions.v001.files]\n"../x"="bad"',
                     'asset="tower"\n[pins."S#10"]\nversion="v001"\nreason=""\napproved_by="ts"\ndate="2026-11-07"',
                     'asset = ['):
            path = self.root / "manifest.toml"
            path.write_text(text, encoding="utf-8")
            with self.subTest(text=text), self.assertRaises(self.errors.InputError):
                self.store.read(path)

    def test_manifest_write_rejects_outside_policy(self):
        with self.assertRaises(self.errors.InputError):
            self.store.write(self.root.parent / "escape.toml", self.model.Manifest("tower"))
