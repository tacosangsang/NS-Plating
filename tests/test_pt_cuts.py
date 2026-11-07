"""SYNTH/T2: C1~C22 컷표 계약. 실제 원문 fixture는 저장하지 않는다."""
import importlib
import json
import os
import subprocess
import sys
import unittest
from tests._pt_support import NetworkBlockedCase
from decimal import Decimal
from pathlib import Path
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))


def table(rows, headers=("컷", "TC", "길이", "화면")):
    return '<table header-row="true">\n<tr>' + ''.join(f'<td>{h}</td>' for h in headers) + '</tr>\n' + '\n'.join(rows) + '\n</table>\n'


def row(cut="S#01-C001", tc="00:00–00:04", length="4s", picture="SYNTH", attrs=""):
    return f'<tr {attrs}><td>{cut}</td><td>{tc}</td><td>{length}</td><td>{picture}</td></tr>'


class CutTests(NetworkBlockedCase):
    def setUp(self):
        super().setUp()
        self.root = Path(__file__).resolve().parents[1] / "out" / "pt-tests" / uuid4().hex
        self.root.mkdir(parents=True)
        self.source_module = importlib.import_module("plating_tools.cuts.source")
        self.extract = importlib.import_module("plating_tools.cuts.extract")
        self.errors = importlib.import_module("plating_tools.errors")

    def source(self, text, newline="\n", bom=False):
        path = self.root / (uuid4().hex + " 한글.md")
        path.write_bytes((b"\xef\xbb\xbf" if bom else b"") + text.replace("\n", newline).encode("utf-8"))
        return self.source_module.NotionMdFile(path)

    def actual(self):
        path = Path(os.environ.get("PLATING_TOOLS_F", r"C:\Users\uicus\Dev\dot-handoff\notion_컷표_fetch_2026-11-07T0706Z.md"))
        if not path.is_file():
            self.skipTest("실제 F 없음")
        source = self.source_module.NotionMdFile(path)
        if source.fingerprint().sha256 != "cae22e2f0637d29ebfe1f6e5a7daa973ee8ea72a397373246ecdddf9cfe6dc37":
            self.skipTest("실제 F 지문 다름")
        return source

    def test_C1_C2_mixed_sections_and_span_titles(self):
        sections = importlib.import_module("plating_tools.cuts.sections").parse_sections(self.actual())
        self.assertEqual([s.scene_id for s in sections if s.container == "toggle_h3"], ["S#01", "S#02", "S#10", "S#11"])
        self.assertEqual(sections[-1].where.line_start, 4881)
        self.assertIsNone(sections[-1].scene_id)
        self.assertEqual(sections[8].title_text, "S#09 수정")
        self.assertEqual(sections[11].title_text, "S#12 수정")
        self.assertTrue(sections[8].title_annotations)

    def test_C3_C4_split_id_annotations_and_headers(self):
        sections = importlib.import_module("plating_tools.cuts.sections").parse_sections(self.actual())
        cells = [cell for _, cells in sections[1].tables[0].rows for cell in cells]
        cell = next(c for c in cells if c.text == "S#02-C016-1")
        self.assertTrue(cell.annotations)
        self.assertIn("discussion-urls", cell.raw_html)
        self.assertEqual(sections[1].tables[0].header[-1], "사운드")
        result = self.extract.extract_scene(self.actual(), "04")
        fields = result.targets[0].fields
        self.assertEqual(fields["dialogue_sound"].kind, "present")
        self.assertEqual(fields["dialogue"].kind, "absent")
        self.assertEqual(fields["sound"].kind, "absent")

    def test_C5_C6_row_and_field_states_are_independent(self):
        result = self.extract.extract_scene(self.actual(), "S#01")
        first = result.targets[0]
        self.assertEqual(first.row_state, "done")
        self.assertEqual(first.fields["dialogue"].cell.colors[0].state, "todo")
        self.assertEqual(first.fields["sound"].cell.colors, ())
        self.assertEqual(first.tc.start_s, Decimal("0"))
        self.assertEqual(first.tc.end_s, Decimal("4"))
        third = next(r for r in result.targets if r.cut_id == "S#01-C003")
        self.assertEqual(third.row_state, "todo")
        self.assertEqual(third.fields["cut_id"].cell.colors[0].state, "done")

    def test_C7_C12_tc_and_context(self):
        result = self.extract.extract_scene(self.actual(), "04")
        self.assertEqual(result.targets[0].tc.end_s, Decimal("2.0"))
        self.assertEqual(result.targets[0].length.raw, "2.0s")
        self.assertEqual(result.targets[0].row_state, "unknown")
        self.assertTrue(result.context[0].row.cut_id.startswith("S#03"))
        self.assertTrue(result.context[1].row.cut_id.startswith("S#05"))

    def test_C9_title_color_does_not_change_rows(self):
        sections = importlib.import_module("plating_tools.cuts.sections").parse_sections(self.actual())
        self.assertEqual(sections[9].title_colors[0].state, "revise")
        result = self.extract.extract_scene(self.actual(), "10")
        self.assertFalse(any(r.row_state == "revise" for r in result.targets))

    def test_C10_summary_id_cannot_be_expanded(self):
        with self.assertRaises(self.errors.InputError):
            self.extract.extract_scene(self.actual(), "02", cut_ids=("S#02-C016-1~3",))

    def test_C11_recording_section_is_excluded(self):
        result = self.extract.extract_scene(self.actual(), "14")
        self.assertEqual(len(result.targets), 24)
        self.assertNotIn("영어 대사", [name for name, _ in result.header_map])

    def test_C13_revision_wins_and_C14_ambiguity_needs_line(self):
        src = self.source("### S#01\n" + table([row()]) + "### S#01 수정\n" + table([row(picture="SYNTH 수정")]))
        result = self.extract.extract_scene(src, "01")
        self.assertTrue(result.selected["is_revision"])
        self.assertEqual(len(result.rejected), 1)
        duplicate = self.source("### S#01 수정\n" + table([row()]) + '<toggle heading="h3">\nS#01 수정\n' + table([row()]) + '</toggle>\n')
        with self.assertRaisesRegex(self.errors.InputError, "CT002"):
            self.extract.extract_scene(duplicate, "01")
        self.assertEqual(len(self.extract.extract_scene(duplicate, "01", section_line=1).targets), 1)

    def test_C15_nested_table_is_reported(self):
        src = self.source("### S#01\n" + table([row()]) + '<toggle>\nSYNTH\n' + table([row()]) + '</toggle>\n')
        result = self.extract.extract_scene(src, "01")
        self.assertIn("CT015", [f.code for f in result.findings])
        self.assertEqual(len(result.targets), 1)

    def test_C16_duplicate_ids_preserve_order(self):
        result = self.extract.extract_scene(self.source("### S#01\n" + table([row(), row()])), "01")
        self.assertIn("CT005", [f.code for f in result.findings])
        self.assertEqual([r.order for r in result.targets], [0, 1])

    def test_C17_duplicate_columns_and_cell_count(self):
        for text in (table([row()], ("컷", "TC", "TC", "화면")), table(['<tr><td>S#01-C001</td></tr>'])):
            result = self.extract.extract_scene(self.source("### S#01\n" + text), "01")
            self.assertIn("CT004", [f.code for f in result.findings])

    def test_C18_unknown_column_empty_and_br(self):
        src = self.source("### S#01\n" + table([row(picture="a<br />b")], ("컷", "TC", "길이", "모르는 열")))
        result = self.extract.extract_scene(src, "01")
        self.assertEqual(result.targets[0].extra[0].text, "a\nb")
        self.assertIn("<br />", result.targets[0].extra[0].raw_html)
        self.assertIn("CT010", [f.code for f in result.findings])
        empty = self.extract.extract_scene(self.source("### S#01\n" + table([row(picture="")])), "01")
        self.assertEqual(empty.targets[0].fields["picture"].kind, "empty")

    def test_C19_unsupported_times_are_preserved(self):
        for tc in ("00:00-00:04", "00:00:00–00:00:04", "01:50–02.0"):
            result = self.extract.extract_scene(self.source("### S#01\n" + table([row(tc=tc, length="4초")])), "01")
            self.assertTrue({"CT006", "CT007"}.issubset({f.code for f in result.findings}))
            self.assertEqual(result.targets[0].tc.raw, tc)

    def test_C20_C21_unknown_color_and_removed(self):
        for attrs, state in (("", "unknown"), ('color="blue_bg"', "unknown"), ('color="gray_bg"', "removed")):
            result = self.extract.extract_scene(self.source("### S#01\n" + table([row(attrs=attrs)])), "01")
            self.assertEqual(result.targets[0].row_state, state)
            self.assertEqual(result.targets[0].excluded_from_generation, state == "removed")

    def test_C22_encodings_keep_positions(self):
        text = "### S#01\n" + table([row()])
        results = [self.extract.extract_scene(self.source(text, newline, bom), "01") for newline, bom in (("\n", False), ("\r\n", False), ("\r\n", True))]
        self.assertEqual([r.targets[0].where.line_start for r in results], [4, 4, 4])

    def test_header_content_selects_table_without_header_row(self):
        for heading in ("### S#01\n", '<toggle heading="h3">\nS#01\n'):
            with self.subTest(heading=heading):
                text = heading + table([row()]).replace(' header-row="true"', '')
                if heading.startswith('<toggle'):
                    text += '</toggle>\n'
                result = self.extract.extract_scene(self.source(text), "01")
                self.assertEqual(len(result.targets), 1)
                self.assertEqual([(f.code, f.severity) for f in result.findings], [("CT018", "info")])
                self.assertIsNotNone(result.findings[0].where)

    def test_header_row_value_does_not_select_table(self):
        for attribute in ('header-row="true"', 'header-row="false"', 'header-row="other"'):
            with self.subTest(attribute=attribute):
                text = "### S#01\n" + table([row()]).replace('header-row="true"', attribute)
                result = self.extract.extract_scene(self.source(text), "01")
                self.assertEqual(len(result.targets), 1)
                self.assertFalse(result.findings)

    def test_cut_table_requires_first_two_header_cells(self):
        for headers in (("컷", "길이", "TC", "화면"), ("TC", "컷", "길이", "화면")):
            with self.subTest(headers=headers):
                source = self.source("### S#01\n" + table([row()], headers))
                with self.assertRaisesRegex(self.errors.InputError, "CT003"):
                    self.extract.extract_scene(source, "01")

    def test_recording_table_is_outside_scene_and_not_a_cut_table(self):
        text = "### S#01\n" + table([row()]).replace(' header-row="true"', '')
        text += "### 녹음 대본\n" + table([row(cut="S#01-C999")])
        source = self.source(text)
        sections = importlib.import_module("plating_tools.cuts.sections").parse_sections(source)
        result = self.extract.extract_scene(source, "01")
        self.assertEqual([r.cut_id for r in result.targets], ["S#01-C001"])
        self.assertIsNone(sections[-1].scene_id)
        self.assertFalse(sections[-1].tables[0].is_cut_table)

    def test_multiple_content_matched_tables_remain_ambiguous(self):
        text = "### S#01\n" + table([row()]) + table([row()]).replace(' header-row="true"', '')
        with self.assertRaisesRegex(self.errors.InputError, "CT003"):
            self.extract.extract_scene(self.source(text), "01")

    def test_cli_info_only_header_finding_keeps_exit_zero(self):
        inputs = self.root / "inputs"
        inputs.mkdir()
        source = inputs / "SYNTH.md"
        source.write_text("### S#01\n" + table([row()]).replace(' header-row="true"', ''), encoding="utf-8")
        config = self.root / "plating.toml"
        config.write_text("[paths]\nwrite_root='.'\noutput_root='out'\n", encoding="utf-8")
        target = self.root / "out" / "extract"
        result = subprocess.run(
            [sys.executable, "-m", "plating_tools", "--config", str(config), "cuts", "extract",
             "--input", str(source), "--scene", "01", "--out", str(target)],
            env={**os.environ, "PYTHONPATH": str(Path(__file__).resolve().parents[1] / "src")},
            capture_output=True, text=True, encoding="utf-8", timeout=30, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["exit_code"], 0)
        data = json.loads((target / "cuts.json").read_text(encoding="utf-8"))
        self.assertEqual([(f["code"], f["severity"]) for f in data["findings"]], [("CT018", "info")])
