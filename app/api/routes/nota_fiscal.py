# app/api/fiscal.py (Atualizando a rota de criação)
from app.schemas.nota_fiscal import MetricaResponse, NotaFiscalCreate, NotaFiscalResponse
from app.services.nota_fiscal_service import FiscalService
from fastapi import APIRouter, Depends, HTTPException, status
from app.db import get_db
from app.dependencies import get_current_active_user # IMPORTAR A NOVA DEPENDÊNCIA
from app.models import User # Importar o modelo User
from sqlalchemy.orm import Session
# ... definições do router e imports ...

router = APIRouter(
    prefix="/api/nfe",  # Usando 'nfe' (Nota Fiscal Eletrônica) ou 'notas'
    tags=["Notas Fiscais"],
    responses={404: {"description": "Not found"}},
)


@router.post("", response_model=NotaFiscalResponse, status_code=status.HTTP_201_CREATED)
async def create_nota_fiscal(
    nota_data: NotaFiscalCreate,
    db: Session = Depends(get_db),
    # ADICIONADO: Dependência para exigir autenticação
    current_user: User = Depends(get_current_active_user) 
):
    """
    Cria uma nova nota fiscal, recalcula as métricas e dispara o alerta.
    """
    try:
        # Usamos o ID do usuário obtido do token
        nota = FiscalService.create_nota_fiscal(db, current_user.id, nota_data)
        
        return nota
        
    except HTTPException:
        # Se for uma exceção HTTPException que levantamos (ex: Usuário Inativo)
        raise
    except Exception as e:
        # Tratamento de qualquer outro erro interno (DB, Serviço de E-mail, etc.)
        import logging
        logging.error(f"Erro ao criar nota fiscal: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno do servidor: {str(e)}"
        )


@router.get("/metrics", response_model=MetricaResponse)
async def get_user_metrics(
    db: Session = Depends(get_db),
    # ADICIONADO: Dependência para exigir autenticação
    current_user: User = Depends(get_current_active_user)
):
    """
    Obtém as métricas atuais do MEI.
    """
    # ... lógica de métricas usando current_user.id ...