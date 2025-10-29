<#
Imports CSV files from a directory into a PostgreSQL database using psql's \copy.

Usage:
    # Simple (uses defaults matching docker-compose.postgres.yml)
    powershell -ExecutionPolicy Bypass -File backend\scripts\import_csvs_to_postgres.ps1 -CsvDir ./sqlite_exports

    # Provide connection details
    powershell -ExecutionPolicy Bypass -File backend\scripts\import_csvs_to_postgres.ps1 -CsvDir ./sqlite_exports -PgHost localhost -Port 5432 -User sq_user -Password sq_password -Database swiftqueue

Parameters:
    -CsvDir : Directory containing CSV files (default: ./sqlite_exports)
    -PgHost : Postgres host (default: localhost)
    -Port   : Postgres port (default: 5432)
    -User   : Postgres username (default: sq_user)
    -Password : Postgres password (default: sq_password)
    -Database : Postgres database name (default: swiftqueue)
    -Force  : Overwrite/skip prompts
    -NoValidate : Skip post-import row-count validation

Notes:
- Ensure `psql` is available on PATH (part of PostgreSQL client tools). On Windows, install PostgreSQL client or use WSL/Docker.
- This script does not create tables; run Alembic migrations first so tables exist and types/constraints match the CSV data.
- Test on a non-production DB first.
#>
param(
    [string]$CsvDir = "./sqlite_exports",
    [string]$PgHost = "localhost",
    [int]$Port = 5432,
    [string]$User = "sq_user",
    [string]$Password = "sq_password",
    [string]$Database = "swiftqueue",
    [switch]$Force,
    [switch]$NoValidate
)

# Resolve CsvDir
try {
    $csvFull = (Resolve-Path -Path $CsvDir -ErrorAction Stop).Path
} catch {
    Write-Error "CsvDir not found: $CsvDir"
    exit 1
}

# Check psql
if (-not (Get-Command psql -ErrorAction SilentlyContinue)) {
    Write-Warning "psql not found on PATH. Install PostgreSQL client tools or run this script from WSL/Docker where psql is available."
}

# Find CSV files
$csvFiles = Get-ChildItem -Path $csvFull -Filter "*.csv" -File | Sort-Object Name
if (-not $csvFiles -or $csvFiles.Count -eq 0) {
    Write-Warning "No CSV files found in $csvFull"
    exit 0
}

Write-Host "Found $($csvFiles.Count) CSV files in: $csvFull" -ForegroundColor Cyan
foreach ($f in $csvFiles) { Write-Host " - $($f.Name)" }

if (-not $Force) {
    $ok = Read-Host "Proceed to import these files into $User@${PgHost}:$Port/$Database? (y/N)"
    if ($ok -ne 'y' -and $ok -ne 'Y') { Write-Host "Aborted by user"; exit 0 }
}

# Set PGPASSWORD for this process to allow psql to use password non-interactively
$oldPGPassword = $env:PGPASSWORD
    $env:PGPASSWORD = $Password

foreach ($file in $csvFiles) {
    $tableName = [System.IO.Path]::GetFileNameWithoutExtension($file.Name)
    $filePath = $file.FullName

    Write-Host "Importing ${filePath} -> table ${tableName}" -ForegroundColor Green

    # Prepare per-file tracking variables
    $status = 'PENDING'
    $errorMessage = ''
    $pgCount = $null
    try {
        $csvLines = (Get-Content -Path $filePath -ErrorAction Stop | Measure-Object -Line).Lines
        $csvRows = [int]$csvLines - 1
    } catch {
        $csvRows = $null
    }

    # Use psql \copy which runs on the server and is fast. The COPY command expects a server-side path when used directly;
    # psql's \copy reads the client file and streams it to the server, so we use psql -c "\copy ..."
    # Escape embedded quotes with backtick to avoid PowerShell parsing issues when variables are next to punctuation.
    $copyCmd = "\\copy `\"${tableName}`\" FROM '${filePath}' WITH (FORMAT csv, HEADER true)"

    # Build psql arguments (avoid automatic $args variable)
    $psqlArgs = @()
    $psqlArgs += "-h"; $psqlArgs += $PgHost
    $psqlArgs += "-p"; $psqlArgs += [string]$Port
    $psqlArgs += "-U"; $psqlArgs += $User
    $psqlArgs += "-d"; $psqlArgs += $Database
    $psqlArgs += "-c"; $psqlArgs += $copyCmd

    try {
        # Invoke psql for the \copy import
    $proc = Start-Process -FilePath psql -ArgumentList $psqlArgs -NoNewWindow -Wait -PassThru -RedirectStandardOutput -RedirectStandardError
        $out = $proc.StandardOutput.ReadToEnd()
        $err = $proc.StandardError.ReadToEnd()
        if ($proc.ExitCode -ne 0) {
            $status = 'FAILED'
            $errorMessage = $err
            Write-Error "psql failed for $filePath. ExitCode: $($proc.ExitCode)\n$err"
        } else {
            Write-Host "Imported $filePath -> $tableName" -ForegroundColor Cyan
            $status = 'IMPORTED'

            # Validation: compare CSV line count (minus header) to table row count in Postgres
            if (-not $NoValidate.IsPresent) {
                try {
                    $csvLines = (Get-Content -Path $filePath -ErrorAction Stop | Measure-Object -Line).Lines
                    $dataRows = [int]$csvLines - 1

                    # Query Postgres for table count using psql -t -A to get plain number
                    $countQuery = "SELECT COUNT(*)::bigint FROM `\"${tableName}`\";"
                    $countArgs = @('-h',$PgHost,'-p',[string]$Port,'-U',$User,'-d',$Database,'-t','-A','-c',$countQuery)
                    $countProc = Start-Process -FilePath psql -ArgumentList $countArgs -NoNewWindow -Wait -PassThru -RedirectStandardOutput -RedirectStandardError
                    $countOut = $countProc.StandardOutput.ReadToEnd().Trim()
                    $countErr = $countProc.StandardError.ReadToEnd()
                    $pgCount = 0
                    if ($countProc.ExitCode -eq 0 -and $countOut -match '\d+') {
                        $pgCount = [int]($countOut -replace '\s+', '')
                    } else {
                        Write-Warning "Could not determine row count for table ${tableName}: ${countErr}"
                    }

                    if ($pgCount -ne $dataRows) {
                        Write-Warning "Row count mismatch for ${tableName}: CSV rows=${dataRows}, Postgres rows=${pgCount}"
                        $status = 'MISMATCH'
                    } else {
                        Write-Host "Row count validated for ${tableName}: ${pgCount} rows" -ForegroundColor Green
                        $status = 'OK'
                    }
                } catch {
                    Write-Warning "Validation failed for ${tableName}: ${_}"
                    $status = 'VALIDATION_ERROR'
                    $errorMessage = "${_}"
                }
            } else {
                Write-Host "Skipping validation for $tableName (NoValidate passed)" -ForegroundColor Yellow
            }
        }
    } catch {
        $status = 'ERROR'
        $errorMessage = "${_}"
        Write-Error "Failed to run psql for ${filePath}: ${_}"
    }

    # Record result for this file in the import report
    $report += [pscustomobject]@{
        File = $file.Name
        Table = $tableName
        CsvRows = $csvRows
        PgRows = $pgCount
        Status = $status
        Error = $errorMessage
    }
}

# Restore previous PGPASSWORD
if ($null -ne $oldPGPassword) { $env:PGPASSWORD = $oldPGPassword } else { Remove-Item Env:\PGPASSWORD -ErrorAction SilentlyContinue }

# Write CSV report next to current working directory
$reportFile = Join-Path -Path (Get-Location) -ChildPath "import_report.csv"
$report | Export-Csv -Path $reportFile -NoTypeInformation -Force

Write-Host "All imports attempted. Check psql output for errors. Import report written to: ${reportFile}" -ForegroundColor Green

