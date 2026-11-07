import importlib.util
from decimal import Decimal
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest

SPEC = importlib.util.spec_from_file_location("claude_design", Path(__file__).resolve().parents[1] / "tools" / "claude_design.py")
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)


class UsageTests(unittest.TestCase):
    def test_cost_includes_cache_read(self):
        self.assertEqual(module.estimate_cost(108, 62, 100), Decimal("0.001692"))

    def test_budget_limits(self):
        self.assertFalse(module.budget_allowed(Decimal("95"), Decimal("99")))
        self.assertFalse(module.budget_allowed(Decimal("2"), Decimal("5")))
        self.assertTrue(module.budget_allowed(Decimal("94.99"), Decimal("5.01")))

    def test_incomplete_response_gets_warning(self):
        self.assertTrue(module.response_text("hello", "end_turn").startswith("hello"))
        self.assertTrue(module.response_text("hello", "max_tokens").startswith("경고"))
        self.assertTrue(module.response_text("hello", "refusal").startswith("경고"))

    def test_error_is_recorded_with_partial_path(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            result = module.perform_request(root / "answer.md", root / "usage.jsonl", "req.md", "high", Decimal("0"), lambda file: (_ for _ in ()).throw(ConnectionError("failure")))
            self.assertEqual(result, 1)
            self.assertTrue((root / "answer.md.partial").exists())
            self.assertEqual(module.read_ledger(root / "usage.jsonl")[-1]["status"], "error")
            self.assertEqual(module.read_ledger(root / "usage.jsonl")[-1]["error_type"], "ConnectionError")

    def test_truncated_result_is_warning_and_exit_one(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            usage = SimpleNamespace(input_tokens=108, output_tokens=62, cache_read_input_tokens=0)
            message = SimpleNamespace(usage=usage, stop_reason="max_tokens")

            def call(file):
                file.write("partial answer")
                return message

            result = module.perform_request(root / "answer.md", root / "usage.jsonl", "req.md", "high", Decimal("0"), call)
            self.assertEqual(result, 1)
            self.assertTrue((root / "answer.md").read_text(encoding="utf-8").startswith("경고"))
            self.assertEqual(module.read_ledger(root / "usage.jsonl")[-1]["status"], "incomplete")


if __name__ == "__main__":
    unittest.main()
