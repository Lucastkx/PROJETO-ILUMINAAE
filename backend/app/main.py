from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .database import Base, engine
from .routers import auth, chamados, painel, postes, usuarios


Base.metadata.create_all(bind=engine)  # cria as tabelas no SQLite se não existirem
Path("uploads").mkdir(exist_ok=True)# cria o diretorio destinado ao armazenamento de arquivos, com tratamento de erro caso a pasta ja exista

app = FastAPI(title="IluminaAê API", version="0.1.0")#inicia minha aplicacao principal definindo o nomd e verssso

# 5173 = web-cidadao, 5174 = web-prefeitura (portas do Vite)
app.add_middleware(#configira o cors permitidno a conexao entre os front ends autotizados e o backend
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173", "http://localhost:5174",
        "http://127.0.0.1:5173", "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")# disponibiliza os arquivos enviados na pasta uploads tambem por uma url

for r in (auth, usuarios, postes, chamados, painel):#regista os grupos ded rotas(routes) n aaplicacao principal, porganizar as funcionalidades em diferentes modulos
    app.include_router(r.router)


@app.get("/", tags=["Saúde"])# Cria a rota raiz da API, retornando informações básicas
def raiz():
    return {"app": "IluminaAê", "docs": "/docs"}
