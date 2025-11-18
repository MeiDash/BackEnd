"""
Testes para modelos e schemas de usuário
"""
import pytest
from pydantic import ValidationError
from app.schemas.user import UserCreate, UserUpdate, UserResponse, UserLogin
from app.models.user import User
from datetime import datetime


class TestUserSchemas:
    """Testes para schemas Pydantic de usuário"""

    def test_user_create_valid(self):
        """Testa criação de UserCreate com dados válidos"""
        data = {
            "email": "test@example.com",
            "name": "Test User",
            "password": "password123",
            "nome_empresa": "Test Company",
            "cnpj": "12345678000123",
            "occupation": "Developer"
        }
        user = UserCreate(**data)
        assert user.email == "test@example.com"
        assert user.name == "Test User"
        assert user.password == "password123"
        assert user.nome_empresa == "Test Company"
        assert user.cnpj == "12345678000123"
        assert user.occupation == "Developer"

    def test_user_create_minimal(self):
        """Testa criação de UserCreate com dados mínimos"""
        data = {
            "email": "test@example.com",
            "name": "Test User",
            "password": "password123"
        }
        user = UserCreate(**data)
        assert user.email == "test@example.com"
        assert user.name == "Test User"
        assert user.password == "password123"
        assert user.nome_empresa is None
        assert user.cnpj is None
        assert user.occupation is None

    def test_user_create_invalid_email(self):
        """Testa criação de UserCreate com email inválido"""
        data = {
            "email": "invalid-email",
            "name": "Test User",
            "password": "password123"
        }
        with pytest.raises(ValidationError):
            UserCreate(**data)

    def test_user_create_short_password(self):
        """Testa criação de UserCreate com senha curta"""
        data = {
            "email": "test@example.com",
            "name": "Test User",
            "password": "123"
        }
        with pytest.raises(ValidationError):
            UserCreate(**data)

    def test_user_create_empty_name(self):
        """Testa criação de UserCreate com nome vazio"""
        data = {
            "email": "test@example.com",
            "name": "",
            "password": "password123"
        }
        with pytest.raises(ValidationError):
            UserCreate(**data)

    def test_user_create_long_name(self):
        """Testa criação de UserCreate com nome muito longo"""
        data = {
            "email": "test@example.com",
            "name": "A" * 121,  # Maior que 120 caracteres
            "password": "password123"
        }
        with pytest.raises(ValidationError):
            UserCreate(**data)

    def test_user_update_partial(self):
        """Testa atualização parcial de usuário"""
        data = {
            "name": "Updated Name",
            "occupation": "Manager"
        }
        update = UserUpdate(**data)
        assert update.name == "Updated Name"
        assert update.occupation == "Manager"
        assert update.email is None
        assert update.password is None

    def test_user_update_empty(self):
        """Testa atualização vazia"""
        update = UserUpdate()
        assert update.name is None
        assert update.email is None
        assert update.password is None

    def test_user_response_from_model(self):
        """Testa criação de UserResponse a partir de modelo"""
        # Simular dados de um modelo
        model_data = {
            "id": 1,
            "email": "test@example.com",
            "name": "Test User",
            "is_active": True,
            "nome_empresa": "Test Company",
            "cnpj": "12345678000123",
            "occupation": "Developer",
            "created_at": datetime.now(),
            "updated_at": None
        }

        response = UserResponse(**model_data)
        assert response.id == 1
        assert response.email == "test@example.com"
        assert response.name == "Test User"
        assert response.is_active is True
        assert response.nome_empresa == "Test Company"
        assert response.cnpj == "12345678000123"
        assert response.occupation == "Developer"
        assert isinstance(response.created_at, datetime)

    def test_user_login_valid(self):
        """Testa UserLogin com dados válidos"""
        data = {
            "email": "login@example.com",
            "password": "password123"
        }
        login = UserLogin(**data)
        assert login.email == "login@example.com"
        assert login.password == "password123"

    def test_user_login_invalid_email(self):
        """Testa UserLogin com email inválido"""
        data = {
            "email": "invalid-email",
            "password": "password123"
        }
        with pytest.raises(ValidationError):
            UserLogin(**data)


class TestUserModel:
    """Testes para o modelo User"""

    def test_user_repr(self):
        """Testa representação string do modelo User"""
        user = User(
            id=1,
            email="test@example.com",
            name="Test User",
            hashed_password="hashed_password",
            is_active=True
        )
        expected_repr = "<User(id=1, email=test@example.com, name=Test User)>"
        assert repr(user) == expected_repr

    def test_user_default_values(self):
        """Testa valores padrão do modelo User"""
        user = User(
            email="test@example.com",
            name="Test User",
            hashed_password="hashed_password"
        )
        # Valores que são None por padrão
        assert user.nome_empresa is None
        assert user.cnpj is None
        assert user.occupation is None
        # is_active pode ser None até ser persistido no banco