from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional

from datetime import date, datetime, time
from io import BytesIO
from collections import defaultdict
import csv
import io

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable

from datetime import date
from app.services.nota_fiscal_service import FiscalService
from app.models.nota_fiscal import NotaFiscal
from app.utils.format_pdf import _build_styles, _build_cards, _build_footer, _build_header, _build_tabela_detalhada, _tabela_resumo
from app.utils.utils import format_date, format_value


class ReportService:
    
    @staticmethod
    def generate_relatorio_geral_pdf(
        db: Session,
        user_id: int,
        data_inicio: Optional[date] = None,
        data_fim: Optional[date] = None,
        empresa: Optional[str] = None,
        valor_min: Optional[float] = None,
        valor_max: Optional[float] = None,
        categoria: Optional[str] = None,
    ) -> bytes:
        notas = FiscalService.get_all_notas_fiscais(
            db=db,
            user_id=user_id,
            skip=0,
            limit=10_000,
            data_inicio=data_inicio, 
            data_fim=data_fim, 
            empresa=empresa, 
            valor_min=valor_min, 
            valor_max=valor_max, 
            categoria=categoria
        )

        total = sum(nota.valor_total for nota in notas)
        total_por_empresa   = defaultdict(float)
        total_por_categoria = defaultdict(float)

        for nota in notas:
            total_por_empresa[nota.empresa or "Não informada"]     += nota.valor_total
            total_por_categoria[nota.categoria or "Sem categoria"] += nota.valor_total

        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
        s_titulo, s_sub, s_secao, s_normal, s_rodape = _build_styles()
        largura = doc.width

        periodo_ini = format_date(data_inicio) if data_inicio else format_date(min((n.data for n in notas if n.data), default=None))
        periodo_fim = format_date(data_fim) if data_fim else format_date(date.today())

        story = []
        _build_header(story, s_titulo, s_sub, s_normal, data_inicio, data_fim, empresa, categoria, valor_min, valor_max, periodo_ini, periodo_fim)
        _build_cards(story, s_normal, largura, total, len(notas))

        story.append(Paragraph("Resumo por Empresa", s_secao))
        story.append(_tabela_resumo(total_por_empresa, total, s_normal, largura))
        story.append(Spacer(1, 0.6 * cm))

        story.append(Paragraph("Resumo por Categoria", s_secao))
        story.append(_tabela_resumo(total_por_categoria, total, s_normal, largura))
        story.append(Spacer(1, 0.6 * cm))

        story.append(Paragraph("Detalhamento das Notas Fiscais", s_secao))
        _build_tabela_detalhada(story, s_normal, largura, notas, total)

        _build_footer(story, s_rodape)

        doc.build(story)
        return buffer.getvalue()
            

    @staticmethod
    def generate_relatorio_geral_csv(
        db: Session,
        user_id: int,
        data_inicio: Optional[date] = None,
        data_fim: Optional[date] = None,
    ) -> str:
        """Gera o relatório agrupado por categoria em CSV."""
        ...
        notas = FiscalService.get_all_notas_fiscais(
            db=db,
            user_id=user_id,
            skip=0,
            limit=10_000,
            data_inicio=data_inicio,
            data_fim=data_fim,
            empresa=None,
            valor_min=None,
            valor_max=None,
            categoria=None
        )

        output = io.StringIO()
        writer = csv.writer(output)

        writer.writerow(["id","valor", "categoria", "empresa"])
        for nota in notas:
            writer.writerow([
                nota.id,
                nota.valor_total,
                nota.categoria or "-",
                nota.empresa or "-",
            ])

        return output.getvalue()
        
  