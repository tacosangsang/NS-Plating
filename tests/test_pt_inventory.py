"""SYNTH: 컷표 inventory와 읽기 전용 실제 원문 검사."""
import importlib
import json
import os
import sys
import unittest
from pathlib import Path
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

F_PATH = Path(os.environ.get("PLATING_TOOLS_F", r"C:\Users\uicus\Dev\dot-handoff\notion_컷표_fetch_2026-11-07T0706Z.md"))
F_SHA = "cae22e2f0637d29ebfe1f6e5a7daa973ee8ea72a397373246ecdddf9cfe6dc37"


class InventoryTests(unittest.TestCase):
    def test_synthetic_inventory_preserves_color_counts(self):
        root = Path(__file__).resolve().parents[1] / "out" / "pt-tests" / uuid4().hex
        root.mkdir(parents=True)
        source = root / "SYNTH.md"
        source.write_text('### S#01 수정\n<table header-row="true"><tr><td>컷</td><td>TC</td></tr><tr color="red_bg"><td><span color="yellow_bg">S#01-C001</span></td><td>00:00–00:01</td></tr></table>\n### 녹음\n', encoding="utf-8")
        module = importlib.import_module("plating_tools.cuts.source")
        report = importlib.import_module("plating_tools.cuts.report")
        result = report.inventory(module.NotionMdFile(source))
        self.assertEqual(result["colors"]["tr"]["red_bg"], 1)
        self.assertEqual(result["colors"]["span"]["yellow_bg"], 1)
        self.assertEqual(result["color_loss"], 0)
        self.assertEqual(len(result["sections"]), 2)

    def test_real_C8_inventory_matches_independent_observations(self):
        if not F_PATH.is_file():
            self.skipTest("실제 F 없음")
        module = importlib.import_module("plating_tools.cuts.source")
        report = importlib.import_module("plating_tools.cuts.report")
        source = module.NotionMdFile(F_PATH)
        if source.fingerprint().sha256 != F_SHA:
            self.skipTest("실제 F SHA-256 다름")
        result = report.inventory(source)
        self.assertEqual(result["colors"], {"callout": {"gray_bg": 2}, "tr": {"green_bg": 5, "red_bg": 79, "gray_bg": 2}, "td": {"red_bg": 9, "green_bg": 155, "gray_bg": 6}, "span": {"yellow_bg": 1}})
        self.assertEqual(result["color_loss"], 0)
        self.assertEqual(result["span_attributes"], [])

    def test_unclosed_table_is_rejected(self):
        root = Path(__file__).resolve().parents[1] / "out" / "pt-tests" / uuid4().hex
        root.mkdir(parents=True)
        source = root / "SYNTH.md"
        source.write_text('### S#01\n<table header-row="true"><tr><td>컷</td></tr>', encoding="utf-8")
        module = importlib.import_module("plating_tools.cuts.source")
        report = importlib.import_module("plating_tools.cuts.report")
        errors = importlib.import_module("plating_tools.errors")
        with self.assertRaises(errors.InputError):
            report.inventory(module.NotionMdFile(source))
