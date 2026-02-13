from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import jwt, JWTError
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
    
    logger.info(f"🔍 Token recebido: {token[:20]}...")  # Log apenas início do token
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Decodifica o token
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        
        logger.info(f"✅ Payload decodificado: {payload}")
        
        # Extrai o user_id
        user_id = payload.get("sub")
        
        if user_id is None:
            logger.error("❌ 'sub' não encontrado no payload")
            raise credentials_exception
        
        logger.info(f"📋 user_id extraído: {user_id} (tipo: {type(user_id)})")
        
        # Converte para int
        user_id = int(user_id)
        logger.info(f"✅ user_id convertido para int: {user_id}")
        
    except JWTError as e:
        logger.error(f"❌ Erro JWT: {str(e)}")
        raise credentials_exception
    except ValueError as e:
        logger.error(f"❌ Erro ao converter user_id: {str(e)}")
        raise credentials_exception
    except Exception as e:
        logger.error(f"❌ Erro inesperado: {str(e)}")
        raise credentials_exception

    # Busca o usuário
    user = UserService.get_user_by_id(db, user_id=user_id)
    
    if user is None:
        logger.error(f"❌ Usuário {user_id} não encontrado no banco")
        raise credentials_exception

    logger.info(f"✅ Usuário encontrado: {user.email} (ativo: {user.is_active})")

    if not user.is_active:
        logger.warning(f"⚠️ Usuário {user.email} está inativo")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuário inativo"
        )

    logger.info(f"🎉 Autenticação bem-sucedida para {user.email}")
    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    return current_user