# IRIS — APS PIVC

Sistema de acesso por reconhecimento facial para uma empresa química.
Site em React, API em Python (FastAPI + OpenCV) e banco MySQL.

## O que instalar

| Programa | Versão | Onde baixar |
|---|---|---|
| Python | 3.12 (marque "Add python.exe to PATH" na instalação) | https://www.python.org/downloads/ |
| Node.js | 20 ou mais novo (versão LTS) | https://nodejs.org/ |
| MySQL Server | 8.0 ou mais novo | https://dev.mysql.com/downloads/installer/ |

Qualquer instalação do MySQL serve. Durante a instalação, **anote a porta e a senha do root**:
elas são usadas na configuração. Também é preciso uma webcam.

## Instalação (uma vez)

Todos os comandos são no Prompt de Comando (cmd), dentro da pasta do projeto, a que tem o `api.py`.

**1. Dependências do Python e modelos de reconhecimento**

```bat
py -3.12 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m processamento_imagens preparar-modelos
```

**2. Dependências do site**

```bat
cd frontend
npm install
copy .env.example .env
cd ..
```

**3. Banco de dados**

Troque `3306` pela porta do seu MySQL e ajuste a pasta se a versão for outra. Ele pede a senha do root.

```bat
"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" -u root -p -P 3306 --default-character-set=utf8mb4 < "sistema biometria APS.sql"
"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" -u root -p -P 3306 --default-character-set=utf8mb4 < migracao_empresa_quimica.sql
```

**4. Porta e senha do MySQL**

Copie o modelo e coloque a porta e a senha do seu MySQL:

```bat
copy config-local.exemplo.bat config-local.bat
notepad config-local.bat
```

**5. Primeiro administrador**

Ninguém entra sem rosto cadastrado, então o primeiro é pela linha de comando.
Coloque de 3 a 5 fotos suas na pasta `dados` (de frente, com boa luz, só você na foto).

```bat
call config-local.bat
.venv\Scripts\python.exe api.py cadastrar-rosto --usuario 6 --admin dados\foto1.jpg dados\foto2.jpg dados\foto3.jpg
```

O usuário 6 é o "João da Silva" do banco de exemplo. Depois de entrar, troque o nome e o CPF em *Usuários*.

## Rodar

Dê dois cliques em `iniciar.bat`. Ele abre a API, o site e o navegador em http://localhost:5173.
Para desligar, feche as janelas que ele abriu.

Para entrar: **Ativar câmera** → **Capturar imagem** → **Entrar com o rosto**.
Outras pessoas são cadastradas pelo administrador em *Usuários* e *Cadastro facial*.

## Problemas comuns

| Mensagem ou sintoma | O que fazer |
|---|---|
| `Baixe o modelo: python alinhado.py baixar-modelo` | Faltam os modelos: rode o comando `preparar-modelos` do passo 1. |
| `Can't connect to MySQL server` (erro 2003) | O MySQL está desligado ou a porta está errada. Ligue o serviço em `services.msc` e confira `APS_DB_PORT` no `config-local.bat`. |
| `Access denied for user 'root'` (erro 1045) | Senha errada no `config-local.bat`. |
| `net start` responde "Acesso negado" | Abra o cmd como administrador. |
| O site abriu na porta 5174 | Já tem outro site aberto. Feche as janelas antigas do `npm run dev` e abra de novo. |
| A câmera não abre | Use `http://localhost:5173` (não o IP) e permita a câmera no cadeado da barra de endereço. |
| Clico em entrar e nada acontece | Capture a imagem antes de clicar em **Entrar com o rosto**. |
| Aparece "Modo demonstração" | Falta o `frontend\.env` do passo 2. Depois de criar, reinicie o site. |
| Rosto não reconhecido | Fique de frente e com boa luz. Se continuar, cadastre mais fotos em *Cadastro facial*. |

## Perfis

| Perfil | Nível | Vê | Aprova e exclui |
|---|---|---|---|
| Analista | 1 | Itens internos | — |
| Diretor | 2 | Internos e restritos do próprio setor | No próprio setor |
| Ministro | 3 | Tudo, inclusive fórmulas | Tudo |

Administrador é uma função à parte: cuida de usuários, setores, instalações e rostos.
As regras estão em `pode_ver`, `pode_editar` e `pode_aprovar`, no `api.py`.

## Pastas

| Pasta | Conteúdo |
|---|---|
| `api.py` | API, login pelo rosto e regras de acesso |
| `processamento_imagens/` | Captura, qualidade e alinhamento do rosto (YuNet) |
| `Reconhecimento Facial/` | Comparação dos rostos (SFace) |
| `frontend/` | Site |
| `tests/` | Testes |
| `docs/` | Requisitos da APS e relatório de testes |

## Testes

```bat
.venv\Scripts\python.exe -m unittest discover -s tests
```

Com `set APS_DB_TESTE=1` também roda o teste da API contra o MySQL, num banco temporário.
O relatório de código para o Teams sai com `.venv\Scripts\python.exe scripts\relatorio_codigo.py`.
