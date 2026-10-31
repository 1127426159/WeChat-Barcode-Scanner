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

echo.
echo Setup complete. Double-click start.bat to run.
pause
