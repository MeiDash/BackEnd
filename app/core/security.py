"""
Utilitários de segurança para autenticação e hashing de senhas
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings

# Configuração do contexto de criptografia
import os
if os.getenv("TESTING"):
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
else:
    pwd_context = CryptContext(
        schemes=["bcrypt"],
        deprecated="auto"
    )


def hash_password(password: str) -> str:
    """
    Hash uma senha usando bcrypt
    
    Args:
        password: Senha em texto plano
        
    Returns:
        Senha criptografada
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica se a senha em texto plano corresponde ao hash
    
    Args:
        plain_password: Senha em texto plano
        hashed_password: Senha criptografada
        
    Returns:
        True se as senhas correspondem, False caso contrário
    """
    try:
        print(f"🔐 verify_password: comparando senhas")
        print(f"   Hash esperado: {hashed_password[:50]}...")
        result = pwd_context.verify(plain_password, hashed_password)
        print(f"🔐 verify_password: resultado = {result}")
        return result
    except Exception as e:
        print(f"❌ verify_password: ERRO durante verificação: {type(e).__name__}: {e}")
        return False


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
    except JWTError as e:
        print("ERRO AO DECODIFICAR TOKEN:", e)
        return None