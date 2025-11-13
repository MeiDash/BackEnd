"""
Configuração e inicialização do banco de dados
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.config import settings

# Criar engine do banco de dados
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.ENVIRONMENT == "development",
    pool_pre_ping=True,
)

# Criar session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base para todos os modelos
Base = declarative_base()


def get_db():
    """
    Dependency para obter a sessão do banco de dados
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
