"""
Funções auxiliares para geração de gráficos no relatório PDF.
Paleta idêntica ao Dashboard frontend (Recharts).
Layout: pizza + barras lado a lado em um único Drawing.
"""
from collections import defaultdict

from reportlab.graphics.shapes import Drawing, String, Line
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.legends import Legend
from reportlab.lib import colors
from reportlab.lib.units import cm

# ---------------------------------------------------------------------------
# Paleta — espelha o array `colors` do Dashboard.tsx
# ---------------------------------------------------------------------------
PALETA = [
    colors.HexColor("#10B981"),  # emerald
    colors.HexColor("#06B6D4"),  # cyan
    colors.HexColor("#8B5CF6"),  # purple
    colors.HexColor("#F59E0B"),  # amber
    colors.HexColor("#EF4444"),  # red
    colors.HexColor("#EC4899"),  # pink
    colors.HexColor("#6366F1"),  # indigo
]

# Cores de UI — espelham os valores usados no Recharts
COR_TITULO    = colors.HexColor("#374151")  
COR_SUBTITULO = colors.HexColor("#6B7280")  
COR_GRID      = colors.HexColor("#F3F4F6")  
COR_EIXO      = colors.HexColor("#6B7280")  
COR_LINHA_MES = colors.HexColor("#10B981")  

MAX_CHARS_PIZZA  = 22
MAX_CHARS_BARRAS = 10


# ---------------------------------------------------------------------------
# Helpers internos
# ---------------------------------------------------------------------------

def _cor_por_indice(indice: int) -> colors.Color:
    """Retorna a cor da paleta para o índice dado (cíclico)."""
    return PALETA[indice % len(PALETA)]


def _construir_color_map(dados: dict) -> dict:
    """
    Mapeia nome -> cor em ordem decrescente de valor.
    Garante que o mesmo nome receba sempre a mesma cor na pizza e nas barras.
    """
    nomes_ordenados = sorted(dados, key=lambda nome: dados[nome], reverse=True)
    return {nome: _cor_por_indice(i) for i, nome in enumerate(nomes_ordenados)}


def _titulo_centralizado(texto: str, x_centro: float, y: float) -> String:
    """Retorna um String centralizado para usar como título de bloco."""
    titulo = String(x_centro, y, texto)
    titulo.textAnchor = "middle"
    titulo.fontSize   = 8.5
    titulo.fontName   = "Helvetica-Bold"
    titulo.fillColor  = COR_TITULO
    return titulo


def _label_valor(valor: float, x: float, y: float, tamanho: float = 7.0) -> String:
    """Retorna um String formatado para exibir valor acima de barra ou ponto."""
    label = String(x, y, f"{valor:,.0f}")
    label.textAnchor = "middle"
    label.fontSize   = tamanho
    label.fontName   = "Helvetica-Bold"
    label.fillColor  = COR_TITULO
    return label


def _truncar(texto: str, max_chars: int) -> str:
    """Trunca o texto adicionando '...' se exceder max_chars."""
    return texto[:max_chars] + "..." if len(texto) > max_chars else texto


def _configurar_eixo_categoria(eixo, labels: list, angulo: int = 0) -> None:
    """Aplica configuração padrão no eixo de categorias de um chart."""
    eixo.categoryNames     = labels
    eixo.labels.fontSize   = 6 if angulo == 0 else 7
    eixo.labels.fontName   = "Helvetica"
    eixo.labels.angle      = angulo
    eixo.labels.dy         = -4 if angulo == 0 else -8
    eixo.labels.textAnchor = "middle" if angulo == 0 else "end"
    eixo.strokeColor       = COR_EIXO
    eixo.strokeWidth       = 0.5


def _configurar_eixo_valor(eixo, valor_max: float = None) -> None:
    """Aplica configuração padrão no eixo de valores de um chart."""
    eixo.labels.fontSize  = 6
    eixo.labels.fontName  = "Helvetica"
    eixo.labels.fillColor = COR_SUBTITULO
    eixo.forceZero        = True
    eixo.strokeColor      = COR_EIXO
    eixo.strokeWidth      = 0.5
    eixo.gridStrokeColor  = COR_GRID
    eixo.gridStrokeWidth  = 0.4
    eixo.visibleGrid      = True
    if valor_max is not None:
        eixo.valueMin = 0
        eixo.valueMax = valor_max


def _agregar_gastos_por_mes(notas: list) -> tuple:
    """
    Agrega notas fiscais por mes e retorna (labels, valores) ordenados
    cronologicamente.
    """
    totais: dict = defaultdict(float)
    for nota in notas:
        if nota.data:
            totais[nota.data.strftime("%m/%Y")] += nota.valor_total

    itens_ordenados = sorted(totais.items(), key=lambda x: (x[0][3:], x[0][:2]))
    labels  = [item[0] for item in itens_ordenados]
    valores = [item[1] for item in itens_ordenados]
    return labels, valores


# ---------------------------------------------------------------------------
# Componentes de grafico
# ---------------------------------------------------------------------------

def _construir_pizza(dados: dict, x_offset: float, largura_bloco: float,
                     altura: float, color_map: dict) -> list:
    """Constroi fatias de pizza + legenda para o bloco esquerdo do grafico duplo."""
    dados_positivos = {k: v for k, v in dados.items() if v > 0}
    if not dados_positivos:
        return []

    itens    = sorted(dados_positivos.items(), key=lambda x: x[1], reverse=True)
    labels   = [item[0] for item in itens]
    valores  = [item[1] for item in itens]
    total    = sum(valores)
    raio     = 2.2 * cm
    centro_x = x_offset + largura_bloco / 2
    centro_y = altura - raio - 1.0 * cm

    grafico            = Pie()
    grafico.x          = centro_x - raio
    grafico.y          = centro_y - raio
    grafico.width      = raio * 2
    grafico.height     = raio * 2
    grafico.data       = valores
    grafico.labels     = None
    grafico.startAngle = 90
    grafico.direction  = "clockwise"

    for i, nome in enumerate(labels):
        grafico.slices[i].fillColor   = color_map[nome]
        grafico.slices[i].strokeColor = colors.white
        grafico.slices[i].strokeWidth = 1.5
        grafico.slices[i].popout      = 3 if i == 0 else 0

    legenda                = Legend()
    legenda.x              = x_offset + 0.4 * cm
    legenda.y              = centro_y - raio - 0.5 * cm
    legenda.dx             = 8
    legenda.dy             = 8
    legenda.fontName       = "Helvetica"
    legenda.fontSize       = 8
    legenda.leading        = 14
    legenda.columnMaximum  = len(labels)
    legenda.strokeWidth    = 0
    legenda.strokeColor    = colors.white
    legenda.deltax         = 0
    legenda.autoXPadding   = 0
    legenda.colorNamePairs = [
        (color_map[nome], f"{_truncar(nome, MAX_CHARS_PIZZA)}  {valores[i] / total * 100:.1f}%")
        for i, nome in enumerate(labels)
    ]

    return [grafico, legenda]


def _construir_barras(dados: dict, x_offset: float, largura_bloco: float,
                      altura: float, color_map: dict, top_n: int = 7) -> list:
    """Constroi grafico de barras verticais para o bloco direito do grafico duplo."""
    itens = sorted(dados.items(), key=lambda x: x[1], reverse=True)[:top_n]
    if not itens:
        return []

    nomes_originais  = [item[0] for item in itens]
    labels_truncados = [_truncar(nome, MAX_CHARS_BARRAS) for nome in nomes_originais]
    valores          = [item[1] for item in itens]
    valor_maximo     = max(valores)

    grafico              = VerticalBarChart()
    grafico.x            = x_offset + 0.8 * cm
    grafico.y            = 1.2 * cm
    grafico.width        = largura_bloco - 1.2 * cm
    grafico.height       = altura - 2.8 * cm
    grafico.data         = [valores]
    grafico.groupSpacing = 8
    grafico.barSpacing   = 2
    grafico.bars.strokeWidth = 0

    _configurar_eixo_categoria(grafico.categoryAxis, labels_truncados)
    _configurar_eixo_valor(grafico.valueAxis)

    for i, nome in enumerate(nomes_originais):
        grafico.bars[0, i].fillColor = color_map[nome]

    largura_barra = (grafico.width - grafico.groupSpacing * (len(valores) - 1)) / len(valores)
    labels_valor  = [
        _label_valor(
            valor=v,
            x=grafico.x + i * (largura_barra + grafico.groupSpacing) + largura_barra / 2,
            y=grafico.y + (v / valor_maximo) * grafico.height + 3,
        )
        for i, v in enumerate(valores)
    ]

    return [grafico, *labels_valor]


def _construir_linha_mensal(labels: list, valores: list,
                             largura: float, altura: float):
    """Constroi o HorizontalLineChart de evolucao mensal."""
    from reportlab.graphics.charts.linecharts import HorizontalLineChart
    from reportlab.graphics.widgets.markers import makeMarker

    margem_esquerda = 2.0 * cm
    margem_inferior = 1.8 * cm
    valor_max_eixo  = max(valores) * 1.25

    grafico        = HorizontalLineChart()
    grafico.x      = margem_esquerda
    grafico.y      = margem_inferior
    grafico.width  = largura - margem_esquerda - 0.5 * cm
    grafico.height = altura  - margem_inferior - 1.2 * cm
    grafico.data   = [valores]

    grafico.lines[0].strokeColor = COR_LINHA_MES
    grafico.lines[0].strokeWidth = 3
    grafico.lines[0].symbol      = makeMarker(
        "FilledCircle",
        size=5,
        fillColor=COR_LINHA_MES,
        strokeColor=colors.white,
        strokeWidth=1,
    )

    _configurar_eixo_categoria(grafico.categoryAxis, labels, angulo=45)
    grafico.categoryAxis.joinAxisMode = "bottom"
    _configurar_eixo_valor(grafico.valueAxis, valor_max=valor_max_eixo)

    return grafico, valor_max_eixo


# ---------------------------------------------------------------------------
# API publica
# ---------------------------------------------------------------------------

def build_grafico_duplo(dados: dict, titulo_pizza: str,
                        titulo_barras: str, largura: float) -> Drawing:
    """
    Retorna um Drawing com pizza a esquerda e barras a direita.
    O mesmo nome sempre recebe a mesma cor nos dois graficos.
    """
    color_map = _construir_color_map(dados)
    metade    = largura / 2
    altura    = 9.0 * cm
    drawing   = Drawing(largura, altura)

    separador             = Line(metade, 0.2 * cm, metade, altura - 0.6 * cm)
    separador.strokeColor = COR_GRID
    separador.strokeWidth = 0.6
    drawing.add(separador)

    drawing.add(_titulo_centralizado(titulo_pizza,  metade / 2,          altura - 0.35 * cm))
    drawing.add(_titulo_centralizado(titulo_barras, metade + metade / 2, altura - 0.35 * cm))

    for shape in _construir_pizza(dados, 0,      metade, altura - 0.6 * cm, color_map):
        drawing.add(shape)
    for shape in _construir_barras(dados, metade, metade, altura - 0.6 * cm, color_map):
        drawing.add(shape)

    return drawing


def build_grafico_gastos_por_mes(notas: list, largura: float) -> Drawing:
    """
    Retorna um Drawing com grafico de linha de gastos mensais
    ocupando a largura total do relatorio.
    """
    labels, valores = _agregar_gastos_por_mes(notas)
    if not valores:
        return Drawing(largura, 1)

    altura  = 7.5 * cm
    drawing = Drawing(largura, altura)
    drawing.add(_titulo_centralizado("Gastos por Mes", largura / 2, altura - 0.35 * cm))

    grafico_linha, valor_max_eixo = _construir_linha_mensal(labels, valores, largura, altura)
    drawing.add(grafico_linha)

    slot = grafico_linha.width / len(valores)
    for i, valor in enumerate(valores):
        ponto_x = grafico_linha.x + slot * i + slot / 2
        ponto_y = grafico_linha.y + (valor / valor_max_eixo) * grafico_linha.height
        drawing.add(_label_valor(valor, ponto_x, ponto_y + 7, tamanho=7.5))

    return drawing