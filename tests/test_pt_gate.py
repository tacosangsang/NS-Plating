"""SYNTH/T2: G1~G13 게이트·비용 계약."""
import importlib
import os
import sys
import unittest
from tests._pt_support import NetworkBlockedCase
from dataclasses import replace
from decimal import Decimal
from pathlib import Path
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))


class GateTests(NetworkBlockedCase):
    def setUp(self):
        super().setUp()
        self.docs = importlib.import_module("plating_tools.docs")
        self.gate = importlib.import_module("plating_tools.gate.checklist")
        self.cost = importlib.import_module("plating_tools.gate.cost")
        self.plan = importlib.import_module("plating_tools.prompt.plan")
        self.model = importlib.import_module("plating_tools.model")
        workflow = Path(os.environ.get("PLATING_TOOLS_WORKFLOW_DIR", r"C:\Users\uicus\Dev\NS-Plating\workflow"))
        if not workflow.is_dir():
            self.skipTest("실제 W 없음")
        self.store = self.docs.WorkflowDir(workflow)
        self.rules = self.gate.read_gate_rules(self.store)

    def inputs(self):
        return tuple(self.gate.ItemInput(i, "예", "", "", ("SYNTH 검수 기록",), "SYNTH 검수자") for i in range(1, 9))

    def context(self, machine=None):
        return self.gate.GateContext("a" * 64, self.rules.approval_words, machine or {}, None, self.model.Unknown("SYNTH 미확인"))

    def clip(self, **changes):
        unknown = self.model.Unknown("SYNTH 미입력")
        clip = self.plan.ClipPlan("A", "video", ("S#01-C001",), unknown, Decimal("4"), "new", "Seedance 2.5", "480p", unknown, "없음", (), {}, unknown, (), ())
        return replace(clip, **changes)

    def test_G1_checklist_is_original_and_above_prompt(self):
        result = self.gate.evaluate_gate(self.rules.lines, self.inputs(), self.context(), None)
        md = self.gate.gate_md(result, "SYNTH_PROMPT")
        self.assertLess(md.index(self.rules.lines[-1].text), md.index("SYNTH_PROMPT"))
        self.assertEqual(len(result.items), 8)

    def test_G2_wrong_item_count_fails(self):
        for lines in (self.rules.lines[:7], (*self.rules.lines, self.rules.lines[0])):
            with self.assertRaises(importlib.import_module("plating_tools.errors").InputError):
                self.gate.evaluate_gate(lines, self.inputs(), self.context(), None)

    def test_G3_G5_no_answer_stays_incomplete(self):
        result = self.gate.evaluate_gate(self.rules.lines, (), self.context(), None)
        self.assertFalse(result.checklist_complete)
        self.assertTrue(all(i.status == "미완료" for i in result.items))

    def test_G4_no_requires_alternative_and_na_requires_reason(self):
        for answer in ("아니오", "해당 없음", "미확인"):
            inputs = list(self.inputs())
            inputs[0] = replace(inputs[0], answer=answer, reason="", alternative="")
            result = self.gate.evaluate_gate(self.rules.lines, tuple(inputs), self.context(), None)
            self.assertEqual(result.items[0].status, "미완료")

    def test_G6_machine_error_contradicts_yes(self):
        error = self.model.Finding("REMOVED", self.model.Severity.ERROR, "SYNTH removed")
        result = self.gate.evaluate_gate(self.rules.lines, self.inputs(), self.context({4: (error,)}), None)
        self.assertEqual(result.items[3].status, "기계 소견과 충돌")

    def test_G7_approval_is_separate_and_bound_to_prompt(self):
        proof = self.gate.ApprovalEvidence("생성해", "SYNTH 대화", "SYNTH", "2026-11-07", "a" * 64)
        for approval, status in ((None, "승인 기록 없음"), (replace(proof, prompt_sha256="b" * 64), "승인 기록 불일치"), (replace(proof, quote="프롬프트 준비"), "어휘 불명확"), (proof, "승인 기록 있음")):
            result = self.gate.evaluate_gate(self.rules.lines, self.inputs(), self.context(), approval)
            self.assertTrue(result.checklist_complete)
            self.assertEqual(result.approval.status, status)

    def test_G8_new_four_seconds_480p_is_eighty_crons(self):
        result = self.cost.cost_for(self.clip(), self.cost.read_cost_table(self.store))
        self.assertEqual(result.lines[0].amount, Decimal("80"))
        self.assertEqual(result.lines[0].unit, "Crons")
        self.assertEqual(len(result.doc_versions[0].sha256), 64)

    def test_G9_edit_ceil_uses_input_length(self):
        result = self.cost.cost_for(self.clip(mode="edit", resolution="1080p", edit_input_seconds=Decimal("1.5"), gen_seconds=Decimal("9")), self.cost.read_cost_table(self.store))
        self.assertEqual(result.lines[0].amount, Decimal("220"))

    def test_G10_new_1080p_has_separate_alternatives(self):
        result = self.cost.cost_for(self.clip(resolution="1080p"), self.cost.read_cost_table(self.store))
        self.assertEqual([line.amount for line in result.lines[:2]], [Decimal("324"), Decimal("80")])
        self.assertEqual(result.lines[2].unit, "Higgsfield 크레딧")
        self.assertIsInstance(result.lines[2].amount, self.model.Unknown)
        self.assertEqual(result.totals, {"Crons": Decimal("324")})

    def test_G11_unknown_or_unsupported_values_do_not_produce_amount(self):
        for changes in ({"model": "SYNTH"}, {"mode": "edit", "resolution": "480p"}, {"gen_seconds": Decimal("3")}, {"gen_seconds": Decimal("4.5")}):
            result = self.cost.cost_for(self.clip(**changes), self.cost.read_cost_table(self.store))
            self.assertIsInstance(result.lines[0].amount, self.model.Unknown)
            self.assertTrue(result.findings)

    def test_G12_rate_pattern_or_unit_changes_fail(self):
        root = Path(__file__).resolve().parents[1] / "out" / "pt-tests" / uuid4().hex
        root.mkdir(parents=True)
        errors = importlib.import_module("plating_tools.errors")
        textio = importlib.import_module("plating_tools.textio")
        for text in ('# 07. 도구·환경 제약\n## 1. 비용표 (Tokens / 크레딧)\nSYNTH', '# 07. 도구·환경 제약\n## 1. 비용표 (Crons / 크레딧)\n| 영상 본 생성 | SYNTH | 단가 미확인 |'):
            path = root / (uuid4().hex + ".md")
            path.write_text(text, encoding="utf-8")
            with self.assertRaises(errors.InputError):
                self.cost.parse_rates(textio.read_document(path, "W07"))

    def test_G13_stale_cut_fingerprint_is_error(self):
        machine, fresh = self.gate.machine_findings(None, {"source": {"sha256": "b" * 64}, "targets": [], "context": []}, None, None, "a" * 64, "a" * 64)
        self.assertFalse(fresh)
        self.assertTrue(any(f.severity.value == "error" for f in machine[4]))

    def test_generation_above_document_limit_requires_split(self):
        machine, _ = self.gate.machine_findings(self.clip(gen_seconds=self.rules.max_seconds + 1), None, None, None, None, "a" * 64, max_seconds=self.rules.max_seconds)
        self.assertTrue(any(f.code == "GATE_DURATION" and f.severity.value == "error" for f in machine[2]))
