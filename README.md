# IluminaAê

Sistema de chamados de iluminação pública para Recife. O cidadão avisa que um poste está apagado ou danificado e acompanha o conserto. A equipe técnica da prefeitura atende os chamados em um painel com mapa e gráficos.

**Tecnologias:** FastAPI (Python) · SQLite · React + Vite · Leaflet (mapa)

```
PROJETO_ILUMINAAEE/
├── backend/          API FastAPI + banco SQLite   → http://localhost:8000  (docs em /docs)
├── web-cidadao/      App do cidadão (React)       → http://localhost:5173
├── web-prefeitura/   Painel da prefeitura (React) → http://localhost:5174
├── iniciar.bat       Liga tudo com dois cliques (Windows)
└── README.md
```

## Logins de demonstração

| Perfil | Login (CPF ou e-mail) | Senha | Onde entra |
|---|---|---|---|
| Cidadão | `12345678909` ou `nariga@exemplo.com` | `123456` | http://localhost:5173 |
| Equipe técnica | `11111111111` ou `equipe@recife.pe.gov.br` | `admin123` | http://localhost:5174 |

São contas fictícias, criadas só no seu computador pelo `seed.py`.

## Instalação (uma vez só)

**Precisa instalar:** Python 3.11 ou mais novo (marque *Add python.exe to PATH*) e Node.js LTS.

**Janela 1: servidor (backend)**

```
cd backend
py -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python seed.py
python seed_extra.py
uvicorn app.main:app --reload
```

- Depois do `activate`, o começo da linha deve mostrar `(.venv)`.
- `python seed.py` cria o banco com as contas e dados básicos. **Apaga tudo o que já existia.**
- `python seed_extra.py` acrescenta 28 chamados de demonstração para os **gráficos** ficarem cheios. Rode depois do `seed.py`, uma vez.
- Para conferir, abra http://localhost:8000/docs.

**Janela 2: app do cidadão**

```
cd web-cidadao
npm install
npm run dev
```

**Janela 3: painel da prefeitura**

```
cd web-prefeitura
npm install
npm run dev
```

No macOS ou Linux, troque a ativação do ambiente por `source .venv/bin/activate`.

## Nas próximas vezes

Depois da instalação, dê dois cliques no **`iniciar.bat`**: ele abre as três janelas e as duas páginas no navegador. Para desligar, feche as três janelas pretas.

Ou, manualmente, em cada janela: `cd backend` e `.venv\Scripts\activate` e `uvicorn app.main:app --reload`; `cd web-cidadao` e `npm run dev`; `cd web-prefeitura` e `npm run dev`.

## O que o painel da prefeitura tem

- **Mapa e lista:** pinos coloridos por situação, filtros por situação, bairro e urgência, detalhe do chamado com fotos e histórico.
- **Ações:** enviar equipe, finalizar, reabrir e marcar urgência.
- **Gráficos:** indicadores (taxa de resolução, tempo médio, em aberto), chamados por situação, abertos e resolvidos por dia, por bairro e por tipo de problema. Dá para trocar o período e clicar num bairro para ver no mapa.
- A tela se atualiza sozinha a cada 15 segundos e avisa quando chega chamado novo.

## Roteiro de demonstração (5 minutos)

1. **Painel** (5174): entre como equipe. Mostre o mapa e o chamado urgente pulsando.
2. Clique em **Gráficos** e mostre os indicadores, a rosca por situação e as barras por bairro. Clique num bairro para voltar ao mapa filtrado.
3. **App do cidadão** (5173): entre como cidadão, toque em **+**, escolha um poste, marque um ou mais problemas, adicione uma foto e envie.
4. Volte ao painel: em até 15 segundos aparece o aviso de chamado novo. Clique nele, **Enviar equipe** e depois **Finalizar chamado**.
5. No app, abra **Meus chamados**: a barra de andamento já mudou.

## Endpoints da API

**Cidadão:** `POST /auth/cadastro` · `POST /auth/login` · `GET /auth/me` · `GET /postes` · `GET /postes/{codigo}` · `POST /chamados` (até 2 fotos) · `GET /chamados/meus` · `GET /chamados/{id}` · `PUT /usuarios/me/dados` · `PUT /usuarios/me/endereco` · `PUT /usuarios/me/senha` · `DELETE /usuarios/me`

**Equipe técnica:** `GET /painel/chamados` · `GET /painel/chamados/{id}` · `PATCH /painel/chamados/{id}` · `GET /painel/resumo`

## Configuração

| Item | Padrão | Como mudar |
|---|---|---|
| Endereço da API nos fronts | `http://localhost:8000` | Copie `.env.example` para `.env` em cada front e ajuste `VITE_API_URL` |
| Chave do token (JWT) | valor de demonstração | Variável de ambiente `SECRET_KEY` antes de subir o backend |
| Banco | SQLite em `backend/ilumina.db` | `DATABASE_URL` em `backend/app/database.py` (PostgreSQL funciona trocando só isso) |

## Problemas comuns

| Sintoma | Solução |
|---|---|
| Erro pedindo `python-multipart` | O ambiente não está ativo. Rode `.venv\Scripts\activate` e `pip install -r requirements.txt` |
| Não loga com o CPF | O banco não foi recriado. Pare o servidor, rode `python seed.py` (dentro de `backend`) e suba de novo |
| Gráficos vazios | Rode `python seed_extra.py` depois do `seed.py` |
| Mapa cinza | Falta internet |
| "Não foi possível conectar ao servidor" | O backend (janela 1) não está rodando |
| Porta em uso (5173, 5174 ou 8000) | Feche janelas antigas e tente de novo |

## Aviso de segurança

Este projeto é uma demonstração. Antes de usar com dados reais, é preciso trocar a `SECRET_KEY`, usar HTTPS, limitar tentativas de login, corrigir o upload de fotos e migrar para PostgreSQL. Os pontos pendentes estão na documentação de segurança do projeto.


