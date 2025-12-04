from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import Optional

from app.db import get_db
from app.core.security import decode_token
from app.services import UserService
from app.schemas import TokenData 
from app.models import User 

# Define o esquema OAuth2. O token é esperado no cabeçalho Authorization: Bearer <token>
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    """
    Dependência FastAPI para obter o usuário atualmente autenticado a partir do JWT.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # 1. Decodificar o Token
    payload = decode_token(token)
    
    if payload is None:
        raise credentials_exception
        
    # 2. Obter o email (subject 'sub') do payload
    try:
        token_data = TokenData(**payload)
        email = token_data.sub
    except Exception:
        # Se o payload não corresponder ao schema TokenData
        raise credentials_exception

    if email is None:
        raise credentials_exception
    
    # 3. Buscar o usuário no banco de dados
    user = UserService.get_user_by_email(db, email=email)
    
    if user is None:
        raise credentials_exception
        
    # 4. Verificar se o usuário está ativo
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuário inativo"
        )
        
    return user


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Dependência que garante que o usuário não só está logado, mas também está ativo.
    (Redundante com a lógica acima, mas útil para clareza e futuro)
    """
    return current_user