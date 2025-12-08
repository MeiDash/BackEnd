from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
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
    url = Column(String, nullable=False) 
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="notas_fiscais")
    
    def __repr__(self):
        return f"<NotaFiscal(id={self.id}, user_id={self.user_id}, valor_total={self.valor_total})>"


class Metrica(Base):
    """Modelo para armazenar as métricas calculadas do usuário MEI"""
    
    __tablename__ = "metricas"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Relação 1:1 com o usuário 
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, index=True, nullable=False)
    
    total_gasto = Column(Float, default=0.0)
    limite = Column(Float, default=81000.00)
    ultimo_alerta_percentual = Column(Float, default=0.0)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    user = relationship("User", back_populates="metrica")
    
    def __repr__(self):
        return f"<Metrica(user_id={self.user_id}, faturamento_total={self.faturamento_total})>"