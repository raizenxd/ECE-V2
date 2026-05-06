@echo off
setlocal

cd /d "%~dp0"

set "VENV_DIR=.env"
set "PYTHON_CMD=python"

where py >nul 2>nul
if %errorlevel%==0 (
    set "PYTHON_CMD=py"
)

if not exist "%VENV_DIR%\Scripts\python.exe" (
    echo Creating virtual environment in %VENV_DIR%...
    %PYTHON_CMD% -m venv "%VENV_DIR%"
    if errorlevel 1 goto :fail
)

call "%VENV_DIR%\Scripts\activate.bat"
if errorlevel 1 goto :fail

echo Installing Python dependencies...
pip install -r requirements.txt
if errorlevel 1 goto :fail

pip install matplotlib
if errorlevel 1 goto :fail

echo Starting ECETHON...
python ECETHON.py
if errorlevel 1 goto :fail

goto :end

:fail
echo.
echo Failed to set up or run ECETHON.
exit /b 1

:end
endlocal
