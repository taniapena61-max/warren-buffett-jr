@echo off
chcp 65001 >nul
title Transcribir clase - Warren Buffett Jr
cd /d "%~dp0"

set "PY=%LOCALAPPDATA%\Programs\Python\Python313\python.exe"
if not exist "%PY%" set "PY=py"

echo ============================================================
echo   TRANSCRIPTOR DE CLASES (local y privado)
echo ============================================================
echo.
echo   Convierte tus audios/videos de clase a texto.
echo   Todo corre en TU PC. Nada se sube a internet.
echo.
echo   Puedes:
echo     - Arrastrar un audio/video encima de este archivo, o
echo     - Dejarlo en "Materiales\Pendiente de transcribir" y
echo       hacer doble clic aqui para transcribir todo.
echo.
echo ------------------------------------------------------------

"%PY%" "%~dp0Herramienta de transcripcion\transcribir.py" %*

echo.
echo ------------------------------------------------------------
echo   Terminado. Puedes cerrar esta ventana.
echo ------------------------------------------------------------
pause
