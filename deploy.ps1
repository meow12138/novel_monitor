param(
    [string]$Port = "8001",
    [string]$InstallDir = "C:\novel_monitor"
)

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Novel Monitor - Deploy Script" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# 1. Check environment
Write-Host "[1/6] Checking environment..." -ForegroundColor Yellow

function Test-Cmd($cmd) {
    try { Get-Command $cmd -ErrorAction Stop | Out-Null; return $true }
    catch { return $false }
}

if (Test-Cmd "python") {
    $pyVer = python --version 2>&1
    Write-Host "  OK: $pyVer" -ForegroundColor Green
} else {
    Write-Host "  ERROR: Python not found! Please install Python 3.11+ first." -ForegroundColor Red
    Write-Host "  Download: https://www.python.org/downloads/" -ForegroundColor Red
    exit 1
}

if (Test-Cmd "node") {
    $nodeVer = node --version 2>&1
    Write-Host "  OK: Node.js $nodeVer" -ForegroundColor Green
} else {
    Write-Host "  ERROR: Node.js not found! Please install Node.js 18+ first." -ForegroundColor Red
    Write-Host "  Download: https://nodejs.org/" -ForegroundColor Red
    exit 1
}

# 2. Pull code
Write-Host ""
Write-Host "[2/6] Pulling code..." -ForegroundColor Yellow

if (Test-Path "$InstallDir\.git") {
    Write-Host "  Directory exists, running git pull..." -ForegroundColor Cyan
    Push-Location $InstallDir
    git pull origin main
    Pop-Location
} else {
    Write-Host "  Code already in place, skip clone." -ForegroundColor Cyan
}

# 3. Install backend dependencies
Write-Host ""
Write-Host "[3/6] Installing backend dependencies..." -ForegroundColor Yellow

Push-Location "$InstallDir\server"
python -m pip install --upgrade pip -q 2>$null
pip install -r requirements.txt -q
Write-Host "  Backend dependencies OK" -ForegroundColor Green
Pop-Location

# 4. Install frontend + build
Write-Host ""
Write-Host "[4/6] Building frontend..." -ForegroundColor Yellow

Push-Location "$InstallDir\web"
npm install --silent 2>$null
npm run build
Write-Host "  Frontend build OK -> web/dist/" -ForegroundColor Green
Pop-Location

# 5. Stop old process + start new
Write-Host ""
Write-Host "[5/6] Starting service on port $Port..." -ForegroundColor Yellow

$existing = Get-Process -Name "python" -ErrorAction SilentlyContinue
if ($existing) {
    Write-Host "  Stopping old python processes..." -ForegroundColor Cyan
    Stop-Process -Name "python" -Force -ErrorAction SilentlyContinue
    Start-Sleep 2
}

$logFile = "$InstallDir\server\server.log"
Start-Process -FilePath "python" -ArgumentList "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", $Port -WorkingDirectory "$InstallDir\server" -WindowStyle Hidden -RedirectStandardOutput $logFile -RedirectStandardError "$InstallDir\server\server_err.log"

Start-Sleep 5

# 6. Register auto-start
Write-Host ""
Write-Host "[6/6] Registering auto-start..." -ForegroundColor Yellow

$taskExists = Get-ScheduledTask -TaskName "NovelMonitor" -ErrorAction SilentlyContinue
if ($taskExists) {
    Unregister-ScheduledTask -TaskName "NovelMonitor" -Confirm:$false -ErrorAction SilentlyContinue
}

$batContent = "@echo off`r`ncd /d $InstallDir\server`r`npython -m uvicorn app.main:app --host 0.0.0.0 --port $Port"
Set-Content -Path "$InstallDir\start_server.bat" -Value $batContent -Encoding ASCII

$action = New-ScheduledTaskAction -Execute "$InstallDir\start_server.bat" -WorkingDirectory "$InstallDir\server"
$trigger = New-ScheduledTaskTrigger -AtStartup
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
$principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest

Register-ScheduledTask -TaskName "NovelMonitor" -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Force | Out-Null
Write-Host "  Auto-start registered: NovelMonitor" -ForegroundColor Green

# 7. Verify
Write-Host ""
try {
    $resp = Invoke-RestMethod -Uri "http://127.0.0.1:$Port/api/health" -TimeoutSec 10
    if ($resp.status -eq "ok") {
        Write-Host "============================================" -ForegroundColor Green
        Write-Host "  DEPLOY SUCCESS!" -ForegroundColor Green
        Write-Host "============================================" -ForegroundColor Green
        Write-Host ""
        Write-Host "  URL:     http://8.163.102.70:$Port" -ForegroundColor Cyan
        Write-Host "  API Doc: http://8.163.102.70:$Port/docs" -ForegroundColor Cyan
        Write-Host "  Health:  http://127.0.0.1:$Port/api/health" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "  Service Management:" -ForegroundColor Yellow
        Write-Host "    Start: Start-ScheduledTask -TaskName NovelMonitor"
        Write-Host "    Stop:  Stop-ScheduledTask -TaskName NovelMonitor"
        Write-Host ""
    }
} catch {
    Write-Host "  Service starting... visit http://127.0.0.1:$Port in a moment." -ForegroundColor Yellow
}
