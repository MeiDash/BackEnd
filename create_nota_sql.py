"""
Script para criar uma nota fiscal com imagem direto no BD usando SQL
"""
import sys
import os
from datetime import datetime

# Adiciona o diretório ao path para importar o app
sys.path.insert(0, r'c:\Users\nicol\OneDrive\Documentos\Trabalho\BackEnd')

from app.db.database import SessionLocal

# Caminho da imagem
IMAGEM_PATH = r'C:\Users\nicol\OneDrive\Área de Trabalho\279.086 IDEAL_page-0001.jpg.jpeg'

def criar_nota_com_sql():
    """Cria nota fiscal diretamente via SQL"""
    
    # Verifica se o arquivo existe
    if not os.path.exists(IMAGEM_PATH):
        print(f"❌ Arquivo não encontrado: {IMAGEM_PATH}")
        return
    
    # Lê o arquivo
    with open(IMAGEM_PATH, 'rb') as f:
        arquivo_conteudo = f.read()
    
    print(f"✅ Arquivo lido: {len(arquivo_conteudo)} bytes")
    
    # Cria a sessão
    db = SessionLocal()
    
    try:
        arquivo_nome = os.path.basename(IMAGEM_PATH)
        
        # INSERT direto usando SQLAlchemy text()
        from sqlalchemy import text
        
        sql = """
        INSERT INTO notas_fiscais 
        (user_id, valor_total, data, empresa, cnpj, arquivo_nome, arquivo_tipo, arquivo_tamanho, arquivo_conteudo, url, categoria, created_at)
        VALUES 
        (:user_id, :valor_total, :data, :empresa, :cnpj, :arquivo_nome, :arquivo_tipo, :arquivo_tamanho, :arquivo_conteudo, :url, :categoria, :created_at)
        RETURNING id, created_at
        """
        
        result = db.execute(
            text(sql),
            {
                "user_id": 1,
                "valor_total": 500.00,
                "data": datetime.now(),
                "empresa": "Empresa Teste com Imagem",
                "cnpj": "12.345.678/0001-90",
                "arquivo_nome": arquivo_nome,
                "arquivo_tipo": "image/jpeg",
                "arquivo_tamanho": len(arquivo_conteudo),
                "arquivo_conteudo": arquivo_conteudo,
                "url": arquivo_nome,  # URL = nome do arquivo
                "categoria": "Mercearia Geral",
                "created_at": datetime.now()
            }
        )
        
        db.commit()
        
        # Pega o resultado
        row = result.fetchone()
        if row:
            nota_id, created_at = row
            print(f"\n✅ Nota Fiscal criada com sucesso!")
            print(f"   ID: {nota_id}")
            print(f"   User ID: 1")
            print(f"   Empresa: Empresa Teste com Imagem")
            print(f"   Valor: R$ 500.00")
            print(f"   Data: {datetime.now().date()}")
            print(f"   Arquivo: {arquivo_nome}")
            print(f"   Tamanho da imagem: {len(arquivo_conteudo)} bytes")
            print(f"   Categoria: Mercearia Geral")
            print(f"   URL: {arquivo_nome}")
            print(f"   Created At: {created_at}")
        else:
            print("❌ Nenhum resultado retornado")
        
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    criar_nota_com_sql()
