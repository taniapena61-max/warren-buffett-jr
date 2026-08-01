@echo off
REM Lanzador del monitor de posiciones para el Programador de tareas de Windows.
REM Corre cada 10 min en horario de mercado; solo manda email si algo dispara.
cd /d "%~dp0..\.."
set PYTHONIOENCODING=utf-8
"engine\.venv\Scripts\python.exe" "engine\scripts\monitor_posiciones.py"
