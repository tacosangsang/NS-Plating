"""버전 폴더의 배타적 공개·목록·지문을 소유한다."""
import hashlib
import os
import shutil
from collections.abc import Iterator, Mapping
from contextlib import contextmanager
from datetime import date
from pathlib import Path
from typing import Protocol
from uuid import uuid4

from ..errors import InputError, OutputConflict
from ..paths import WritePolicy
from .model import Version, required_text, version_number


class VersionStore(Protocol):
    def list(self, asset_dir: Path) -> tuple[Path, ...]: ...
    def hashes(self, directory: Path) -> Mapping[str, str]: ...
    def create(self, directory: Path, sources: tuple[Path, ...], change: str, by: str) -> Version: ...


@contextmanager
def asset_lock(asset_dir: Path, policy: WritePolicy) -> Iterator[None]:
    """manifest를 읽고 갱신하는 동안 같은 자산의 다른 쓰기를 거부한다."""
    path = policy.check(asset_dir / ".blockout.lock")
    try:
        stream = path.open("x", encoding="utf-8")
    except FileExistsError as exc:
        raise OutputConflict(f"자산 쓰기 잠금 충돌: {path}") from exc
    try:
        with stream:
            stream.write(f"pid={os.getpid()}\n")
            stream.flush()
            yield
    finally:
        policy.check(path).unlink()


class FileVersionStore:
    def __init__(self, policy: WritePolicy):
        self.policy = policy

    def list(self, asset_dir: Path) -> tuple[Path, ...]:
        return tuple(sorted(path for name in ("versions", "archive")
                            for path in (asset_dir / name).iterdir()))

    def hashes(self, directory: Path) -> Mapping[str, str]:
        """링크를 따라가지 않고 실제 상대 파일 목록과 SHA-256을 읽는다."""
        pending = [directory]
        hashes: dict[str, str] = {}
        while pending:
            path = pending.pop()
            if path.is_symlink() or path.is_junction():
                raise InputError(f"버전 폴더의 링크 금지: {path}")
            if path.is_dir():
                pending.extend(path.iterdir())
            elif path.is_file():
                with path.open("rb") as stream:
                    hashes[path.relative_to(directory).as_posix()] = hashlib.file_digest(stream, "sha256").hexdigest()
            else:
                raise InputError(f"버전 파일을 읽을 수 없음: {path}")
        return hashes

    def create(self, directory: Path, sources: tuple[Path, ...], change: str, by: str) -> Version:
        version_number(directory.name)
        required_text(change, "change")
        required_text(by, "by")
        names = [source.name.casefold() for source in sources]
        if not sources or len(set(names)) != len(names) or "notes.md" in names:
            raise InputError("--from: 파일 필요, 같은 파일명·생성되는 NOTES.md 중복 금지")
        if any(not source.is_file() for source in sources):
            raise InputError("--from: 존재하는 일반 파일 필요")
        target = self.policy.check(directory)
        if target.exists():
            raise OutputConflict(f"기존 버전 덮어쓰기 금지: {target}")
        stage = self.policy.check(directory.parent / f".staging-{uuid4().hex}")
        stage.mkdir()
        # 실패 staging은 진단용으로 보존한다. 공개된 버전과 기존 버전은 손대지 않는다.
        for source in sources:
            shutil.copy2(source, self.policy.check(stage / source.name))
        today = date.today().isoformat()
        notes = self.policy.check(stage / "NOTES.md")
        with notes.open("x", encoding="utf-8", newline="\n") as stream:
            stream.write(f"# {directory.name}\n\n날짜: {today}\n작성자: {by}\n변경: {change}\n\n"
                         "## 변경 내용\n\n## 확인한 것\n\n## 미결\n")
        record = Version(today, change, by, dict(self.hashes(stage)))
        self.policy.check(target)
        if target.exists():
            raise OutputConflict(f"버전 공개 충돌: {target}")
        try:
            os.rename(stage, target)
        except FileExistsError as exc:
            raise OutputConflict(f"버전 공개 충돌: {target}") from exc
        return record
