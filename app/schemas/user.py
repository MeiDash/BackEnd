"""
Schemas (Pydantic models) para validação de dados de usuário — adaptados ao novo esquema oficial
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """Schema base de usuário"""
    email: EmailStr = Field(..., description="Email do usuário")
    name: str = Field(..., min_length=1, max_length=120, description="Nome")


class UserCreate(UserBase):
    """Schema para criação de usuário"""
    password: str = Field(..., min_length=8, description="Senha do usuário")
    nome_empresa: Optional[str] = Field(None, description="Nome da empresa")
    cnpj: Optional[str] = Field(None, description="CNPJ da empresa")
    occupation: Optional[str] = Field(None, description="Profissão/ocupação")


class UserUpdate(BaseModel):
    """Schema para atualização de usuário"""
    email: Optional[EmailStr] = None
    name: Optional[str] = Field(None, min_length=1, max_length=120)
    password: Optional[str] = Field(None, min_length=8)
    nome_empresa: Optional[str] = None
    cnpj: Optional[str] = None
    occupation: Optional[str] = None


class UserResponse(UserBase):
    """Schema para resposta de usuário (sem senha)"""
    id: int
    is_active: bool
    nome_empresa: Optional[str] = None
    cnpj: Optional[str] = None
    occupation: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    """Schema para login de usuário"""
    email: EmailStr = Field(..., description="Email do usuário")
    password: str = Field(..., description="Senha do usuário")


class Token(BaseModel):
    """Schema para token JWT"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenData(BaseModel):
    """Schema para dados do token"""
    sub: str  # email do usuário
    exp: Optional[datetime] = None
