"""기존 결과를 덮어쓰지 않는 파일 게시."""

import os
from pathlib import Path

from .errors import QCError


def publish(source: Path, target: Path) -> None:
    try:
        os.link(source, target)
        return
    except FileExistsError as exc:
        raise QCError(3, f"출력 파일이 이미 있습니다: {target}") from exc
    except OSError as link_error:
        if os.name != "nt":
            raise QCError(5, f"덮어쓰기 방지 저장 실패: {link_error}") from link_error
    try:
        os.rename(source, target)
    except FileExistsError as exc:
        raise QCError(3, f"출력 파일이 이미 있습니다: {target}") from exc
    except OSError as exc:
        raise QCError(5, f"덮어쓰기 방지 저장 실패: {exc}") from exc
