"""
Script para criar uma nota fiscal com imagem no banco de dados
"""
import sys
from datetime import date
from sqlalchemy.orm import Session

# Adiciona o diretório ao path para importar o app
sys.path.insert(0, r'c:\Users\nicol\OneDrive\Documentos\Trabalho\BackEnd')

from app.db.database import SessionLocal
from app.schemas.nota_fiscal import NotaFiscalCreate, CategoriaEnum
from app.services.nota_fiscal_service import FiscalService

# Caminho da imagem
IMAGEM_PATH = r'C:\Users\nicol\OneDrive\Área de Trabalho\279.086 IDEAL_page-0001.jpg.jpeg'

def criar_nota_fiscal_com_imagem():
    """Cria uma nota fiscal com a imagem especificada"""
    
    # Verifica se o arquivo existe
    import os
    if not os.path.exists(IMAGEM_PATH):
        print(f"❌ Arquivo não encontrado: {IMAGEM_PATH}")
        return
    
    # Lê o arquivo de imagem em bytes
    with open(IMAGEM_PATH, 'rb') as f:
        arquivo_conteudo = f.read()
    
    print(f"✅ Arquivo lido: {len(arquivo_conteudo)} bytes")
    
    # Cria a sessão do banco de dados
    db: Session = SessionLocal()
    
    try:
        # Dados da nota fiscal
        nota_data = NotaFiscalCreate(
            valor_total=500.00,  # Valor de exemplo
            data=date.today(),
            empresa="Empresa Teste com Imagem",
            cnpj="12.345.678/0001-90",
            categoria=CategoriaEnum.MERCEARIA  # Categoria de exemplo
        )
        
        # Obtém nome do arquivo original
        arquivo_nome = os.path.basename(IMAGEM_PATH)
        arquivo_tipo = "image/jpeg"
        
        # Chama o serviço para criar a nota fiscal
        nota = FiscalService.create_nota_fiscal_with_file(
            db=db,
            user_id=1,  # Usuário ID 1
            nota_data=nota_data,
            arquivo_nome=arquivo_nome,
            arquivo_tipo=arquivo_tipo,
            arquivo_conteudo=arquivo_conteudo
        )
        
        # Se a nota criada não tem URL, atualiza com o nome do arquivo
        if not nota.url:
            nota.url = arquivo_nome
            db.commit()
        
        print(f"\n✅ Nota Fiscal criada com sucesso!")
        print(f"   ID: {nota.id}")
        print(f"   User ID: {nota.user_id}")
        print(f"   Empresa: {nota.empresa}")
        print(f"   Valor: R$ {nota.valor_total}")
        print(f"   Data: {nota.data}")
        print(f"   Arquivo: {nota.arquivo_nome}")
        print(f"   Tamanho da imagem: {nota.arquivo_tamanho} bytes")
        print(f"   Categoria: {nota.categoria}")
        
    except Exception as e:
        print(f"❌ Erro ao criar nota fiscal: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    criar_nota_fiscal_com_imagem()
