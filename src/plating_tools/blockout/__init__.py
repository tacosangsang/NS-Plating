"""정본 manifest 기반 블록아웃 규약 도구."""
import os
from argparse import Namespace
from dataclasses import replace
from uuid import uuid4

from ..config import Config
from ..errors import InputError, Unavailable
from .manifest import FileManifestStore
from .model import Manifest, asset_name, next_version
from .storage import FileVersionStore, asset_lock


def execute(args: Namespace, argv: list[str], cfg: Config):
    sources = tuple(path.resolve() for path in getattr(args, "sources", ()))
    policy = cfg.policy(sources)
    directory = policy.check(args.root / asset_name(args.asset))
    manifests = FileManifestStore(policy)
    versions = FileVersionStore(policy)
    if args.command == "init":
        if directory.exists():
            raise InputError(f"이미 존재하는 자산: {directory}")
        stage = policy.check(directory.parent / f".staging-{uuid4().hex}")
        stage.mkdir(parents=True)
        for name in ("versions", "renders", "archive"):
            policy.check(stage / name).mkdir()
        manifests.write(stage / "manifest.toml", Manifest(args.asset))
        if directory.exists():
            raise InputError(f"이미 존재하는 자산: {directory}")
        try:
            os.rename(stage, directory)
        except FileExistsError as exc:
            raise InputError(f"이미 존재하는 자산: {directory}") from exc
        return {"command": "blockout init", "exit_code": 0, "asset": args.asset, "output": str(directory)}
    manifest_path = directory / "manifest.toml"
    if not manifest_path.is_file():
        raise InputError(f"초기화된 자산 manifest 필요: {manifest_path}")
    with asset_lock(directory, policy):
        manifest = manifests.read(manifest_path)
        if manifest.asset != args.asset:
            raise InputError("자산 폴더와 manifest asset 불일치")
        if args.command == "new-version":
            number = next_version(tuple(set(manifest.versions) | {path.name for path in versions.list(directory)}))
            record = versions.create(directory / "versions" / number, sources, args.change, args.by)
            updated = replace(manifest, versions={**manifest.versions, number: record},
                              current=number if args.set_current else manifest.current)
            manifests.write(manifest_path, updated)
            return {"command": "blockout new-version", "exit_code": 0, "asset": args.asset,
                    "version": number, "current": updated.current, "output": str(directory / "versions" / number)}
    raise Unavailable("아직 구현되지 않은 blockout 명령")
