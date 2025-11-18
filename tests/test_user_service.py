"""
Testes unitários para o serviço de usuários
"""
import pytest
from sqlalchemy.orm import Session
from app.models import User
from app.schemas import UserCreate, UserUpdate
from app.services.user_service import UserService
from app.core.security import hash_password, verify_password


class TestUserService:
    """Testes para UserService"""

    def test_get_user_by_email_existing(self, test_db, db_session):
        """Testa obtenção de usuário por email existente"""
        # Criar usuário de teste
        user_data = UserCreate(
            email="test@example.com",
            name="Test User",
            password="password123"
        )
        created_user = UserService.create_user(db_session, user_data)

        # Buscar por email
        user = UserService.get_user_by_email(db_session, "test@example.com")
        assert user is not None
        assert user.email == "test@example.com"
        assert user.name == "Test User"

    def test_get_user_by_email_nonexistent(self, test_db, db_session):
        """Testa obtenção de usuário por email inexistente"""
        user = UserService.get_user_by_email(db_session, "nonexistent@example.com")
        assert user is None

    def test_get_user_by_username_existing(self, test_db, db_session):
        """Testa obtenção de usuário por username existente"""
        user_data = UserCreate(
            email="test@example.com",
            name="Test User",
            password="password123"
        )
        created_user = UserService.create_user(db_session, user_data)

        user = UserService.get_user_by_username(db_session, "Test User")
        assert user is not None
        assert user.name == "Test User"

    def test_get_user_by_username_nonexistent(self, test_db, db_session):
        """Testa obtenção de usuário por username inexistente"""
        user = UserService.get_user_by_username(db_session, "Nonexistent User")
        assert user is None

    def test_get_user_by_id_existing(self, test_db, db_session):
        """Testa obtenção de usuário por ID existente"""
        user_data = UserCreate(
            email="test@example.com",
            name="Test User",
            password="password123"
        )
        created_user = UserService.create_user(db_session, user_data)

        user = UserService.get_user_by_id(db_session, created_user.id)
        assert user is not None
        assert user.id == created_user.id

    def test_get_user_by_id_nonexistent(self, test_db, db_session):
        """Testa obtenção de usuário por ID inexistente"""
        user = UserService.get_user_by_id(db_session, 999)
        assert user is None

    def test_get_all_users_empty(self, test_db, db_session):
        """Testa obtenção de todos os usuários quando vazio"""
        users = UserService.get_all_users(db_session)
        assert users == []

    def test_get_all_users_with_data(self, test_db, db_session):
        """Testa obtenção de todos os usuários com dados"""
        # Criar usuários de teste
        for i in range(3):
            user_data = UserCreate(
                email=f"user{i}@example.com",
                name=f"User {i}",
                password="password123"
            )
            UserService.create_user(db_session, user_data)

        users = UserService.get_all_users(db_session)
        assert len(users) == 3

    def test_get_all_users_pagination(self, test_db, db_session):
        """Testa paginação na obtenção de usuários"""
        # Criar 5 usuários
        for i in range(5):
            user_data = UserCreate(
                email=f"user{i}@example.com",
                name=f"User {i}",
                password="password123"
            )
            UserService.create_user(db_session, user_data)

        # Testar paginação
        users = UserService.get_all_users(db_session, skip=2, limit=2)
        assert len(users) == 2

    def test_get_all_users_filter_active(self, test_db, db_session):
        """Testa filtro por usuários ativos"""
        # Criar usuários ativos e inativos
        active_user = UserCreate(
            email="active@example.com",
            name="Active User",
            password="password123"
        )
        UserService.create_user(db_session, active_user)

        inactive_user = UserCreate(
            email="inactive@example.com",
            name="Inactive User",
            password="password123"
        )
        created_inactive = UserService.create_user(db_session, inactive_user)
        UserService.delete_user(db_session, created_inactive.id)  # Soft delete

        # Testar filtro ativo
        active_users = UserService.get_all_users(db_session, is_active=True)
        assert len(active_users) == 1
        assert active_users[0].email == "active@example.com"

        # Testar filtro inativo
        inactive_users = UserService.get_all_users(db_session, is_active=False)
        assert len(inactive_users) == 1
        assert inactive_users[0].email == "inactive@example.com"

    def test_create_user_success(self, test_db, db_session):
        """Testa criação de usuário com sucesso"""
        user_data = UserCreate(
            email="newuser@example.com",
            name="New User",
            password="password123",
            nome_empresa="Test Company",
            cnpj="12345678000123",
            occupation="Developer"
        )

        user = UserService.create_user(db_session, user_data)

        assert user.email == "newuser@example.com"
        assert user.name == "New User"
        assert user.nome_empresa == "Test Company"
        assert user.cnpj == "12345678000123"
        assert user.occupation == "Developer"
        assert user.is_active is True
        assert verify_password("password123", user.hashed_password)

    def test_update_user_success(self, test_db, db_session):
        """Testa atualização de usuário com sucesso"""
        # Criar usuário
        user_data = UserCreate(
            email="update@example.com",
            name="Update User",
            password="password123"
        )
        created_user = UserService.create_user(db_session, user_data)

        # Atualizar dados
        update_data = UserUpdate(
            name="Updated User",
            email="updated@example.com",
            password="newpassword123",
            occupation="Manager"
        )

        updated_user = UserService.update_user(db_session, created_user.id, update_data)

        assert updated_user is not None
        assert updated_user.name == "Updated User"
        assert updated_user.email == "updated@example.com"
        assert updated_user.occupation == "Manager"
        assert verify_password("newpassword123", updated_user.hashed_password)

    def test_update_user_nonexistent(self, test_db, db_session):
        """Testa atualização de usuário inexistente"""
        update_data = UserUpdate(name="New Name")
        result = UserService.update_user(db_session, 999, update_data)
        assert result is None

    def test_delete_user_success(self, test_db, db_session):
        """Testa exclusão de usuário com sucesso"""
        # Criar usuário
        user_data = UserCreate(
            email="delete@example.com",
            name="Delete User",
            password="password123"
        )
        created_user = UserService.create_user(db_session, user_data)

        # Deletar
        success = UserService.delete_user(db_session, created_user.id)
        assert success is True

        # Verificar se foi desativado
        user = UserService.get_user_by_id(db_session, created_user.id)
        assert user.is_active is False

    def test_delete_user_nonexistent(self, test_db, db_session):
        """Testa exclusão de usuário inexistente"""
        success = UserService.delete_user(db_session, 999)
        assert success is False

    def test_authenticate_user_success(self, test_db, db_session):
        """Testa autenticação de usuário com sucesso"""
        # Criar usuário
        user_data = UserCreate(
            email="auth@example.com",
            name="Auth User",
            password="password123"
        )
        UserService.create_user(db_session, user_data)

        # Autenticar
        user = UserService.authenticate_user(db_session, "auth@example.com", "password123")
        assert user is not None
        assert user.email == "auth@example.com"

    def test_authenticate_user_wrong_password(self, test_db, db_session):
        """Testa autenticação com senha incorreta"""
        # Criar usuário
        user_data = UserCreate(
            email="auth@example.com",
            name="Auth User",
            password="password123"
        )
        UserService.create_user(db_session, user_data)

        # Tentar autenticar com senha errada
        user = UserService.authenticate_user(db_session, "auth@example.com", "wrongpassword")
        assert user is None

    def test_authenticate_user_inactive(self, test_db, db_session):
        """Testa autenticação de usuário inativo"""
        # Criar e desativar usuário
        user_data = UserCreate(
            email="inactive@example.com",
            name="Inactive User",
            password="password123"
        )
        created_user = UserService.create_user(db_session, user_data)
        UserService.delete_user(db_session, created_user.id)

        # Tentar autenticar
        user = UserService.authenticate_user(db_session, "inactive@example.com", "password123")
        assert user is None

    def test_authenticate_user_nonexistent(self, test_db, db_session):
        """Testa autenticação de usuário inexistente"""
        user = UserService.authenticate_user(db_session, "nonexistent@example.com", "password123")
        assert user is None

    def test_user_exists_by_email(self, test_db, db_session):
        """Testa verificação de existência por email"""
        # Criar usuário
        user_data = UserCreate(
            email="exists@example.com",
            name="Exists User",
            password="password123"
        )
        UserService.create_user(db_session, user_data)

        # Verificar existência
        exists = UserService.user_exists(db_session, email="exists@example.com")
        assert exists is True

        exists = UserService.user_exists(db_session, email="nonexistent@example.com")
        assert exists is False

    def test_user_exists_by_username(self, test_db, db_session):
        """Testa verificação de existência por username"""
        # Criar usuário
        user_data = UserCreate(
            email="exists@example.com",
            name="Exists User",
            password="password123"
        )
        UserService.create_user(db_session, user_data)

        # Verificar existência
        exists = UserService.user_exists(db_session, username="Exists User")
        assert exists is True

        exists = UserService.user_exists(db_session, username="Nonexistent User")
        assert exists is False

    def test_user_exists_no_filters(self, test_db, db_session):
        """Testa verificação de existência sem filtros"""
        exists = UserService.user_exists(db_session)
        assert exists is False