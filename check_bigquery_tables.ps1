# BigQuery 테이블 존재 확인 스크립트

$projectId = "neoprime0305"
$datasetId = "ds_neoprime_entrance"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "BigQuery 테이블 존재 확인" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "프로젝트: $projectId" -ForegroundColor Yellow
Write-Host "데이터셋: $datasetId" -ForegroundColor Yellow
Write-Host ""

$tables = @(
    "tb_raw_2026_SUBJECT3",
    "tb_raw_2026_RAWSCORE",
    "tb_raw_2026_이과계열분석결과",
    "tb_raw_2026_문과계열분석결과",
    "tb_raw_2026_SUBJECT1",
    "tb_raw_2026_INDEX"
)

Write-Host "테이블 확인 중..." -ForegroundColor Green
Write-Host ""

foreach ($table in $tables) {
    $fullTableName = "$projectId.$datasetId.$table"
    Write-Host "확인 중: $table" -NoNewline
    
    try {
        $query = "SELECT COUNT(*) as cnt FROM `$fullTableName`"
        $result = bq query --use_legacy_sql=false --format=json "$query" 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            $rowCount = ($result | ConvertFrom-Json)[0].cnt
            Write-Host " ✅ 존재 (행 수: $rowCount)" -ForegroundColor Green
        } else {
            Write-Host " ❌ 존재하지 않음" -ForegroundColor Red
        }
    } catch {
        Write-Host " ❌ 확인 실패: $_" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "Staging 테이블 확인 중..." -ForegroundColor Yellow
Write-Host ""

$stagingTables = @(
    "tb_raw_2026_이과계열분석결과_staging",
    "tb_raw_2026_문과계열분석결과_staging",
    "tb_raw_2026_SUBJECT1_staging",
    "tb_raw_2026_INDEX_staging"
)

foreach ($table in $stagingTables) {
    $fullTableName = "$projectId.$datasetId.$table"
    Write-Host "확인 중: $table" -NoNewline
    
    try {
        $query = "SELECT COUNT(*) as cnt FROM `$fullTableName`"
        $result = bq query --use_legacy_sql=false --format=json "$query" 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            $rowCount = ($result | ConvertFrom-Json)[0].cnt
            Write-Host " ✅ 존재 (행 수: $rowCount)" -ForegroundColor Yellow
        } else {
            Write-Host " ❌ 존재하지 않음 (이미 삭제됨)" -ForegroundColor Gray
        }
    } catch {
        Write-Host " ❌ 확인 실패" -ForegroundColor Gray
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "확인 완료" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
