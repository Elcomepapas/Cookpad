param()

$ErrorActionPreference = "Stop"
$repositoryRoot = $PSScriptRoot
$backendDirectory = Join-Path $repositoryRoot "backend"
$frontendDirectory = Join-Path $repositoryRoot "frontend"
$results = New-Object System.Collections.Generic.List[object]

function Invoke-Check {
    param(
        [string]$Name,
        [string]$WorkingDirectory,
        [string]$Executable,
        [string[]]$Arguments
    )

    Write-Host "`n=== $Name ===" -ForegroundColor Cyan
    Push-Location $WorkingDirectory
    try {
        & $Executable @Arguments
        $exitCode = $LASTEXITCODE
        if ($null -eq $exitCode) {
            $exitCode = 0
        }

        if ($exitCode -eq 0) {
            Write-Host "PASS: $Name" -ForegroundColor Green
            $results.Add([PSCustomObject]@{ Name = $Name; Status = "PASS" })
        }
        else {
            Write-Host "FAIL: $Name (exit code $exitCode)" -ForegroundColor Red
            $results.Add([PSCustomObject]@{ Name = $Name; Status = "FAIL" })
        }
    }
    catch {
        Write-Host "FAIL: $Name ($($_.Exception.Message))" -ForegroundColor Red
        $results.Add([PSCustomObject]@{ Name = $Name; Status = "FAIL" })
    }
    finally {
        Pop-Location
    }
}

function Add-BlockedCheck {
    param([string]$Name, [string]$Reason)

    Write-Host "`nBLOCKED: $Name - $Reason" -ForegroundColor Yellow
    $results.Add([PSCustomObject]@{ Name = $Name; Status = "BLOCKED" })
}

Write-Host "Cookpad: backend and frontend verification" -ForegroundColor White

if (-not (Test-Path $backendDirectory)) {
    Add-BlockedCheck "Backend" "Directory not found: $backendDirectory"
}
else {
    $python = Join-Path $backendDirectory ".venv\Scripts\python.exe"
    if (-not (Test-Path $python)) {
        $pythonCommand = Get-Command py.exe -ErrorAction SilentlyContinue
        if ($null -ne $pythonCommand) {
            $python = $pythonCommand.Source
            $pythonPrefix = @("-3")
        }
        else {
            $pythonCommand = Get-Command python.exe -ErrorAction SilentlyContinue
            if ($null -ne $pythonCommand) {
                $python = $pythonCommand.Source
                $pythonPrefix = @()
            }
            else {
                $python = $null
            }
        }
    }
    else {
        $pythonPrefix = @()
    }

    if ($null -eq $python) {
        Add-BlockedCheck "Backend syntax" "Python was not found."
        Add-BlockedCheck "Backend tests" "Python was not found."
    }
    else {
        Invoke-Check "Backend syntax" $backendDirectory $python ($pythonPrefix + @("-m", "compileall", "-q", "src"))
        Invoke-Check "Backend tests" $backendDirectory $python ($pythonPrefix + @("-m", "unittest", "discover", "-v"))
    }
}

if (-not (Test-Path $frontendDirectory)) {
    Add-BlockedCheck "Frontend" "Directory not found: $frontendDirectory"
}
elseif (-not (Test-Path (Join-Path $frontendDirectory "node_modules"))) {
    Add-BlockedCheck "Frontend tests, lint, type-check and build" "Dependencies are missing. Run 'npm ci' in the frontend directory, then rerun this script."
}
else {
    $npmCommand = Get-Command npm.cmd -ErrorAction SilentlyContinue
    if ($null -eq $npmCommand) {
        Add-BlockedCheck "Frontend tests, lint and build" "npm.cmd was not found."
    }
    else {
        $npm = $npmCommand.Source
        Invoke-Check "Frontend tests" $frontendDirectory $npm @("test", "--", "--run")
        Invoke-Check "Frontend lint" $frontendDirectory $npm @("run", "lint")

        $typeScriptCompiler = Join-Path $frontendDirectory "node_modules\.bin\tsc.cmd"
        if (Test-Path $typeScriptCompiler) {
            Invoke-Check "Frontend TypeScript" $frontendDirectory $typeScriptCompiler @("--noEmit")
        }
        else {
            Add-BlockedCheck "Frontend TypeScript" "Local TypeScript compiler was not found."
        }

        Invoke-Check "Frontend build" $frontendDirectory $npm @("run", "build")
    }
}

Write-Host "`n=== Summary ===" -ForegroundColor Cyan
$results | Format-Table -AutoSize

$failedCount = @($results | Where-Object { $_.Status -eq "FAIL" }).Count
$blockedCount = @($results | Where-Object { $_.Status -eq "BLOCKED" }).Count
if (($failedCount + $blockedCount) -gt 0) {
    Write-Host "$failedCount failed; $blockedCount blocked." -ForegroundColor Red
    exit 1
}

Write-Host "All checks passed." -ForegroundColor Green
exit 0
