import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from plating_qc.backend.base import MediaBackend
from plating_qc.errors import QCError
from plating_qc.layout import SceneLayout


class LayoutTests(unittest.TestCase):
    def test_default_names(self):
        self.assertEqual(SceneLayout.from_config({}).names(), ("raw", "prores"))

    def test_rejects_same_raw_and_prores(self):
        with self.assertRaises(QCError) as caught:
            SceneLayout.from_config({"layout": {"raw": "raw", "prores": "RAW"}})
        self.assertEqual(caught.exception.code, 2)

    def test_unsupported_backend_method_is_exit_four(self):
        with self.assertRaises(QCError) as caught:
            MediaBackend().probe(Path("video.mp4"))
        self.assertEqual(caught.exception.code, 4)


if __name__ == "__main__":
    unittest.main()
