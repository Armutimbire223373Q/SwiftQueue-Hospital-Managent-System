<#
Exports all user tables from a SQLite database into individual CSV files.
Usage:
  # From project root
  powershell -ExecutionPolicy Bypass -File backend\scripts\export_sqlite_tables_to_csv.ps1 -DbPath backend\queue_management.db -OutDir ./sqlite_exports

Parameters:
  -DbPath: Path to the SQLite .db file (default: backend\queue_management.db)
  -OutDir: Directory to place CSV files (default: ./sqlite_exports)

Notes:
- Requires `sqlite3` CLI available on PATH. On Windows you can install it or use WSL.
- CSV files will include headers. Existing files in OutDir with same name will be overwritten after confirmation.
- Excludes sqlite internal tables (sqlite_sequence, sqlite_stat1, etc.).
#>

param(
    [string]$DbPath = "backend\queue_management.db",
    [string]$OutDir = "./sqlite_exports",
    [switch]$Force
)

# Resolve paths
$DbPath = Resolve-Path -Path $DbPath -ErrorAction Stop | Select-Object -ExpandProperty Path
$OutDirFull = Resolve-Path -LiteralPath (New-Item -ItemType Directory -Path $OutDir -Force | Select-Object -ExpandProperty FullName)

Write-Host "Using DB: $DbPath" -ForegroundColor Cyan
Write-Host "Exporting CSVs to: $OutDirFull" -ForegroundColor Cyan

# Ensure sqlite3 is available
if (-not (Get-Command sqlite3 -ErrorAction SilentlyContinue)) {
    Write-Warning "sqlite3 CLI was not found on PATH. Please install sqlite3 or run this script inside WSL/WSL2."
}

# Query tables from sqlite_master excluding internal tables
$tablesQuery = "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name;"

try {
    $tables = & sqlite3 `"$DbPath`" -csv -header `"$tablesQuery`" 2>$null | ConvertFrom-Csv -ErrorAction SilentlyContinue | ForEach-Object { $_.name }
} catch {
    # Fallback: call without -csv and parse
    $raw = & sqlite3 `"$DbPath`" `"$tablesQuery`" 2>$null
    $tables = $raw -split "\n" | Where-Object { $_ -ne '' }
}

if (-not $tables -or $tables.Count -eq 0) {
    Write-Warning "No user tables found in $DbPath"
    exit 0
}

foreach ($table in $tables) {
    $safeName = $table -replace '[^A-Za-z0-9_\-]', '_'
    $outFile = Join-Path $OutDirFull "$safeName.csv"

    if ((Test-Path $outFile) -and -not $Force) {
        $answer = Read-Host "File $outFile exists — overwrite? (y/N)"
        if ($answer -ne 'y' -and $answer -ne 'Y') {
            Write-Host "Skipping $table" -ForegroundColor Yellow
            continue
        }
    }

    Write-Host "Exporting table: $table -> $outFile" -ForegroundColor Green
    # Use sqlite3 with CSV mode and headers. Prefer calling sqlite3 directly and capture output.
    $select = "SELECT * FROM '$table';"
    try {
        # sqlite3 expects options first: sqlite3 -header -csv <db> "SQL"
        & sqlite3 -header -csv $DbPath $select | Out-File -FilePath $outFile -Encoding utf8
    } catch {
        Write-Warning "Failed to export $table with sqlite3 CLI: $_"
    }
}

# Build summary of exported files and row counts
$exported = @()
foreach ($csv in Get-ChildItem -Path $OutDirFull -Filter "*.csv" -File) {
    try {
        $lines = (Get-Content -Path $csv.FullName -ErrorAction Stop | Measure-Object -Line).Lines
    } catch {
        $lines = 0
    }
    $exported += [pscustomobject]@{ File = $csv.Name; Rows = [int]($lines - 1) }
}

if ($exported.Count -gt 0) {
    Write-Host "\nExport summary:" -ForegroundColor Cyan
    $totalRows = 0
    foreach ($e in $exported) {
        Write-Host " - $($e.File): $($e.Rows) rows"
        $totalRows += $e.Rows
    }
    Write-Host "\nExported $($exported.Count) CSV files with total $totalRows data rows to: $OutDirFull" -ForegroundColor Cyan
} else {
    Write-Host "No CSV files were exported to: $OutDirFull" -ForegroundColor Yellow
}

Write-Host "Export complete." -ForegroundColor Cyan
