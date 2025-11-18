"""
Script para inicializar o banco de dados com dados de teste
"""
from app.db import SessionLocal, Base, engine
from app.models import User
from app.core.security import hash_password
import sys


def init_db():
    """Inicializa o banco de dados com tabelas e dados de teste"""
    
    # Criar todas as tabelas (se ainda não existirem)
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    # Verificar se já existem usuários
    existing_user = db.query(User).filter(User.email == "admin@example.com").first()
    
    if not existing_user:
        # Criar usuário de teste/admin (novo esquema)
        admin_user = User(
            email="admin@example.com",
            name="Administrador",
            hashed_password=hash_password("admin123"),
            nome_empresa="Empresa Admin",
            cnpj=None,
            occupation="Administrador",
            is_active=True,
        )
        db.add(admin_user)
        
        # Criar usuário de teste
        test_user = User(
            email="test@example.com",
            name="Usuário Teste",
            hashed_password=hash_password("test123"),
            nome_empresa=None,
            cnpj=None,
            occupation="Desenvolvedor",
            is_active=True,
        )
        db.add(test_user)
        
        db.commit()
        
        print("✅ Banco de dados inicializado com sucesso!")
        print("Usuários de teste criados:")
        print("  - Email: admin@example.com / Senha: admin123")
        print("  - Email: test@example.com / Senha: test123")
    else:
        print("ℹ️ Banco de dados já contém dados. Nenhuma inicialização necessária.")
    
    db.close()


if __name__ == "__main__":
    # Se for passado o argumento 'recreate', dropará e recriará todas as tabelas (útil em dev)
    if len(sys.argv) > 1 and sys.argv[1] in ("recreate", "--recreate"):
        print("⚠️  Recriando o banco de dados: dropando todas as tabelas e criando novamente...")
        Base.metadata.drop_all(bind=engine)
        init_db()
    else:
        init_db()
