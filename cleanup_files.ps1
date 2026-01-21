# NeoPrime Project File Cleanup Script (Safe Archiving Version)
# Moves files to archive/ folder instead of deleting
#
# Usage:
#   .\cleanup_files.ps1                    # Execute (archive/ folder)
#   .\cleanup_files.ps1 -DryRun            # Preview (no actual changes)
#   .\cleanup_files.ps1 -UseTimestamp      # Use timestamp subfolder

param(
    [switch]$DryRun = $false,
    [switch]$UseTimestamp = $false
)

$ErrorActionPreference = "SilentlyContinue"
$rootPath = "C:\Neoprime"

if ($DryRun) {
    Write-Host "========================================" -ForegroundColor Magenta
    Write-Host "  DRY-RUN MODE: No actual changes" -ForegroundColor Magenta
    Write-Host "========================================" -ForegroundColor Magenta
    Write-Host ""
}

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"

if ($UseTimestamp) {
    $archivePath = Join-Path $rootPath "archive\$timestamp"
    Write-Host "[Timestamp] Subfolder: archive\$timestamp" -ForegroundColor Cyan
} else {
    $archivePath = Join-Path $rootPath "archive"
}

$archiveReportsPath = Join-Path $archivePath "reports"
$archiveScriptsPath = Join-Path $archivePath "scripts"
$archiveDesignMatePath = Join-Path $archivePath "designmate"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "NeoPrime Project File Cleanup (Safe Archive)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
if ($UseTimestamp) {
    Write-Host "  Archive location: archive\$timestamp" -ForegroundColor Yellow
}
Write-Host ""

if (-not $DryRun) {
    New-Item -ItemType Directory -Path $archivePath -Force | Out-Null
    New-Item -ItemType Directory -Path $archiveReportsPath -Force | Out-Null
    New-Item -ItemType Directory -Path $archiveScriptsPath -Force | Out-Null
    New-Item -ItemType Directory -Path $archiveDesignMatePath -Force | Out-Null
}

# 1. Temp files (Word temp, nul) - Delete
$tempFiles = @(
    "~`$oPrime_IR_Deck.docx",
    "~`$oPrime_PRD_Final_v2.docx",
    "~`$signMate_PRD_v2.docx",
    "nul"
)

# 2. Reports - Move to archive/reports/
$reportsToArchive = @(
    "P0_수정_검증보고서_20260118.md",
    "P0플러스_개선완료_보고서_20260118.md",
    "THEORY_ENGINE_V3_구현완료_보고서.md",
    "THEORY_ENGINE_V3_심층구현_에이전트_프롬프트.md",
    "THEORY_ENGINE_구현_완료_보고서_20260117.md",
    "THEORY_ENGINE_실제테스트_분석보고서_20260118.md",
    "THEORY_ENGINE_실행_결과_검증_20260117.md",
    "THEORY_ENGINE_원안검증_미식별갭_디벨롭안_20260121.md",
    "THEORY_ENGINE_이행현황_수정보고서_20260118.md",
    "THEORY_ENGINE_즉시실행_개발플랜_v2.md",
    "THEORY_ENGINE_최종개선플랜_20260118.md",
    "THEORY_ENGINE_현재상태_종합보고서_20260118_최종.md",
    "작업_최종_총결산_20260117.md",
    "프로젝트_종합점검_최종보고서_20260118.md",
    "프로젝트_종합점검_최종보고서_v2_20260118.md",
    "프로젝트_현재_상태_보고서_20260118.md",
    "EXCEL_시트_구조_분석_20260117.md"
)

# 3. Old PRD versions - Move to archive/
$oldPRD = @(
    "NeoPrim_PRD.md",
    "NeoPrime_PRD.md"
)

# 4. Verification scripts - Move to archive/scripts/
$scriptsToArchive = @(
    "verify_cutoff_discrepancy.py",
    "verify_p0_fixes.py",
    "verify_p0plus_final.py"
)

# 5. DesignMate files - Move to archive/designmate/
$designMateFiles = @(
    "DesignMate_IR_Deck.docx",
    "DesignMate_IR_Deck.md",
    "DesignMate_PRD_v1.md",
    "DesignMate_PRD_v2.docx",
    "DesignMate_PRD_v2.pdf",
    "Cariv Export.pdf"
)

function Remove-FileIfExists {
    param([string]$filePath)
    if (Test-Path $filePath) {
        if ($DryRun) {
            Write-Host "[DRY-RUN DELETE] $filePath" -ForegroundColor Gray
        } else {
            Remove-Item $filePath -Force
            Write-Host "[DELETED] $filePath" -ForegroundColor Red
        }
        return $true
    }
    return $false
}

function Move-FileToArchive {
    param([string]$filePath, [string]$destFolder)
    if (Test-Path $filePath) {
        $fileName = Split-Path $filePath -Leaf
        $destPath = Join-Path $destFolder $fileName
        if ($DryRun) {
            Write-Host "[DRY-RUN MOVE] $fileName -> $destFolder" -ForegroundColor Gray
        } else {
            Move-Item $filePath $destPath -Force
            Write-Host "[ARCHIVED] $fileName -> $destFolder" -ForegroundColor Yellow
        }
        return $true
    }
    return $false
}

$processedCount = 0

Write-Host "`n[1/6] Deleting temp files..." -ForegroundColor Green
foreach ($file in $tempFiles) {
    if (Remove-FileIfExists (Join-Path $rootPath $file)) { $processedCount++ }
}

Write-Host "`n[2/6] Archiving reports to archive/reports/..." -ForegroundColor Green
foreach ($file in $reportsToArchive) {
    if (Move-FileToArchive (Join-Path $rootPath $file) $archiveReportsPath) { $processedCount++ }
}

Write-Host "`n[3/6] Archiving old PRD versions..." -ForegroundColor Green
foreach ($file in $oldPRD) {
    if (Move-FileToArchive (Join-Path $rootPath $file) $archivePath) { $processedCount++ }
}

Write-Host "`n[4/6] Archiving verification scripts to archive/scripts/..." -ForegroundColor Green
foreach ($file in $scriptsToArchive) {
    if (Move-FileToArchive (Join-Path $rootPath $file) $archiveScriptsPath) { $processedCount++ }
}

Write-Host "`n[5/6] Archiving DesignMate files to archive/designmate/..." -ForegroundColor Green
foreach ($file in $designMateFiles) {
    if (Move-FileToArchive (Join-Path $rootPath $file) $archiveDesignMatePath) { $processedCount++ }
}

Write-Host "`n[6/6] Deleting __pycache__ directories..." -ForegroundColor Green
$pycacheDirs = Get-ChildItem -Path $rootPath -Directory -Recurse -Filter "__pycache__" -ErrorAction SilentlyContinue
foreach ($dir in $pycacheDirs) {
    if ($DryRun) {
        Write-Host "[DRY-RUN DELETE] $($dir.FullName)" -ForegroundColor Gray
    } else {
        Remove-Item $dir.FullName -Recurse -Force
        Write-Host "[DELETED] $($dir.FullName)" -ForegroundColor Red
    }
    $processedCount++
}

Write-Host "`n========================================" -ForegroundColor Cyan
if ($DryRun) {
    Write-Host "DRY-RUN Complete! Target items: $processedCount" -ForegroundColor Magenta
    Write-Host "(No changes made. Run without -DryRun to execute)" -ForegroundColor Magenta
} else {
    Write-Host "Cleanup Complete! Processed items: $processedCount" -ForegroundColor Cyan
}
Write-Host "========================================" -ForegroundColor Cyan

Write-Host "`n[Archive Locations]" -ForegroundColor Magenta
Write-Host "  - archive/reports/     : Reports (recoverable)"
Write-Host "  - archive/scripts/     : Verification scripts (recoverable)"
Write-Host "  - archive/designmate/  : DesignMate files"

Write-Host "`n[Preserved Core Files]" -ForegroundColor Green
Write-Host "  - docs/                    : Documents (IA, specs)"
Write-Host "  - outputs/                 : Excel formula analysis (IMPORTANT!)"
Write-Host "  -   formula_catalog.csv    : 303,215 formulas"
Write-Host "  -   sheet_flow_graph.json  : Sheet dependency graph"
Write-Host "  - theory_engine/           : Engine source code"
Write-Host "  -   formula_mining/        : Formula extraction tools"
Write-Host "  - tests/                   : Test code"
Write-Host "  - tools/                   : Utilities (excel_oracle.py)"
Write-Host "  - NeoPrime_PRD_Final.md    : Final PRD"
Write-Host "  - 202511*.xlsx             : Original Excel file"

Write-Host "`n[IMPORTANT RECOMMENDATIONS]" -ForegroundColor Yellow
Write-Host "  [!] Backup original Excel file:"
Write-Host "      Copy-Item '202511*.xlsx' -Destination 'backup/'"
Write-Host "  [!] Check outputs/ folder before weight extraction:"
Write-Host "      - formula_catalog.csv (303,215 formulas)"
Write-Host "      - probe_report.txt (OFFSET 2,200 uses)"
