from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, LargeBinary
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db import Base 


class NotaFiscal(Base):
    """Modelo de Nota Fiscal de entrada/saída"""
    
    __tablename__ = "notas_fiscais"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    
    valor_total = Column(Float, nullable=False)
    data = Column(DateTime, nullable=False)
    empresa = Column(String, nullable=False)
    cnpj = Column(String(18), nullable=True)
    
    arquivo_nome = Column(String(255), nullable=False)
    arquivo_tipo = Column(String(50), nullable=False)
    arquivo_tamanho = Column(Integer, nullable=False)
    arquivo_conteudo = Column(LargeBinary, nullable=True)  
    
    categoria = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="notas_fiscais")
    
    def __repr__(self):
        return f"<NotaFiscal(id={self.id}, user_id={self.user_id}, valor_total={self.valor_total}, categoria={self.categoria}, arquivo={self.arquivo_nome})>"


class Metrica(Base):
    """Modelo para armazenar as métricas calculadas do usuário MEI"""
    
    __tablename__ = "metricas"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, index=True, nullable=False)
    
    total_gasto = Column(Float, default=0.0)
    limite = Column(Float, default=81000.00)
    ultimo_alerta_percentual = Column(Float, default=0.0)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    user = relationship("User", back_populates="metrica")
    
    def __repr__(self):
        return f"<Metrica(user_id={self.user_id}, total_gasto={self.total_gasto})>"