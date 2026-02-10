"""
Utilitários de segurança para autenticação e hashing de senhas
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import bcrypt as bcrypt_lib
from app.core.config import settings


# Configuração do contexto de criptografia
# Usar bcrypt em produção, mas plaintext para testes
import os

if os.getenv("TESTING"):
    pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
else:
    pwd_context = CryptContext(
        schemes=["argon2"],
        deprecated="auto",
        # bcrypt__default_rounds=12,
        # bcrypt__ident="2b"  # Usar versão mais recente do bcrypt
    )



def hash_password(password: str) -> str:
    """
    Hash uma senha usando bcrypt
    
    Args:
        password: Senha em texto plano
        
    Returns:
        Senha criptografada
    """
    # bcrypt limita a 72 bytes, truncar se necessário
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
    
    # Gerar salt e hash
    salt = bcrypt_lib.gensalt(rounds=12)
    hashed = bcrypt_lib.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica se a senha em texto plano corresponde ao hash
    
    Args:
        plain_password: Senha em texto plano
        hashed_password: Senha criptografada
        
    Returns:
        True se as senhas correspondem, False caso contrário
    """
    # Garantir comportamento consistente com `hash_password`:
    # bcrypt tem limite de 72 bytes — truncar antes de verificar.
    plain_bytes = plain_password.encode("utf-8")
    if len(plain_bytes) > 72:
        plain_bytes = plain_bytes[:72]
    
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt_lib.checkpw(plain_bytes, hashed_bytes)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Cria um JWT token de acesso
    
    Args:
        data: Dados a serem inclusos no token
        expires_delta: Tempo de expiração do token
        
    Returns:
        JWT token codificado
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    
    return encoded_jwt


def decode_token(token: str) -> Optional[dict]:
    """
    Decodifica um JWT token
    
    Args:
        token: JWT token
        
    Returns:
        Dados decodificados ou None se inválido
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        return None
