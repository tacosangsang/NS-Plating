"""SYNTH/T2: 문서 앵커, 골격과 완성본 검사 P1~P12."""
import importlib
import json
import os
import subprocess
import sys
import unittest
from tests._pt_support import NetworkBlockedCase
from pathlib import Path
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))


class PromptTests(NetworkBlockedCase):
    def setUp(self):
        super().setUp()
        self.root = Path(__file__).resolve().parents[1] / "out" / "pt-tests" / uuid4().hex
        self.root.mkdir(parents=True)
        self.docs = importlib.import_module("plating_tools.docs")
        self.rules_module = importlib.import_module("plating_tools.prompt.rules")
        self.assemble = importlib.import_module("plating_tools.prompt.assemble")
        self.check = importlib.import_module("plating_tools.prompt.check")
        self.plan_module = importlib.import_module("plating_tools.prompt.plan")
        self.errors = importlib.import_module("plating_tools.errors")

    def rules(self):
        path = Path(os.environ.get("PLATING_TOOLS_WORKFLOW_DIR", r"C:\Users\uicus\Dev\NS-Plating\workflow"))
        if not path.is_dir():
            self.skipTest("실제 W 없음")
        return self.rules_module.read_rules(self.docs.WorkflowDir(path))

    def cuts(self, removed=False):
        source = importlib.import_module("plating_tools.cuts.source")
        extract = importlib.import_module("plating_tools.cuts.extract")
        path = self.root / "SYNTH.md"
        color = ' color="gray_bg"' if removed else ''
        path.write_text('### S#01\n<table header-row="true"><tr><td>컷</td><td>TC</td><td>길이</td><td>화면</td></tr><tr' + color + '><td>S#01-C001</td><td>00:00–00:04</td><td>4s</td><td>SYNTH</td></tr></table>\n', encoding="utf-8")
        return extract.extract_scene(source.NotionMdFile(path), "01")

    def plan(self, extra=""):
        path = self.root / (uuid4().hex + ".toml")
        path.write_text('scene="S#01"\n[[clip]]\nid="A"\nkind="video"\ncuts=["S#01-C001"]\ngen_seconds="6"\npeople="없음"\n' + extra, encoding="utf-8")
        return self.plan_module.load_plan(path, "A")

    def test_P1_P3_original_blocks_and_order_have_sources(self):
        rules = self.rules()
        block = rules.catalog["AVOID"]
        source = Path(block.where.doc_path) if hasattr(block.where, "doc_path") else rules.documents["W10"]
        doc = self.docs.read_document(source, "W10")
        expected = "\n".join(doc.lines[block.where.line_start - 1:block.where.line_end])
        self.assertEqual(block.text, expected)
        self.assertEqual(block.where.mark.value, "파일 단위 예외")
        self.assertEqual(len(rules.order), 8)
        self.assertTrue(rules.order[0].startswith("REFERENCE ROLES"))

    def test_P2_anchor_changes_fail_without_fallback(self):
        textio = importlib.import_module("plating_tools.textio")
        anchor = self.docs.Anchor("SYNTH", ("SYNTH", "1. 블록"), "fences", 1)
        for text in ("# SYNTH\n## 1. 다른 제목\n```\nx\n```", "# SYNTH\n## 1. 블록\n```\nx\n```\n## 1. 블록\n```\ny\n```", "# SYNTH\n## 1. 블록\n```\nx"):
            path = self.root / (uuid4().hex + ".md")
            path.write_text(text, encoding="utf-8")
            with self.assertRaises(self.errors.InputError):
                self.docs.resolve(textio.read_document(path, "SYNTH"), anchor)

    def test_P4_P12_no_plan_stays_unresolved(self):
        skeleton = self.assemble.build_skeleton(self.cuts(), None, self.rules())
        self.assertEqual(skeleton.lengths.verdict, "not_final")
        self.assertGreater(skeleton.lengths.placeholders, 0)
        self.assertIsInstance(skeleton.length_table[0]["gen_seconds"], importlib.import_module("plating_tools.model").Unknown)
        md = self.assemble.skeleton_md(skeleton)
        self.assertIn("[검수 대기]", md)
        self.assertIn("(전송본 아님)", md)

    def test_P5_plan_preserves_lengths_and_computes_slack(self):
        skeleton = self.assemble.build_skeleton(self.cuts(), self.plan(), self.rules())
        self.assertEqual(str(skeleton.length_table[0]["slack"]), "2")

    def test_P6_absent_people_or_far_faces_excluded(self):
        select = importlib.import_module("plating_tools.prompt.select")
        rules = self.rules()
        decisions = select.select_blocks(self.plan(), rules)
        self.assertEqual(next(d.decision for d in decisions if d.block_key == "FACE_RULE"), "제외")
        self.assertEqual(next(d.decision for d in select.select_blocks(None, rules) if d.block_key == "FACE_RULE"), "미결")
        for name, group, face in (("진우", "하층민", "close"), ("흰토끼", "하층민", "close"), ("SYNTH", "상류층", "close"), ("SYNTH", "하층민", "far")):
            from dataclasses import replace
            person = self.plan_module.CharacterMeta(name, group, face, "SYNTH")
            plan = replace(self.plan(), people="있음", characters=(person,))
            result = select.select_blocks(plan, rules)
            self.assertEqual(next(d.decision for d in result if d.block_key == "FACE_RULE"), "제외")

    def test_underclass_proportions_follow_style_only_for_underclass(self):
        from dataclasses import replace
        select = importlib.import_module("plating_tools.prompt.select")
        rules = self.rules()
        self.assertTrue(rules.catalog["UNDERCLASS_PROPORTIONS"].text.startswith("UNDERCLASS PROPORTIONS:"))
        for group, expected in (("하층민", "포함"), ("요리사", "제외")):
            person = self.plan_module.CharacterMeta("SYNTH", group, "far", "SYNTH")
            plan = replace(self.plan(), people="있음", characters=(person,))
            decision = next(d.decision for d in select.select_blocks(plan, rules) if d.block_key == "UNDERCLASS_PROPORTIONS")
            self.assertEqual(decision, expected, group)
        person = self.plan_module.CharacterMeta("SYNTH", "하층민", "far", "SYNTH")
        skeleton = self.assemble.build_skeleton(self.cuts(), replace(self.plan(), people="있음", characters=(person,)), rules)
        style_slot = next(s for s in skeleton.slots if "STYLE" in s.block_keys)
        self.assertEqual(style_slot.block_keys[:2], ("STYLE", "UNDERCLASS_PROPORTIONS"))

    def test_P7_image_scene_conflict_is_not_applied_to_video_skeleton(self):
        from dataclasses import replace
        skeleton = self.assemble.build_skeleton(self.cuts(), replace(self.plan(), scene_module="SCENE_D"), self.rules())
        self.assertNotIn("PR_CONFLICT", [f.code for f in skeleton.conflicts])
        self.assertNotIn("SCENE_D", [k for s in skeleton.slots for k in s.block_keys])

    def test_P8_image_limits_and_unicode_counts(self):
        rules = self.rules()
        for text, verdict in (("a" * 3000, "within"), ("a" * 3001, "over"), ("a" * 2999 + "\U0001D11E", "over_by_utf16_only")):
            self.assertEqual(self.check.length_report(text, "image", rules).verdict, verdict)
        result = self.check.length_report("a\r\nb\r\n", "image", rules)
        self.assertEqual(result.total.codepoints, 3)

    def test_P9_video_has_no_confirmed_limit(self):
        result = self.check.length_report("a" * 4000, "video", self.rules())
        self.assertEqual(result.verdict, "no_limit")

    def test_P10_modified_blocks_placeholders_and_reference_errors(self):
        rules = self.rules()
        from dataclasses import replace
        ref = importlib.import_module("plating_tools.model").RefEntry(1, "SYNTH")
        plan = replace(self.plan(), references=(ref,))
        original = rules.catalog["STYLE"].text + "\n\n" + rules.catalog["AVOID"].text
        changed = original.replace(rules.catalog["STYLE"].text[-1], "X", 1)
        result = self.check.check_prompt(changed + '\n{{미결: SYNTH}}\n@[이미지 1](image_1) @image3', plan, rules, "video")
        self.assertTrue({"PR001", "PR002", "PR003", "PR004"}.issubset({f.code for f in result.findings}))

    def test_P11_block_placeholder_is_rejected(self):
        from dataclasses import replace
        rules = self.rules()
        blocks = dict(rules.catalog)
        blocks["STYLE"] = replace(blocks["STYLE"], text="{{SYNTH}}")
        with self.assertRaises(self.errors.InputError):
            self.assemble.build_skeleton(self.cuts(), self.plan(), replace(rules, catalog=blocks))

    def test_removed_cut_is_error_and_context_is_not_target(self):
        skeleton = self.assemble.build_skeleton(self.cuts(True), self.plan(), self.rules())
        self.assertTrue(any(f.severity.value == "error" for f in skeleton.conflicts))

    def test_video_excludes_scene_slot_and_keeps_upper_avoid_slot(self):
        from dataclasses import replace
        skeleton = self.assemble.build_skeleton(self.cuts(), replace(self.plan(), scene_module="SCENE_A"), self.rules())
        self.assertNotIn("SCENE_A", skeleton.slots[3].block_keys)
        self.assertIn("UPPER_AVOID", skeleton.slots[7].block_keys)

    def test_video_scene_modules_are_excluded_from_selection_and_check(self):
        from dataclasses import replace
        select = importlib.import_module("plating_tools.prompt.select")
        rules = self.rules()
        text = "\n\n".join(rules.catalog[key].text for key in ("STYLE", "AVOID", "UPPER_AVOID"))
        for module in importlib.import_module("plating_tools.profile_plating").SCENE_BLOCKS:
            with self.subTest(module=module):
                # Given
                plan = replace(self.plan(), scene_module=module)
                # When
                decisions = select.select_blocks(plan, rules)
                checked = self.check.check_prompt(text, plan, rules, "video")
                # Then
                scenes = [d for d in decisions if d.block_key.startswith("SCENE_")]
                self.assertTrue(all(d.decision == "제외" and d.reason == "이미지 전용 모듈(W10 7행)" for d in scenes))
                self.assertNotIn("PR001", [f.code for f in checked.findings])
                self.assertNotIn("PR_CONFLICT", [f.code for f in checked.findings])
                self.assertFalse(set(checked.blocks) & {d.block_key for d in scenes})

    def test_image_scene_module_still_requires_original_block(self):
        from dataclasses import replace
        # Given
        rules = self.rules()
        plan = replace(self.plan(), kind="image", scene_module="SCENE_LOW")
        text = "\n\n".join(rules.catalog[key].text for key in ("STYLE", "WORLD", "AVOID"))
        # When
        checked = self.check.check_prompt(text, plan, rules, "image")
        # Then
        self.assertIn("SCENE_LOW", checked.blocks)
        self.assertEqual([f.code for f in checked.findings if f.code.startswith("PR")], ["PR001"])

    def test_video_layout_module_is_still_selected(self):
        from dataclasses import replace
        # Given
        rules = self.rules()
        plan = replace(self.plan(), scene_module="LAYOUT_TRUCK")
        # When
        skeleton = self.assemble.build_skeleton(self.cuts(), plan, rules)
        # Then
        self.assertIn("LAYOUT_TRUCK", skeleton.slots[3].block_keys)

    def test_cli_checks_scene_block_only_for_images(self):
        # Given
        rules = self.rules()
        inputs = self.root / "inputs"
        inputs.mkdir()
        config = self.root / "plating.toml"
        config.write_text(f"[paths]\nworkflow_dir='{rules.documents['W10'].parent}'\n", encoding="utf-8")
        for kind in ("video", "image"):
            with self.subTest(kind=kind):
                prompt = inputs / f"{kind}.txt"
                prompt.write_text("\n\n".join(rules.catalog[key].text for key in ("STYLE", "WORLD", "AVOID")), encoding="utf-8")
                plan = inputs / f"{kind}.toml"
                plan.write_text(f'[[clip]]\nid="A"\nkind="{kind}"\npeople="없음"\nscene_module="SCENE_LOW"\n', encoding="utf-8")
                target = self.root / "out" / kind
                # When
                process = subprocess.run(
                    [sys.executable, "-m", "plating_tools", "--config", str(config), "prompt", "check",
                     "--prompt", str(prompt), "--plan", str(plan), "--kind", kind, "--out", str(target)],
                    env={**os.environ, "PYTHONPATH": str(Path(__file__).resolve().parents[1] / "src")},
                    capture_output=True, text=True, encoding="utf-8", timeout=30, check=False,
                )
                # Then
                self.assertEqual(process.returncode, int(kind == "image" or bool(rules.findings)), process.stderr)
                result = json.loads((target / "check.json").read_text(encoding="utf-8"))["result"]
                self.assertEqual([f["code"] for f in result["findings"] if f["code"] == "PR001"],
                                 ["PR001"] if kind == "image" else [])

    def test_image_check_always_checks_world_block(self):
        rules = self.rules()
        text = rules.catalog["STYLE"].text + "\n\n" + rules.catalog["AVOID"].text
        result = self.check.check_prompt(text, None, rules, "image")
        self.assertEqual(result.blocks["WORLD"], "원문 불일치")
