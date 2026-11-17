import os
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

SECRET_KEY = os.getenv("SECRET_KEY", "troque-esta-chave-em-producao")
ALGORITHM = "HS256"
TOKEN_HORAS = 12



def hash_senha(senha: str) -> str: #pega a senha informada e transforma em rash antes de enviar ao banco de dados
    return bcrypt.hashpw(senha.encode(), bcrypt.gensalt()).decode()#Gera o hash da senha.


def verificar_senha(senha: str, hash_: str) -> bool:#verifica a senha informada com a senha armazenada no banco de dados
    return bcrypt.checkpw(senha.encode(), hash_.encode())


def criar_token(usuario_id: int, perfil: str) -> str:
    exp = datetime.now(timezone.utc) + timedelta(hours=TOKEN_HORAS)
    return jwt.encode(
        {"sub": str(usuario_id), "perfil": perfil, "exp": exp}, SECRET_KEY, algorithm=ALGORITHM
    )


def ler_token(token: str) -> dict:
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
