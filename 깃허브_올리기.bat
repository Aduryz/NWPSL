@echo off
rem ASCII only - Korean text is printed by the python script (see scripts/publish_github.py)
chcp 65001 >nul
title Publish to GitHub
cd /d "%~dp0scripts"

set "PY=%LOCALAPPDATA%\Programs\Python\Python314\python.exe"
if not exist "%PY%" set "PY=python"

"%PY%" publish_github.py
echo.
pause
