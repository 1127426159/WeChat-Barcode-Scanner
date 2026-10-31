@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"

set "VENV=%~dp0.venv"
set "PY=%VENV%\Scripts\python.exe"
set "PIP_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple"

if exist "%PY%" goto :check_venv

echo [1/3] Looking for Python 3.7 or newer...
set "BASEPY="
where py >nul 2>nul && set "BASEPY=py -3"
if not defined BASEPY where python >nul 2>nul && set "BASEPY=python"

if not defined BASEPY goto :install_python
!BASEPY! -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 7) else 1)"
if errorlevel 1 set "BASEPY="

:install_python
if not defined BASEPY (
    echo Python was not found. Downloading a compatible Python version...
    powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0install_python.ps1"
    if errorlevel 1 (
        echo Failed to install Python automatically.
        echo Install Python 3.8.10 from the opened download page and tick "Add Python 3.8 to PATH".
        echo Then run START-FOR-WINDOWS.bat again.
        exit /b 1
    )
    for %%P in (
        "%LOCALAPPDATA%\Programs\Python\Python313\python.exe"
        "%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
        "%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
        "%LOCALAPPDATA%\Programs\Python\Python310\python.exe"
        "%LOCALAPPDATA%\Programs\Python\Python39\python.exe"
        "%LOCALAPPDATA%\Programs\Python\Python38\python.exe"
        "%LOCALAPPDATA%\Programs\Python\Python37\python.exe"
        "%ProgramFiles%\Python313\python.exe"
        "%ProgramFiles%\Python312\python.exe"
        "%ProgramFiles%\Python311\python.exe"
        "%ProgramFiles%\Python310\python.exe"
        "%ProgramFiles%\Python39\python.exe"
        "%ProgramFiles%\Python38\python.exe"
        "%ProgramFiles%\Python37\python.exe"
    ) do (
        if not defined BASEPY if exist %%P set "BASEPY=%%~P"
    )
)

if not defined BASEPY (
    echo Python installation finished, but python.exe could not be found.
    echo Restart the computer and run start.bat again.
    exit /b 1
)

!BASEPY! -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 7) else 1)"
if errorlevel 1 (
    echo The installed Python is older than 3.7.
    exit /b 1
)

echo [1/3] Creating virtual environment...
!BASEPY! -m venv "%VENV%"
if errorlevel 1 (
    echo Failed to create the virtual environment.
    exit /b 1
)

:check_venv
"%PY%" -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 7) else 1)"
if errorlevel 1 (
    echo The existing .venv uses Python older than 3.7.
    echo Delete the .venv folder and run start.bat again.
    exit /b 1
)

"%PY%" -c "import pyautogui" >nul 2>nul
if errorlevel 1 (
    echo [2/3] Installing required dependencies...
    "%PY%" -m pip install --disable-pip-version-check --timeout 20 --retries 2 -i "%PIP_INDEX%" -r "%~dp0requirements.txt"
    if errorlevel 1 (
        echo Failed to install dependencies. Check your network connection.
        exit /b 1
    )
)

rem QR output is optional: a quick check keeps startup fast when offline.
"%PY%" -c "import segno" >nul 2>nul
if errorlevel 1 (
    echo [3/3] Installing optional QR support...
    "%PY%" -m pip install --disable-pip-version-check --timeout 15 --retries 1 -i "%PIP_INDEX%" segno >nul 2>nul
    if errorlevel 1 echo       Skipped: QR support unavailable, text output will be used.
)

exit /b 0
