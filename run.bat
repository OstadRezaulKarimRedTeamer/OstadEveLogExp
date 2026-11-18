@echo off
title Ostad EveLogExp - Ostad Red Team Forge
echo Launching Ostad EveLogExp...
echo Founder & Director: Ostad Rezaul Karim
cd /d "%~dp0"
python main.py
if %ERRORLEVEL% neq 0 (
    echo.
    echo Application exited with error. Press any key to close.
    pause >nul
)
