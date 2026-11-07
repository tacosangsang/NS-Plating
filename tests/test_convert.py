import sys
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from plating_qc.errors import QCError
from plating_qc.publish import publish


class PublishTests(unittest.TestCase):
    def test_existing_target_is_not_replaced(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "source"
            target = Path(directory) / "target"
            source.write_text("new")
            target.write_text("old")
            with self.assertRaises(QCError) as caught:
                publish(source, target)
            self.assertEqual(caught.exception.code, 3)
            self.assertEqual(target.read_text(), "old")

    @unittest.skipUnless(sys.platform == "win32", "Windows rename fallback")
    def test_windows_falls_back_when_hardlink_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "source"
            target = Path(directory) / "target"
            source.write_text("data")
            with patch("plating_qc.publish.os.link", side_effect=OSError("unsupported")):
                publish(source, target)
            self.assertEqual(target.read_text(), "data")

    @unittest.skipUnless(sys.platform == "win32", "Windows rename fallback")
    def test_windows_fallback_keeps_existing_target(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "source"
            target = Path(directory) / "target"
            source.write_text("new")
            target.write_text("old")
            with patch("plating_qc.publish.os.link", side_effect=OSError("unsupported")):
                with self.assertRaises(QCError) as caught:
                    publish(source, target)
            self.assertEqual(caught.exception.code, 3)
            self.assertEqual(target.read_text(), "old")


if __name__ == "__main__":
    unittest.main()
