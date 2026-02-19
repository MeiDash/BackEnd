from datetime import date
from typing import List, Optional
from app.schemas.nota_fiscal import MetricaResponse, NotaFiscalCreate, NotaFiscalResponse, NotaFiscalUpdate
from app.services.nota_fiscal_service import FiscalService
from app.utils.response import PaginationParams
from fastapi import APIRouter, Depends, HTTPException, status, Query
from app.db import get_db
from app.dependencies import get_current_active_user 
from app.models import User 
from sqlalchemy.orm import Session
import logging
from app.schemas.nota_fiscal import CategoriaEnum


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
        nota = FiscalService.create_nota_fiscal(db, current_user.id, nota_data)
        
        return nota
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Erro ao criar nota fiscal: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno do servidor: {str(e)}"
        ) 


@router.get("", response_model=dict)
async def get_notas_fiscais(
    skip: int = Query(0, ge=0, description="Número de registros para pular"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros a retornar"),
    data_inicio: Optional[date] = Query(None, description="Data inicial (formato: YYYY-MM-DD)"),
    data_fim: Optional[date] = Query(None, description="Data final (formato: YYYY-MM-DD)"),
    empresa: Optional[str] = Query(None, description="Nome ou parte do nome da empresa"),
    valor_min: Optional[float] = Query(None, ge=0, description="Valor mínimo da nota fiscal"),
    valor_max: Optional[float] = Query(None, ge=0, description="Valor máximo da nota fiscal"),
    categoria: Optional[str] = Query(None, description="Categoria da nota fiscal"),  
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtém lista de notas fiscais do usuário autenticado com paginação e filtros opcionais."""
    
    if data_inicio and data_fim and data_inicio > data_fim:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="data_inicio não pode ser maior que data_fim"
        )
    
    if valor_min is not None and valor_max is not None and valor_min > valor_max:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="valor_min não pode ser maior que valor_max"
        )
    
    notas = FiscalService.get_all_notas_fiscais(
        db,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        data_inicio=data_inicio,
        data_fim=data_fim,
        empresa=empresa,
        valor_min=valor_min,
        valor_max=valor_max,
        categoria=categoria  
    )
    
    total = FiscalService.count_notas_fiscais(
        db,
        user_id=current_user.id,
        data_inicio=data_inicio,
        data_fim=data_fim,
        empresa=empresa,
        valor_min=valor_min,
        valor_max=valor_max,
        categoria=categoria  
    )
    
    return {
        "data": [NotaFiscalResponse.model_validate(nota) for nota in notas],
        "total": total,
        "skip": skip,
        "limit": limit,
        "has_next": (skip + limit) < total,
        "has_previous": skip > 0
    }

@router.get("/categorias", response_model=list[str])
async def get_categorias():
    """Retorna lista de categorias disponíveis"""
    return [categoria.value for categoria in CategoriaEnum]
    
@router.get("/metrics", response_model=MetricaResponse)
async def get_user_metrics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Obtém as métricas atuais do MEI.
    """
    return FiscalService.get_user_metrics(db, current_user.id)

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


