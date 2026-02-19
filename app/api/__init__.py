"""
Inicialização do módulo API
"""
from fastapi import APIRouter
from app.api.routes import auth_router, users_router, fiscal_router, upload_router
from app.api.routes.extraction import router as extraction_router
from app.api.routes.report import router as report_router

api_router = APIRouter()

# Incluir rotas
api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(fiscal_router) 
api_router.include_router(upload_router)
api_router.include_router(extraction_router)
api_router.include_router(report_router) 


__all__ = ["api_router"]