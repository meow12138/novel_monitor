<#
.SYNOPSIS
    Novel Monitor 一键部署脚本 (Windows 10 / 阿里云 ECS)
.DESCRIPTION
    自动完成: 环境检测 → 依赖安装 → 前端构建 → 后端启动 → 注册开机自启
.USAGE
    以管理员身份运行 PowerShell，执行：
    Set-ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
    .\deploy.ps1
#>

param(
    [string]$Port = "8001",
    [string]$InstallDir = "C:\novel_monitor",
    [switch]$SkipEnvCheck
)

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Novel Monitor - 一键部署脚本" -ForegroundColor Cyan
Write-Host "  目标: 阿里云 ECS (Windows 10)" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# ============================================================
# 1. 环境检测
# ============================================================
function Test-Command($cmd) {
    try { Get-Command $cmd -ErrorAction Stop | Out-Null; return $true }
    catch { return $false }
}

Write-Host "[1/7] 检测运行环境..." -ForegroundColor Yellow

if (-not $SkipEnvCheck) {
    # Python
    if (Test-Command "python") {
        $pyVer = python --version 2>&1
        Write-Host "  Python: $pyVer" -ForegroundColor Green
    } else {
        Write-Host "  Python 未安装! 正在下载安装..." -ForegroundColor Red
        $pyInstaller = "$env:TEMP\python-installer.exe"
        Invoke-WebRequest -Uri "https://www.python.org/ftp/python/3.12.8/python-3.12.8-amd64.exe" -OutFile $pyInstaller
        Start-Process -FilePath $pyInstaller -ArgumentList "/quiet", "InstallAllUsers=1", "PrependPath=1" -Wait
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")
        Write-Host "  Python 安装完成" -ForegroundColor Green
    }

    # Node.js
    if (Test-Command "node") {
        $nodeVer = node --version 2>&1
        Write-Host "  Node.js: $nodeVer" -ForegroundColor Green
    } else {
        Write-Host "  Node.js 未安装! 正在下载安装..." -ForegroundColor Red
        $nodeInstaller = "$env:TEMP\node-installer.msi"
        Invoke-WebRequest -Uri "https://nodejs.org/dist/v22.12.0/node-v22.12.0-x64.msi" -OutFile $nodeInstaller
        Start-Process -FilePath "msiexec.exe" -ArgumentList "/i", $nodeInstaller, "/quiet", "/norestart" -Wait
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")
        Write-Host "  Node.js 安装完成" -ForegroundColor Green
    }

    # Git
    if (Test-Command "git") {
        $gitVer = git --version 2>&1
        Write-Host "  Git: $gitVer" -ForegroundColor Green
    } else {
        Write-Host "  Git 未安装! 请手动安装 Git: https://git-scm.com/download/win" -ForegroundColor Red
        Write-Host "  安装后重新运行此脚本" -ForegroundColor Red
        exit 1
    }
}

# ============================================================
# 2. 拉取代码
# ============================================================
Write-Host ""
Write-Host "[2/7] 拉取代码到 $InstallDir ..." -ForegroundColor Yellow

if (Test-Path "$InstallDir\.git") {
    Write-Host "  目录已存在，执行 git pull..." -ForegroundColor Cyan
    Push-Location $InstallDir
    git pull origin main
    Pop-Location
} else {
    if (Test-Path $InstallDir) {
        Remove-Item -Recurse -Force $InstallDir
    }
    git clone https://github.com/meow12138/novel_monitor.git $InstallDir
}

# ============================================================
# 3. 安装后端依赖
# ============================================================
Write-Host ""
Write-Host "[3/7] 安装后端 Python 依赖..." -ForegroundColor Yellow

Push-Location "$InstallDir\server"
python -m pip install --upgrade pip -q
pip install -r requirements.txt -q
Write-Host "  后端依赖安装完成" -ForegroundColor Green
Pop-Location

# ============================================================
# 4. 安装前端依赖 + 构建
# ============================================================
Write-Host ""
Write-Host "[4/7] 安装前端依赖并构建..." -ForegroundColor Yellow

Push-Location "$InstallDir\web"
npm install --silent
npm run build
Write-Host "  前端构建完成 -> web/dist/" -ForegroundColor Green
Pop-Location

# ============================================================
# 5. 停止旧服务（如果存在）
# ============================================================
Write-Host ""
Write-Host "[5/7] 停止旧服务..." -ForegroundColor Yellow

$existingTask = Get-ScheduledTask -TaskName "NovelMonitor" -ErrorAction SilentlyContinue
if ($existingTask) {
    Stop-ScheduledTask -TaskName "NovelMonitor" -ErrorAction SilentlyContinue
    Unregister-ScheduledTask -TaskName "NovelMonitor" -Confirm:$false
    Write-Host "  已移除旧的计划任务" -ForegroundColor Cyan
}

Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object {
    $_.CommandLine -like "*novel_monitor*" -or $_.CommandLine -like "*uvicorn*app.main*"
} | Stop-Process -Force -ErrorAction SilentlyContinue

Start-Sleep -Seconds 2

# ============================================================
# 6. 创建启动脚本 + 注册开机自启
# ============================================================
Write-Host ""
Write-Host "[6/7] 配置服务与开机自启..." -ForegroundColor Yellow

$startScript = @"
@echo off
cd /d $InstallDir\server
python -m uvicorn app.main:app --host 0.0.0.0 --port $Port --workers 2
"@

Set-Content -Path "$InstallDir\start_server.bat" -Value $startScript -Encoding ASCII

$action = New-ScheduledTaskAction -Execute "$InstallDir\start_server.bat" -WorkingDirectory "$InstallDir\server"
$trigger = New-ScheduledTaskTrigger -AtStartup
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 1)
$principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest

Register-ScheduledTask -TaskName "NovelMonitor" -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Force | Out-Null
Write-Host "  已注册 Windows 计划任务 [NovelMonitor] 开机自启" -ForegroundColor Green

# ============================================================
# 7. 启动服务
# ============================================================
Write-Host ""
Write-Host "[7/7] 启动服务..." -ForegroundColor Yellow

Start-ScheduledTask -TaskName "NovelMonitor"
Start-Sleep -Seconds 5

try {
    $resp = Invoke-RestMethod -Uri "http://127.0.0.1:$Port/api/health" -TimeoutSec 10
    if ($resp.status -eq "ok") {
        Write-Host ""
        Write-Host "============================================" -ForegroundColor Green
        Write-Host "  部署成功!" -ForegroundColor Green
        Write-Host "============================================" -ForegroundColor Green
        Write-Host ""
        Write-Host "  访问地址:  http://<ECS公网IP>:$Port" -ForegroundColor Cyan
        Write-Host "  API 文档:  http://<ECS公网IP>:$Port/docs" -ForegroundColor Cyan
        Write-Host "  健康检查:  http://127.0.0.1:$Port/api/health" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "  服务管理:" -ForegroundColor Yellow
        Write-Host "    启动:  Start-ScheduledTask -TaskName NovelMonitor" -ForegroundColor White
        Write-Host "    停止:  Stop-ScheduledTask -TaskName NovelMonitor" -ForegroundColor White
        Write-Host "    状态:  Get-ScheduledTask -TaskName NovelMonitor" -ForegroundColor White
        Write-Host ""
        Write-Host "  重要: 请在阿里云安全组中放行 TCP $Port 端口!" -ForegroundColor Red
        Write-Host ""
    }
} catch {
    Write-Host "  服务启动中，请稍后访问 http://127.0.0.1:$Port" -ForegroundColor Yellow
    Write-Host "  如果无法访问，请检查: Get-ScheduledTask -TaskName NovelMonitor" -ForegroundColor Yellow
}
