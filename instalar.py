"""Instala tudo o que o IRIS precisa: dependências, modelos, MySQL portátil e banco. Rode pelo instalar.bat.

O MySQL fica em C:\\iris-mysql (fora do projeto, longe do OneDrive e de caminhos com acento), na porta 3307.
Pode ser executado de novo: passos já feitos são pulados.
"""
import hashlib
import os
import shutil
import subprocess
import sys
import time
import urllib.request
import zipfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
PASTA_MYSQL = Path(os.environ.get("IRIS_MYSQL_DIR", Path(os.environ.get("SystemDrive", "C:") + "\\") / "iris-mysql"))
PORTA = 3307
VERSAO = "mysql-8.0.42-winx64"
URL = f"https://cdn.mysql.com/archives/mysql-8.0/{VERSAO}.zip"
MD5 = "f67b6765a1649ddc4191bc0241f910f4"
BIN = PASTA_MYSQL / VERSAO / "bin"
PYTHON = RAIZ / ".venv" / "Scripts" / "python.exe"


def passo(texto):
    print(f"\n== {texto}", flush=True)


def parar(texto):
    print(f"\nERRO: {texto}")
    sys.exit(1)


def rodar(*cmd, **kw):
    subprocess.run([str(c) for c in cmd], check=True, **kw)


def mysql(*args, entrada=None):
    return subprocess.run([str(BIN / "mysql.exe"), "-uroot", "-h127.0.0.1", f"-P{PORTA}", "--default-character-set=utf8mb4", *args],
                          stdin=entrada, capture_output=True, text=True, check=True).stdout


def conferir_requisitos():
    passo("Conferindo requisitos")
    if not shutil.which("npm"):
        parar("Node.js não encontrado. Instale em https://nodejs.org/ e rode de novo.")
    if not Path(os.environ.get("SystemRoot", r"C:\Windows"), "System32", "vcruntime140_1.dll").exists():
        parar("Falta o Visual C++ do Windows, usado pelo MySQL. Instale "
              "https://aka.ms/vs/17/release/vc_redist.x64.exe e rode de novo.")
    print("ok")


def instalar_python():
    passo("Dependências do Python")
    if not PYTHON.exists():
        rodar(sys.executable, "-m", "venv", RAIZ / ".venv")
    rodar(PYTHON, "-m", "pip", "install", "-q", "-r", RAIZ / "requirements.txt")
    passo("Modelos de reconhecimento (YuNet e SFace)")
    rodar(PYTHON, "-m", "processamento_imagens", "preparar-modelos", cwd=RAIZ)


def instalar_site():
    passo("Dependências do site")
    rodar("npm.cmd", "install", "--no-audit", "--no-fund", cwd=RAIZ / "frontend")
    env = RAIZ / "frontend" / ".env"
    if not env.exists():
        shutil.copy(RAIZ / "frontend" / ".env.example", env)


def baixar_mysql():
    passo(f"MySQL portátil em {PASTA_MYSQL}")
    if (BIN / "mysqld.exe").exists():
        print("já instalado")
        return
    PASTA_MYSQL.mkdir(parents=True, exist_ok=True)
    zip_ = PASTA_MYSQL / "mysql.zip"
    print("baixando 245 MB...", flush=True)
    with urllib.request.urlopen(URL, timeout=60) as origem, zip_.open("wb") as destino:
        total, lido, marca = int(origem.headers.get("Content-Length", 0)), 0, 0
        while bloco := origem.read(1 << 20):
            destino.write(bloco)
            lido += len(bloco)
            if total and lido * 10 // total > marca:
                marca = lido * 10 // total
                print(f"  {marca * 10}%", flush=True)
    md5 = hashlib.md5()
    with zip_.open("rb") as f:
        while bloco := f.read(1 << 20):
            md5.update(bloco)
    if md5.hexdigest() != MD5:
        zip_.unlink()
        parar("o arquivo baixado veio corrompido. Rode o instalador de novo.")
    print("extraindo...", flush=True)
    with zipfile.ZipFile(zip_) as z:
        z.extractall(PASTA_MYSQL)
    zip_.unlink()


def preparar_banco():
    passo("Banco de dados")
    ini = PASTA_MYSQL / "my.ini"
    dados = PASTA_MYSQL / "data"
    ini.write_text(f"[mysqld]\nbasedir={(PASTA_MYSQL / VERSAO).as_posix()}\ndatadir={dados.as_posix()}\nport={PORTA}\n"
                   "bind-address=127.0.0.1\nmysqlx=OFF\ncharacter-set-server=utf8mb4\n", encoding="ascii")
    if not dados.exists():
        rodar(BIN / "mysqld.exe", f"--defaults-file={ini}", "--initialize-insecure")
    servidor = subprocess.Popen([str(BIN / "mysqld.exe"), f"--defaults-file={ini}"],
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        for _ in range(60):
            if subprocess.run([str(BIN / "mysqladmin.exe"), "-uroot", "-h127.0.0.1", f"-P{PORTA}", "ping"],
                              capture_output=True).returncode == 0:
                break
            time.sleep(1)
        else:
            parar(f"o MySQL não ligou. A porta {PORTA} pode estar em uso.")
        if "sistema_biometrico" in mysql("-N", "-e", "SHOW DATABASES LIKE 'sistema_biometrico'"):
            print("banco já existe; nada foi alterado")
        else:
            for arquivo in ("sistema biometria APS.sql", "migracao_empresa_quimica.sql"):
                with (RAIZ / arquivo).open("rb") as f:
                    mysql(entrada=f)
                print(f"importado: {arquivo}")
    finally:
        subprocess.run([str(BIN / "mysqladmin.exe"), "-uroot", "-h127.0.0.1", f"-P{PORTA}", "shutdown"], capture_output=True)
        servidor.wait(timeout=60)


def gravar_config():
    config = RAIZ / "config-local.bat"
    if config.exists():
        print(f"\nAviso: {config.name} já existe e não foi alterado. Para usar o MySQL do instalador, ele precisa ter:\n"
              f"  set IRIS_MYSQL={PASTA_MYSQL}\n  set APS_DB_PORT={PORTA}\n  set APS_DB_PASSWORD=")
        return
    config.write_text(f"rem Criado pelo instalar.bat\nset IRIS_MYSQL={PASTA_MYSQL}\nset APS_DB_PORT={PORTA}\nset APS_DB_PASSWORD=\n",
                      encoding="ascii")


if __name__ == "__main__":
    os.chdir(RAIZ)
    try:
        conferir_requisitos()
        instalar_python()
        instalar_site()
        baixar_mysql()
        preparar_banco()
        gravar_config()
    except subprocess.CalledProcessError as erro:
        parar(f"o comando falhou: {' '.join(map(str, erro.cmd))}\n{erro.stderr or ''}")
    except OSError as erro:
        parar(str(erro))
    print("\nInstalação concluída. Próximo passo: cadastrar o primeiro administrador (veja o README).")
