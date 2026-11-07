import os
from pathlib import Path
import subprocess
import sys
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "tools" / "claude_design.py"


class ClaudeDesignTests(unittest.TestCase):
    def test_low_balance_stops_before_request(self):
        request = SCRIPT.parents[1] / "README.md"
        result = subprocess.run(
            [sys.executable, str(SCRIPT), str(request), "--balance-before", "5", "--output", "unused.md"],
            capture_output=True, text=True, env=os.environ.copy(), check=False,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("5", result.stderr)

    def test_missing_request_stops_before_request(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "missing-request.md", "--balance-before", "100", "--output", "unused.md"],
            capture_output=True, text=True, env=os.environ.copy(), check=False,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("missing-request.md", result.stderr)


if __name__ == "__main__":
    unittest.main()
