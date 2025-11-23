"""
Inicialização do módulo routes
"""
from app.api.routes.auth import router as auth_router
from app.api.routes.users import router as users_router
from app.api.routes.nota_fiscal import router as fiscal_router # NOVO: Importa o roteador fiscal

__all__ = ["auth_router", "users_router", "fiscal_router"] # NOVO: Exporta o roteador fiscal