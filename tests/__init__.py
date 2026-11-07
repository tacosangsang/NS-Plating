"""저장소 unittest 테스트 패키지."""
import tempfile
from pathlib import Path

# 단독 unittest 명령에서도 모든 합성 임시 파일은 저장소 안에 둔다.
_TEMP_ROOT = Path(__file__).resolve().parents[1] / "out" / "pt-tests" / "tempfile"
_TEMP_ROOT.mkdir(parents=True, exist_ok=True)
tempfile.tempdir = str(_TEMP_ROOT)
