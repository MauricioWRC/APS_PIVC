@echo off
rem Instala dependencias, modelos, MySQL portatil e banco. Pode rodar de novo.
cd /d "%~dp0"
where py >nul 2>&1 && (py -3 instalar.py) || (python instalar.py)
pause
