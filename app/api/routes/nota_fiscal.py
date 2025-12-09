from typing import List
from app.schemas.nota_fiscal import MetricaResponse, NotaFiscalCreate, NotaFiscalResponse, NotaFiscalUpdate
from app.services.nota_fiscal_service import FiscalService
from app.utils.response import PaginationParams
from fastapi import APIRouter, Depends, HTTPException, status, Query
from app.db import get_db
from app.dependencies import get_current_active_user 
from app.models import User 
from sqlalchemy.orm import Session


router = APIRouter(
    prefix="/api/nfe",  
    tags=["Notas Fiscais"],
    responses={404: {"description": "Not found"}},
)


@router.post("", response_model=NotaFiscalResponse, status_code=status.HTTP_201_CREATED)
async def create_nota_fiscal(
    nota_data: NotaFiscalCreate,
    db: Session = Depends(get_db),
    
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


@router.get("", response_model=list[NotaFiscalResponse], response_model_by_alias=False)
async def get_notas_fiscais(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Obtém lista de notas fiscais do usuário autenticado com paginação
    """
    pagination = PaginationParams(skip=skip, limit=limit)
    notas = FiscalService.get_all_notas_fiscais(
        db,
        user_id=current_user.id,
        skip=pagination.get_skip(),
        limit=pagination.get_limit()
    )
    return notas


@router.get("/{nota_id}", response_model=NotaFiscalResponse, response_model_by_alias=False)
async def get_nota_fiscal(
    nota_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Obtém detalhes de uma nota fiscal específica
    """
    nota = FiscalService.get_nota_fiscal_by_id(db, nota_id, current_user.id)
    
    if not nota:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nota fiscal não encontrada"
        )
    
    return nota


@router.put("/{nota_id}", response_model=NotaFiscalResponse, response_model_by_alias=False)
async def update_nota_fiscal(
    nota_id: int,
    nota_data: NotaFiscalUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Atualiza dados de uma nota fiscal
    """
    nota = FiscalService.get_nota_fiscal_by_id(db, nota_id, current_user.id)
    
    if not nota:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nota fiscal não encontrada"
        )
    
    try:
        updated_nota = FiscalService.update_nota_fiscal(
            db, 
            nota_id, 
            current_user.id, 
            nota_data
        )
        return updated_nota
    except HTTPException:
        raise
    except Exception as e:
        import logging
        logging.error(f"Erro ao atualizar nota fiscal: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno: {str(e)}"
        )


@router.delete("/{nota_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_nota_fiscal(
    nota_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Deleta uma nota fiscal (hard delete)
    """
    success = FiscalService.delete_nota_fiscal(db, nota_id, current_user.id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nota fiscal não encontrada"
        )
    
    return None


@router.get("", response_model=List[NotaFiscalResponse])
async def get_notas_fiscais(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Obtém todas as notas fiscais do usuário autenticado.
    """
    notas = FiscalService.get_notas_fiscais_by_user(db, current_user.id)
    return notas


@router.get("/metrics", response_model=dict)
async def get_user_metrics(
    db: Session = Depends(get_db),
    
    current_user: User = Depends(get_current_active_user)
):
    """
    Obtém as métricas atuais do MEI.
    """
    