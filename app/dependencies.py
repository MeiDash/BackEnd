from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import jwt, JWTError, ExpiredSignatureError
import logging

from app.db import get_db
from app.core.config import settings
from app.services import UserService
from app.schemas import TokenData
from app.models import User

# Configure logging
logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido ou expirado. Por favor, faça login novamente.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Decodifica o token
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        
        # Extrai o user_id
        user_id = payload.get("sub")
        
        if user_id is None:
            logger.warning("Token sem 'sub' no payload")
            raise credentials_exception
        
        # Converte para int
        user_id = int(user_id)
        
    except jwt.ExpiredSignatureError:
        logger.info("Token expirado recebido")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expirado. Por favor, faça login novamente.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JWTError as e:
        logger.warning(f"Erro JWT: {type(e).__name__}")
        raise credentials_exception
    except ValueError:
        logger.warning("Erro ao converter user_id para int")
        raise credentials_exception
    except Exception as e:
        logger.error(f"Erro inesperado na validação do token: {type(e).__name__}")
        raise credentials_exception

    # Busca o usuário
    try:
        user = UserService.get_user_by_id(db, user_id=user_id)
    except Exception as e:
        logger.error(f"Erro ao buscar usuário: {type(e).__name__}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao validar usuário"
        )
    
    if user is None:
        logger.warning(f"Usuário {user_id} não encontrado")
        raise credentials_exception

    if not user.is_active:
        logger.warning(f"Tentativa de acesso com usuário inativo: {user.email}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário inativo"
        )

    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    return current_user