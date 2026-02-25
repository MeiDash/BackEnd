from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from datetime import datetime
from app.utils.utils import format_date, format_value

COR_PRIMARIA   = colors.HexColor("#1A56DB")
COR_HEADER_TAB = colors.HexColor("#059669")
COR_LINHA_PAR  = colors.HexColor("#EBF5FB")
COR_TOTAL      = colors.HexColor("#D1FAE5")
COR_TEXTO      = colors.HexColor("#1F2937")
COR_SUBTEXTO   = colors.HexColor("#6B7280")


def _build_styles():
    """Cria e retorna os estilos customizados do relatório."""
    base = getSampleStyleSheet()

    titulo = ParagraphStyle(
        "Titulo",
        parent=base["Title"],
        fontSize=20,
        textColor=COR_PRIMARIA,
        spaceAfter=4,
        alignment=TA_LEFT,
    )
    subtitulo = ParagraphStyle(
        "Subtitulo",
        parent=base["Normal"],
        fontSize=10,
        textColor=COR_SUBTEXTO,
        spaceAfter=2,
        alignment=TA_LEFT,
    )
    secao = ParagraphStyle(
        "Secao",
        parent=base["Heading2"],
        fontSize=12,
        textColor=COR_PRIMARIA,
        spaceBefore=16,
        spaceAfter=6,
    )
    normal = ParagraphStyle(
        "NormalCustom",
        parent=base["Normal"],
        fontSize=9,
        textColor=COR_TEXTO,
        leading=14,
    )
    rodape = ParagraphStyle(
        "Rodape",
        parent=base["Normal"],
        fontSize=8,
        textColor=COR_SUBTEXTO,
        alignment=TA_CENTER,
    )
    return titulo, subtitulo, secao, normal, rodape


def _tabela_resumo(dados: dict[str, float], total: int, s_normal, largura) -> Table:
    s_dir = ParagraphStyle("Dir", parent=s_normal, alignment=TA_RIGHT)

    rows = [[
        Paragraph("<b>Nome</b>", s_normal),
        Paragraph("<b>Total (R$)</b>", s_normal),
        Paragraph("<b>% do Total</b>", s_normal),
    ]]
    for nome, valor in sorted(dados.items(), key=lambda x: -x[1]):
        pct = (valor / total * 100) if total else 0
        rows.append([
            Paragraph(nome, s_normal),
            Paragraph(format_value(valor), s_dir),
            Paragraph(f"{pct:.1f}%", s_dir),
        ])
    rows.append([
        Paragraph("<b>Total geral</b>", s_normal),
        Paragraph(f"<b>{format_value(total)}</b>", s_dir),
        Paragraph("<b>100%</b>", s_dir),
    ])

    n = len(rows)
    t = Table(rows, colWidths=[largura * 0.55, largura * 0.25, largura * 0.20])
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0),     COR_HEADER_TAB),
        ("TEXTCOLOR",     (0, 0), (-1, 0),     colors.white),
        ("ROWBACKGROUND", (0, 1), (-1, n - 2), [colors.white, COR_LINHA_PAR]),
        ("BACKGROUND",    (0, n - 1), (-1, -1), COR_TOTAL),
        ("BOX",           (0, 0), (-1, -1),    0.5, colors.grey),
        ("INNERGRID",     (0, 0), (-1, -1),    0.3, colors.lightgrey),
        ("TOPPADDING",    (0, 0), (-1, -1),    5),
        ("BOTTOMPADDING", (0, 0), (-1, -1),    5),
        ("LEFTPADDING",   (0, 0), (-1, -1),    6),
    ]))
    return t


def _build_header(story, s_titulo, s_sub, s_normal, data_inicio, data_fim, empresa, categoria, valor_min, valor_max, periodo_ini, periodo_fim):
    """Cabeçalho do relatório — título, período e filtros ativos.
    
    Nota: 'Gerado em' foi removido daqui pois agora aparece no bloco
    de informações do usuário (format_user_header.py).
    """
    story.append(Paragraph("Relatório Geral de Notas Fiscais", s_titulo))
    story.append(Spacer(1, 0.3 * cm))

    story.append(Paragraph(f"<b>Período:</b> {periodo_ini} até {periodo_fim}", s_normal))
    if empresa:
        story.append(Paragraph(f"<b>Empresa:</b> {empresa}", s_normal))
    if categoria:
        story.append(Paragraph(f"<b>Categoria:</b> {categoria}", s_normal))
    if valor_min is not None:
        story.append(Paragraph(f"<b>Valor mínimo:</b> {format_value(valor_min)}", s_normal))
    if valor_max is not None:
        story.append(Paragraph(f"<b>Valor máximo:</b> {format_value(valor_max)}", s_normal))


def _build_cards(story, s_normal, largura, total, qtd_notas):
    story.append(Spacer(1, 0.5 * cm))
    s_card_val = ParagraphStyle("CardVal", parent=s_normal, fontSize=15, textColor=COR_PRIMARIA, alignment=TA_CENTER)
    card_data = [
        [Paragraph("<b>Total de Notas</b>", s_normal), Paragraph("<b>Valor Total</b>", s_normal)],
        [Paragraph(str(qtd_notas), s_card_val),        Paragraph(format_value(total), s_card_val)],
    ]
    card = Table(card_data, colWidths=[largura / 2] * 2)
    card.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0), COR_HEADER_TAB),
        ("TEXTCOLOR",     (0, 0), (-1, 0), colors.white),
        ("ALIGN",         (0, 0), (-1, -1), "CENTER"),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("BACKGROUND",    (0, 1), (-1, 1), COR_LINHA_PAR),
        ("BOX",           (0, 0), (-1, -1), 0.5, COR_PRIMARIA),
        ("INNERGRID",     (0, 0), (-1, -1), 0.5, COR_PRIMARIA),
        ("TOPPADDING",    (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(card)
    story.append(Spacer(1, 0.6 * cm))


def _build_tabela_detalhada(story, s_normal, largura, notas, total):
    s_dir = ParagraphStyle("DirNotas", parent=s_normal, alignment=TA_RIGHT)
    notas_rows = [[
        Paragraph("<b>ID</b>", s_normal),
        Paragraph("<b>Data</b>", s_normal),
        Paragraph("<b>Empresa</b>", s_normal),
        Paragraph("<b>Categoria</b>", s_normal),
        Paragraph("<b>Valor (R$)</b>", s_normal),
    ]]
    for nota in notas:
        notas_rows.append([
            Paragraph(str(nota.id), s_normal),
            Paragraph(format_date(nota.data), s_normal),
            Paragraph(nota.empresa or "-", s_normal),
            Paragraph(nota.categoria or "-", s_normal),
            Paragraph(format_value(nota.valor_total), s_dir),
        ])
    notas_rows.append([
        Paragraph("", s_normal),
        Paragraph("", s_normal),
        Paragraph("", s_normal),
        Paragraph("<b>Total</b>", s_normal),
        Paragraph(f"<b>{format_value(total)}</b>", s_dir),
    ])

    n = len(notas_rows)
    tabela = Table(
        notas_rows,
        colWidths=[largura * 0.08, largura * 0.14, largura * 0.34, largura * 0.22, largura * 0.22],
        repeatRows=1,
    )
    tabela.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0),     COR_HEADER_TAB),
        ("TEXTCOLOR",     (0, 0), (-1, 0),     colors.white),
        ("ROWBACKGROUND", (0, 1), (-1, n - 2), [colors.white, COR_LINHA_PAR]),
        ("BACKGROUND",    (0, n - 1), (-1, -1), COR_TOTAL),
        ("BOX",           (0, 0), (-1, -1),    0.5, colors.grey),
        ("INNERGRID",     (0, 0), (-1, -1),    0.3, colors.lightgrey),
        ("TOPPADDING",    (0, 0), (-1, -1),    5),
        ("BOTTOMPADDING", (0, 0), (-1, -1),    5),
        ("LEFTPADDING",   (0, 0), (-1, -1),    6),
    ]))
    story.append(tabela)
    story.append(Spacer(1, 0.8 * cm))


def _build_footer(story, s_rodape):
    story.append(HRFlowable(width="100%", thickness=0.5, color=COR_SUBTEXTO))
    story.append(Spacer(1, 0.2 * cm))
    story.append(Paragraph(
        "Documento gerado automaticamente pelo sistema MeiDash.",
        s_rodape,
    ))