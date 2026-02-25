"""
Script para listar usuários e adicionar notas fiscais de exemplo
"""
from app.db import SessionLocal, Base, engine
from app.models import User, NotaFiscal
from datetime import datetime, timedelta
import random

def list_users():
    """Lista todos os usuários do banco"""
    db = SessionLocal()
    users = db.query(User).all()
    
    print("\n" + "="*60)
    print("📋 USUÁRIOS NO BANCO DE DADOS")
    print("="*60)
    
    if not users:
        print("❌ Nenhum usuário encontrado!")
        return users
    
    for user in users:
        print(f"\n🔹 ID: {user.id}")
        print(f"   Nome: {user.name}")
        print(f"   Email: {user.email}")
        print(f"   Ativo: {'✅ Sim' if user.is_active else '❌ Não'}")
        print(f"   Empresa: {user.nome_empresa or 'N/A'}")
    
    print("\n" + "="*60 + "\n")
    db.close()
    return users


def add_sample_notas_fiscais():
    """Adiciona notas fiscais de exemplo para cada usuário"""
    db = SessionLocal()
    
    users = db.query(User).filter(User.is_active == True).all()
    
    if not users:
        print("❌ Nenhum usuário ativo encontrado!")
        db.close()
        return
    
    print("\n" + "="*60)
    print("➕ ADICIONANDO NOTAS FISCAIS")
    print("="*60 + "\n")
    
    # Dados de exemplo
    empresas = [
        "Empresa A LTDA",
        "Fornecedor B",
        "Distribuidora C",
        "Serviços D",
        "Comércio E"
    ]
    
    categorias = [
        "Alimentação",
        "Transporte",
        "Serviços",
        "Materiais",
        "Equipamentos"
    ]
    
    # Adicionar 5 notas para cada usuário
    total_added = 0
    for user in users:
        print(f"📝 Adicionando notas para: {user.name} (ID: {user.id})")
        
        for i in range(5):
            # Gerar data aleatória nos últimos 3 meses
            dias_atras = random.randint(0, 90)
            data = datetime.now() - timedelta(days=dias_atras)
            
            # Gerar valores aleatórios entre 100 e 5000
            valor = round(random.uniform(100, 5000), 2)
            
            # Selecionar empresa e categoria aleatórias
            empresa = random.choice(empresas)
            categoria = random.choice(categorias)
            
            nf = NotaFiscal(
                user_id=user.id,
                valor_total=valor,
                data=data,
                empresa=empresa,
                url=f"http://localhost:8000/uploads/nf_{user.id}_{i}.pdf",
                cnpj=f"{random.randint(10000000, 99999999)}0001{random.randint(10, 99)}",
                categoria=categoria
            )
            
            db.add(nf)
            total_added += 1
            print(f"   ✅ NF {i+1}: {empresa} - R$ {valor:.2f} ({categoria})")
        
        print()
    
    # Commit de todas as notas
    db.commit()
    
    print("="*60)
    print(f"✅ {total_added} notas fiscais adicionadas com sucesso!")
    print("="*60 + "\n")
    
    db.close()


def verify_notas_fiscais():
    """Verifica quantas notas foram adicionadas por usuário"""
    db = SessionLocal()
    
    print("\n" + "="*60)
    print("📊 RESUMO DE NOTAS FISCAIS")
    print("="*60 + "\n")
    
    users = db.query(User).all()
    
    for user in users:
        nfs_count = db.query(NotaFiscal).filter(NotaFiscal.user_id == user.id).count()
        total_value = db.query(NotaFiscal).filter(NotaFiscal.user_id == user.id).all()
        total_sum = sum([nf.valor_total for nf in total_value]) if total_value else 0
        
        print(f"👤 {user.name} (ID: {user.id})")
        print(f"   📄 Notas: {nfs_count}")
        print(f"   💰 Total: R$ {total_sum:.2f}\n")
    
    print("="*60 + "\n")
    db.close()


if __name__ == "__main__":
    print("\n🚀 INICIANDO SCRIPT DE NOTAS FISCAIS\n")
    
    # 1. Listar usuários
    users = list_users()
    
    if users:
        # 2. Adicionar notas fiscais
        add_sample_notas_fiscais()
        
        # 3. Verificar
        verify_notas_fiscais()
        
        print("✅ Script finalizado com sucesso!")
    else:
        print("❌ Nenhum usuário disponível. Crie um usuário primeiro.")
