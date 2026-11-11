@echo off
rem Sobe a API e o site do IRIS. Porta e senha do MySQL ficam em config-local.bat.
cd /d "%~dp0"
if exist config-local.bat call config-local.bat

rem MySQL portatil em C:\mysql, se existir. MySQL instalado como servico ja liga sozinho.
set MYSQL=C:\mysql\mysql-8.0.42-winx64\bin
if not exist "%MYSQL%\mysqld.exe" goto api
tasklist /fi "imagename eq mysqld.exe" | find /i "mysqld.exe" >nul || start "MySQL" /min "%MYSQL%\mysqld.exe" --defaults-file=C:\mysql\my.ini --console
echo Aguardando o MySQL...
:espera
"%MYSQL%\mysqladmin.exe" -uroot -h127.0.0.1 ping >nul 2>&1 || (timeout /t 1 /nobreak >nul & goto espera)

:api
start "API IRIS" cmd /k ".venv\Scripts\python.exe api.py"
start "Site IRIS" cmd /k "cd frontend && npm run dev"
timeout /t 6 /nobreak >nul
start http://localhost:5173
