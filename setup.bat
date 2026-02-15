@echo off
setlocal enabledelayedexpansion

set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

echo ========================================
echo     HonToAnki Setup (Windows)
echo ========================================
echo.

REM Check for Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed.
    echo Please install Python from: https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

echo Found Python:
python --version
echo.

REM Create dict directory if it doesn't exist
if not exist "dict" mkdir dict

REM Check if dictionary already exists
set "dict_file="
for %%F in (dict\jmdict-examples-eng-*.json) do set "dict_file=%%F"

if not "%dict_file%"=="" (
    echo Dictionary already found: %dict_file%
    echo Skipping download...
) else (
    echo Downloading latest JMdict dictionary...
    
    powershell -Command "& { $response = Invoke-RestMethod -Uri 'https://api.github.com/repos/scriptin/jmdict-simplified/releases/latest'; $asset = $response.assets | Where-Object { $_.name -match 'jmdict-examples-eng-.*\.json\.zip' }; Invoke-WebRequest -Uri $asset.browser_download_url -OutFile 'dict.zip'; }"
    
    if errorlevel 1 (
        echo ERROR: Failed to download dictionary.
        pause
        exit /b 1
    )
    
    echo Extracting dictionary...
    powershell -Command "Expand-Archive -Path 'dict.zip' -DestinationPath 'dict' -Force"
    del /f dict.zip
    
    echo Dictionary downloaded and extracted.
)

echo.
echo Installing Python dependencies...
python -m pip install -r requirements.txt

if errorlevel 1 (
    echo ERROR: Failed to install dependencies.
    pause
    exit /b 1
)

echo.
echo ========================================
echo Setup complete!
echo ========================================
echo.
echo To run the app, use:
echo   python main.py
echo.
pause
