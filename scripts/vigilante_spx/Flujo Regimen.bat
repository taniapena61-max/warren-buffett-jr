@echo off
REM Regimen de flujo (calls vs puts) MarketSnack -> cache para selector_metodo.
REM Lo corre la tarea WBJ Flujo Regimen 2x/dia (10:30 y 14:30 ET). No requiere terminal.
setlocal
set "ROOT=%~dp0..\..\"
if not exist "%ROOT%logs" mkdir "%ROOT%logs"
cd /d "%ROOT%"
set PYTHONIOENCODING=utf-8
echo [%date% %time%] flujo_regimen >> "%ROOT%logs\flujo_regimen.log"
py "scripts\flujo_regimen.py" SPX >> "%ROOT%logs\flujo_regimen.log" 2>&1
echo. >> "%ROOT%logs\flujo_regimen.log"
endlocal
