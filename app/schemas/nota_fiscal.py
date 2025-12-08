# app/schemas/fiscal.py
from pydantic import Field
from typing import Optional
from datetime import datetime, date

# Reutilizando seu CamelModel 
from app.schemas.base import CamelModel


class NotaFiscalBase(CamelModel):
    """Schema base para Nota Fiscal"""
    
    valor_total: float = Field(..., gt=0, description="Valor total da nota fiscal que conta para o faturamento.")
    data: date = Field(..., description="Data da emissão ou registro da nota")
    empresa: str = Field(..., description="Nome da empresa cliente/receptora da nota")
    url: str = Field(..., description="URL ou caminho para o arquivo da nota fiscal")


class NotaFiscalCreate(NotaFiscalBase):
    """Schema para criação de Nota Fiscal (dados de entrada)"""
    pass


class NotaFiscalUpdate(CamelModel):
    """Schema para atualização de Nota Fiscal"""
    valor_total: Optional[float] = Field(None, gt=0)
    data: Optional[date] = None
    empresa: Optional[str] = Field(None, min_length=1, max_length=255)
    url: Optional[str] = Field(None, min_length=1)


class NotaFiscalResponse(NotaFiscalBase):
    """Schema para resposta de Nota Fiscal (dados de saída)"""
    id: int
    user_id: int
    created_at: datetime

    model_config = {
        "from_attributes": True,
    }


class MetricaResponse(CamelModel):
    """Schema para resposta das Métricas do MEI"""
    user_id: int
    total_gasto: float = Field(..., description="Faturamento total acumulado que é comparado ao limite de R$ 81k.")
    limite: float = Field(..., description="Limite anual de faturamento (Ex: 81000.00)")
    updated_at: Optional[datetime] = None
    percentual_atingido: float = Field(..., description="Percentual do limite anual atingido")

    model_config = {
        "from_attributes": True,
    }