"""save_next_version.py를 가짜 bpy로 검사한다. 실제 Blender 실행은 검증하지 않는다."""
import runpy
import subprocess
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / "tools" / "blender" / "save_next_version.py"


class FakeItem:
    def __init__(self, filepath: str) -> None:
        self.filepath = filepath
        self.library = None


class BlenderSaveTests(unittest.TestCase):
    def test_relative_paths_are_absolute_only_while_saving_and_child_uses_utf8(self) -> None:
        image, absolute = FakeItem("//tex/wood.png"), FakeItem("C:/lib/stone.png")
        seen: dict[str, object] = {}

        def save_as_mainfile(**kwargs: object) -> set[str]:
            seen["paths"] = (image.filepath, absolute.filepath)
            Path(str(kwargs["filepath"])).write_bytes(b"blend")
            return {"FINISHED"}

        data = types.SimpleNamespace(images=[image, absolute], libraries=[], movieclips=[], sounds=[], fonts=[],
                                     cache_files=[], volumes=[])
        bpy = types.SimpleNamespace(data=data, path=types.SimpleNamespace(abspath=lambda path: "/scene/" + path[2:]),
                                    ops=types.SimpleNamespace(wm=types.SimpleNamespace(save_as_mainfile=save_as_mainfile)))

        def run(command: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
            seen["encoding"] = kwargs["env"]["PYTHONIOENCODING"]
            return subprocess.CompletedProcess(command, 0, "", "")

        with tempfile.TemporaryDirectory() as folder, patch.dict(sys.modules, {"bpy": bpy}), \
                patch("subprocess.run", side_effect=run):
            config = Path(folder) / "plating.toml"
            config.write_text("", encoding="utf-8")
            main = runpy.run_path(str(SCRIPT))["main"]
            code = main(["chair", "--root", folder, "--change", "c", "--by", "ts",
                         "--python", sys.executable, "--config", str(config)])
        self.assertEqual(code, 0)
        self.assertEqual(seen["paths"], ("/scene/tex/wood.png", "C:/lib/stone.png"))
        self.assertEqual((image.filepath, absolute.filepath), ("//tex/wood.png", "C:/lib/stone.png"))
        self.assertEqual(seen["encoding"], "utf-8")


if __name__ == "__main__":
    unittest.main()
