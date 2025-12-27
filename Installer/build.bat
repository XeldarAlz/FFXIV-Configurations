@echo off
echo ========================================
echo  FFXIV Configuration Installer Builder
echo ========================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing dependencies...
pip install -r requirements.txt

echo.
echo Building executable...
echo.

pyinstaller --onefile ^
    --windowed ^
    --name "Xeldar FFXIV Installer" ^
    --icon "X.ico" ^
    --add-data "X.ico;." ^
    --add-data "..\Configs\FFXIV Configs;FFXIV Configs" ^
    --add-data "..\Configs\Mods Configs;Mods Configs" ^
    --add-data "..\Configs\ReShade Configs;ReShade Configs" ^
    --add-data "..\Configs\XIVLauncher Configs;XIVLauncher Configs" ^
    --clean ^
    ffxiv_config_installer.py

echo.
if exist "dist\Xeldar FFXIV Installer.exe" (
    echo ========================================
    echo  BUILD SUCCESSFUL!
    echo ========================================
    echo.
    echo Executable created at:
    echo   dist\Xeldar FFXIV Installer.exe
    echo.
    echo You can distribute this .exe file - it contains
    echo all config folders bundled inside.
) else (
    echo ========================================
    echo  BUILD FAILED
    echo ========================================
    echo Check the output above for errors.
)

echo.
pause