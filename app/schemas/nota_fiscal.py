from pydantic import BaseModel, field_validator, ConfigDict
from datetime import date, datetime
from typing import Optional
from enum import Enum


class CategoriaEnum(str, Enum):
    """Categorias disponíveis para notas fiscais"""
    MATERIAL_ESCRITORIO = "Material de Escritório"
    SERVICOS_DIGITAIS = "Serviços Digitais"
    ALIMENTACAO = "Alimentação"
    TRANSPORTE = "Transporte"


class NotaFiscalCreate(BaseModel):
    valor_total: float
    data: date
    empresa: str
    url: str
    categoria: Optional[CategoriaEnum] = None 
    cnpj: Optional[str] = None
    
    @field_validator('valor_total')
    @classmethod
    def validar_valor(cls, v):
        if v <= 0:
            raise ValueError('Valor deve ser maior que zero')
        return v


class NotaFiscalUpdate(BaseModel):
    valor_total: Optional[float] = None
    data: Optional[date] = None
    empresa: Optional[str] = None
    url: Optional[str] = None
    cnpj: Optional[str] = None
    categoria: Optional[CategoriaEnum] = None  
    
    @field_validator('valor_total')
    @classmethod
    def validar_valor(cls, v):
        if v is not None and v <= 0:
            raise ValueError('Valor deve ser maior que zero')
        return v


class NotaFiscalResponse(BaseModel):
    id: int
    user_id: int
    valor_total: float
    data: datetime
    empresa: str
    cnpj: Optional[str] = None
    url: str
    categoria: Optional[str] = None  
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class NotaFiscalFilter(BaseModel):
    """Schema para filtros de listagem"""
    data_inicio: Optional[date] = None
    data_fim: Optional[date] = None
    empresa: Optional[str] = None
    valor_min: Optional[float] = None
    valor_max: Optional[float] = None
    categoria: Optional[str] = None  
    
    @field_validator('valor_min', 'valor_max')
    @classmethod
    def validar_valores(cls, v):
        if v is not None and v < 0:
            raise ValueError('Valores não podem ser negativos')
        return v


class MetricaResponse(BaseModel):
    user_id: int
    total_gasto: float
    limite: float
    percentual_atingido: float
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)