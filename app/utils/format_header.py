import os
import pathlib
from datetime import datetime

from dotenv import load_dotenv
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import HRFlowable, Paragraph, Spacer, Table, TableStyle
from reportlab.platypus.flowables import Image

# Alinhado com as cores de format_pdf.py
COR_PRIMARIA  = colors.HexColor("#1A56DB")
COR_SUBTEXTO  = colors.HexColor("#6B7280")
COR_SEPARADOR = colors.HexColor("#1A56DB")

LOGO_LARGURA_MAXIMA = 7.0 * cm
LOGO_ALTURA_MAXIMA  = 4.0 * cm
PROPORCAO_COLUNA_INFO = 0.65
PROPORCAO_COLUNA_LOGO = 0.35


# ---------------------------------------------------------------------------
# Helpers internos
# ---------------------------------------------------------------------------

def _resolver_caminho_logo(path_relativo: str) -> pathlib.Path:
    """
    Converte um path relativo em absoluto a partir da raiz do projeto.
    A raiz e inferida subindo 3 niveis a partir deste arquivo
    (app/utils/format_user_header.py -> app/utils -> app -> BackEnd).
    """
    caminho = pathlib.Path(path_relativo)
    if caminho.is_absolute():
        return caminho
    raiz_projeto = pathlib.Path(__file__).parent.parent.parent
    return raiz_projeto / caminho


def _redimensionar_imagem(imagem: Image, largura_max: float, altura_max: float) -> Image:
    """Redimensiona a imagem mantendo proporcao dentro dos limites dados."""
    proporcao = imagem.imageWidth / imagem.imageHeight
    if imagem.imageWidth > largura_max:
        imagem.drawWidth  = largura_max
        imagem.drawHeight = largura_max / proporcao
    if imagem.drawHeight > altura_max:
        imagem.drawHeight = altura_max
        imagem.drawWidth  = altura_max * proporcao
    return imagem


def _carregar_logo() -> Image | None:
    """
    Carrega o logo do caminho configurado em REPORT_LOGO_PATH.
    Retorna None silenciosamente se nao configurado ou nao encontrado.
    """
    load_dotenv()
    path_env = os.getenv("REPORT_LOGO_PATH", "")
    if not path_env:
        return None

    caminho_resolvido = _resolver_caminho_logo(path_env)
    if not caminho_resolvido.is_file():
        print(f"[WARN] Logo nao encontrado: {caminho_resolvido}")
        return None

    try:
        imagem = Image(str(caminho_resolvido))
        return _redimensionar_imagem(imagem, LOGO_LARGURA_MAXIMA, LOGO_ALTURA_MAXIMA)
    except Exception as erro:
        print(f"[WARN] Erro ao carregar logo: {erro}")
        return None


def _criar_estilos(s_normal) -> tuple:
    """Retorna os estilos (nome, detalhe, data) para o bloco de usuario."""
    estilo_nome = ParagraphStyle(
        "UserNome",
        parent=s_normal,
        fontSize=13,
        fontName="Helvetica-Bold",
        textColor=COR_PRIMARIA,
        leading=18,
        alignment=TA_LEFT,
    )
    estilo_detalhe = ParagraphStyle(
        "UserDetalhe",
        parent=s_normal,
        fontSize=9,
        textColor=COR_SUBTEXTO,
        leading=14,
        alignment=TA_LEFT,
    )
    estilo_data = ParagraphStyle(
        "UserData",
        parent=s_normal,
        fontSize=8,
        textColor=COR_SUBTEXTO,
        leading=12,
        alignment=TA_LEFT,
    )
    return estilo_nome, estilo_detalhe, estilo_data


def _extrair_dados_usuario(usuario) -> tuple:
    """
    Extrai nome, email, cnpj do objeto usuario com fallback
    para variacoes comuns de nome de atributo.
    """
    nome  = getattr(usuario, "nome", None) or getattr(usuario, "name", None) or getattr(usuario, "full_name", "—")
    email = getattr(usuario, "email", "—")
    cnpj  = getattr(usuario, "cnpj", None) or getattr(usuario, "documento", "—")
    return nome, email, cnpj


def _construir_paragrafos_info(usuario, s_normal) -> list:
    """Monta a lista de Paragraphs com as informacoes do usuario."""
    estilo_nome, estilo_detalhe, estilo_data = _criar_estilos(s_normal)
    nome, email, cnpj = _extrair_dados_usuario(usuario)
    gerado_em = datetime.now().strftime("%d/%m/%Y as %H:%M")

    return [
        Paragraph(nome, estilo_nome),
        Paragraph(f"<b>E-mail:</b> {email}", estilo_detalhe),
        Paragraph(f"<b>CNPJ:</b> {cnpj}", estilo_detalhe),
        Spacer(1, 0.15 * cm),
        Paragraph(f"Gerado em {gerado_em}", estilo_data),
    ]


def _construir_tabela_cabecalho(paragrafos_info: list, logo: Image | None,
                                 largura: float) -> Table:
    """
    Monta a Table do cabecalho.
    Com logo: info (65%) | logo (35%).
    Sem logo: info (100%) alinhada a direita.
    """
    if logo:
        tabela = Table(
            [[paragrafos_info, logo]],
            colWidths=[largura * PROPORCAO_COLUNA_INFO, largura * PROPORCAO_COLUNA_LOGO],
        )
        tabela.setStyle(TableStyle([
            ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
            ("ALIGN",         (0, 0), (0,  0),  "LEFT"),
            ("ALIGN",         (1, 0), (1,  0),  "RIGHT"),
            ("LEFTPADDING",   (0, 0), (-1, -1), 0),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 0),
            ("TOPPADDING",    (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ]))
    else:
        tabela = Table([[paragrafos_info]], colWidths=[largura])
        tabela.setStyle(TableStyle([
            ("VALIGN",        (0, 0), (0, 0), "TOP"),
            ("ALIGN",         (0, 0), (0, 0), "RIGHT"),
            ("LEFTPADDING",   (0, 0), (-1, -1), 0),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 0),
            ("TOPPADDING",    (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ]))

    return tabela


# ---------------------------------------------------------------------------
# API publica
# ---------------------------------------------------------------------------

def build_user_header(story: list, usuario, s_normal, largura: float) -> None:
    """
    Insere no story o cabecalho do relatorio contendo:
      - Informacoes do usuario (nome, e-mail, CNPJ, data de geracao) a esquerda
      - Logo a direita (se REPORT_LOGO_PATH estiver configurado)
      - Linha separadora azul abaixo
    """
    paragrafos_info = _construir_paragrafos_info(usuario, s_normal)
    logo            = _carregar_logo()
    tabela          = _construir_tabela_cabecalho(paragrafos_info, logo, largura)

    story.append(tabela)
    story.append(Spacer(1, 0.1 * cm))
    story.append(HRFlowable(width=largura, thickness=1.5, color=COR_SEPARADOR, spaceAfter=0.3 * cm))