# NEO GOD 통합 환경 설정 (PowerShell 전용)
# 파일명: quick_all.ps1
# 버전: 2.1 (인코딩 및 오류 처리 개선)

# [0] 출력 인코딩 설정 (한글 표시를 위해)
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
$PSDefaultParameterValues['*:Encoding'] = 'utf8'

# [1] 기본 경로 설정
$BaseDir = "Y:\0126"
$WorkDir = "$BaseDir\0126"
$PythonDir = "$BaseDir\python_env.env"
$PythonScripts = "$PythonDir\Scripts"
$NodeDir = "$BaseDir\nodejs"
$GcloudBin = "$BaseDir\google-cloud-sdk\google-cloud-sdk\bin"
$GitBin = "$BaseDir\Git\cmd"
$ClaudeBin = "$BaseDir\0126\node_modules\.bin"
$CursorHome = "$BaseDir\Cursor"

# [2] PATH 환경 변수 최상단에 추가 (중복 방지)
$pathsToAdd = @(
    $PythonDir,
    $PythonScripts,
    $NodeDir,
    $GitBin,
    $GcloudBin,
    $ClaudeBin,
    "$BaseDir\0127\node_modules\.bin",  # 0127 워크스페이스 경로도 추가
    $CursorHome
)
$existingPaths = $env:PATH -split ';'
$newPaths = $pathsToAdd | Where-Object { $_ -notin $existingPaths }
if ($newPaths.Count -gt 0) {
    $env:PATH = ($newPaths -join ';') + ';' + $env:PATH
}

# [3] Python 환경 변수 설정 (중복 방지)
$env:PYTHONIOENCODING = "utf-8"
$existingPythonPaths = if ($env:PYTHONPATH) { $env:PYTHONPATH -split ';' } else { @() }
if ($WorkDir -notin $existingPythonPaths) {
    $env:PYTHONPATH = "$WorkDir;$env:PYTHONPATH"
}
# 0127 경로도 추가 (듀플리케이트 워크스페이스 지원)
$otherWorkDir = "$BaseDir\0127"
if ($otherWorkDir -notin $existingPythonPaths -and $otherWorkDir -ne $WorkDir) {
    $env:PYTHONPATH = "$otherWorkDir;$env:PYTHONPATH"
}

# [4] 작업 디렉토리 이동
Set-Location $WorkDir

# [5] 별칭 설정
Set-Alias python "$PythonDir\python.exe" -Scope Global -Force
Set-Alias pip "$PythonScripts\pip.exe" -Scope Global -Force
Set-Alias python3 "$PythonDir\python.exe" -Scope Global -Force

# [6] 시스템 가동 확인 및 표시
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "[SYSTEM] NEO GOD AI INTEGRATED ENV (PS)" -ForegroundColor Cyan
Write-Host "[VERSION] 2.1 - 인코딩 및 오류 처리 개선" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "[BASE DIRECTORY] $BaseDir" -ForegroundColor Gray
Write-Host "[WORK DIRECTORY] $WorkDir" -ForegroundColor Gray
Write-Host ""

# [7] Python 환경 확인
Write-Host "[1] Python 환경 확인:" -ForegroundColor Yellow
$pythonExe = "$PythonDir\python.exe"
$pythonCheck = & $pythonExe --version 2>&1
$pythonSuccess = ($LASTEXITCODE -eq 0) -or $?
if ($pythonSuccess) {
    Write-Host "  OK $pythonCheck" -ForegroundColor Green
    Write-Host "  경로: $pythonExe" -ForegroundColor Gray
}
if (-not $pythonSuccess) {
    Write-Host "  FAIL Python을 찾을 수 없습니다." -ForegroundColor Red
}

Write-Host ""
Write-Host "[2] 필수 Python 패키지 확인:" -ForegroundColor Yellow
$pandasCmd = "import pandas; print('pandas ' + pandas.__version__)"
try {
    $pandasOutput = & $pythonExe -c $pandasCmd 2>&1
    $pandasError = $pandasOutput | Where-Object { $_ -is [System.Management.Automation.ErrorRecord] }
    $pandasText = $pandasOutput | Where-Object { $_ -isnot [System.Management.Automation.ErrorRecord] } | Out-String
    $pandasSuccess = ($null -eq $pandasError) -and ($pandasText -match "pandas\s+\d+\.\d+")
    if ($pandasSuccess) {
        Write-Host "  OK $($pandasText.Trim())" -ForegroundColor Green
    } else {
        Write-Host "  WARN pandas 설치 필요: pip install -r requirements.txt" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  WARN pandas 설치 필요: pip install -r requirements.txt" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "[3] Claude Code 확인:" -ForegroundColor Yellow
$claudePath = "$ClaudeBin\claude.cmd"
$claudeExists = Test-Path $claudePath
if ($claudeExists) {
    Write-Host "  OK Claude Code 설치됨" -ForegroundColor Green
    Write-Host "  경로: $claudePath" -ForegroundColor Gray
    Write-Host "  사용법: claude.cmd 또는 claude" -ForegroundColor Gray
}
if (-not $claudeExists) {
    Write-Host "  WARN Claude Code를 찾을 수 없습니다." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "[4] Google Cloud SDK 확인:" -ForegroundColor Yellow
$gcloudPath = "$GcloudBin\gcloud.cmd"
$gcloudExists = Test-Path $gcloudPath
if ($gcloudExists) {
    try {
        $gcloudCheck = & $gcloudPath --version 2>&1 | Where-Object { $_ -notmatch "오류|Error|용어가" -and $_ -match "\d+\.\d+" } | Select-Object -First 1
        if ($gcloudCheck -and ($gcloudCheck -notmatch "오류|Error|용어가")) {
            Write-Host "  OK Google Cloud SDK 설치됨" -ForegroundColor Green
            Write-Host "  경로: $gcloudPath" -ForegroundColor Gray
        } else {
            Write-Host "  OK Google Cloud SDK 설치됨 (버전 확인 실패)" -ForegroundColor Green
            Write-Host "  경로: $gcloudPath" -ForegroundColor Gray
        }
    } catch {
        Write-Host "  OK Google Cloud SDK 설치됨" -ForegroundColor Green
        Write-Host "  경로: $gcloudPath" -ForegroundColor Gray
    }
} else {
    Write-Host "  WARN GCloud SDK를 찾을 수 없습니다." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "[5] Git 확인:" -ForegroundColor Yellow
$gitCheck = & git --version 2>&1
$gitSuccess = ($LASTEXITCODE -eq 0) -or $?
if ($gitSuccess) {
    Write-Host "  OK $gitCheck" -ForegroundColor Green
}
if (-not $gitSuccess) {
    Write-Host "  WARN Git을 찾을 수 없습니다." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "[6] Node.js 확인:" -ForegroundColor Yellow
$nodeCheck = & node --version 2>&1
$nodeSuccess = ($LASTEXITCODE -eq 0) -or $?
if ($nodeSuccess) {
    Write-Host "  OK Node.js $nodeCheck" -ForegroundColor Green
}
if (-not $nodeSuccess) {
    Write-Host "  WARN Node.js를 찾을 수 없습니다." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "[7] 서비스 계정 키 파일 확인:" -ForegroundColor Yellow
$keyFile = "$WorkDir\neoprime-admin-key.json"
$keyExists = Test-Path $keyFile
if ($keyExists) {
    $fileSize = (Get-Item $keyFile).Length
    if ($fileSize -gt 0) {
        $sizeInfo = "$fileSize bytes"
        Write-Host "  OK neoprime-admin-key.json 존재 ($sizeInfo)" -ForegroundColor Green
    }
    if ($fileSize -eq 0) {
        Write-Host "  WARN neoprime-admin-key.json 파일이 비어있습니다." -ForegroundColor Yellow
    }
}
if (-not $keyExists) {
    Write-Host "  WARN neoprime-admin-key.json 파일을 찾을 수 없습니다." -ForegroundColor Yellow
}

# [8] 사용 가능한 명령어 안내
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "[사용 가능한 명령어]" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Python 관련:" -ForegroundColor Yellow
Write-Host "  python --version              - Python 버전 확인"
Write-Host "  python check_pandas.py       - 패키지 설치 확인"
Write-Host "  python test_uploader.py       - 전체 환경 테스트"
Write-Host "  python uploader.py ...        - BigQuery 업로더 실행"
Write-Host "  pip list                      - 설치된 패키지 목록"
Write-Host ""
Write-Host "기타 도구:" -ForegroundColor Yellow
Write-Host "  claude.cmd                    - Claude Code CLI 실행"
Write-Host "  gcloud                        - Google Cloud SDK"
Write-Host "  git                           - Git 버전 관리"
Write-Host "  node                          - Node.js 실행"
Write-Host ""
Write-Host "빠른 테스트:" -ForegroundColor Yellow
Write-Host "  python check_pandas.py       - 패키지 확인"
Write-Host "  python test_uploader.py       - 환경 테스트"
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "OK 환경 설정 완료! 이제 모든 명령어를 사용할 수 있습니다." -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
