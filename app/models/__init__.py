"""
Inicialização do módulo models
"""
from app.models.user import User
from app.models.nota_fiscal import NotaFiscal, Metrica

__all__ = ["User", "NotaFiscal", "Metrica"]
