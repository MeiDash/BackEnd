"""
Inicialização do módulo API
"""
from fastapi import APIRouter
# NOVO: Importamos o roteador fiscal, se ele não estiver sendo importado automaticamente
from app.api.routes import auth_router, users_router, fiscal_router 

api_router = APIRouter()

# Incluir rotas
api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(fiscal_router) # CORREÇÃO: Incluir o roteador de Notas Fiscais

__all__ = ["api_router"]