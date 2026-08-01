@echo off
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
title Conectar / Renovar TradeStation
cd /d "%~dp0engine"
".venv\Scripts\python.exe" "scripts\tradestation_catch.py"
echo.
echo (Puedes cerrar esta ventana.)
pause
