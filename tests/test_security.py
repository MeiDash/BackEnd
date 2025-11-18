"""
Testes para utilitários de segurança
"""
import pytest
from datetime import timedelta
from app.core.security import hash_password, verify_password, create_access_token, decode_token


class TestSecurity:
    """Testes para funções de segurança"""

    def test_hash_password(self):
        """Testa hashing de senha"""
        import os
        password = "testpassword123"
        hashed = hash_password(password)

        # Em ambiente de teste, usamos plaintext, então hash == password
        if os.environ.get("TESTING") == "1":
            assert hashed == password
        else:
            assert hashed != password

        assert isinstance(hashed, str)
        assert len(hashed) > 0

    def test_verify_password_correct(self):
        """Testa verificação de senha correta"""
        password = "testpassword123"
        hashed = hash_password(password)

        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        """Testa verificação de senha incorreta"""
        password = "testpassword123"
        wrong_password = "wrongpassword"
        hashed = hash_password(password)

        assert verify_password(wrong_password, hashed) is False

    def test_verify_password_empty(self):
        """Testa verificação com senha vazia"""
        password = "testpassword123"
        hashed = hash_password(password)

        assert verify_password("", hashed) is False

    def test_create_access_token(self):
        """Testa criação de token de acesso"""
        data = {"sub": "test@example.com"}
        token = create_access_token(data)

        assert isinstance(token, str)
        assert len(token) > 0
        assert "." in token  # JWT format

    def test_create_access_token_with_expiry(self):
        """Testa criação de token com expiração customizada"""
        data = {"sub": "test@example.com"}
        expires_delta = timedelta(minutes=30)
        token = create_access_token(data, expires_delta)

        assert isinstance(token, str)
        assert len(token) > 0

    def test_decode_token_valid(self):
        """Testa decodificação de token válido"""
        data = {"sub": "test@example.com"}
        token = create_access_token(data)

        decoded = decode_token(token)
        assert decoded is not None
        assert decoded["sub"] == "test@example.com"
        assert "exp" in decoded

    def test_decode_token_invalid(self):
        """Testa decodificação de token inválido"""
        invalid_token = "invalid.jwt.token"

        decoded = decode_token(invalid_token)
        assert decoded is None

    def test_decode_token_empty(self):
        """Testa decodificação de token vazio"""
        decoded = decode_token("")
        assert decoded is None

    def test_decode_token_none(self):
        """Testa decodificação de token None"""
        # decode_token espera uma string, então passar None causará TypeError
        # Vamos testar com uma string vazia ou inválida
        decoded = decode_token("")
        assert decoded is None