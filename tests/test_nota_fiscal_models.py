import pytest
from pydantic import ValidationError
from datetime import datetime, date

from app.models.nota_fiscal import NotaFiscal
from app.schemas.nota_fiscal import (
    NotaFiscalCreate, 
    NotaFiscalResponse, 
    NotaFiscalUpdate,
    CategoriaEnum
)


class TestNotaFiscalSchemas:

    def test_create_valid(self):
        data = {
            "valor_total": 500.0,
            "data": date(2024, 1, 15),
            "empresa": "Empresa Teste"
        }
        nota = NotaFiscalCreate(**data)
        assert nota.valor_total == 500.0
        assert nota.data == date(2024, 1, 15)
        assert nota.empresa == "Empresa Teste"
        assert nota.categoria is None

    def test_create_with_categoria(self):
        data = {
            "valor_total": 500.0,
            "data": date(2024, 1, 15),
            "empresa": "Empresa Teste",
            "categoria": CategoriaEnum.AGUA_MINERAL
        }
        nota = NotaFiscalCreate(**data)
        assert nota.categoria == CategoriaEnum.AGUA_MINERAL

    def test_create_invalid_valor_total_negative(self):
        data = {
            "valor_total": -10,
            "data": date(2024, 1, 15),
            "empresa": "Empresa Teste"
        }
        with pytest.raises(ValidationError):
            NotaFiscalCreate(**data)

    def test_create_invalid_valor_total_zero(self):
        data = {
            "valor_total": 0,
            "data": date(2024, 1, 15),
            "empresa": "Empresa Teste"
        }
        with pytest.raises(ValidationError):
            NotaFiscalCreate(**data)

    def test_create_invalid_categoria(self):
        data = {
            "valor_total": 500.0,
            "data": date(2024, 1, 15),
            "empresa": "Empresa Teste",
            "categoria": "Categoria Inválida"
        }
        with pytest.raises(ValidationError):
            NotaFiscalCreate(**data)

    def test_create_missing_valor_total(self):
        data = {
            "data": date(2024, 1, 15),
            "empresa": "Empresa Teste"
        }
        with pytest.raises(ValidationError):
            NotaFiscalCreate(**data)

    def test_create_missing_data(self):
        data = {
            "valor_total": 500.0,
            "empresa": "Empresa Teste"
        }
        with pytest.raises(ValidationError):
            NotaFiscalCreate(**data)

    def test_create_missing_empresa(self):
        data = {
            "valor_total": 500.0,
            "data": date(2024, 1, 15)
        }
        with pytest.raises(ValidationError):
            NotaFiscalCreate(**data)

    def test_update_partial_valor(self):
        data = {"valor_total": 800.0}
        update = NotaFiscalUpdate(**data)
        assert update.valor_total == 800.0
        assert update.empresa is None
        assert update.data is None
        assert update.categoria is None

    def test_update_partial_empresa(self):
        data = {"empresa": "Nova Empresa"}
        update = NotaFiscalUpdate(**data)
        assert update.empresa == "Nova Empresa"
        assert update.valor_total is None

    def test_update_partial_categoria(self):
        data = {"categoria": CategoriaEnum.AGUA_MINERAL}
        update = NotaFiscalUpdate(**data)
        assert update.categoria == CategoriaEnum.AGUA_MINERAL

    def test_update_multiple_fields(self):
        data = {
            "valor_total": 800.0,
            "empresa": "Nova Empresa",
            "categoria": CategoriaEnum.BEBIDAS_NAO_ALCOOLICAS
        }
        update = NotaFiscalUpdate(**data)
        assert update.valor_total == 800.0
        assert update.empresa == "Nova Empresa"
        assert update.categoria == CategoriaEnum.BEBIDAS_NAO_ALCOOLICAS
        assert update.data is None

    def test_update_invalid_valor_negative(self):
        with pytest.raises(ValidationError):
            NotaFiscalUpdate(valor_total=-1)

    def test_update_invalid_valor_zero(self):
        with pytest.raises(ValidationError):
            NotaFiscalUpdate(valor_total=0)

    def test_update_invalid_categoria(self):
        with pytest.raises(ValidationError):
            NotaFiscalUpdate(categoria="Categoria Inválida")

    def test_update_all_fields_none(self):
        update = NotaFiscalUpdate()
        assert update.valor_total is None
        assert update.data is None
        assert update.empresa is None
        assert update.categoria is None

    def test_response_valid(self):
        model_data = {
            "id": 1,
            "user_id": 10,
            "valor_total": 500.0,
            "data": date(2024, 1, 15),
            "empresa": "Empresa Teste",
            "arquivo_nome": "nota.pdf",
            "arquivo_tipo": "application/pdf",
            "arquivo_tamanho": 12345,
            "created_at": datetime.now()
        }
        resp = NotaFiscalResponse(**model_data)

        assert resp.id == 1
        assert resp.user_id == 10
        assert resp.valor_total == 500.0
        assert resp.empresa == "Empresa Teste"
        assert resp.arquivo_nome == "nota.pdf"
        assert resp.categoria is None
        assert isinstance(resp.created_at, datetime)

    def test_response_with_categoria(self):
        model_data = {
            "id": 1,
            "user_id": 10,
            "valor_total": 500.0,
            "data": date(2024, 1, 15),
            "empresa": "Empresa Teste",
            "arquivo_nome": "nota.pdf",
            "arquivo_tipo": "application/pdf",
            "arquivo_tamanho": 12345,
            "categoria": "Água Mineral",
            "created_at": datetime.now()
        }
        resp = NotaFiscalResponse(**model_data)

        assert resp.id == 1
        assert resp.categoria == "Água Mineral"

    def test_categoria_enum_values(self):
        assert CategoriaEnum.AGUA_MINERAL == "Água Mineral"
        assert CategoriaEnum.AGUA_SANEAMENTO == "Água e Saneamento"
        assert CategoriaEnum.CALCADOS == "Calçados"
        assert CategoriaEnum.EQUIP_TI == "Equipamentos de TI"

    def test_categoria_enum_count(self):
        assert len(CategoriaEnum) == 99


class TestNotaFiscalModel:

    def test_model_repr(self):
        nota = NotaFiscal(
            id=1,
            user_id=2,
            valor_total=150.0,
            data=datetime(2024, 1, 15),
            empresa="Empresa Teste",
            arquivo_nome="nota.pdf",
            arquivo_tipo="application/pdf",
            arquivo_tamanho=12345,
            categoria=None
        )
        expected = "<NotaFiscal(id=1, user_id=2, valor_total=150.0, categoria=None, arquivo=nota.pdf)>"
        assert repr(nota) == expected

    def test_model_repr_with_categoria(self):
        nota = NotaFiscal(
            id=1,
            user_id=2,
            valor_total=150.0,
            data=datetime(2024, 1, 15),
            empresa="Empresa Teste",
            arquivo_nome="nota.pdf",
            arquivo_tipo="application/pdf",
            arquivo_tamanho=12345,
            categoria="Alimentação"
        )
        expected = "<NotaFiscal(id=1, user_id=2, valor_total=150.0, categoria=Alimentação, arquivo=nota.pdf)>"
        assert repr(nota) == expected

    def test_default_values(self):
        nota = NotaFiscal(
            user_id=1,
            valor_total=500.0,
            data=datetime(2024, 1, 15),
            empresa="Empresa",
            arquivo_nome="nota.pdf",
            arquivo_tipo="application/pdf",
            arquivo_tamanho=1000
        )
        assert nota.created_at is None
        assert nota.categoria is None

    def test_model_with_all_fields(self):
        nota = NotaFiscal(
            id=5,
            user_id=3,
            valor_total=1500.0,
            data=datetime(2024, 2, 20),
            empresa="Google Brasil",
            arquivo_nome="nota.pdf",
            arquivo_tipo="application/pdf",
            arquivo_tamanho=25000,
            categoria="Serviços Digitais",
            created_at=datetime(2024, 2, 20, 10, 30, 0)
        )
        assert nota.id == 5
        assert nota.user_id == 3
        assert nota.valor_total == 1500.0
        assert nota.empresa == "Google Brasil"
        assert nota.categoria == "Serviços Digitais"
        assert nota.arquivo_nome == "nota.pdf"
        assert nota.created_at is not None
        
    def test_create_with_cnpj_valid(self):
        data = {
            "valor_total": 500.0,
            "data": date(2024, 1, 15),
            "empresa": "Empresa Teste",
            "cnpj": "06.990.590/0001-23"
        }
        nota = NotaFiscalCreate(**data)
        assert nota.cnpj == "06.990.590/0001-23"