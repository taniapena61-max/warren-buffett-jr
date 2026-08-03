@echo off
chcp 65001 >nul
title Traer updates de Victor (solo cuando quieras)
cd /d "%~dp0"
echo ============================================================
echo   Traer los updates de Victor (upstream) - SIN mezclar aun
echo ============================================================
echo.
echo   Descarga lo nuevo de Victor pero NO lo mezcla con lo tuyo
echo   (para no romper nada). Tu decides que tomar.
echo.
git fetch upstream
echo.
echo ------------------------------------------------------------
echo   Listo: se bajaron los cambios de Victor a "upstream/main".
echo   NO se tocaron tus archivos.
echo.
echo   Dile a Claude: "integra los updates de Victor" y el los
echo   revisa y mezcla con cuidado, respetando TUS adiciones.
echo ------------------------------------------------------------
pause
