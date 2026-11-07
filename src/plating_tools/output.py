"""배타적 파일 생성, staging 공개, 실패 격리. 기존 파일은 지우지 않는다."""
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from .errors import InputError, OutputConflict
from .model import json_text
from .paths import WritePolicy, within


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def new_target(root: Path, command: str, label: str) -> Path:
    safe = re.sub(r"[^\w-]", "", label.replace("#", ""))
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    return root / f"{stamp}-{uuid4().hex[:6]}_{command}_{safe}"


class RunDir:
    """한 실행의 가변 쓰기 상태와 공개 책임을 소유한다."""

    def __init__(self, target: Path, policy: WritePolicy):
        self.policy = policy
        self.target = policy.check(target)
        self.run_id = uuid4().hex
        self.stage = self.target.parent / f".staging-{self.run_id}"
        self.started = now()
        self.finished = False

    def __enter__(self):
        if self.target.exists():
            raise OutputConflict(f"출력 폴더 충돌: {self.target}")
        self.policy.check(self.stage).mkdir(parents=True, exist_ok=False)
        self.policy.check(self.stage)
        return self

    def write_text(self, name: str, text: str, encoding: str = "utf-8") -> None:
        path = self.policy.check(self.stage / name)
        if not within(path, self.stage):
            raise InputError(f"실행 폴더 밖 파일: {name}")
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("x", encoding=encoding, newline="\n") as stream:
            stream.write(text)

    def write_json(self, name: str, value) -> None:
        self.write_text(name, json_text(value))

    def finish(self, metadata) -> None:
        self.write_json("run.json", {**metadata, "started": self.started, "ended": now()})
        self.policy.check(self.stage)
        self.policy.check(self.target)
        if self.target.exists():
            raise OutputConflict(f"출력 공개 충돌: {self.target}")
        try:
            os.rename(self.stage, self.target)
        except FileExistsError as exc:
            raise OutputConflict(f"출력 공개 충돌: {self.target}") from exc
        self.finished = True

    def __exit__(self, exc_type, exc, traceback) -> bool:
        if self.finished:
            return False
        failed = self.policy.check(self.target.parent / "_failed" / self.run_id)
        failed.parent.mkdir(parents=True, exist_ok=True)
        log = self.stage / "run.json"
        self.policy.check(log)
        if not log.exists():
            self.write_json("run.json", {"status": "failed", "error": str(exc), "started": self.started, "ended": now()})
        else:
            self.write_json("failure.json", {"status": "failed", "error": str(exc)})
        self.policy.check(self.stage)
        os.rename(self.stage, failed)
        return False
