# 💡 IluminaAê — Sistema de Gestão de Iluminação Pública

![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=black)
![Vite](https://img.shields.io/badge/Vite-5-646CFF?logo=vite&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?logo=sqlite&logoColor=white)

**Plataforma para registro, acompanhamento e gerenciamento de ocorrências de iluminação pública.**

O **IluminaAê** é um sistema web desenvolvido para facilitar a comunicação entre cidadãos e equipes responsáveis pela manutenção da iluminação pública.

A solução permite que moradores registrem problemas em postes, acompanhem o andamento das solicitações e visualizem atualizações. Paralelamente, uma interface administrativa oferece ferramentas para monitoramento, priorização e gerenciamento dos chamados.

O projeto utiliza uma arquitetura com **API REST em Python/FastAPI**, interfaces desenvolvidas em **React** e armazenamento de dados em **SQLite**.

> **Nota:** Projeto acadêmico demonstrativo, inspirado em necessidades de cidades como Recife (PE), sem vínculo oficial com a Prefeitura do Recife.

---

## 🚀 Funcionalidades

### 👤 Portal do cidadão

- Cadastro e autenticação de usuários.
- Registro de problemas na iluminação pública, em quatro etapas: local, problema, foto e revisão.
- Seleção de postes no mapa interativo, com busca por código ou rua.
- Classificação do tipo de problema, com **mais de uma opção** por chamado.
- Envio de até duas fotografias por chamado.
- Consulta e acompanhamento das solicitações, com número de protocolo.
- Visualização do histórico e do status dos chamados: *Recebido*, *Equipe a caminho* e *Resolvido*.
- Atualização de informações pessoais, endereço (com preenchimento automático pelo CEP) e senha.
- Exclusão da conta, com anonimização dos dados pessoais (LGPD).

### 🏛️ Painel de gestão

- Visualização centralizada dos chamados cadastrados, em lista e em mapa.
- Mapa interativo com pinos coloridos por situação.
- Filtros por bairro, urgência e situação.
- Consulta de fotografias e histórico de cada ocorrência.
- Encaminhamento de equipes técnicas.
- Atualização, resolução e reabertura de chamados.
- Classificação de ocorrências por prioridade (urgência).
- Indicadores e gráficos para acompanhamento operacional.
- Atualização automática do painel a cada 15 segundos, com aviso de novos chamados.

### 📊 Indicadores e gráficos

O painel administrativo disponibiliza recursos para análise das ocorrências, incluindo:

- Taxa de resolução de chamados.
- Tempo médio de atendimento.
- Quantidade de ocorrências em aberto e há quanto tempo a mais antiga espera.
- Distribuição de chamados por situação.
- Chamados abertos e resolvidos por dia.
- Distribuição de ocorrências por bairro.
- Classificação por tipo de problema.

Os gráficos permitem escolher o período (7 dias, 30 dias ou todo o período) e clicar em um bairro ou em uma situação para ver as ocorrências no mapa. Eles são desenhados em SVG dentro do React, sem biblioteca de gráficos.

---

## 🛠️ Tecnologias utilizadas

### Back-end

| Tecnologia | Aplicação |
|---|---|
| Python 3.11+ | Linguagem de programação |
| FastAPI | Desenvolvimento da API REST e documentação automática (`/docs`) |
| Uvicorn | Servidor que executa a API |
| SQLAlchemy 2 | Mapeamento objeto-relacional (ORM) |
| Pydantic | Estruturação e validação de dados |
| SQLite | Banco de dados relacional |
| PyJWT | Autenticação baseada em tokens JWT |
| bcrypt | Proteção das senhas (hash) |
| python-multipart | Recebimento de formulários e fotos |

### Front-end

| Tecnologia | Aplicação |
|---|---|
| React 18 | Desenvolvimento das interfaces |
| JavaScript (JSX) | Lógica das aplicações |
| Vite | Ferramenta de desenvolvimento e build |
| React Router | Navegação entre as telas |
| Leaflet e React-Leaflet | Mapas interativos (imagens do OpenStreetMap) |
| CSS | Estilização das interfaces, sem biblioteca de componentes |

### Serviços externos usados pelo navegador

| Serviço | Uso | Chave de API |
|---|---|---|
| OpenStreetMap | Imagens do mapa | Não precisa |
| ViaCEP | Preencher o endereço a partir do CEP | Não precisa |
| Google Fonts | Fontes do texto | Não precisa |

Esses serviços exigem internet. Sem conexão, o mapa fica cinza, mas o restante do sistema continua funcionando.

---

## 🏗️ Arquitetura do sistema

O projeto é organizado em três aplicações:

**1. API (Back-end)**

Desenvolvida em Python com FastAPI, responsável por receber requisições HTTP, validar dados, aplicar regras de negócio, realizar autenticação e acessar o banco de dados.(ainda sem algumas validacoes eficientes. EX: CPF que apenas retira espaços e verifica se possui 11 digitos)

**2. Portal do cidadão**

Aplicação React responsável pela interação com o usuário, incluindo cadastro, abertura e acompanhamento dos chamados.

**3. Painel da prefeitura**

Aplicação React destinada à gestão das solicitações, com recursos de visualização geográfica, gráficos e atualização das ocorrências.

### Fluxo de comunicação

**Cidadão / Equipe técnica → Interfaces React → Requisições HTTP/JSON → FastAPI → SQLAlchemy → SQLite**

As respostas da API retornam às interfaces para apresentação das informações.

```text
 FRONT-END (React)                 BACKEND (FastAPI)                      DADOS
+--------------------+  HTTP   +-----------------------------+     +----------------+
| Portal do cidadão  | <-----> | Rotas (routers)             | --> | SQLite         |
| porta 5173         |  JSON   |   Segurança (deps, token)   |     | ilumina.db     |
+--------------------+         |   Validação (schemas)       |     +----------------+
| Painel prefeitura  | <-----> |   Dados (models, ORM)       | --> | pasta uploads  |
| porta 5174         |         | porta 8000                  |     | (fotos)        |
+--------------------+         +-----------------------------+     +----------------+
```

### Perfis de acesso

| Perfil | Como é criado | Onde entra | O que pode fazer |
|---|---|---|---|
| Cidadão | Cadastro pelo próprio portal | Portal do cidadão (5173) | Abrir e acompanhar os próprios chamados |
| Equipe técnica | Script `seed.py` (não há cadastro público) | Painel da prefeitura (5174) | Ver todos os chamados e alterar situação e urgência |

A permissão é conferida **no servidor**, em cada rota. Um cidadão que tente chamar uma rota do painel recebe o erro 403.

### Organização do repositório

```text
PROJETO-ILUMINAAE/
│
├── backend/
│   ├── app/
│   │   ├── routers/
│   │   │   ├── auth.py          cadastro, login, perfil
│   │   │   ├── chamados.py      abrir e consultar chamados
│   │   │   ├── painel.py        chamados e ações da equipe
│   │   │   ├── postes.py        postes para o mapa
│   │   │   └── usuarios.py      dados, endereço, senha e exclusão
│   │   ├── database.py          conexão com o SQLite
│   │   ├── deps.py              usuário logado e acesso só da equipe
│   │   ├── main.py              criação do app, CORS e rotas
│   │   ├── models.py            tabelas do banco (SQLAlchemy)
│   │   ├── schemas.py           validação de entrada e saída (Pydantic)
│   │   └── security.py          hash de senha e token JWT
│   ├── apagar_chamado.py        utilitário para apagar chamados sem deixar sobras
│   ├── requirements.txt
│   ├── seed.py                  recria o banco com dados de demonstração
│   └── seed_extra.py            acrescenta chamados para os gráficos
│
├── web-cidadao/
│   ├── src/
│   │   ├── components/          mapa, layout, cartão de chamado, ícones
│   │   ├── pages/               telas do portal
│   │   ├── api.js               único arquivo que fala com o backend
│   │   ├── auth.jsx             estado de login
│   │   └── util.js
│   ├── .env.example
│   ├── package.json
│   └── vite.config.js
│
├── web-prefeitura/
│   ├── src/
│   │   ├── components/          mapa, gráficos, ícones
│   │   ├── pages/               login e painel
│   │   ├── api.js
│   │   ├── auth.jsx
│   │   └── util.js
│   ├── .env.example
│   ├── package.json
│   └── vite.config.js
│
├── .gitignore
├── .gitattributes
├── iniciar.bat                  liga tudo no Windows com dois cliques
└── README.md
```

---

## ⚙️ Instalação e execução

Este guia foi escrito para **Windows**. No fim da seção há as diferenças para macOS e Linux.

### 1. Pré-requisitos

| Programa | Versão | Onde baixar | Observação |
|---|---|---|---|
| Python | 3.11 ou superior | python.org/downloads | Na primeira tela do instalador, **marque *Add python.exe to PATH*** |
| Node.js | versão LTS | nodejs.org | Instalação padrão (já inclui o npm) |
| Git | qualquer versão recente | git-scm.com | Instalação padrão |

Depois de instalar, **feche e abra o PowerShell** e confira:

```powershell
py --version
node --version
npm --version
git --version
```

Os quatro comandos precisam mostrar um número de versão.

> **Dica:** não coloque o projeto numa pasta sincronizada pelo OneDrive. A sincronização pode travar o arquivo do banco de dados. Prefira algo como `C:\PROJETO-ILUMINAAE`.

### 2. Obter o projeto

```bash
git clone https://github.com/Lucastkx/PROJETO-ILUMINAAE.git
cd PROJETO-ILUMINAAE
```

Se você recebeu o projeto em um arquivo `.zip`, extraia-o e abra o PowerShell dentro da pasta. Dica: no Explorador de Arquivos, clique na barra de endereço, digite `powershell` e aperte Enter.

O sistema precisa de **três janelas do PowerShell abertas ao mesmo tempo**, uma para cada parte (a API e as duas interfaces).

### 3. Janela 1: o servidor (back-end)

```powershell
cd backend
py -m venv .venv
.venv\Scripts\activate
```

Depois do `activate`, o começo da linha deve mostrar **`(.venv)`**. Se não aparecer, o ambiente não foi ativado e o próximo passo vai falhar.

> Se o PowerShell reclamar que a execução de scripts está desabilitada, rode uma vez `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`, responda `S` e tente o `activate` de novo.

Instale as bibliotecas:

```powershell
pip install -r requirements.txt
```

Crie o banco com os dados de demonstração:

```powershell
python seed.py
python seed_extra.py
```

| Comando | O que faz |
|---|---|
| `python seed.py` | Cria o banco `ilumina.db` com as duas contas de demonstração, 5 postes e 3 chamados. **Apaga tudo o que já existia no banco** |
| `python seed_extra.py` | Acrescenta 5 postes e 28 chamados fictícios dos últimos dias, para os **gráficos** ficarem cheios ou mais intuitivo. Rode **depois** do `seed.py`, uma vez |

> **Atenção:** o `seed.py` apaga o banco inteiro. Use apenas em ambiente de testes.

Inicie o servidor:

```powershell
uvicorn app.main:app --reload
```

Você deve ver `Uvicorn running on http://127.0.0.1:8000` e `Application startup complete`. **Deixe esta janela aberta.**

Para conferir, abra http://localhost:8000/docs no navegador. Se aparecer a documentação da API, o servidor está funcionando.

### 4. Janela 2: o portal do cidadão

Abra **outro** PowerShell na pasta principal do projeto:

```powershell
cd web-cidadao
npm install
npm run dev
```

O primeiro `npm install` demora um pouco. Ao final, o terminal mostra `Local: http://localhost:5173/`. Acesse esse endereço.

### 5. Janela 3: o painel da prefeitura

Abra **mais um** PowerShell na pasta principal:

```powershell
cd web-prefeitura
npm install
npm run dev
```

Acesse http://localhost:5174.

### 6. Resumo dos endereços

| O que | Endereço |
|---|---|
| Portal do cidadão | http://localhost:5173 |
| Painel da prefeitura | http://localhost:5174 |
| API | http://localhost:8000 |
| Documentação interativa da API | http://localhost:8000/docs |

### 7. Nas próximas vezes

Não é preciso instalar nada de novo. Basta ligar as três partes.

**Opção 1: com dois cliques.** Dê dois cliques no arquivo **`iniciar.bat`**. Ele abre as três janelas e as duas páginas no navegador. Para desligar, feche as três janelas pretas.

**Opção 2: manualmente**, uma janela para cada comando:

```powershell
# Janela 1
cd backend
.venv\Scripts\activate
uvicorn app.main:app --reload

# Janela 2
cd web-cidadao
npm run dev

# Janela 3
cd web-prefeitura
npm run dev
```

### 8. macOS e Linux

Os passos são os mesmos. Mudam apenas os comandos do ambiente virtual do back-end:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

O `iniciar.bat` só funciona no Windows. No macOS e no Linux, use as três janelas manuais.




## 🔐 Contas de demonstração

O sistema possui contas fictícias para testar as funcionalidades.

| Perfil | Login (CPF ou e-mail) | Senha | Onde entra |
|---|---|---|---|
| Cidadão | `12345678909` ou `nariga@exemplo.com` | `123456` | http://localhost:5173 |
| Equipe técnica | `11111111111` ou `equipe@recife.pe.gov.br` | `admin123` | http://localhost:5174 |

Esses usuários são criados localmente pelo script `seed.py`. O CPF pode ser digitado com ou sem pontos e traço.

Cada perfil só entra no seu endereço: se você tentar entrar no painel com a conta de cidadão, o sistema avisa que o acesso é restrito à equipe técnica.

As credenciais apresentadas são destinadas exclusivamente a demonstrações e não devem ser utilizadas em produção.


---

## 🧭 Como usar o sistema

### Portal do cidadão

1. **Criar conta:** na tela de entrada, toque em *Criar cadastro* e preencha nome, CPF, e-mail e senha (mínimo de 6 caracteres). Você entra automaticamente.
2. **Tela inicial:** mostra o mapa com os postes, a legenda das cores e o cartão *Seus chamados em aberto*.
3. **Abrir um chamado**, tocando no botão **+**:
   - **Etapa 1, local:** busque o poste pelo código ou pela rua, ou toque no pino dele no mapa. Se não achar, informe o endereço manualmente.
   - **Etapa 2, problema:** marque todas as opções que se aplicam e responda se o poste tem lâmpada e se a rua está sem energia.
   - **Etapa 3, foto:** opcional, até duas fotos nos formatos JPG, PNG ou WEBP.
   - **Etapa 4, revisão:** confira, escreva observações (até 500 caracteres) e envie. Guarde o número do protocolo.
4. **Acompanhar:** em *Meus chamados* há as abas *Todos*, *Em aberto* e *Resolvidos*. Toque em um chamado para ver o andamento e o histórico.
5. **Configurações:** em *Perfil* é possível editar dados pessoais, endereço e senha, sair, ou excluir a conta.

### Painel da prefeitura

1. **Entrar** com a conta da equipe técnica.
2. **Mapa e lista:** a faixa do topo mostra os números gerais. Use os filtros de situação, bairro e *Só urgentes*. Clique em um chamado (na lista ou no pino) para ver os detalhes e as fotos.
3. **Atender um chamado:** *Enviar equipe*, depois *Finalizar chamado*. Chamados resolvidos podem ser reabertos. Em chamados abertos é possível *Marcar como urgente*.
4. **Gráficos:** na aba *Gráficos*, escolha o período e explore os indicadores. Clicar em um bairro ou situação leva ao mapa já filtrado.
5. **Chamados novos** aparecem sozinhos em até 15 segundos, com um aviso no topo.

---

## 🧪 Roteiro de demonstração

Para conhecer o funcionamento do sistema (cerca de 5 minutos):

1. Acesse o painel administrativo e entre como equipe técnica.
2. Visualize as ocorrências no mapa e consulte os gráficos.
3. Abra o portal do cidadão e autentique-se.
4. Registre uma ocorrência, selecionando o poste, um ou mais problemas e uma fotografia.
5. Retorne ao painel administrativo: em até 15 segundos o novo chamado é anunciado.
6. Encaminhe a ocorrência para atendimento (*Enviar equipe*) e atualize seu status.
7. No portal do cidadão, confira o andamento da solicitação em **Meus chamados**.
8. **Persistência dos dados:** saia da conta e entre de novo nos dois lados. O chamado e o status continuam lá, porque estão gravados no banco. Para provar, pare o servidor com `Ctrl+C`, suba-o de novo e atualize as telas.

Esse fluxo demonstra a integração entre as duas interfaces, a API e o banco de dados.

---

## 🔌 Principais endpoints da API

A documentação interativa completa pode ser consultada em `/docs` com o servidor em execução. Todas as rotas, exceto as marcadas como públicas, exigem o cabeçalho `Authorization: Bearer <token>`.

### Autenticação

| Método | Endpoint | Descrição | Acesso |
|---|---|---|---|
| POST | `/auth/cadastro` | Cadastro de usuários (sempre cria cidadão) | Público |
| POST | `/auth/login` | Autenticação por CPF ou e-mail e senha | Público |
| GET | `/auth/me` | Dados do usuário autenticado | Logado |
| POST | `/auth/esqueci-senha` | Recuperação de senha (apenas demonstrativa) | Público |

### Postes e chamados

| Método | Endpoint | Descrição |
|---|---|---|
| GET | `/postes` | Listagem de postes |
| GET | `/postes/{codigo}` | Consulta de um poste |
| POST | `/chamados` | Abertura de chamado, com até 2 fotos |
| GET | `/chamados/meus` | Chamados do usuário logado |
| GET | `/chamados/{id}` | Detalhes de um chamado do próprio usuário |

### Gestão administrativa (apenas equipe técnica)

| Método | Endpoint | Descrição |
|---|---|---|
| GET | `/painel/chamados` | Consulta de ocorrências, com filtros |
| GET | `/painel/chamados/{id}` | Detalhes da ocorrência |
| PATCH | `/painel/chamados/{id}` | Atualização de situação e urgência |
| GET | `/painel/resumo` | Indicadores administrativos |

### Dados do usuário

| Método | Endpoint | Descrição |
|---|---|---|
| PUT | `/usuarios/me/dados` | Atualização cadastral |
| PUT | `/usuarios/me/endereco` | Alteração de endereço |
| PUT | `/usuarios/me/senha` | Alteração de senha |
| DELETE | `/usuarios/me` | Exclusão da conta (anonimização) |

---

## 🔧 Configuração do ambiente

| Item | Padrão | Como alterar |
|---|---|---|
| Endereço da API nas interfaces (`VITE_API_URL`) | `http://localhost:8000` | Copie `.env.example` para `.env` em cada front-end e ajuste o valor |
| Chave dos tokens JWT (`SECRET_KEY`) | valor de demonstração | Variável de ambiente, definida antes de subir o servidor |
| Banco de dados | SQLite em `backend/ilumina.db` | Constante `DATABASE_URL` em `backend/app/database.py` |
| Origens liberadas (CORS) | `localhost` e `127.0.0.1`, portas 5173 e 5174 | Lista `allow_origins` em `backend/app/main.py` |
| Portas | 8000, 5173 e 5174 | Opção `--port` do `uvicorn` e `vite.config.js` |

**Definindo uma chave secreta própria** (recomendado fora da demonstração):

```powershell
# Gera uma chave aleatória
python -c "import secrets; print(secrets.token_urlsafe(48))"

# Define a chave no PowerShell, antes de subir o servidor
$env:SECRET_KEY="cole-a-chave-gerada-aqui"
uvicorn app.main:app --reload
```

No Linux ou macOS, use `export SECRET_KEY="..."`.

**Apontando o front-end para outra API:**

```powershell
cd web-cidadao
copy .env.example .env
# edite o .env e ajuste a linha VITE_API_URL=...
```

Uma futura migração para PostgreSQL exigirá a troca da `DATABASE_URL`, a instalação do driver adequado e a validação da compatibilidade da aplicação.

---

## 🗄️ Banco de dados

O banco é o arquivo **`backend/ilumina.db`** (SQLite). As tabelas são criadas automaticamente quando a API sobe, a partir das classes do `models.py`.

| Tabela | O que guarda |
|---|---|
| `usuarios` | Cidadãos e equipe técnica (a senha é guardada só como hash) |
| `postes` | Código, rua, bairro e posição no mapa |
| `chamados` | Cada ocorrência: local, tipos de problema, situação, urgência e datas |
| `fotos_chamado` | O caminho das fotos de cada chamado |
| `historico_status` | Uma linha a cada mudança de situação, para o acompanhamento |

As **fotos** ficam na pasta `backend/uploads/`. O banco guarda só o caminho. Para um backup completo, copie o `ilumina.db` e a pasta `uploads` juntos.

### Conferindo o conteúdo

Use o programa gratuito **DB Browser for SQLite** (sqlitebrowser.org) e abra o `ilumina.db`, ou consulte pelo terminal, na pasta `backend` com o ambiente ativo:

```powershell
python -c "import sqlite3; c=sqlite3.connect('ilumina.db'); print(c.execute('select protocolo, status from chamados').fetchall())"
```

### Voltando aos dados de demonstração

Com o servidor parado, na pasta `backend`:

```powershell
python seed.py
python seed_extra.py
```

### Apagando chamados de teste

O utilitário `apagar_chamado.py` apaga um chamado **junto com o histórico e as fotos dele**, sem deixar sobras no banco:

```powershell
python apagar_chamado.py              # lista os chamados e os totais
python apagar_chamado.py 5            # apaga o chamado de id 5 (pergunta antes)
python apagar_chamado.py 5 6 10       # apaga vários
python apagar_chamado.py --limpar     # remove sobras de apagamentos feitos por outros meios
```

> Evite apagar linhas diretamente no banco: o SQLite não impede deixar registros soltos, e o número de um chamado apagado pode ser reaproveitado, fazendo o histórico antigo aparecer no chamado novo.

---

## 🩺 Solução de problemas

| Sintoma | Causa provável | Solução |
|---|---|---|
| `py` ou `python` não é reconhecido | Python instalado sem o PATH | Reinstale marcando *Add python.exe to PATH* e abra um PowerShell novo |
| `npm` não é reconhecido | Node recém-instalado | Feche e abra o PowerShell; se persistir, reinicie o computador |
| O `activate` é bloqueado | Política de scripts do Windows | `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` e responda `S` |
| Erro pedindo `python-multipart` | O ambiente virtual não está ativo | Rode `.venv\Scripts\activate` e `pip install -r requirements.txt` |
| "Não foi possível conectar ao servidor" | O back-end não está rodando | Confira a janela 1 e suba com `uvicorn app.main:app --reload` |
| Não loga com o CPF | O banco não foi criado ou foi criado em outra pasta | Pare o servidor, rode `python seed.py` **dentro de `backend`** e suba de novo |
| Gráficos vazios | Faltam os dados de demonstração | Rode `python seed_extra.py` depois do `seed.py` |
| Mapa cinza | Sem internet para baixar as imagens do mapa | Conecte-se à internet e atualize a página |
| Porta em uso (5173, 5174 ou 8000) | Outra janela ou programa usa a porta | Feche as janelas antigas e tente de novo |
| Tela branca | Erro de JavaScript no front-end | Aperte F12, abra a aba *Console* e leia a primeira linha vermelha. Tente `Ctrl+F5` |
| Erro 500 ou `Traceback` no terminal | Exceção no Python | Leia a última linha do terminal da API, que diz o arquivo e o erro. Se for um `AttributeError` em `models`, o `models.py` está incompleto ou desatualizado: restaure a versão do Git |
| `database is locked` | Outro programa está com o `ilumina.db` aberto, ou o OneDrive está sincronizando | Feche o DB Browser (ou grave e feche as alterações) e mantenha o projeto fora do OneDrive |
| O `seed.py` não consegue apagar o banco | O servidor ainda está rodando | Pare o servidor com `Ctrl+C` antes de rodar o seed |

---


### O que já existe

- Senhas guardadas apenas como hash (bcrypt).
- Sessão por token JWT com validade de 12 horas.
- Permissões conferidas no servidor, a cada pedido, pelo perfil e pelo dono do dado.
- Um cidadão só enxerga os próprios chamados.
- Validação de entrada com Pydantic e acesso ao banco por ORM, sem SQL montado à mão.
- CORS restrito aos endereços das interfaces.
- Exclusão de conta com anonimização dos dados pessoais.

### Pontos de atenção

- Utilização de uma `SECRET_KEY` própria e segura (o valor padrão é só de demonstração).
- Configuração de HTTPS.
- Limitação de tentativas de autenticação.
- Reforço das validações e restrições dos uploads de imagens (tipo real do arquivo, tamanho e remoção de metadados).
- Fotos servidas apenas a usuários autorizados.
- Recuperação de senha por e-mail (hoje é apenas demonstrativa).
- Configuração de um banco de dados adequado para produção.
- Revisão das políticas de armazenamento e proteção de dados pessoais.
- Testes automatizados.

Os arquivos de ambiente, bancos locais, fotos enviadas e outros arquivos sensíveis são excluídos do versionamento por meio do `.gitignore`.

---

## 🗺️ Próximos passos

- Recuperação de senha por e-mail.
- Migração para PostgreSQL e uso de HTTPS.
- Detecção de chamados duplicados no mesmo poste.
- Notificações ao cidadão quando o status mudar.
- Relatórios exportáveis (CSV e impressão em PDF) no painel.
- Integração com sensores de iluminação (IoT).
- Testes automatizados.



## 📌 Sobre o projeto

O **IluminaAê** foi desenvolvido como projeto acadêmico para aplicar conceitos de engenharia de software e desenvolvimento de aplicações web.

O desenvolvimento contempla a criação de uma API REST, modelagem de banco de dados, autenticação e autorização, validação de informações, integração entre front-end e back-end e apresentação de dados por meio de mapas e gráficos.

O objetivo é demonstrar uma solução tecnológica para um problema real de gestão urbana, integrando diferentes ferramentas e conceitos em um sistema funcional.

---
