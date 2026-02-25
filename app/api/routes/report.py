from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import Response, StreamingResponse
from sqlalchemy.orm import Session
import logging
import io

from app.db import get_db
from app.services.report_service import ReportService
from app.dependencies import get_current_active_user 
from app.models.user import User 

router = APIRouter(
    prefix="/api/reports",
    tags=["Relatórios"],
    responses={404: {"description": "Not found"}},
)


# ---------------------------------------------------------------------------
# Relatório Geral
# ---------------------------------------------------------------------------

@router.get("/pdf")
async def relatorio_geral_pdf(
    current_user = Depends(get_current_active_user),
    data_inicio: Optional[date] = Query(None, description="Data inicial (YYYY-MM-DD)"),
    data_fim: Optional[date] = Query(None, description="Data final (YYYY-MM-DD)"),
    empresa: Optional[str] = Query(None, description="Nome ou parte do nome da empresa"),
    valor_min: Optional[float] = Query(None, ge=0, description="Valor mínimo"),
    valor_max: Optional[float] = Query(None, ge=0, description="Valor máximo"),
    categoria: Optional[str] = Query(None, description="Categoria da nota fiscal"),
    db: Session = Depends(get_db),
):
    """Gera o relatório geral de notas fiscais em PDF."""
    try:
        pdf_bytes = ReportService.generate_relatorio_geral_pdf(
            db=db,
            user=current_user,
            data_inicio=data_inicio,
            data_fim=data_fim,
            empresa=empresa,
            valor_min=valor_min,
            valor_max=valor_max,
            categoria=categoria,
        )
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": "inline; filename=relatorio_geral.pdf"},
        )
    except Exception as e:
        logging.error(f"Erro ao gerar relatório geral PDF: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/csv")
async def relatorio_geral_csv(
    current_user: int = Depends(get_current_active_user),
    data_inicio: Optional[date] = Query(None),
    data_fim: Optional[date] = Query(None),
    empresa: Optional[str] = Query(None),
    valor_min: Optional[float] = Query(None, ge=0),
    valor_max: Optional[float] = Query(None, ge=0),
    categoria: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Gera o relatório geral de notas fiscais em CSV."""
    try:
        csv_str = ReportService.generate_relatorio_geral_csv(
            db=db,
            user_id=current_user.id,
            data_inicio=data_inicio,
            data_fim=data_fim,
            empresa=empresa,
            valor_min=valor_min,
            valor_max=valor_max,
            categoria=categoria
        )
        return Response(
            content=csv_str.encode("utf-8-sig"), 
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=relatorio_geral.csv"},
        )
    except NotImplementedError:
        raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Ainda não implementado.")
    except Exception as e:
        logging.error(f"Erro ao gerar relatório geral CSV: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# @router.get("/pdf/preview")  
# async def preview_pdf(
#     user = ,
#     db: Session = Depends(get_db),
# ):
#     pdf_bytes = ReportService.generate_relatorio_geral_pdf(db=db, user_id=user_id)
#     import base64
#     b64 = base64.b64encode(pdf_bytes).decode()
#     html = f'<iframe src="data:application/pdf;base64,{b64}" width="100%" height="100%" style="position:fixed;top:0;left:0;border:none"></iframe>'
#     return Response(content=html, media_type="text/html")