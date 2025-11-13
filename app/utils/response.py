"""
Utilitários gerais da aplicação
"""
from typing import List, Dict, Any


class APIResponse:
    """Classe para padronizar respostas da API"""
    
    @staticmethod
    def success(
        data: Any = None,
        message: str = "Success",
        status_code: int = 200
    ) -> Dict[str, Any]:
        """Cria resposta de sucesso"""
        return {
            "status": "success",
            "message": message,
            "data": data,
            "status_code": status_code,
        }
    
    @staticmethod
    def error(
        message: str = "Error",
        errors: List[str] = None,
        status_code: int = 400
    ) -> Dict[str, Any]:
        """Cria resposta de erro"""
        return {
            "status": "error",
            "message": message,
            "errors": errors or [],
            "status_code": status_code,
        }


class PaginationParams:
    """Classe para parametrização de paginação"""
    
    def __init__(self, skip: int = 0, limit: int = 100):
        self.skip = max(0, skip)
        self.limit = min(limit, 1000)  # Máximo de 1000 itens
    
    def get_skip(self) -> int:
        return self.skip
    
    def get_limit(self) -> int:
        return self.limit
