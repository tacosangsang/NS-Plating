"""SYNTH: 작성 기준 지문은 줄바꿈·BOM과 무관해야 한다."""
import importlib
import sys
import unittest
from pathlib import Path
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
REPO = Path(__file__).resolve().parents[1]


class ContentFingerprintTests(unittest.TestCase):
    def test_crlf_lf_and_bom_share_content_fingerprint(self):
        textio = importlib.import_module("plating_tools.textio")
        root = REPO / "out" / "pt-tests" / uuid4().hex
        root.mkdir(parents=True)
        variants = {"lf": b"# SYNTH\n\xea\xb0\x80\n", "crlf": b"# SYNTH\r\n\xea\xb0\x80\r\n", "bom": b"\xef\xbb\xbf# SYNTH\n\xea\xb0\x80\n"}
        prints = {}
        for name, data in variants.items():
            path = root / f"{name}.md"
            path.write_bytes(data)
            prints[name] = textio.read_document(path, "W99").fingerprint
        self.assertEqual(len({p.content_sha256 for p in prints.values()}), 1)
        self.assertEqual(len({p.sha256 for p in prints.values()}), 3)

    def test_changed_since_authored(self):
        model = importlib.import_module("plating_tools.model")
        base = model.DocFingerprint("W99", "SYNTH", 1, "b" * 64, content_sha256="a" * 64)
        self.assertFalse(base.changed_since_authored)
        self.assertFalse(model.DocFingerprint(**{**{f: getattr(base, f) for f in base.__slots__}, "authored_sha256": "a" * 64}).changed_since_authored)
        self.assertTrue(model.DocFingerprint(**{**{f: getattr(base, f) for f in base.__slots__}, "authored_sha256": "c" * 64}).changed_since_authored)
