"""
Inicialização do módulo API
"""
from fastapi import APIRouter
from app.api.routes import auth_router, users_router, fiscal_router 

api_router = APIRouter()

# Incluir rotas
api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(fiscal_router) 

__all__ = ["api_router"]