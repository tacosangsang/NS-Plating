"""SYNTH: S7~S10. 격리 사본도 저장소 out/에만 만든다. 삭제하지 않는다."""
import ast
import importlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from uuid import uuid4

from tests._pt_support import NetworkBlockedCase

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))


class IndependenceTests(NetworkBlockedCase):
    def setUp(self):
        super().setUp()
        self.root = REPO / "out" / "pt-tests" / uuid4().hex
        self.root.mkdir(parents=True)

    def test_S7_cli_in_copy_without_p1_packages(self):
        workflow = Path(os.environ.get("PLATING_TOOLS_WORKFLOW_DIR", r"C:\Users\uicus\Dev\NS-Plating\workflow"))
        if not workflow.is_dir():
            self.skipTest("실제 W 없음")
        source = self.root / "inputs"
        source.mkdir()
        cutfile = source / "SYNTH.md"
        cutfile.write_text('### S#01\n<table header-row="true"><tr><td>컷</td><td>TC</td><td>길이</td></tr><tr><td>S#01-C001</td><td>00:00–00:04</td><td>4s</td></tr></table>\n', encoding="utf-8")
        cfg = self.root / "plating.toml"
        cfg.write_text(f"[paths]\nwrite_root='.'\noutput_root='out'\nworkflow_dir='{workflow}'\n[cuts]\ninput='{cutfile}'\n[qc]\ntimeout_s='SYNTH 미확인'\n[network]\nmax_bytes='SYNTH 미확인'\n[tools]\nffmpeg_path=[]\n", encoding="utf-8")
        copied = self.root / "src" / "plating_tools"
        shutil.copytree(REPO / "src" / "plating_tools", copied, ignore=shutil.ignore_patterns("refs", "versions", "qc.py", "__pycache__"))
        for name in ("refs", "versions", "qc.py"):
            self.assertFalse((copied / name).exists())
        (copied.parent / "sitecustomize.py").write_text(
            'import atexit, json, os, socket, sys\n'
            'from pathlib import Path\n'
            'attempts = 0\n'
            'def reject(*args, **kwargs):\n'
            '    global attempts\n'
            '    attempts += 1\n'
            '    raise AssertionError("SYNTH P0 network forbidden")\n'
            'socket.create_connection = reject\n'
            'socket.socket.connect = reject\n'
            'def record():\n'
            '    loaded = [n for n in sys.modules if n == "plating_qc" or n.startswith(("plating_qc.", "plating_tools.refs", "plating_tools.versions", "plating_tools.qc"))]\n'
            '    Path(os.environ["PLATING_TEST_NETWORK_AUDIT"]).write_text(json.dumps({"attempts": attempts, "loaded": loaded}), encoding="utf-8")\n'
            'atexit.register(record)\n', encoding="utf-8")
        env = {**os.environ, "PYTHONPATH": str(copied.parent), "PYTHONDONTWRITEBYTECODE": "1", "PYTHONIOENCODING": "utf-8"}
        def run(*args):
            audit = self.root / f"network-{uuid4().hex}.json"
            result = subprocess.run([sys.executable, "-m", "plating_tools", *args], cwd=self.root, env={**env, "PLATING_TEST_NETWORK_AUDIT": str(audit)}, capture_output=True, text=True, encoding="utf-8", timeout=30, check=False)
            self.assertEqual(json.loads(audit.read_text(encoding="utf-8")), {"attempts": 0, "loaded": []})
            return result
        self.assertEqual(run("--help").returncode, 0)
        for group in ("refs", "versions", "qc"):
            self.assertEqual(run(group, "--help").returncode, 0)
        inventory = run("cuts", "inventory")
        self.assertEqual(inventory.returncode, 0, inventory.stderr)
        result = run("cuts", "extract", "--scene", "01")
        self.assertEqual(result.returncode, 0, result.stderr)
        cuts = Path(json.loads(result.stdout)["output"]) / "cuts.json"
        skeleton = run("prompt", "skeleton", "--cuts-json", str(cuts), "--kind", "video")
        self.assertEqual(skeleton.returncode, 1, skeleton.stderr)
        output = Path(json.loads(skeleton.stdout)["output"])
        check = run("prompt", "check", "--prompt", str(output / "skeleton.md"), "--kind", "video")
        self.assertEqual(check.returncode, 1, check.stderr)
        gate = run("gate", "check", "--gate", str(output / "gate.toml"), "--prompt", str(cutfile))
        self.assertEqual(gate.returncode, 1, gate.stderr)
        self.assertEqual(run("gate", "cost", "--model", "Seedance 2.5", "--mode", "new", "--resolution", "480p", "--seconds", "4").returncode, 0)
        self.assertEqual(run("refs", "check", "--list", str(cutfile)).returncode, 4)
        self.assertEqual(run("versions", "check", "--spec", str(cutfile)).returncode, 4)
        self.assertEqual(run("qc", "probe", str(cutfile)).returncode, 4)

    def test_S8_p0_imports_only_standard_library_and_p0(self):
        forbidden = {"refs", "versions", "qc", "plating_qc"}
        for file in (REPO / "src" / "plating_tools").rglob("*.py"):
            if file.relative_to(REPO / "src" / "plating_tools").parts[0] in {"refs", "versions", "qc.py"}:
                continue
            tree = ast.parse(file.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    imports = [alias.name for alias in node.names]
                elif isinstance(node, ast.ImportFrom):
                    imports = [node.module or ""]
                else:
                    continue
                for name in imports:
                    self.assertFalse(forbidden & set(name.split(".")), (file, name))
                    if not isinstance(node, ast.ImportFrom) or node.level == 0:
                        self.assertIn(name.split(".")[0], {*sys.stdlib_module_names, "plating_tools", "__future__"})

    def test_S9_p0_does_not_import_network_clients(self):
        for file in (REPO / "src" / "plating_tools").rglob("*.py"):
            if file.relative_to(REPO / "src" / "plating_tools").parts[0] in {"refs", "versions", "qc.py"}:
                continue
            names = {n.id for n in ast.walk(ast.parse(file.read_text(encoding="utf-8"))) if isinstance(n, ast.Name)}
            self.assertFalse(names & {"socket", "urllib", "http", "requests", "httpx", "httpx2"}, file)

    def test_S10_document_commands_remain_data(self):
        docs = importlib.import_module("plating_tools.docs")
        textio = importlib.import_module("plating_tools.textio")
        path = self.root / "SYNTH.md"
        path.write_text('# SYNTH\n## payload\n```text\n$(start-process SYNTH)\nC:\\SYNTH\\outside.txt\n```\n', encoding="utf-8")
        doc = textio.read_document(path, "SYNTH")
        with patch("subprocess.run", side_effect=AssertionError("문서 실행 금지")) as process, patch("builtins.open", side_effect=AssertionError("문서 경로 열기 금지")) as opened, patch("pathlib.Path.open", side_effect=AssertionError("문서 경로 열기 금지")):
            result = docs.resolve(doc, docs.Anchor("SYNTH", ("SYNTH", "payload"), "fences", 1))
        self.assertEqual(len(result), 1)
        process.assert_not_called()
        opened.assert_not_called()

    def test_S9_default_test_temp_directory_stays_in_repository(self):
        self.assertTrue(Path(tempfile.gettempdir()).resolve().is_relative_to(REPO / "out" / "pt-tests"))
