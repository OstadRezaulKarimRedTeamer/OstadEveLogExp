@echo off
title Push Ostad EveLogExp to GitHub
echo ========================================================
echo Ostad EveLogExp - Git Push Automation Helper
echo Ostad Red Team Forge - Founder & Director: Ostad Rezaul Karim
echo ========================================================
echo.

where git >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Git command line is not installed or not in PATH!
    echo.
    echo Please do one of the following:
    echo 1. Install Git from: https://git-scm.com/download/win
    echo 2. OR use GitHub Desktop (File -^> Add Local Repository)
    echo.
    pause
    exit /b
)

echo Initializing Git repository...
git init
git add .
git commit -m "Initial commit: Ostad EveLogExp v1.0 - Ostad Red Team Forge"
git branch -M main

echo.
set /p REPO_URL="Enter your GitHub Repository URL (e.g. https://github.com/username/OstadEveLogExp.git): "

if "%REPO_URL%"=="" (
    echo [!] No URL entered. Aborting push.
    pause
    exit /b
)

git remote remove origin >nul 2>nul
git remote add origin %REPO_URL%

echo.
echo Pushing to GitHub (main branch)...
git push -u origin main

echo.
if %ERRORLEVEL% equ 0 (
    echo ========================================================
    echo Successfully pushed to GitHub!
    echo ========================================================
) else (
    echo [ERROR] Git push failed. Please check your credentials and repository URL.
)
pause
