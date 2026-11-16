# assets

`current.toml`은 PLATING 자산의 현재본 목록이다. 스레드는 자산을 이름으로 검색하지 않고 여기서 key로 꺼낸다.

- 소스는 드라이브에서만 가져온다(`drive_id`). 클라우드 사본·PC 로컬·백업 저장소는 소스가 아니다.
- confirmed는 사용자가 확정한 문장(`quote`)이 있을 때만 쓴다. 문장이 없으면 temp다.
- 같은 파일 판정은 이름이 아니라 `md5`로 한다.
- 폐기된 자료는 `[[retired]]`로 옮겨 두면 검사가 막는다.

## 검사

```sh
python3 assets/check_assets.py                       # 목록 형식 + 문서 속 폐기 파일 이름
python3 assets/check_assets.py --prompt-json X.json  # 프롬프트 입력 그림 대조
python3 -m unittest discover -s assets -p "test_*.py"
```

프롬프트 JSON의 입력 항목에는 `asset`(목록 key)을 적는다. 목록에 없는 그림, 폐기본, temp, `media_id`/`md5`가 목록과 다른 그림은 실패한다.
새 규칙은 `check_assets.py`의 `Rule`을 구현해 `RULES`에 넣는다.
