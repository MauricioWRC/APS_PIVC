@echo off
rem Sobe o MySQL (se for o do instalador), a API e o site. Porta e senha ficam em config-local.bat.
cd /d "%~dp0"
if exist config-local.bat call config-local.bat
if not defined APS_DB_PORT set APS_DB_PORT=3306

rem MySQL do instalar.bat (IRIS_MYSQL) ou o portatil antigo em C:\mysql. MySQL instalado como servico ja liga sozinho.
if defined IRIS_MYSQL (
  set "MYSQL=%IRIS_MYSQL%\mysql-8.0.42-winx64\bin"
  set "MYSQL_INI=%IRIS_MYSQL%\my.ini"
) else (
  set "MYSQL=C:\mysql\mysql-8.0.42-winx64\bin"
  set "MYSQL_INI=C:\mysql\my.ini"
)
if not exist "%MYSQL%\mysqld.exe" goto api
"%MYSQL%\mysqladmin.exe" -uroot -h127.0.0.1 -P%APS_DB_PORT% ping >nul 2>&1 || start "MySQL" /min "%MYSQL%\mysqld.exe" --defaults-file="%MYSQL_INI%" --console
echo Aguardando o MySQL...
:espera
"%MYSQL%\mysqladmin.exe" -uroot -h127.0.0.1 -P%APS_DB_PORT% ping >nul 2>&1 || (timeout /t 1 /nobreak >nul & goto espera)

:api
start "API IRIS" cmd /k ".venv\Scripts\python.exe api.py"
start "Site IRIS" cmd /k "cd frontend && npm run dev"
timeout /t 6 /nobreak >nul
start http://localhost:5173
