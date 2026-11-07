#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["anthropic>=0.75,<1"]
# ///
# Install uv: https://docs.astral.sh/uv/getting-started/installation/
# Run: uv run tools/claude_design.py request.md --balance-before 100 --output result.md

from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
MODEL = "claude-opus-5-5"
SYSTEM = "AI 설계자. 인터페이스/추상 클래스 우선, 의존 최소, 한국어, 이모지 금지, 지어내지 않고 미결은 질문 목록으로."


def main() -> int:
    parser = argparse.ArgumentParser(description="Claude 설계 요청과 사용량 기록")
    parser.add_argument("request", type=Path)
    parser.add_argument("--balance-before", required=True, help="호출 직전 Console 프로모션 잔액 (USD)")
    parser.add_argument("--output", type=Path, required=True, help="새 결과 파일 경로")
    parser.add_argument("--max-tokens", type=int, default=16000)
    args = parser.parse_args()
    try:
        balance = Decimal(args.balance_before)
        if not balance.is_finite() or balance <= 5:
            parser.error("Console 프로모션 잔액이 5 USD 이하면 호출할 수 없습니다")
    except InvalidOperation:
        parser.error("잔액은 USD 숫자여야 합니다")
    if args.max_tokens < 1 or args.max_tokens > 16000:
        parser.error("max-tokens는 1~16000이어야 합니다")
    try:
        prompt = args.request.read_text(encoding="utf-8")
    except OSError as error:
        parser.error(str(error))
    if args.output.exists():
        parser.error(f"결과 파일이 이미 존재합니다: {args.output}")
    if not os.environ.get("ANTHROPIC_API_KEY"):
        parser.error("ANTHROPIC_API_KEY 환경 변수가 없습니다")

    from anthropic import Anthropic

    with args.output.open("x", encoding="utf-8") as output:
        timestamp = datetime.now(timezone(timedelta(hours=9))).strftime("%Y-%m-%d %H:%M:%S %z")
        with (ROOT / "handoff" / "claude-usage.md").open("a", encoding="utf-8") as log:
            log.write(f"\n호출 전 {timestamp}: {args.request}, Console 잔액 ${balance}, 누적 비용 미확인.\n\n")
        with Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"], base_url="https://api.anthropic.com", max_retries=0) as client:
            with client.messages.stream(
                model=MODEL, max_tokens=args.max_tokens, system=SYSTEM,
                messages=[{"role": "user", "content": prompt}],
            ) as stream:
                for chunk in stream.text_stream:
                    output.write(chunk)
                    output.flush()
                message = stream.get_final_message()

    timestamp = datetime.now(timezone(timedelta(hours=9))).strftime("%Y-%m-%d %H:%M:%S %z")
    with (ROOT / "handoff" / "claude-usage.md").open("a", encoding="utf-8") as log:
        log.write(f"호출 후 {timestamp}: 모델 {MODEL}, 입력 {message.usage.input_tokens} 토큰, 출력 {message.usage.output_tokens} 토큰, 결과 `{args.output}`, Console 잔액 미확인, 누적 비용 미확인.\n")
    print(f"입력 {message.usage.input_tokens} 토큰, 출력 {message.usage.output_tokens} 토큰. 호출 후 Console 잔액과 누적 비용을 기록하세요.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
