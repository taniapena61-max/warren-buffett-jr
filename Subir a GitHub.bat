@echo off
chcp 65001 >nul
title Subir mis cambios a MI GitHub
cd /d "%~dp0"
echo ============================================================
echo   Subir tus cambios a TU repo (origin = taniapena61-max)
echo ============================================================
echo.
echo   Sube a LO TUYO. No depende de permisos de Victor.
echo   Si aparece la ventana de GitHub, dale "Sign in with your
echo   browser" y completa el login. La ventana se queda viva.
echo.
git push origin actualizacion-victor
echo.
echo ------------------------------------------------------------
echo   OPCIONAL: si quieres compartir de vuelta a Victor, abre:
echo   https://github.com/infusionvictor/warren-buffett-jr/compare/main...taniapena61-max:actualizacion-victor
echo.
echo   Para TRAER updates de Victor (solo cuando te sirvan):
echo   abre "Traer updates de Victor.bat"
echo ------------------------------------------------------------
pause
