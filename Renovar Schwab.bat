@echo off
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
title Renovar Schwab
cd /d "%~dp0engine"
".venv\Scripts\python.exe" "scripts\renovar_schwab.py"
echo.
echo (Puedes cerrar esta ventana.)
pause
