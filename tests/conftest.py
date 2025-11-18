"""
Configuração do pytest
"""
import pytest
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db import Base, get_db
from app.main import app as fastapi_app

# Definir variável de ambiente para testes
os.environ["TESTING"] = "1"


# Engine de teste (SQLite em memória)
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def test_db():
    """Cria banco de dados de teste"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session(test_db):
    """Cria sessão de banco de dados para testes"""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="function")
def test_client(test_db):
    """Cria cliente de teste FastAPI"""
    from fastapi.testclient import TestClient
    from passlib.context import CryptContext

    # Sobrescrever o contexto de criptografia para usar plaintext nos testes
    import app.core.security
    app.core.security.pwd_context = CryptContext(schemes=["plaintext"], deprecated="auto")

    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()

    fastapi_app.dependency_overrides[get_db] = override_get_db
    client = TestClient(fastapi_app)
    return client