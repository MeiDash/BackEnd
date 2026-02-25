"""
Schemas (Pydantic models) para validação de dados de usuário — adaptados ao novo esquema oficial
"""
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime


def to_camel(string: str) -> str:
    parts = string.split("_")
    return parts[0] + "".join(p.title() for p in parts[1:])


class CamelModel(BaseModel):
    """BaseModel que converte nomes snake_case em camelCase para aliases.

    Isso mantém compatibilidade com a API existente (aceita snake_case no body),
    mas apresenta os campos em camelCase na documentação (OpenAPI)."""
    model_config = {
        "alias_generator": to_camel,
        "populate_by_name": True,
    }


class UserBase(CamelModel):
    """Schema base de usuário"""
    email: EmailStr = Field(..., description="Email do usuário")
    name: str = Field(..., min_length=1, max_length=120, description="Nome")


class UserCreate(UserBase):
    """Schema para criação de usuário"""
    password: str = Field(..., min_length=8, description="Senha do usuário")
    nome_empresa: Optional[str] = Field(None, description="Nome da empresa")
    cnpj: Optional[str] = Field(None, description="CNPJ da empresa")
    occupation: Optional[str] = Field(None, description="Profissão/ocupação")

    @field_validator('password')
    @classmethod
    def validate_password_length(cls, v):
        if len(v.encode('utf-8')) > 72:
            raise ValueError('password cannot be longer than 72 bytes (utf-8 encoded)')
        return v


class UserUpdate(CamelModel):
    """Schema para atualização de usuário"""
    email: Optional[EmailStr] = None
    name: Optional[str] = Field(None, min_length=1, max_length=120)
    password: Optional[str] = Field(None, min_length=8)
    nome_empresa: Optional[str] = None
    cnpj: Optional[str] = None
    occupation: Optional[str] = None

    @field_validator('password')
    @classmethod
    def validate_update_password_length(cls, v):
        # permitir None (campo não enviado)
        if v is None:
            return v
        if len(v.encode('utf-8')) > 72:
            raise ValueError('password cannot be longer than 72 bytes (utf-8 encoded)')
        return v


class UserResponse(UserBase):
    """Schema para resposta de usuário (sem senha)"""
    id: int
    is_active: bool
    nome_empresa: Optional[str] = None
    cnpj: Optional[str] = None
    occupation: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # pydantic v2 config
    model_config = {
        "from_attributes": True,
    }
    
class UserUpdatePassword(CamelModel):
    """Schema para atualização de senha do usuário logado"""
    current_password: str = Field(..., description="Senha atual do usuário")
    new_password: str = Field(..., min_length=8, description="Nova senha")

    @field_validator('new_password')
    @classmethod
    def validate_password_length(cls, v):
        if len(v.encode('utf-8')) > 72:
            raise ValueError('A nova senha não pode exceder 72 bytes')
        return v


class UserLogin(CamelModel):
    """Schema para login de usuário"""
    email: EmailStr = Field(..., description="Email do usuário")
    password: str = Field(..., description="Senha do usuário")


class Token(CamelModel):
    """Schema para token JWT"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenData(CamelModel):
    """Schema para dados do token"""
    sub: str  # email do usuário
    exp: Optional[datetime] = None
