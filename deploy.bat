@echo off
chcp 65001 >nul
echo.
echo ============================================
echo   Novel Monitor - 一键部署 (Windows 10)
echo   以管理员身份运行此脚本
echo ============================================
echo.

:: 检查管理员权限
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [错误] 请右键 - 以管理员身份运行此脚本!
    echo.
    pause
    exit /b 1
)

:: 设置 PowerShell 执行策略并运行部署脚本
powershell -ExecutionPolicy Bypass -File "%~dp0deploy.ps1" -Port 8001 -InstallDir "C:\novel_monitor"

pause
