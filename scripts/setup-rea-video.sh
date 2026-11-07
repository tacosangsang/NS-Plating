#!/usr/bin/env bash
# rea-video CLI 설치 (로컬 macOS/Linux, Claude Code 클라우드 공용). 여러 번 실행해도 안전.
#   bash scripts/setup-rea-video.sh          # 설치 (이미 같은 버전이면 건너뜀)
#   REA_VIDEO_REF=<commit> bash scripts/...  # 다른 커밋으로 설치
# 스킬 문서(.claude/skills/rea-video)와 CLI 버전을 맞추기 위해 커밋을 고정한다.
# 업스트림 갱신 절차는 .claude/skills/rea-video/UPSTREAM.md 참고.
set -euo pipefail

REF="${REA_VIDEO_REF:-c9359c46f90c9824713081ea18fd207a45a0636a}"
REPO="https://github.com/JuneYaooo/rea-video"
HOME_DIR="${REA_VIDEO_INSTALL_DIR:-$HOME/.local/share/rea-video}"
VENV="$HOME_DIR/venv"
BIN_DIR="$HOME/.local/bin"
MARKER="$HOME_DIR/REF"

# ---- 이미 설치됨 ----
if [ -x "$VENV/bin/rea-video" ] && [ "$(cat "$MARKER" 2>/dev/null)" = "$REF" ]; then
  echo "rea-video ${REF:0:7} 이미 설치됨: $BIN_DIR/rea-video"
  exit 0
fi

# ---- ffmpeg ----
if ! command -v ffmpeg >/dev/null 2>&1 || ! command -v ffprobe >/dev/null 2>&1; then
  if [ "$(id -u)" = "0" ] && command -v apt-get >/dev/null 2>&1; then
    apt-get update -qq && apt-get install -y -qq ffmpeg
  else
    echo "ffmpeg/ffprobe 없음. macOS: brew install ffmpeg / Ubuntu: sudo apt install ffmpeg" >&2
    exit 1
  fi
fi

# ---- Python >= 3.10 (OCR 의존성 rapidocr가 3.13 미지원 -> 3.12 이하 우선) ----
py_ok() { "$1" -c 'import sys; sys.exit(sys.version_info < (3, 10))' 2>/dev/null; }
PY="${PYTHON_BIN:-}"
if [ -z "$PY" ]; then
  for c in python3.12 python3.11 python3.10 python3; do
    if command -v "$c" >/dev/null 2>&1 && py_ok "$c"; then PY="$c"; break; fi
  done
fi
if [ -z "$PY" ] || ! py_ok "$PY"; then
  echo "Python 3.10 이상 필요. macOS: brew install python@3.12 후 PYTHON_BIN=python3.12 bash $0" >&2
  exit 1
fi

EXTRAS="[ocr]"
if "$PY" -c 'import sys; sys.exit(sys.version_info < (3, 13))'; then
  EXTRAS=""
  echo "주의: $("$PY" --version) 에는 OCR(자막 글자 인식) 의존성이 없어 OCR 없이 설치. 필요하면 python3.12 설치 후 재실행" >&2
fi

# ---- 전용 venv 새로 설치 (시스템 Python 오염, PEP 668 문제 회피) ----
mkdir -p "$HOME_DIR" "$BIN_DIR"
rm -rf "$VENV"
"$PY" -m venv "$VENV"
"$VENV/bin/python" -m pip install -q --upgrade pip
"$VENV/bin/python" -m pip install -q "rea-video$EXTRAS @ git+$REPO@$REF"

# [ocr]이 끌고 오는 opencv-python이 opencv-python-headless와 cv2 디렉터리를 덮어씀 -> headless만 남김
if "$VENV/bin/python" -m pip show opencv-python >/dev/null 2>&1; then
  "$VENV/bin/python" -m pip uninstall -q -y opencv-python
  "$VENV/bin/python" -m pip install -q --force-reinstall --no-deps "opencv-python-headless>=4.8,<5"
fi

ln -sfn "$VENV/bin/rea-video" "$BIN_DIR/rea-video"
echo "$REF" > "$MARKER"

echo "rea-video ${REF:0:7} 설치 완료: $BIN_DIR/rea-video"
case ":$PATH:" in
  *":$BIN_DIR:"*) ;;
  *) echo "주의: $BIN_DIR 가 PATH에 없음. 셸 설정에 export PATH=\"\$HOME/.local/bin:\$PATH\" 추가" >&2 ;;
esac
