# PowerShell에서 Python을 쉽게 사용하기 위한 스크립트
# 사용법: .\quick_python.ps1

# Python 경로 설정
$pythonPath = "Y:\0126\python_env.env\python.exe"
$pythonDir = "Y:\0126\python_env.env"
$scriptsDir = "$pythonDir\Scripts"

# PATH에 추가 (현재 세션만)
$env:PATH = "$pythonDir;$scriptsDir;" + $env:PATH

# 별칭 생성
Set-Alias python $pythonPath -Scope Global -Force
Set-Alias pip "$scriptsDir\pip.exe" -Scope Global -Force

Write-Host "========================================" -ForegroundColor Green
Write-Host "Python 환경 설정 완료" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Python 경로: $pythonPath" -ForegroundColor Cyan
Write-Host ""
Write-Host "사용 가능한 명령어:" -ForegroundColor Yellow
Write-Host "  python --version          - Python 버전 확인"
Write-Host "  python check_pandas.py   - 패키지 확인"
Write-Host "  pip list                  - 설치된 패키지 목록"
Write-Host "  python uploader.py ...    - BigQuery 업로더 실행"
Write-Host ""
Write-Host "테스트 실행:" -ForegroundColor Yellow
python --version
Write-Host ""
