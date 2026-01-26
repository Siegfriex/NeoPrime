# ============================================================
# BigQuery 권한 설정 스크립트 (PowerShell)
# NEO GOD Ultra Framework v2.0
# ============================================================

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "BigQuery 권한 설정" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# 프로젝트 ID
$PROJECT_ID = "neoprime0305"
$SERVICE_ACCOUNT = "sa-bq-loader@neoprime0305.iam.gserviceaccount.com"

Write-Host "[INFO] 프로젝트: $PROJECT_ID" -ForegroundColor Yellow
Write-Host "[INFO] 서비스 계정: $SERVICE_ACCOUNT" -ForegroundColor Yellow
Write-Host ""

# 1. 현재 권한 확인
Write-Host "[1단계] 현재 권한 확인 중..." -ForegroundColor Green
try {
    $current_policy = gcloud projects get-iam-policy $PROJECT_ID `
        --format="table(bindings.role)" `
        --filter="bindings.members:serviceAccount:$SERVICE_ACCOUNT" 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host $current_policy
        Write-Host ""
        Write-Host "[INFO] 현재 권한 확인 완료" -ForegroundColor Green
    } else {
        Write-Host "[WARNING] 권한 확인 실패 (서비스 계정에 권한이 없을 수 있음)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "[ERROR] 권한 확인 중 오류: $_" -ForegroundColor Red
}

Write-Host ""

# 2. BigQuery Job User 역할 추가
Write-Host "[2단계] BigQuery Job User 역할 추가 중..." -ForegroundColor Green
try {
    gcloud projects add-iam-policy-binding $PROJECT_ID `
        --member="serviceAccount:$SERVICE_ACCOUNT" `
        --role="roles/bigquery.jobUser"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[SUCCESS] BigQuery Job User 역할 추가 완료" -ForegroundColor Green
    } else {
        Write-Host "[ERROR] 역할 추가 실패" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "[ERROR] 역할 추가 중 오류: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""

# 3. BigQuery Data Editor 역할 확인/추가 (필요시)
Write-Host "[3단계] BigQuery Data Editor 역할 확인 중..." -ForegroundColor Green
try {
    $has_data_editor = gcloud projects get-iam-policy $PROJECT_ID `
        --format="value(bindings.role)" `
        --filter="bindings.members:serviceAccount:$SERVICE_ACCOUNT AND bindings.role:roles/bigquery.dataEditor" 2>&1
    
    if ($LASTEXITCODE -eq 0 -and $has_data_editor) {
        Write-Host "[INFO] BigQuery Data Editor 역할 이미 있음" -ForegroundColor Green
    } else {
        Write-Host "[INFO] BigQuery Data Editor 역할 추가 중..." -ForegroundColor Yellow
        gcloud projects add-iam-policy-binding $PROJECT_ID `
            --member="serviceAccount:$SERVICE_ACCOUNT" `
            --role="roles/bigquery.dataEditor"
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "[SUCCESS] BigQuery Data Editor 역할 추가 완료" -ForegroundColor Green
        } else {
            Write-Host "[WARNING] Data Editor 역할 추가 실패 (선택사항)" -ForegroundColor Yellow
        }
    }
} catch {
    Write-Host "[WARNING] Data Editor 역할 확인 중 오류 (선택사항): $_" -ForegroundColor Yellow
}

Write-Host ""

# 4. 최종 권한 확인
Write-Host "[4단계] 최종 권한 확인 중..." -ForegroundColor Green
try {
    $final_policy = gcloud projects get-iam-policy $PROJECT_ID `
        --format="table(bindings.role,bindings.members)" `
        --filter="bindings.members:serviceAccount:$SERVICE_ACCOUNT"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host $final_policy
        Write-Host ""
        Write-Host "[SUCCESS] 권한 설정 완료!" -ForegroundColor Green
    } else {
        Write-Host "[ERROR] 최종 권한 확인 실패" -ForegroundColor Red
    }
} catch {
    Write-Host "[ERROR] 최종 권한 확인 중 오류: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "다음 단계:" -ForegroundColor Cyan
Write-Host "  python test_bigquery_actual_load.py" -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Cyan
