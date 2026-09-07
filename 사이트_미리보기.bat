@echo off
rem ASCII only - stop the preview by closing this window (or Ctrl+C)
chcp 65001 >nul
title Local preview - http://localhost:8765/
cd /d "%~dp0docs"

set "PY=%LOCALAPPDATA%\Programs\Python\Python314\python.exe"
if not exist "%PY%" set "PY=python"

echo Opening http://localhost:8765/ in your browser.
echo Close this window to stop the preview.
echo.
start "" http://localhost:8765/
"%PY%" -m http.server 8765
