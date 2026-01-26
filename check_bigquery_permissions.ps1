# ============================================================
# BigQuery 권한 확인 스크립트 (PowerShell)
# NEO GOD Ultra Framework v2.0
# ============================================================

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "BigQuery 권한 확인" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# 프로젝트 ID
$PROJECT_ID = "neoprime0305"
$SERVICE_ACCOUNT = "sa-bq-loader@neoprime0305.iam.gserviceaccount.com"

Write-Host "[INFO] 프로젝트: $PROJECT_ID" -ForegroundColor Yellow
Write-Host "[INFO] 서비스 계정: $SERVICE_ACCOUNT" -ForegroundColor Yellow
Write-Host ""

# 현재 권한 확인
Write-Host "[1단계] 현재 권한 확인 중..." -ForegroundColor Green
try {
    $result = gcloud projects get-iam-policy $PROJECT_ID `
        --format="table(bindings.role,bindings.members)" `
        --filter="bindings.members:serviceAccount:$SERVICE_ACCOUNT" 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host $result
        Write-Host ""
        
        # 필요한 역할 확인
        $hasJobUser = $result -match "roles/bigquery.jobUser"
        $hasDataEditor = $result -match "roles/bigquery.dataEditor"
        
        Write-Host "[권한 상태]" -ForegroundColor Cyan
        if ($hasJobUser) {
            Write-Host "  ✅ bigquery.jobUser: 있음" -ForegroundColor Green
        } else {
            Write-Host "  ❌ bigquery.jobUser: 없음" -ForegroundColor Red
        }
        
        if ($hasDataEditor) {
            Write-Host "  ✅ bigquery.dataEditor: 있음" -ForegroundColor Green
        } else {
            Write-Host "  ⚠️  bigquery.dataEditor: 없음 (선택사항)" -ForegroundColor Yellow
        }
        
        Write-Host ""
        
        if ($hasJobUser) {
            Write-Host "[SUCCESS] 필요한 권한이 설정되어 있습니다!" -ForegroundColor Green
        } else {
            Write-Host "[WARNING] bigquery.jobUser 권한이 없습니다." -ForegroundColor Yellow
            Write-Host "  다음 명령어로 권한을 추가하세요:" -ForegroundColor Yellow
            Write-Host "  .\setup_bigquery_permissions.ps1" -ForegroundColor Cyan
        }
    } else {
        Write-Host "[ERROR] 권한 확인 실패" -ForegroundColor Red
        Write-Host $result
    }
} catch {
    Write-Host "[ERROR] 권한 확인 중 오류: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
