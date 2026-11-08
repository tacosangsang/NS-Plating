"""고정 스키마 TOML 저장 경계."""
import json
import os
import tomllib
from pathlib import Path
from typing import Protocol
from uuid import uuid4

from ..errors import InputError
from ..paths import WritePolicy
from .model import Manifest, Pin, Version


class ManifestStore(Protocol):
    def read(self, path: Path) -> Manifest: ...
    def write(self, path: Path, manifest: Manifest) -> None: ...


class FileManifestStore:
    def __init__(self, policy: WritePolicy):
        self.policy = policy

    def read(self, path: Path) -> Manifest:
        try:
            data = tomllib.loads(path.read_text(encoding="utf-8-sig"))
        except (tomllib.TOMLDecodeError, UnicodeError) as exc:
            raise InputError(f"manifest TOML 오류: {path}: {exc}") from exc
        if set(data) - {"asset", "current", "variants", "versions", "pins"}:
            raise InputError("manifest에 알 수 없는 필드")
        variants = data.get("variants", [])
        versions = data.get("versions", {})
        pins = data.get("pins", {})
        if not isinstance(variants, list) or not isinstance(versions, dict) or not isinstance(pins, dict):
            raise InputError("manifest: variants 목록, versions/pins 표 필요")
        try:
            return Manifest(data["asset"], data.get("current", ""), tuple(variants),
                            {key: Version(**value) for key, value in versions.items()},
                            {key: Pin(**value) for key, value in pins.items()})
        except (KeyError, TypeError) as exc:
            raise InputError(f"manifest 필드 누락 또는 형식 오류: {path}: {exc}") from exc

    def write(self, path: Path, manifest: Manifest) -> None:
        # 필드가 고정된 TOML만 직렬화한다. JSON 문자열 escape는 TOML basic string과 호환된다.
        quote = lambda text: json.dumps(text, ensure_ascii=False)
        lines = [f"asset = {quote(manifest.asset)}", f"current = {quote(manifest.current)}",
                 "variants = [" + ", ".join(quote(v) for v in manifest.variants) + "]"]
        for name, version in sorted(manifest.versions.items()):
            lines.extend(("", f"[versions.{name}]", f"date = {quote(version.date)}",
                          f"change = {quote(version.change)}", f"by = {quote(version.by)}", f"[versions.{name}.files]"))
            lines.extend(f"{quote(name)} = {quote(digest)}" for name, digest in sorted(version.files.items()))
        lines.extend(("", "[pins]"))
        for scene, pin in sorted(manifest.pins.items()):
            lines.append(f"{quote(scene)} = {{ version = {quote(pin.version)}, reason = {quote(pin.reason)}, "
                         f"approved_by = {quote(pin.approved_by)}, date = {quote(pin.date)} }}")
        target = self.policy.check(path)
        stage = self.policy.check(path.with_name(f".manifest-{uuid4().hex}.tmp"))
        try:
            with stage.open("x", encoding="utf-8", newline="\n") as stream:
                stream.write("\n".join(lines) + "\n")
                stream.flush()
                os.fsync(stream.fileno())
            self.policy.check(path)
            os.replace(stage, target)
        finally:
            stage.unlink(missing_ok=True)
