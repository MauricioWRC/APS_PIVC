# IRIS — APS PIVC

Sistema de acesso por reconhecimento facial para uma empresa química.
Site em React, API em Python (FastAPI + OpenCV) e banco MySQL.

## O que instalar

| Programa | Versão | Onde baixar |
|---|---|---|
| Python | 3.11 a 3.13 (marque "Add python.exe to PATH" na instalação) | https://www.python.org/downloads/ |
| Node.js | 20 ou mais novo (versão LTS) | https://nodejs.org/ |

O MySQL não precisa ser instalado: o instalador baixa uma versão própria. Também é preciso uma webcam.

## Instalação (uma vez)

**1. Rode o `instalar.bat`** (dois cliques). Ele instala as dependências do Python e do site, baixa os
modelos de reconhecimento e um MySQL próprio em `C:\iris-mysql` (porta 3307) e cria o banco com os dados
de exemplo. Leva alguns minutos e baixa cerca de 300 MB. Se der erro no meio, corrija o que a mensagem
pedir e rode de novo: o que já foi feito é pulado.

**2. Cadastre o primeiro administrador.** Ninguém entra sem rosto cadastrado, então o primeiro é pela
linha de comando. Coloque de 3 a 5 fotos suas na pasta `dados` (de frente, com boa luz, só você na foto)
e, no cmd, dentro da pasta do projeto:

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
| Instalador: "Node.js não encontrado" ou "Falta o Visual C++" | Instale pelo link que a mensagem mostra e rode o `instalar.bat` de novo. |
| `Baixe o modelo: python alinhado.py baixar-modelo` | Faltam os modelos: rode o `instalar.bat` de novo. |
| `Can't connect to MySQL server` (erro 2003) | O MySQL não ligou. Abra o projeto pelo `iniciar.bat`, que liga o MySQL antes da API. |
| `Access denied for user 'root'` (erro 1045) | Senha errada no `config-local.bat` (só acontece usando outro MySQL; veja abaixo). |
| O site abriu na porta 5174 | Já tem outro site aberto. Feche as janelas antigas do `npm run dev` e abra de novo. |
| A câmera não abre | Use `http://localhost:5173` (não o IP) e permita a câmera no cadeado da barra de endereço. |
| Clico em entrar e nada acontece | Capture a imagem antes de clicar em **Entrar com o rosto**. |
| Aparece "Modo demonstração" | Falta o `frontend\.env` do passo 2. Depois de criar, reinicie o site. |
| Rosto não reconhecido | Fique de frente e com boa luz. Se continuar, cadastre mais fotos em *Cadastro facial*. |

## Usar um MySQL que já está instalado

Se preferir o MySQL do seu computador (8.0 ou mais novo), importe o banco, informando a porta e a senha
do root dele:

```bat
"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" -u root -p -P 3306 --default-character-set=utf8mb4 < "sistema biometria APS.sql"
"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" -u root -p -P 3306 --default-character-set=utf8mb4 < migracao_empresa_quimica.sql
```

Depois copie `config-local.exemplo.bat` para `config-local.bat` e coloque a porta e a senha. Nesse caso,
o MySQL precisa estar ligado (em `services.msc`) antes do `iniciar.bat`.

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
