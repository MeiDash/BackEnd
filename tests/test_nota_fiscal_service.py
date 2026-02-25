import pytest
from datetime import date, datetime
from sqlalchemy.orm import Session
from app.models import User
from app.models.nota_fiscal import NotaFiscal, Metrica
from app.schemas import UserCreate
from fastapi import HTTPException
from app.schemas.nota_fiscal import NotaFiscalCreate, NotaFiscalUpdate, CategoriaEnum
from app.services.user_service import UserService
from app.services.nota_fiscal_service import FiscalService


class TestFiscalService:

    @pytest.fixture
    def test_user(self, test_db, db_session):
        user_data = UserCreate(
            email="testuser@example.com",
            name="Test User",
            password="password123"
        )
        return UserService.create_user(db_session, user_data)

    def test_get_nota_fiscal_by_id_existing(self, test_db, db_session, test_user):
        nota_data = NotaFiscalCreate(
            valor_total=1000.00,
            data=date(2024, 1, 15),
            empresa="Empresa Teste LTDA",
            url="https://example.com/nota1.pdf"
        )
        created_nota = FiscalService.create_nota_fiscal(db_session, test_user.id, nota_data)

        nota = FiscalService.get_nota_fiscal_by_id(db_session, created_nota.id, test_user.id)
        assert nota is not None
        assert nota.id == created_nota.id
        assert nota.valor_total == 1000.00
        assert nota.empresa == "Empresa Teste LTDA"

    def test_get_nota_fiscal_by_id_nonexistent(self, test_db, db_session, test_user):
        nota = FiscalService.get_nota_fiscal_by_id(db_session, 999, test_user.id)
        assert nota is None

    def test_get_nota_fiscal_by_id_wrong_user(self, test_db, db_session, test_user):
        other_user_data = UserCreate(
            email="other@example.com",
            name="Other User",
            password="password123"
        )
        other_user = UserService.create_user(db_session, other_user_data)

        nota_data = NotaFiscalCreate(
            valor_total=1000.00,
            data=date(2024, 1, 15),
            empresa="Empresa Teste LTDA",
            url="https://example.com/nota1.pdf"
        )
        created_nota = FiscalService.create_nota_fiscal(db_session, test_user.id, nota_data)

        nota = FiscalService.get_nota_fiscal_by_id(db_session, created_nota.id, other_user.id)
        assert nota is None

    def test_get_all_notas_fiscais_empty(self, test_db, db_session, test_user):
        notas = FiscalService.get_all_notas_fiscais(db_session, test_user.id)
        assert notas == []

    def test_get_all_notas_fiscais_with_data(self, test_db, db_session, test_user):
        for i in range(3):
            nota_data = NotaFiscalCreate(
                valor_total=1000.00 * (i + 1),
                data=date(2024, 1, i + 1),
                empresa=f"Empresa {i} LTDA",
                url=f"https://example.com/nota{i}.pdf"
            )
            FiscalService.create_nota_fiscal(db_session, test_user.id, nota_data)

        notas = FiscalService.get_all_notas_fiscais(db_session, test_user.id)
        assert len(notas) == 3

    def test_get_all_notas_fiscais_pagination(self, test_db, db_session, test_user):
        for i in range(5):
            nota_data = NotaFiscalCreate(
                valor_total=1000.00,
                data=date(2024, 1, i + 1),
                empresa=f"Empresa {i} LTDA",
                url=f"https://example.com/nota{i}.pdf"
            )
            FiscalService.create_nota_fiscal(db_session, test_user.id, nota_data)

        notas = FiscalService.get_all_notas_fiscais(db_session, test_user.id, skip=2, limit=2)
        assert len(notas) == 2

    def test_get_all_notas_fiscais_ordered_by_date(self, test_db, db_session, test_user):
        nota_data_1 = NotaFiscalCreate(
            valor_total=1000.00,
            data=date(2024, 1, 1),
            empresa="Empresa A",
            url="https://example.com/nota1.pdf"
        )
        nota_data_2 = NotaFiscalCreate(
            valor_total=2000.00,
            data=date(2024, 1, 15),
            empresa="Empresa B",
            url="https://example.com/nota2.pdf"
        )
        nota_data_3 = NotaFiscalCreate(
            valor_total=3000.00,
            data=date(2024, 1, 10),
            empresa="Empresa C",
            url="https://example.com/nota3.pdf"
        )

        FiscalService.create_nota_fiscal(db_session, test_user.id, nota_data_1)
        FiscalService.create_nota_fiscal(db_session, test_user.id, nota_data_2)
        FiscalService.create_nota_fiscal(db_session, test_user.id, nota_data_3)

        notas = FiscalService.get_all_notas_fiscais(db_session, test_user.id)
        
        assert notas[0].data.date() == date(2024, 1, 15)
        assert notas[1].data.date() == date(2024, 1, 10)
        assert notas[2].data.date() == date(2024, 1, 1)

    def test_filter_by_data_inicio(self, test_db, db_session, test_user):
        for i, dia in enumerate([5, 15, 25]):
            nota_data = NotaFiscalCreate(
                valor_total=1000.00,
                data=date(2024, 1, dia),
                empresa=f"Empresa {i}",
                url=f"https://example.com/nota{i}.pdf"
            )
            FiscalService.create_nota_fiscal(db_session, test_user.id, nota_data)

        notas = FiscalService.get_all_notas_fiscais(
            db_session,
            test_user.id,
            data_inicio=date(2024, 1, 10)
        )
        
        assert len(notas) == 2
        assert all(nota.data.date() >= date(2024, 1, 10) for nota in notas)

    def test_filter_by_data_fim(self, test_db, db_session, test_user):
        for i, dia in enumerate([5, 15, 25]):
            nota_data = NotaFiscalCreate(
                valor_total=1000.00,
                data=date(2024, 1, dia),
                empresa=f"Empresa {i}",
                url=f"https://example.com/nota{i}.pdf"
            )
            FiscalService.create_nota_fiscal(db_session, test_user.id, nota_data)

        notas = FiscalService.get_all_notas_fiscais(
            db_session,
            test_user.id,
            data_fim=date(2024, 1, 20)
        )
        
        assert len(notas) == 2
        assert all(nota.data.date() <= date(2024, 1, 20) for nota in notas)

    def test_filter_by_periodo(self, test_db, db_session, test_user):
        for i, dia in enumerate([5, 15, 25]):
            nota_data = NotaFiscalCreate(
                valor_total=1000.00,
                data=date(2024, 1, dia),
                empresa=f"Empresa {i}",
                url=f"https://example.com/nota{i}.pdf"
            )
            FiscalService.create_nota_fiscal(db_session, test_user.id, nota_data)

        notas = FiscalService.get_all_notas_fiscais(
            db_session,
            test_user.id,
            data_inicio=date(2024, 1, 10),
            data_fim=date(2024, 1, 20)
        )
        
        assert len(notas) == 1
        assert notas[0].data.date() == date(2024, 1, 15)

    def test_filter_by_empresa(self, test_db, db_session, test_user):
        empresas = ["Google Brasil", "Microsoft Brasil", "Amazon Brasil"]
        for i, empresa in enumerate(empresas):
            nota_data = NotaFiscalCreate(
                valor_total=1000.00,
                data=date(2024, 1, i + 1),
                empresa=empresa,
                url=f"https://example.com/nota{i}.pdf"
            )
            FiscalService.create_nota_fiscal(db_session, test_user.id, nota_data)

        notas = FiscalService.get_all_notas_fiscais(
            db_session,
            test_user.id,
            empresa="Google"
        )
        
        assert len(notas) == 1
        assert "Google" in notas[0].empresa

    def test_filter_by_empresa_case_insensitive(self, test_db, db_session, test_user):
        nota_data = NotaFiscalCreate(
            valor_total=1000.00,
            data=date(2024, 1, 1),
            empresa="Google Brasil LTDA",
            url="https://example.com/nota.pdf"
        )
        FiscalService.create_nota_fiscal(db_session, test_user.id, nota_data)

        notas = FiscalService.get_all_notas_fiscais(
            db_session,
            test_user.id,
            empresa="google"
        )
        
        assert len(notas) == 1

    def test_filter_by_valor_min(self, test_db, db_session, test_user):
        valores = [500.0, 2000.0, 7500.0]
        for i, valor in enumerate(valores):
            nota_data = NotaFiscalCreate(
                valor_total=valor,
                data=date(2024, 1, i + 1),
                empresa=f"Empresa {i}",
                url=f"https://example.com/nota{i}.pdf"
            )
            FiscalService.create_nota_fiscal(db_session, test_user.id, nota_data)

        notas = FiscalService.get_all_notas_fiscais(
            db_session,
            test_user.id,
            valor_min=1000.0
        )
        
        assert len(notas) == 2
        assert all(nota.valor_total >= 1000.0 for nota in notas)

    def test_filter_by_valor_max(self, test_db, db_session, test_user):
        valores = [500.0, 2000.0, 7500.0]
        for i, valor in enumerate(valores):
            nota_data = NotaFiscalCreate(
                valor_total=valor,
                data=date(2024, 1, i + 1),
                empresa=f"Empresa {i}",
                url=f"https://example.com/nota{i}.pdf"
            )
            FiscalService.create_nota_fiscal(db_session, test_user.id, nota_data)

        notas = FiscalService.get_all_notas_fiscais(
            db_session,
            test_user.id,
            valor_max=5000.0
        )
        
        assert len(notas) == 2
        assert all(nota.valor_total <= 5000.0 for nota in notas)

    def test_filter_by_valor_range(self, test_db, db_session, test_user):
        valores = [500.0, 2000.0, 7500.0]
        for i, valor in enumerate(valores):
            nota_data = NotaFiscalCreate(
                valor_total=valor,
                data=date(2024, 1, i + 1),
                empresa=f"Empresa {i}",
                url=f"https://example.com/nota{i}.pdf"
            )
            FiscalService.create_nota_fiscal(db_session, test_user.id, nota_data)

        notas = FiscalService.get_all_notas_fiscais(
            db_session,
            test_user.id,
            valor_min=1000.0,
            valor_max=5000.0
        )
        
        assert len(notas) == 1
        assert notas[0].valor_total == 2000.0

    def test_filter_combined_periodo_categoria(self, test_db, db_session, test_user):
        nota1 = NotaFiscalCreate(
            valor_total=1000.0,
            data=date(2024, 1, 5),
            empresa="Empresa A",
            url="https://example.com/nota1.pdf",
            categoria=CategoriaEnum.ALIMENTACAO
        )
        nota2 = NotaFiscalCreate(
            valor_total=2000.0,
            data=date(2024, 1, 15),
            empresa="Empresa B",
            url="https://example.com/nota2.pdf",
            categoria=CategoriaEnum.TRANSPORTE
        )
        nota3 = NotaFiscalCreate(
            valor_total=1500.0,
            data=date(2024, 1, 25),
            empresa="Empresa C",
            url="https://example.com/nota3.pdf",
            categoria=CategoriaEnum.ALIMENTACAO
        )
        
        FiscalService.create_nota_fiscal(db_session, test_user.id, nota1)
        FiscalService.create_nota_fiscal(db_session, test_user.id, nota2)
        FiscalService.create_nota_fiscal(db_session, test_user.id, nota3)

        notas = FiscalService.get_all_notas_fiscais(
            db_session,
            test_user.id,
            data_inicio=date(2024, 1, 10),
            data_fim=date(2024, 1, 31),
            categoria="Alimentação"
        )
        
        assert len(notas) == 1
        assert notas[0].valor_total == 1500.0

    def test_filter_combined_empresa_valor(self, test_db, db_session, test_user):
        nota1 = NotaFiscalCreate(
            valor_total=500.0,
            data=date(2024, 1, 1),
            empresa="Google Brasil",
            url="https://example.com/nota1.pdf"
        )
        nota2 = NotaFiscalCreate(
            valor_total=5000.0,
            data=date(2024, 1, 2),
            empresa="Google Brasil",
            url="https://example.com/nota2.pdf"
        )
        nota3 = NotaFiscalCreate(
            valor_total=2000.0,
            data=date(2024, 1, 3),
            empresa="Microsoft",
            url="https://example.com/nota3.pdf"
        )
        
        FiscalService.create_nota_fiscal(db_session, test_user.id, nota1)
        FiscalService.create_nota_fiscal(db_session, test_user.id, nota2)
        FiscalService.create_nota_fiscal(db_session, test_user.id, nota3)

        notas = FiscalService.get_all_notas_fiscais(
            db_session,
            test_user.id,
            empresa="Google",
            valor_min=1000.0
        )
        
        assert len(notas) == 1
        assert notas[0].valor_total == 5000.0

    def test_count_notas_with_filters(self, test_db, db_session, test_user):
        for i in range(5):
            nota_data = NotaFiscalCreate(
                valor_total=1000.0 * (i + 1),
                data=date(2024, 1, i + 1),
                empresa=f"Empresa {i}",
                url=f"https://example.com/nota{i}.pdf",
                categoria=CategoriaEnum.SERVICOS_DIGITAIS if i % 2 == 0 else CategoriaEnum.ALIMENTACAO
            )
            FiscalService.create_nota_fiscal(db_session, test_user.id, nota_data)

        total = FiscalService.count_notas_fiscais(
            db_session,
            test_user.id,
            categoria="Serviços Digitais"
        )
        
        assert total == 3

    def test_calculate_and_update_metrics_single_nota(self, test_db, db_session, test_user):
        nota_data = NotaFiscalCreate(
            valor_total=5000.00,
            data=date(datetime.now().year, 1, 15),
            empresa="Empresa Teste",
            url="https://example.com/nota.pdf"
        )
        FiscalService.create_nota_fiscal(db_session, test_user.id, nota_data)

        metrica = FiscalService.calculate_and_update_metrics(db_session, test_user.id)
        
        assert metrica.total_gasto == 5000.00

    def test_calculate_and_update_metrics_multiple_notas(self, test_db, db_session, test_user):
        valores = [1000.00, 2000.00, 3000.00]
        for i, valor in enumerate(valores):
            nota_data = NotaFiscalCreate(
                valor_total=valor,
                data=date(datetime.now().year, 1, i + 1),
                empresa=f"Empresa {i}",
                url=f"https://example.com/nota{i}.pdf"
            )
            FiscalService.create_nota_fiscal(db_session, test_user.id, nota_data)

        metrica = FiscalService.calculate_and_update_metrics(db_session, test_user.id)
        
        assert metrica.total_gasto == 6000.00

    def test_calculate_and_update_metrics_only_current_year(self, test_db, db_session, test_user):
        current_year = datetime.now().year
        
        nota_antiga = NotaFiscalCreate(
            valor_total=10000.00,
            data=date(current_year - 1, 12, 31),
            empresa="Empresa Antiga",
            url="https://example.com/nota_antiga.pdf"
        )
        
        nota_atual = NotaFiscalCreate(
            valor_total=5000.00,
            data=date(current_year, 1, 15),
            empresa="Empresa Atual",
            url="https://example.com/nota_atual.pdf"
        )
        
        FiscalService.create_nota_fiscal(db_session, test_user.id, nota_antiga)
        FiscalService.create_nota_fiscal(db_session, test_user.id, nota_atual)

        metrica = FiscalService.calculate_and_update_metrics(db_session, test_user.id)
        
        assert metrica.total_gasto == 5000.00

    def test_calculate_and_update_metrics_reset_alert(self, test_db, db_session, test_user):
        metrica = Metrica(
            user_id=test_user.id,
            total_gasto=50000.00,
            ultimo_alerta_percentual=0.80
        )
        db_session.add(metrica)
        db_session.commit()

        metrica_atualizada = FiscalService.calculate_and_update_metrics(db_session, test_user.id)
        
        assert metrica_atualizada.total_gasto == 0.0
        assert metrica_atualizada.ultimo_alerta_percentual == 0.0

    def test_create_nota_fiscal_success(self, test_db, db_session, test_user):
        nota_data = NotaFiscalCreate(
            valor_total=15000.00,
            data=date(2024, 6, 15),
            empresa="Empresa Cliente LTDA",
            url="https://example.com/nota_fiscal.pdf"
        )

        nota = FiscalService.create_nota_fiscal(db_session, test_user.id, nota_data)

        assert nota.user_id == test_user.id
        assert nota.valor_total == 15000.00
        assert nota.data.date() == date(2024, 6, 15)
        assert nota.empresa == "Empresa Cliente LTDA"
        assert nota.url == "https://example.com/nota_fiscal.pdf"
        assert nota.created_at is not None

    def test_create_nota_fiscal_inactive_user(self, test_db, db_session, test_user):
        UserService.delete_user(db_session, test_user.id)

        nota_data = NotaFiscalCreate(
            valor_total=1000.00,
            data=date(2024, 1, 15),
            empresa="Empresa Teste",
            url="https://example.com/nota.pdf"
        )
        
        with pytest.raises(HTTPException) as exc_info:
            FiscalService.create_nota_fiscal(db_session, test_user.id, nota_data)
        
        assert exc_info.value.status_code == 400

    def test_create_nota_fiscal_updates_metrics(self, test_db, db_session, test_user):
        nota_data = NotaFiscalCreate(
            valor_total=10000.00,
            data=date(datetime.now().year, 1, 15),
            empresa="Empresa Teste",
            url="https://example.com/nota.pdf"
        )

        FiscalService.create_nota_fiscal(db_session, test_user.id, nota_data)

        metrica = db_session.query(Metrica).filter(Metrica.user_id == test_user.id).first()
        assert metrica is not None
        assert metrica.total_gasto == 10000.00

    def test_update_nota_fiscal_success(self, test_db, db_session, test_user):
        nota_data = NotaFiscalCreate(
            valor_total=5000.00,
            data=date(2024, 1, 15),
            empresa="Empresa Original",
            url="https://example.com/nota_original.pdf"
        )
        created_nota = FiscalService.create_nota_fiscal(db_session, test_user.id, nota_data)

        update_data = NotaFiscalUpdate(
            valor_total=7500.00,
            empresa="Empresa Atualizada",
            url="https://example.com/nota_atualizada.pdf"
        )

        updated_nota = FiscalService.update_nota_fiscal(
            db_session, 
            created_nota.id, 
            test_user.id, 
            update_data
        )

        assert updated_nota is not None
        assert updated_nota.valor_total == 7500.00
        assert updated_nota.empresa == "Empresa Atualizada"
        assert updated_nota.url == "https://example.com/nota_atualizada.pdf"
        assert updated_nota.data.date() == date(2024, 1, 15)

    def test_update_nota_fiscal_nonexistent(self, test_db, db_session, test_user):
        update_data = NotaFiscalUpdate(valor_total=5000.00)
        result = FiscalService.update_nota_fiscal(db_session, 999, test_user.id, update_data)
        assert result is None

    def test_update_nota_fiscal_wrong_user(self, test_db, db_session, test_user):
        other_user_data = UserCreate(
            email="other@example.com",
            name="Other User",
            password="password123"
        )
        other_user = UserService.create_user(db_session, other_user_data)

        nota_data = NotaFiscalCreate(
            valor_total=5000.00,
            data=date(2024, 1, 15),
            empresa="Empresa Teste",
            url="https://example.com/nota.pdf"
        )
        created_nota = FiscalService.create_nota_fiscal(db_session, test_user.id, nota_data)

        update_data = NotaFiscalUpdate(valor_total=7500.00)
        result = FiscalService.update_nota_fiscal(
            db_session, 
            created_nota.id, 
            other_user.id, 
            update_data
        )
        assert result is None

    def test_update_nota_fiscal_recalculates_metrics(self, test_db, db_session, test_user):
        current_year = datetime.now().year
        
        nota_data = NotaFiscalCreate(
            valor_total=5000.00,
            data=date(current_year, 1, 15),
            empresa="Empresa Teste",
            url="https://example.com/nota.pdf"
        )
        created_nota = FiscalService.create_nota_fiscal(db_session, test_user.id, nota_data)

        update_data = NotaFiscalUpdate(valor_total=10000.00)
        FiscalService.update_nota_fiscal(db_session, created_nota.id, test_user.id, update_data)

        metrica = db_session.query(Metrica).filter(Metrica.user_id == test_user.id).first()
        assert metrica.total_gasto == 10000.00

    def test_delete_nota_fiscal_success(self, test_db, db_session, test_user):
        nota_data = NotaFiscalCreate(
            valor_total=5000.00,
            data=date(2024, 1, 15),
            empresa="Empresa Teste",
            url="https://example.com/nota.pdf"
        )
        created_nota = FiscalService.create_nota_fiscal(db_session, test_user.id, nota_data)

        success = FiscalService.delete_nota_fiscal(db_session, created_nota.id, test_user.id)
        assert success is True

        nota = FiscalService.get_nota_fiscal_by_id(db_session, created_nota.id, test_user.id)
        assert nota is None

    def test_delete_nota_fiscal_nonexistent(self, test_db, db_session, test_user):
        success = FiscalService.delete_nota_fiscal(db_session, 999, test_user.id)
        assert success is False

    def test_delete_nota_fiscal_wrong_user(self, test_db, db_session, test_user):
        other_user_data = UserCreate(
            email="other@example.com",
            name="Other User",
            password="password123"
        )
        other_user = UserService.create_user(db_session, other_user_data)

        nota_data = NotaFiscalCreate(
            valor_total=5000.00,
            data=date(2024, 1, 15),
            empresa="Empresa Teste",
            url="https://example.com/nota.pdf"
        )
        created_nota = FiscalService.create_nota_fiscal(db_session, test_user.id, nota_data)

        success = FiscalService.delete_nota_fiscal(db_session, created_nota.id, other_user.id)
        assert success is False

    def test_delete_nota_fiscal_recalculates_metrics(self, test_db, db_session, test_user):
        current_year = datetime.now().year
        
        nota_data_1 = NotaFiscalCreate(
            valor_total=5000.00,
            data=date(current_year, 1, 15),
            empresa="Empresa A",
            url="https://example.com/nota1.pdf"
        )
        nota_data_2 = NotaFiscalCreate(
            valor_total=3000.00,
            data=date(current_year, 2, 15),
            empresa="Empresa B",
            url="https://example.com/nota2.pdf"
        )
        
        nota1 = FiscalService.create_nota_fiscal(db_session, test_user.id, nota_data_1)
        FiscalService.create_nota_fiscal(db_session, test_user.id, nota_data_2)

        metrica = db_session.query(Metrica).filter(Metrica.user_id == test_user.id).first()
        assert metrica.total_gasto == 8000.00

        FiscalService.delete_nota_fiscal(db_session, nota1.id, test_user.id)

        db_session.refresh(metrica)
        assert metrica.total_gasto == 3000.00
        
    def test_create_nota_fiscal_with_categoria(self, test_db, db_session, test_user):
        nota_data = NotaFiscalCreate(
            valor_total=1500.00,
            data=date(2026, 2, 13),
            empresa="Amazon Web Services",
            url="https://example.com/nota.pdf",
            categoria=CategoriaEnum.SERVICOS_DIGITAIS
        )
        
        nota = FiscalService.create_nota_fiscal(db_session, test_user.id, nota_data)
        
        assert nota.categoria == "Serviços Digitais"
        assert nota.valor_total == 1500.00

    def test_create_nota_fiscal_without_categoria(self, test_db, db_session, test_user):
        nota_data = NotaFiscalCreate(
            valor_total=800.00,
            data=date(2026, 2, 13),
            empresa="Padaria do João",
            url="https://example.com/nota.pdf"
        )
        
        nota = FiscalService.create_nota_fiscal(db_session, test_user.id, nota_data)
        
        assert nota.categoria is None
        assert nota.valor_total == 800.00

    def test_filter_notas_by_categoria(self, test_db, db_session, test_user):
        nota1_data = NotaFiscalCreate(
            valor_total=1000.0,
            data=date(2026, 1, 15),
            empresa="Restaurante ABC",
            url="https://example.com/nota1.pdf",
            categoria=CategoriaEnum.ALIMENTACAO
        )
        
        nota2_data = NotaFiscalCreate(
            valor_total=2000.0,
            data=date(2026, 1, 16),
            empresa="Uber",
            url="https://example.com/nota2.pdf",
            categoria=CategoriaEnum.TRANSPORTE
        )
        
        nota3_data = NotaFiscalCreate(
            valor_total=1500.0,
            data=date(2026, 1, 17),
            empresa="Restaurante XYZ",
            url="https://example.com/nota3.pdf",
            categoria=CategoriaEnum.ALIMENTACAO
        )
        
        FiscalService.create_nota_fiscal(db_session, test_user.id, nota1_data)
        FiscalService.create_nota_fiscal(db_session, test_user.id, nota2_data)
        FiscalService.create_nota_fiscal(db_session, test_user.id, nota3_data)
        
        notas_alimentacao = FiscalService.get_all_notas_fiscais(
            db_session,
            test_user.id,
            categoria="Alimentação"
        )
        
        assert len(notas_alimentacao) == 2
        assert all(nota.categoria == "Alimentação" for nota in notas_alimentacao)
        
        notas_transporte = FiscalService.get_all_notas_fiscais(
            db_session,
            test_user.id,
            categoria="Transporte"
        )
        
        assert len(notas_transporte) == 1
        assert notas_transporte[0].categoria == "Transporte"

    def test_update_nota_fiscal_categoria(self, test_db, db_session, test_user):
        nota_data = NotaFiscalCreate(
            valor_total=5000.00,
            data=date(2026, 1, 15),
            empresa="Empresa Original",
            url="https://example.com/nota.pdf"
        )
        created_nota = FiscalService.create_nota_fiscal(db_session, test_user.id, nota_data)
        assert created_nota.categoria is None
        
        update_data = NotaFiscalUpdate(
            categoria=CategoriaEnum.MATERIAL_ESCRITORIO
        )
        
        updated_nota = FiscalService.update_nota_fiscal(
            db_session, 
            created_nota.id, 
            test_user.id, 
            update_data
        )
        
        assert updated_nota is not None
        assert updated_nota.categoria == "Material de Escritório"
        assert updated_nota.valor_total == 5000.00

    def test_count_notas_by_categoria(self, test_db, db_session, test_user):
        for i in range(3):
            nota_data = NotaFiscalCreate(
                valor_total=1000.00,
                data=date(2026, 1, i + 1),
                empresa=f"Empresa {i}",
                url=f"https://example.com/nota{i}.pdf",
                categoria=CategoriaEnum.SERVICOS_DIGITAIS
            )
            FiscalService.create_nota_fiscal(db_session, test_user.id, nota_data)
        
        total = FiscalService.count_notas_fiscais(
            db_session,
            test_user.id,
            categoria="Serviços Digitais"
        )
        
        assert total == 3
        
    def test_create_nota_fiscal_with_cnpj(self, test_db, db_session, test_user):
        nota_data = NotaFiscalCreate(
            valor_total=5000.0,
            data=date(2026, 2, 13),
            empresa="Google Brasil LTDA",
            cnpj="06.990.590/0001-23",
            url="https://example.com/nota.pdf"
        )
        
        nota = FiscalService.create_nota_fiscal(db_session, test_user.id, nota_data)
        
        assert nota.cnpj == "06.990.590/0001-23"
        assert nota.empresa == "Google Brasil LTDA"


    def test_create_nota_fiscal_without_cnpj(self, test_db, db_session, test_user):
        nota_data = NotaFiscalCreate(
            valor_total=1000.0,
            data=date(2026, 2, 13),
            empresa="Padaria do João",
            url="https://example.com/nota.pdf"
        )
        
        nota = FiscalService.create_nota_fiscal(db_session, test_user.id, nota_data)
        
        assert nota.cnpj is None