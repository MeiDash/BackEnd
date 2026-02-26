from pydantic import BaseModel, Field, field_validator, ConfigDict
from datetime import date, datetime
from typing import Optional
from enum import Enum
from fastapi import UploadFile


class CategoriaEnum(str, Enum):
    """Categorias detalhadas baseadas na estrutura do Frontend"""
    
    # Alimentação & Bebidas
    AGUA_MINERAL = "Água Mineral"
    BEBIDAS_ALCOOLICAS = "Bebidas Alcoólicas"
    BEBIDAS_NAO_ALCOOLICAS = "Bebidas Não Alcoólicas"
    CARNES_FRIOS = "Carnes e Frios"
    CEREAIS_GRAOS = "Cereais e Grãos"
    CONDIMENTOS_TEMPEROS = "Condimentos e Temperos"
    CONGELADOS = "Congelados e Semi-prontos"
    DERIVADOS_TRIGO = "Derivados de Trigo"
    DOCES_CONFEITARIA = "Doces e Confeitaria"
    FRUTOS_MAR = "Frutos do Mar"
    HORTIFRUTI = "Hortifruti"
    LATICINIOS = "Laticínios"
    MERCEARIA = "Mercearia Geral"
    OVOS = "Ovos"
    PADARIA = "Padaria e Panificação"
    SNACKS = "Snacks e Petiscos"
    SUPLEMENTOS = "Suplementos Alimentares"

    # Escritório & Papelaria
    EQUIP_ESCRITORIO = "Equipamentos de Escritório"
    IMPRESSAO_GRAFICA = "Impressão e Gráfica"
    MATERIAL_ESCRITORIO = "Material de Escritório"
    MOBILIARIO_ESCRITORIO = "Mobiliário de Escritório"
    ORGANIZACAO_ARQUIVO = "Organização e Arquivo"
    PAPELARIA_ENCADERNACAO = "Papelaria e Encadernação"
    PERIFERICOS_INFO = "Periféricos e Acessórios de Informática"
    SOFTWARE_LICENCAS = "Software e Licenças"

    # Limpeza & Higiene
    DESCARTAVEIS_EMBALAGENS = "Descartáveis e Embalagens"
    HIGIENE_PESSOAL = "Higiene Pessoal"
    LIMPEZA_CONSERVACAO = "Limpeza e Conservação"
    LIMPEZA_TERCEIRIZADA = "Limpeza Terceirizada"
    PRODUTOS_HIGIENE_IND = "Produtos de Higiene Industrial"
    UNIFORMES_EPIS = "Uniformes e EPIs"

    # Infraestrutura & Utilidades
    AGUA_SANEAMENTO = "Água e Saneamento"
    ENERGIA_ELETRICA = "Energia Elétrica"
    GAS_COMBUSTIVEL = "Gás e Combustível"
    INTERNET_TELECOM = "Internet e Telecomunicações"
    MANUTENCAO_REPAROS = "Manutenção e Reparos"
    SEGURANCA_VIGILANCIA = "Segurança e Vigilância"
    TELEFONIA = "Telefonia"

    # Vestuário & Calçados
    ACESSORIOS_MODA = "Acessórios de Moda"
    CALCADOS = "Calçados"
    ROUPAS_VESTUARIO = "Roupas e Vestuário"
    ROUPAS_PROFISSIONAIS = "Roupas Profissionais e Uniformes"
    TECIDOS_ARMARINHO = "Tecidos e Armarinho"

    # Saúde & Bem-estar
    FARMACIA_MEDICAMENTOS = "Farmácia e Medicamentos"
    PLANO_SAUDE = "Plano de Saúde"
    PRODUTOS_MEDICOS = "Produtos Médicos e Hospitalares"
    SAUDE_BEM_ESTAR = "Saúde e Bem-estar"
    SUPLEMENTOS_VITAMINAS = "Suplementos e Vitaminas"

    # Tecnologia
    ELETRONICOS_GADGETS = "Eletrônicos e Gadgets"
    EQUIP_TI = "Equipamentos de TI"
    HARDWARE_COMPONENTES = "Hardware e Componentes"
    CLOUD_HOSPEDAGEM = "Serviços de Cloud e Hospedagem"
    SUPORTE_TI = "Serviços de TI e Suporte"
    SOFTWARE_APPS = "Software e Aplicativos"

    # Transporte & Logística
    FRETE_ENTREGA = "Frete e Entrega"
    MANUTENCAO_VEICULOS = "Manutenção de Veículos"
    PEDAGIO_ESTACIONAMENTO = "Pedágio e Estacionamento"
    TRANSPORTE_MOBILIDADE = "Transporte e Mobilidade"

    # Marketing & Comunicação
    DESIGN_VISUAL = "Design e Identidade Visual"
    EMBALAGEM_ROTULOS = "Embalagem e Rótulos"
    FOTO_AUDIOVISUAL = "Fotografia e Audiovisual"
    MARKETING_DIGITAL = "Marketing Digital"
    MATERIAIS_PROMOCIONAIS = "Materiais Promocionais"
    MIDIA_PUBLICIDADE = "Mídia e Publicidade"
    PRODUCAO_CONTEUDO = "Produção de Conteúdo"
    REDES_SOCIAIS_ANUNCIOS = "Redes Sociais e Anúncios"

    # Finanças & Jurídico
    ASSINATURAS_MENSALIDADES = "Assinaturas e Mensalidades"
    CONTABILIDADE_FISCAL = "Contabilidade e Assessoria Fiscal"
    CONSULTORIA_EMPRESARIAL = "Consultoria Empresarial"
    HONORARIOS_ADVOCATICIOS = "Honorários Advocatícios"
    SEGUROS = "Seguros"
    SERVICOS_BANCARIOS = "Serviços Bancários e Tarifas"
    SERVICOS_FINANCEIROS = "Serviços Financeiros"

    # Construção & Reforma
    CONSTRUCAO_REFORMA = "Construção e Reforma"
    ELETRICA_HIDRAULICA = "Elétrica e Hidráulica"
    FERRAMENTAS_EQUIP = "Ferramentas e Equipamentos"
    MATERIAL_CONSTRUCAO = "Material de Construção"
    PINTURA_ACABAMENTO = "Pintura e Acabamento"

    # Eventos & Hospitalidade
    ALOJAMENTO_HOSPEDAGEM = "Alojamento e Hospedagem"
    BUFFET_CATERING = "Buffet e Catering"
    DECORACAO_AMBIENTACAO = "Decoração e Ambientação"
    EVENTOS_CONFRATERNIZACOES = "Eventos e Confraternizações"
    FLORES_PLANTAS = "Flores e Plantas"

    # Educação & Capacitação
    CURSOS_TREINAMENTOS = "Cursos e Treinamentos"
    LIVROS_PUBLICACOES = "Livros e Publicações"
    MATERIAL_DIDATICO = "Material Didático"
    PALESTRAS_WORKSHOPS = "Palestras e Workshops"

    # Serviços Gerais
    CORREIOS_POSTAGEM = "Correios e Postagem"
    LAVANDERIA_PASSADORIA = "Lavanderia e Passadoria"
    PET_SHOP = "Pet Shop e Cuidados com Animais"
    LIMPEZA_URBANA = "Serviços de Limpeza Urbana"
    SERVICOS_DOMESTICOS = "Serviços Domésticos"
    TERCEIRIZACAO = "Terceirização de Serviços"

    # Agro & Insumos
    FERTILIZANTES_DEFENSIVOS = "Fertilizantes e Defensivos"
    INSUMOS_AGRICOLAS = "Insumos Agrícolas"
    MAQUINAS_AGRICOLAS = "Máquinas e Implementos Agrícolas"
    SEMENTES_MUDAS = "Sementes e Mudas"
    VETERINARIA_AGRO = "Veterinária e Agropecuária"

    OUTROS = "Outros"


class NotaFiscalCreate(BaseModel):
    valor_total: float
    data: date
    empresa: str
    cnpj: Optional[str] = None
    categoria: Optional[CategoriaEnum] = None
    
    @field_validator('valor_total')
    @classmethod
    def validar_valor(cls, v):
        if v <= 0:
            raise ValueError('Valor deve ser maior que zero')
        return v


class NotaFiscalUpdate(BaseModel):
    valor_total: Optional[float] = None
    data: Optional[date] = None
    empresa: Optional[str] = None
    cnpj: Optional[str] = None
    categoria: Optional[CategoriaEnum] = None  
    
    @field_validator('valor_total')
    @classmethod
    def validar_valor(cls, v):
        if v is not None and v <= 0:
            raise ValueError('Valor deve ser maior que zero')
        return v


class NotaFiscalResponse(BaseModel):
    id: int
    user_id: int
    valor_total: float
    data: datetime
    empresa: str
    cnpj: Optional[str] = None
    arquivo_nome: str             
    arquivo_tipo: str              
    arquivo_tamanho: int           
    categoria: Optional[str] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class NotaFiscalFilter(BaseModel):
    """Schema para filtros de listagem"""
    data_inicio: Optional[date] = None
    data_fim: Optional[date] = None
    empresa: Optional[str] = None
    valor_min: Optional[float] = None
    valor_max: Optional[float] = None
    categoria: Optional[str] = None  
    
    @field_validator('valor_min', 'valor_max')
    @classmethod
    def validar_valores(cls, v):
        if v is not None and v < 0:
            raise ValueError('Valores não podem ser negativos')
        return v


class MetricaResponse(BaseModel):
    user_id: int
    total_gasto: float
    limite: float
    percentual_atingido: float
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)

class MetricaUpdate(BaseModel):
    limite: float = Field(..., ge=0, description="Novo limite de faturamento anual")

    @field_validator('limite')
    @classmethod
    def validar_limite(cls, v):
        if v > 500000: 
            raise ValueError('Limite superior ao permitido para microempresas')
        return v