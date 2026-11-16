# Claude 설계 호출

Python 3.12 이상, 해당 Python에서 가져올 수 있는 Anthropic SDK와 `ANTHROPIC_API_KEY` 환경 변수가 필요하다. 패키지는 자동 설치하지 않는다. SDK 확인: `python -c "import anthropic; print(anthropic.__version__)"`.

```powershell
python tools/claude_design.py design/requests/plating-qc.md --output design/plating-qc-draft.md --balance 99.99
```

`--balance`는 당일 Console에서 확인한 프로모션 잔액이며 당일 첫 실행 시 또는 잔액 보정 시 입력한다. 같은 날 이후 생략할 수 있다. 예시 값은 실행 시 실제 잔액으로 바꾼다. `--effort high|xhigh|max`와 `--max-tokens`를 선택할 수 있다.

예상 비용은 이 도구의 장부와 사용자 입력을 기준으로 하며 실제 Console 청구·다른 도구의 사용량을 자동 조회하지 않는다. 오류로 비용을 알 수 없는 경우 다음 호출이 차단된다. Console에서 실제 사용량을 확인하고 `handoff/claude-usage.jsonl`의 오류 항목을 근거와 함께 정정한 후 사용한다. 동시 호출은 지원하지 않는다.
