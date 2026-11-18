@echo off
title Build Ostad EveLogExp Standalone Executable
echo ========================================================
echo Building Ostad EveLogExp (Ostad Red Team Forge)
echo Founder & Director: Ostad Rezaul Karim
echo ========================================================
echo.
cd /d "%~dp0"
python -m PyInstaller --noconfirm --onedir --windowed ^
    --name "OstadEveLogExp" ^
    --icon "assets\app_icon.ico" ^
    --add-data "color_rules.json;." ^
    --add-data "assets;assets" ^
    main.py

echo.
if %ERRORLEVEL% equ 0 (
    echo ========================================================
    echo Build Successful!
    echo Executable: dist\OstadEveLogExp\OstadEveLogExp.exe
    echo ========================================================
) else (
    echo [ERROR] Build failed.
)
pause
