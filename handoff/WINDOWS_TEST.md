# Windows 테스트

`ce779b0`을 현재 Windows 저장소에서 FFmpeg 경로를 지정해 검증했다. 전체 로그: `handoff/logs/win_ce779b0_2026-11-07_161459.txt`.

별도 깨끗한 복제본에서 재현:

```powershell
cd C:\Users\uicus\Dev
git clone https://github.com/tacosangsang/plating-qc-workflows.git plating-qc-verify
cd plating-qc-verify
git fetch origin design/plating-qc-request
git checkout --detach ce779b0
$env:PATH = "D:\Plating\tools\ffmpeg\bin;" + $env:PATH
New-Item -ItemType Directory -Force handoff\logs | Out-Null
python -m unittest discover -s tests -v *> "handoff\logs\win_ce779b0_manual.txt"
echo "exit=$LASTEXITCODE" >> "handoff\logs\win_ce779b0_manual.txt"
```

실제 작업용 저장소를 detach하기 전에 미커밋 상태를 확인한다. 이 명령은 합성 입력을 테스트하며 실제 영상·편집기 재생 검증이 아니다.
