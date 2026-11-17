import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from . import models
from .database import get_db
from .security import ler_token 

oauth2 = OAuth2PasswordBearer(tokenUrl="auth/login")


# 1. Recebe o token JWT através do Depends(oauth2).
# 2. Valida e decodifica o token.
# 3. Extrai o ID do usuário presente no payload (sub).
# 4. Consulta o banco de dados para verificar se o usuário existe.
# 5. Verifica se o usuário está ativo.
# 6. Trata possíveis erros de autenticação, retornando HTTP 401.
# 7. Retorna o objeto do usuário caso todas as verificações sejam aprovadas.
def usuario_atual(token: str = Depends(oauth2), db: Session = Depends(get_db)) -> models.Usuario:
    erro = HTTPException(status.HTTP_401_UNAUTHORIZED, "Token inválido ou expirado")
    try:
        dados = ler_token(token)
    except jwt.PyJWTError:
        raise erro
    usuario = db.get(models.Usuario, int(dados["sub"]))# AINDA NÃO ENTENDI ESSA LINHA, MAS ACHO QUE É PARA PEGAR O ID DO USUARIO E VERIFICAR SE ELE EXISTE NO BANCO DE DADOS(PESQUISAR DEPOIS)
    if not usuario or not usuario.ativo:
        raise erro
    return usuario


# 1. Recebe o usuário autenticado através do Depends(usuario_atual).
# 2. Verifica o perfil cadastrado para o usuário.
# 3. Compara o perfil com "equipe_tecnica".
# 4. Caso o perfil seja diferente, bloqueia o acesso e retorna HTTP 403 
# 5. Caso o perfil seja permitido, retorna o objeto do usuário.
#TRATAMNETIO PARA VERIFICAR O TIPO DE USUARIO 
def so_equipe(usuario: models.Usuario = Depends(usuario_atual)) -> models.Usuario:# vai na minha classe usuario e verifica se o usuario tem o perfil de equipe tecnica, caso nao tenha, ele retorna um erro de acesso negado
    if usuario.perfil != "equipe_tecnica":
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Acesso restrito à equipe técnica")
    return usuario
