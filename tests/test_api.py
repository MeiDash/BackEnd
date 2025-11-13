"""
Testes da API de usuários
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root():
    """Testa endpoint raiz"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "Bem-vindo ao Backend API"


def test_health_check():
    """Testa health check"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


class TestAuth:
    """Testes de autenticação"""
    
    def test_login_invalid_credentials(self):
        """Testa login com credenciais inválidas"""
        response = client.post(
            "/api/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "password123"
            }
        )
        assert response.status_code == 401


class TestUsers:
    """Testes de usuários"""
    
    def test_get_users_empty(self):
        """Testa obtenção de lista vazia de usuários"""
        response = client.get("/api/users")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_get_nonexistent_user(self):
        """Testa obtenção de usuário que não existe"""
        response = client.get("/api/users/999")
        assert response.status_code == 404
