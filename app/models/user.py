"""
Modelo de usuário no banco de dados
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from app.db import Base


class User(Base):
    """Modelo de usuário"""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    # armazenamos a senha hashed na coluna física chamada 'password'
    hashed_password = Column('password', String, nullable=False)
    nome_empresa = Column('nomeEmpresa', String, nullable=True)
    cnpj = Column(String, nullable=True)
    occupation = Column(String, nullable=True)
    # coluna física chamada 'ativo' para manter compatibilidade com outros sistemas
    is_active = Column('ativo', Boolean, default=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, name={self.name})>"
