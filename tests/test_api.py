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

    def test_login_success(self, test_client):
        """Testa login com credenciais válidas"""
        # Primeiro criar um usuário
        create_response = test_client.post(
            "/api/users",
            json={
                "email": "login@example.com",
                "name": "Login User",
                "password": "password123"
            }
        )
        assert create_response.status_code == 201

        # Agora fazer login
        login_response = test_client.post(
            "/api/auth/login",
            json={
                "email": "login@example.com",
                "password": "password123"
            }
        )
        assert login_response.status_code == 200
        data = login_response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "expires_in" in data

    def test_logout(self, test_client):
        """Testa logout"""
        response = test_client.post("/api/auth/logout")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "Logout realizado com sucesso" in data["message"]


class TestUsers:
    """Testes de usuários"""

    def test_get_users_empty(self, test_client):
        """Testa obtenção de lista vazia de usuários"""
        response = test_client.get("/api/users")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
        assert len(response.json()) == 0

    def test_get_nonexistent_user(self, test_client):
        """Testa obtenção de usuário que não existe"""
        response = test_client.get("/api/users/999")
        assert response.status_code == 404
        data = response.json()
        assert "Usuário não encontrado" in data["detail"]

    def test_create_user_success(self, test_client):
        """Testa criação de usuário com sucesso"""
        user_data = {
            "email": "test@example.com",
            "name": "Test User",
            "password": "password123",
            "nome_empresa": "Test Company",
            "cnpj": "12345678000123",
            "occupation": "Developer"
        }
        response = test_client.post("/api/users", json=user_data)
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "test@example.com"
        assert data["name"] == "Test User"
        assert data["nome_empresa"] == "Test Company"
        assert data["cnpj"] == "12345678000123"
        assert data["occupation"] == "Developer"
        assert data["is_active"] is True
        assert "id" in data
        assert "created_at" in data

    def test_create_user_duplicate_email(self, test_client):
        """Testa criação de usuário com email duplicado"""
        user_data = {
            "email": "duplicate@example.com",
            "name": "First User",
            "password": "password123"
        }
        # Criar primeiro usuário
        response1 = test_client.post("/api/users", json=user_data)
        assert response1.status_code == 201

        # Tentar criar segundo com mesmo email
        user_data["name"] = "Second User"
        response2 = test_client.post("/api/users", json=user_data)
        assert response2.status_code == 400
        data = response2.json()
        assert "Email ou name já registrado" in data["detail"]

    def test_get_user_by_id(self, test_client):
        """Testa obtenção de usuário por ID"""
        # Criar usuário
        create_data = {
            "email": "get@example.com",
            "name": "Get User",
            "password": "password123"
        }
        create_response = test_client.post("/api/users", json=create_data)
        assert create_response.status_code == 201
        user_id = create_response.json()["id"]

        # Obter usuário
        get_response = test_client.get(f"/api/users/{user_id}")
        assert get_response.status_code == 200
        data = get_response.json()
        assert data["id"] == user_id
        assert data["email"] == "get@example.com"
        assert data["name"] == "Get User"

    def test_get_users_with_pagination(self, test_client):
        """Testa obtenção de usuários com paginação"""
        # Criar vários usuários
        for i in range(5):
            user_data = {
                "email": f"user{i}@example.com",
                "name": f"User {i}",
                "password": "password123"
            }
            response = test_client.post("/api/users", json=user_data)
            assert response.status_code == 201

        # Testar paginação
        response = test_client.get("/api/users?skip=2&limit=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    def test_update_user_success(self, test_client):
        """Testa atualização de usuário com sucesso"""
        # Criar usuário
        create_data = {
            "email": "update@example.com",
            "name": "Update User",
            "password": "password123"
        }
        create_response = test_client.post("/api/users", json=create_data)
        assert create_response.status_code == 201
        user_id = create_response.json()["id"]

        # Atualizar usuário
        update_data = {
            "name": "Updated User",
            "occupation": "Manager"
        }
        update_response = test_client.put(f"/api/users/{user_id}", json=update_data)
        assert update_response.status_code == 200
        data = update_response.json()
        assert data["name"] == "Updated User"
        assert data["occupation"] == "Manager"
        assert data["email"] == "update@example.com"  # Não mudou

    def test_update_user_email_duplicate(self, test_client):
        """Testa atualização de usuário com email duplicado"""
        # Criar dois usuários
        user1_data = {
            "email": "user1@example.com",
            "name": "User 1",
            "password": "password123"
        }
        user2_data = {
            "email": "user2@example.com",
            "name": "User 2",
            "password": "password123"
        }
        test_client.post("/api/users", json=user1_data)
        create2_response = test_client.post("/api/users", json=user2_data)
        user2_id = create2_response.json()["id"]

        # Tentar atualizar user2 com email de user1
        update_response = test_client.put(
            f"/api/users/{user2_id}",
            json={"email": "user1@example.com"}
        )
        assert update_response.status_code == 400
        data = update_response.json()
        assert "Email já registrado" in data["detail"]

    def test_update_nonexistent_user(self, test_client):
        """Testa atualização de usuário inexistente"""
        update_data = {"name": "New Name"}
        response = test_client.put("/api/users/999", json=update_data)
        assert response.status_code == 404
        data = response.json()
        assert "Usuário não encontrado" in data["detail"]

    def test_delete_user_success(self, test_client):
        """Testa exclusão de usuário com sucesso"""
        # Criar usuário
        create_data = {
            "email": "delete@example.com",
            "name": "Delete User",
            "password": "password123"
        }
        create_response = test_client.post("/api/users", json=create_data)
        assert create_response.status_code == 201
        user_id = create_response.json()["id"]

        # Deletar usuário
        delete_response = test_client.delete(f"/api/users/{user_id}")
        assert delete_response.status_code == 204

        # Verificar se foi removido (soft delete)
        get_response = test_client.get(f"/api/users/{user_id}")
        assert get_response.status_code == 200
        data = get_response.json()
        assert data["is_active"] is False

    def test_delete_nonexistent_user(self, test_client):
        """Testa exclusão de usuário inexistente"""
        response = test_client.delete("/api/users/999")
        assert response.status_code == 404
        data = response.json()
        assert "Usuário não encontrado" in data["detail"]

    def test_create_user_validation_error(self, test_client):
        """Testa criação de usuário com dados inválidos"""
        # Email inválido
        invalid_data = {
            "email": "invalid-email",
            "name": "",
            "password": "123"
        }
        response = test_client.post("/api/users", json=invalid_data)
        assert response.status_code == 422  # Validation error

    def test_update_user_validation_error(self, test_client):
        """Testa atualização de usuário com dados inválidos"""
        # Criar usuário válido
        create_data = {
            "email": "valid@example.com",
            "name": "Valid User",
            "password": "password123"
        }
        create_response = test_client.post("/api/users", json=create_data)
        user_id = create_response.json()["id"]

        # Tentar atualizar com dados inválidos
        invalid_update = {
            "name": "",  # Nome vazio
            "password": "12"  # Senha muito curta
        }
        response = test_client.put(f"/api/users/{user_id}", json=invalid_update)
        assert response.status_code == 422  # Validation error
