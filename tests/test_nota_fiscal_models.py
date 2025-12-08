import pytest
from pydantic import ValidationError
from datetime import datetime, date

from app.models.nota_fiscal import NotaFiscal
from app.schemas.nota_fiscal import NotaFiscalCreate, NotaFiscalResponse, NotaFiscalUpdate



class TestNotaFiscalSchemas:

    def test_create_valid(self):
        """Testa criação de NotaFiscalCreate com dados válidos"""
        data = {
            "valor_total": 500.0,
            "data": date(2024, 1, 15),
            "empresa": "Empresa Teste",
            "url": "https://example.com/nota.pdf"
        }
        nota = NotaFiscalCreate(**data)
        assert nota.valor_total == 500.0
        assert nota.data == date(2024, 1, 15)
        assert nota.empresa == "Empresa Teste"
        assert nota.url == "https://example.com/nota.pdf"

    def test_create_invalid_valor_total(self):
        """Testa criação com valor_total inválido"""
        data = {
            "valor_total": -10,
            "data": date(2024, 1, 15),
            "empresa": "Empresa Teste",
            "url": "https://example.com/nota.pdf"
        }
        with pytest.raises(ValidationError):
            NotaFiscalCreate(**data)

    def test_create_missing_fields(self):
        """Testa tentativa de criação faltando campos obrigatórios"""
        data = {
            "valor_total": 500.0
        }
        with pytest.raises(ValidationError):
            NotaFiscalCreate(**data)

    def test_update_partial(self):
        """Testa atualização parcial com NotaFiscalUpdate"""
        data = {
            "valor_total": 800.0,
            "empresa": "Nova Empresa"
        }
        update = NotaFiscalUpdate(**data)
        assert update.valor_total == 800.0
        assert update.empresa == "Nova Empresa"
        assert update.data is None
        assert update.url is None

    def test_update_invalid_valor(self):
        """Testa valor_total inválido em update"""
        with pytest.raises(ValidationError):
            NotaFiscalUpdate(valor_total=-1)

    def test_response_valid(self):
        """Testa criação de NotaFiscalResponse válida"""
        model_data = {
            "id": 1,
            "user_id": 10,
            "valor_total": 500.0,
            "data": date(2024, 1, 15),
            "empresa": "Empresa Teste",
            "url": "https://example.com/nota.pdf",
            "created_at": datetime.now()
        }
        resp = NotaFiscalResponse(**model_data)

        assert resp.id == 1
        assert resp.user_id == 10
        assert resp.valor_total == 500.0
        assert resp.empresa == "Empresa Teste"
        assert isinstance(resp.created_at, datetime)


class TestNotaFiscalModel:

    def test_model_repr(self):
        """Testa a representação string do modelo NotaFiscal"""
        nota = NotaFiscal(
            id=1,
            user_id=2,
            valor_total=150.0,
            data=datetime(2024, 1, 15),
            empresa="Empresa Teste",
            url="https://example.com"
        )
        expected = "<NotaFiscal(id=1, user_id=2, valor_total=150.0)>"
        assert repr(nota) == expected

    def test_default_values(self):
        """Testa valores padrão do modelo NotaFiscal"""
        nota = NotaFiscal(
            user_id=1,
            valor_total=500.0,
            data=datetime(2024, 1, 15),
            empresa="Empresa",
            url="a.pdf"
        )
        # created_at será gerado pelo DB, logo aqui pode ser None
        assert nota.created_at is None
