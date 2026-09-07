@echo off
rem ASCII only - Korean output comes from the python script (see scripts/run_console.py)
chcp 65001 >nul
title Naver Webtoon - paid transition list
cd /d "%~dp0scripts"

set "PY=%LOCALAPPDATA%\Programs\Python\Python314\python.exe"
if not exist "%PY%" set "PY=python"

"%PY%" run_console.py
echo.
pause
