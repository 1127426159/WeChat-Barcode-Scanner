@echo off
setlocal
cd /d "%~dp0"

call "%~dp0setup_windows.cmd"
if errorlevel 1 (
    echo.
    echo Setup failed.
    pause
    exit /b 1
)

set "PY=%~dp0.venv\Scripts\python.exe"
echo.
"%PY%" -m host %*
if errorlevel 1 pause
