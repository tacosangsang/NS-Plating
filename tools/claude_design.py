#!/usr/bin/env python3
# 실행: python tools/claude_design.py request.md --output result.md
from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
MODEL = "claude-opus-5-5"
SYSTEM = "AI 설계자. 인터페이스/추상 클래스 우선, 의존 최소, 한국어, 이모지 금지, 지어내지 않고 미결은 질문 목록으로."
KST = timezone(timedelta(hours=9))
# Anthropic Opus 5.5 표준 요금, 2026-11-07 확인:
# https://platform.claude.com/docs/en/models/opus-5-5/overview
RATES = (Decimal("4"), Decimal("20"), Decimal("0.20"))


def estimate_cost(input_tokens: int, output_tokens: int, cache_read: int) -> Decimal:
    return sum((Decimal(count) * rate for count, rate in zip((input_tokens, output_tokens, cache_read), RATES)), Decimal(0)) / Decimal(1_000_000)


def budget_allowed(cumulative: Decimal, balance: Decimal) -> bool:
    return cumulative < 95 and balance > 5


def response_text(text: str, stop_reason: str | None) -> str:
    return text if stop_reason == "end_turn" else f"경고: 응답이 완료되지 않았습니다 (stop_reason={stop_reason}).\n{text}"


def read_ledger(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def perform_request(output: Path, ledger: Path, request: str, effort: str, cumulative: Decimal, call) -> int:
    partial = output.with_name(output.name + ".partial")
    entry = {"ts": datetime.now(KST).isoformat(), "request": request, "output": str(output),
             "model": MODEL, "effort": effort, "input_tokens": None, "output_tokens": None,
             "cache_read_input_tokens": None, "stop_reason": None, "status": "error",
             "est_cost_usd": None, "est_cumulative_usd": str(cumulative)}
    result = 1
    try:
        with partial.open("x", encoding="utf-8") as file:
            message = call(file)
        usage = message.usage
        cost = estimate_cost(usage.input_tokens, usage.output_tokens, usage.cache_read_input_tokens or 0)
        entry.update(input_tokens=usage.input_tokens, output_tokens=usage.output_tokens,
                     cache_read_input_tokens=usage.cache_read_input_tokens or 0, stop_reason=message.stop_reason,
                     status="success" if message.stop_reason == "end_turn" else "incomplete",
                     est_cost_usd=str(cost), est_cumulative_usd=str(cumulative + cost))
        content = partial.read_text(encoding="utf-8")
        partial.write_text(response_text(content, message.stop_reason), encoding="utf-8")
        # Windows와 POSIX 양쪽에서 기존 결과를 덮어쓰지 않는다.
        os.link(partial, output)
        partial.unlink()
        result = 0 if message.stop_reason == "end_turn" else 1
    except Exception as error:
        entry["status"] = "error"
        entry["error_type"] = type(error).__name__
        entry["output"] = str(partial)
        print(f"호출 실패: {type(error).__name__}. 비용을 Console에서 확인하세요.", file=sys.stderr)
    finally:
        with ledger.open("a", encoding="utf-8") as file:
            file.write(json.dumps(entry, ensure_ascii=False) + "\n")
        with ledger.with_suffix(".md").open("a", encoding="utf-8") as file:
            file.write(f"\n- {entry['ts']}: {entry['request']}, 상태 {entry['status']}, 종료 사유 {entry['stop_reason']}, 입력 {entry['input_tokens']}, 출력 {entry['output_tokens']}, 캐시 읽기 {entry['cache_read_input_tokens']}, 예상 비용 ${entry['est_cost_usd']}, 누적 ${entry['est_cumulative_usd']}, 결과 `{entry['output']}`.\n")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Claude 설계 요청과 사용량 기록")
    parser.add_argument("request", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--effort", choices=("high", "xhigh", "max"), default="high")
    parser.add_argument("--max-tokens", type=int, default=64000)
    parser.add_argument("--balance", help="오늘 확인한 Console 프로모션 잔액(USD)")
    args = parser.parse_args()
    if not 1 <= args.max_tokens <= 128000:
        parser.error("max-tokens는 1~128000이어야 합니다")
    try:
        prompt = args.request.read_text(encoding="utf-8")
    except OSError as error:
        parser.error(str(error))
    if args.output.exists() or args.output.with_name(args.output.name + ".partial").exists():
        parser.error("결과 파일 또는 partial 파일이 이미 존재합니다")
    ledger = ROOT / "handoff" / "claude-usage.jsonl"
    balance_file = ROOT / "handoff" / "claude-balance.json"
    entries = read_ledger(ledger)
    if any(item["status"] == "error" for item in entries):
        parser.error("비용 미확인 오류 기록이 있습니다. Console과 대조해 장부를 먼저 정정하세요")
    cumulative = sum((Decimal(item["est_cost_usd"]) for item in entries), Decimal(0))
    if args.balance is not None:
        try:
            balance = Decimal(args.balance)
            if not balance.is_finite() or balance < 0:
                parser.error("잔액은 0 이상의 USD 숫자여야 합니다")
        except InvalidOperation:
            parser.error("잔액은 USD 숫자여야 합니다")
        balance_file.write_text(json.dumps({"date": datetime.now(KST).date().isoformat(),
                                           "balance": str(balance), "cumulative": str(cumulative)}), encoding="utf-8")
    if not balance_file.exists():
        parser.error("오늘 Console 잔액을 확인하고 --balance로 입력하세요")
    snapshot = json.loads(balance_file.read_text(encoding="utf-8"))
    if snapshot["date"] != datetime.now(KST).date().isoformat():
        parser.error("오늘 Console 잔액을 확인하고 --balance로 입력하세요")
    balance = Decimal(snapshot["balance"]) - (cumulative - Decimal(snapshot["cumulative"]))
    if not budget_allowed(cumulative, balance):
        parser.error("누적 예상 비용이 $95 이상이거나 잔액이 $5 이하입니다")
    if not os.environ.get("ANTHROPIC_API_KEY"):
        parser.error("ANTHROPIC_API_KEY 환경 변수가 없습니다")
    from anthropic import Anthropic

    def call(file):
        with Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"], base_url="https://api.anthropic.com", max_retries=0) as client:
            with client.messages.stream(model=MODEL, max_tokens=args.max_tokens, system=SYSTEM,
                                        thinking={"type": "adaptive"}, output_config={"effort": args.effort},
                                        messages=[{"role": "user", "content": prompt}]) as stream:
                for chunk in stream.text_stream:
                    file.write(chunk)
                    file.flush()
                return stream.get_final_message()

    return perform_request(args.output, ledger, str(args.request), args.effort, cumulative, call)


if __name__ == "__main__":
    raise SystemExit(main())
