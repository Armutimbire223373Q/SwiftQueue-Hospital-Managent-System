<#
PowerShell script to restore a SQLite .db backup into backend/queue_management.db
Usage:
  # Provide backup path
  .\restore_db.ps1 -BackupPath "C:\path\to\queue_management.db.bak"

  # Or run interactively and paste the path when prompted
  .\restore_db.ps1

The script will:
- Verify the backup file exists
- Create a timestamped backup of the current `backend/queue_management.db` (if present)
- Copy the provided backup into `backend/queue_management.db`
#>

param(
    [string]$BackupPath = ""
)

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
# The target DB is one level up from scripts (backend/queue_management.db)
$targetDb = Join-Path $scriptDir "..\queue_management.db" | Resolve-Path -Relative -ErrorAction SilentlyContinue
if (-not $targetDb) {
    # Fallback to building the path without Resolve-Path
    $targetDb = Join-Path $scriptDir "..\queue_management.db"
}

if ([string]::IsNullOrWhiteSpace($BackupPath)) {
    Write-Host "Enter path to the .db or .db.bak file to restore:" -ForegroundColor Yellow
    $BackupPath = Read-Host
}

if (-not (Test-Path $BackupPath)) {
    Write-Error "Backup file not found: $BackupPath"
    exit 1
}

$targetDbFull = (Resolve-Path (Join-Path $scriptDir "..\queue_management.db")).Path

# Create a safe backup of the current DB if it exists
if (Test-Path $targetDbFull) {
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $backupCopy = "$targetDbFull.bak.$timestamp"
    Write-Host "Backing up current DB to: $backupCopy" -ForegroundColor Cyan
    Copy-Item -Path $targetDbFull -Destination $backupCopy -Force
}

Write-Host "Restoring $BackupPath -> $targetDbFull" -ForegroundColor Green
Copy-Item -Path $BackupPath -Destination $targetDbFull -Force

Write-Host "Restore complete. Consider running migrations or checks if you switched DB backends." -ForegroundColor Green

return 0
