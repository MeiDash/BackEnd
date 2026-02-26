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
    
    @pytest.fixture
    def fake_pdf(self):
        """Arquivo PDF fake para testes"""
        return b"%PDF-1.4\n%fake pdf content for testing\n%%EOF"
    
    @pytest.fixture
    def fake_image(self):
        """Imagem fake para testes"""
        return b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"

    def test_get_nota_fiscal_by_id_existing(self, test_db, db_session, test_user, fake_pdf):
        nota_data = NotaFiscalCreate(
            valor_total=1000.00,
            data=date(2024, 1, 15),
            empresa="Empresa Teste LTDA"
        )
        created_nota = FiscalService.create_nota_fiscal_with_file(
            db_session,
            test_user.id,
            nota_data,
            arquivo_nome="nota1.pdf",
            arquivo_tipo="application/pdf",
            arquivo_conteudo=fake_pdf
        )

        nota = FiscalService.get_nota_fiscal_by_id(db_session, created_nota.id, test_user.id)
        assert nota is not None
        assert nota.id == created_nota.id
        assert nota.valor_total == 1000.00
        assert nota.empresa == "Empresa Teste LTDA"

    def test_get_nota_fiscal_by_id_nonexistent(self, test_db, db_session, test_user):
        nota = FiscalService.get_nota_fiscal_by_id(db_session, 999, test_user.id)
        assert nota is None

    def test_get_nota_fiscal_by_id_wrong_user(self, test_db, db_session, test_user, fake_pdf):
        other_user_data = UserCreate(
            email="other@example.com",
            name="Other User",
            password="password123"
        )
        other_user = UserService.create_user(db_session, other_user_data)

        nota_data = NotaFiscalCreate(
            valor_total=1000.00,
            data=date(2024, 1, 15),
            empresa="Empresa Teste LTDA"
        )
        created_nota = FiscalService.create_nota_fiscal_with_file(
            db_session,
            test_user.id,
            nota_data,
            arquivo_nome="nota1.pdf",
            arquivo_tipo="application/pdf",
            arquivo_conteudo=fake_pdf
        )

        nota = FiscalService.get_nota_fiscal_by_id(db_session, created_nota.id, other_user.id)
        assert nota is None

    def test_get_all_notas_fiscais_empty(self, test_db, db_session, test_user):
        notas = FiscalService.get_all_notas_fiscais(db_session, test_user.id)
        assert notas == []

    def test_get_all_notas_fiscais_with_data(self, test_db, db_session, test_user, fake_pdf):
        for i in range(3):
            nota_data = NotaFiscalCreate(
                valor_total=1000.00 * (i + 1),
                data=date(2024, 1, i + 1),
                empresa=f"Empresa {i} LTDA"
            )
            FiscalService.create_nota_fiscal_with_file(
                db_session,
                test_user.id,
                nota_data,
                arquivo_nome=f"nota{i}.pdf",
                arquivo_tipo="application/pdf",
                arquivo_conteudo=fake_pdf
            )

        notas = FiscalService.get_all_notas_fiscais(db_session, test_user.id)
        assert len(notas) == 3

    def test_get_all_notas_fiscais_pagination(self, test_db, db_session, test_user, fake_pdf):
        for i in range(5):
            nota_data = NotaFiscalCreate(
                valor_total=1000.00,
                data=date(2024, 1, i + 1),
                empresa=f"Empresa {i} LTDA"
            )
            FiscalService.create_nota_fiscal_with_file(
                db_session,
                test_user.id,
                nota_data,
                arquivo_nome=f"nota{i}.pdf",
                arquivo_tipo="application/pdf",
                arquivo_conteudo=fake_pdf
            )

        notas = FiscalService.get_all_notas_fiscais(db_session, test_user.id, skip=2, limit=2)
        assert len(notas) == 2

    def test_get_all_notas_fiscais_ordered_by_date(self, test_db, db_session, test_user, fake_pdf):
        nota_data_1 = NotaFiscalCreate(
            valor_total=1000.00,
            data=date(2024, 1, 1),
            empresa="Empresa A"
        )
        nota_data_2 = NotaFiscalCreate(
            valor_total=2000.00,
            data=date(2024, 1, 15),
            empresa="Empresa B"
        )
        nota_data_3 = NotaFiscalCreate(
            valor_total=3000.00,
            data=date(2024, 1, 10),
            empresa="Empresa C"
        )

        FiscalService.create_nota_fiscal_with_file(db_session, test_user.id, nota_data_1, "nota1.pdf", "application/pdf", fake_pdf)
        FiscalService.create_nota_fiscal_with_file(db_session, test_user.id, nota_data_2, "nota2.pdf", "application/pdf", fake_pdf)
        FiscalService.create_nota_fiscal_with_file(db_session, test_user.id, nota_data_3, "nota3.pdf", "application/pdf", fake_pdf)

        notas = FiscalService.get_all_notas_fiscais(db_session, test_user.id)
        
        assert notas[0].data.date() == date(2024, 1, 15)
        assert notas[1].data.date() == date(2024, 1, 10)
        assert notas[2].data.date() == date(2024, 1, 1)

    def test_filter_by_data_inicio(self, test_db, db_session, test_user, fake_pdf):
        for i, dia in enumerate([5, 15, 25]):
            nota_data = NotaFiscalCreate(
                valor_total=1000.00,
                data=date(2024, 1, dia),
                empresa=f"Empresa {i}"
            )
            FiscalService.create_nota_fiscal_with_file(
                db_session,
                test_user.id,
                nota_data,
                arquivo_nome=f"nota{i}.pdf",
                arquivo_tipo="application/pdf",
                arquivo_conteudo=fake_pdf
            )

        notas = FiscalService.get_all_notas_fiscais(
            db_session,
            test_user.id,
            data_inicio=date(2024, 1, 10)
        )
        
        assert len(notas) == 2
        assert all(nota.data.date() >= date(2024, 1, 10) for nota in notas)

    def test_filter_by_data_fim(self, test_db, db_session, test_user, fake_pdf):
        for i, dia in enumerate([5, 15, 25]):
            nota_data = NotaFiscalCreate(
                valor_total=1000.00,
                data=date(2024, 1, dia),
                empresa=f"Empresa {i}"
            )
            FiscalService.create_nota_fiscal_with_file(
                db_session,
                test_user.id,
                nota_data,
                arquivo_nome=f"nota{i}.pdf",
                arquivo_tipo="application/pdf",
                arquivo_conteudo=fake_pdf
            )

        notas = FiscalService.get_all_notas_fiscais(
            db_session,
            test_user.id,
            data_fim=date(2024, 1, 20)
        )
        
        assert len(notas) == 2
        assert all(nota.data.date() <= date(2024, 1, 20) for nota in notas)

    def test_filter_by_periodo(self, test_db, db_session, test_user, fake_pdf):
        for i, dia in enumerate([5, 15, 25]):
            nota_data = NotaFiscalCreate(
                valor_total=1000.00,
                data=date(2024, 1, dia),
                empresa=f"Empresa {i}"
            )
            FiscalService.create_nota_fiscal_with_file(
                db_session,
                test_user.id,
                nota_data,
                arquivo_nome=f"nota{i}.pdf",
                arquivo_tipo="application/pdf",
                arquivo_conteudo=fake_pdf
            )

        notas = FiscalService.get_all_notas_fiscais(
            db_session,
            test_user.id,
            data_inicio=date(2024, 1, 10),
            data_fim=date(2024, 1, 20)
        )
        
        assert len(notas) == 1
        assert notas[0].data.date() == date(2024, 1, 15)

    def test_filter_by_empresa(self, test_db, db_session, test_user, fake_pdf):
        empresas = ["Google Brasil", "Microsoft Brasil", "Amazon Brasil"]
        for i, empresa in enumerate(empresas):
            nota_data = NotaFiscalCreate(
                valor_total=1000.00,
                data=date(2024, 1, i + 1),
                empresa=empresa
            )
            FiscalService.create_nota_fiscal_with_file(
                db_session,
                test_user.id,
                nota_data,
                arquivo_nome=f"nota{i}.pdf",
                arquivo_tipo="application/pdf",
                arquivo_conteudo=fake_pdf
            )

        notas = FiscalService.get_all_notas_fiscais(
            db_session,
            test_user.id,
            empresa="Google"
        )
        
        assert len(notas) == 1
        assert "Google" in notas[0].empresa

    def test_filter_by_empresa_case_insensitive(self, test_db, db_session, test_user, fake_pdf):
        nota_data = NotaFiscalCreate(
            valor_total=1000.00,
            data=date(2024, 1, 1),
            empresa="Google Brasil LTDA"
        )
        FiscalService.create_nota_fiscal_with_file(
            db_session,
            test_user.id,
            nota_data,
            arquivo_nome="nota.pdf",
            arquivo_tipo="application/pdf",
            arquivo_conteudo=fake_pdf
        )

        notas = FiscalService.get_all_notas_fiscais(
            db_session,
            test_user.id,
            empresa="google"
        )
        
        assert len(notas) == 1

    def test_filter_by_valor_min(self, test_db, db_session, test_user, fake_pdf):
        valores = [500.0, 2000.0, 7500.0]
        for i, valor in enumerate(valores):
            nota_data = NotaFiscalCreate(
                valor_total=valor,
                data=date(2024, 1, i + 1),
                empresa=f"Empresa {i}"
            )
            FiscalService.create_nota_fiscal_with_file(
                db_session,
                test_user.id,
                nota_data,
                arquivo_nome=f"nota{i}.pdf",
                arquivo_tipo="application/pdf",
                arquivo_conteudo=fake_pdf
            )

        notas = FiscalService.get_all_notas_fiscais(
            db_session,
            test_user.id,
            valor_min=1000.0
        )
        
        assert len(notas) == 2
        assert all(nota.valor_total >= 1000.0 for nota in notas)

    def test_filter_by_valor_max(self, test_db, db_session, test_user, fake_pdf):
        valores = [500.0, 2000.0, 7500.0]
        for i, valor in enumerate(valores):
            nota_data = NotaFiscalCreate(
                valor_total=valor,
                data=date(2024, 1, i + 1),
                empresa=f"Empresa {i}"
            )
            FiscalService.create_nota_fiscal_with_file(
                db_session,
                test_user.id,
                nota_data,
                arquivo_nome=f"nota{i}.pdf",
                arquivo_tipo="application/pdf",
                arquivo_conteudo=fake_pdf
            )

        notas = FiscalService.get_all_notas_fiscais(
            db_session,
            test_user.id,
            valor_max=5000.0
        )
        
        assert len(notas) == 2
        assert all(nota.valor_total <= 5000.0 for nota in notas)

    def test_filter_by_valor_range(self, test_db, db_session, test_user, fake_pdf):
        valores = [500.0, 2000.0, 7500.0]
        for i, valor in enumerate(valores):
            nota_data = NotaFiscalCreate(
                valor_total=valor,
                data=date(2024, 1, i + 1),
                empresa=f"Empresa {i}"
            )
            FiscalService.create_nota_fiscal_with_file(
                db_session,
                test_user.id,
                nota_data,
                arquivo_nome=f"nota{i}.pdf",
                arquivo_tipo="application/pdf",
                arquivo_conteudo=fake_pdf
            )

        notas = FiscalService.get_all_notas_fiscais(
            db_session,
            test_user.id,
            valor_min=1000.0,
            valor_max=5000.0
        )
        
        assert len(notas) == 1
        assert notas[0].valor_total == 2000.0

    def test_filter_combined_periodo_categoria(self, test_db, db_session, test_user, fake_pdf):
        nota1 = NotaFiscalCreate(
            valor_total=1000.0,
            data=date(2024, 1, 5),
            empresa="Empresa A",
            categoria=CategoriaEnum.AGUA_MINERAL
        )
        nota2 = NotaFiscalCreate(
            valor_total=2000.0,
            data=date(2024, 1, 15),
            empresa="Empresa B",
            categoria=CategoriaEnum.BEBIDAS_ALCOOLICAS
        )
        nota3 = NotaFiscalCreate(
            valor_total=1500.0,
            data=date(2024, 1, 25),
            empresa="Empresa C",
            categoria=CategoriaEnum.CARNES_FRIOS
        )
        
        FiscalService.create_nota_fiscal_with_file(db_session, test_user.id, nota1, "nota1.pdf", "application/pdf", fake_pdf)
        FiscalService.create_nota_fiscal_with_file(db_session, test_user.id, nota2, "nota2.pdf", "application/pdf", fake_pdf)
        FiscalService.create_nota_fiscal_with_file(db_session, test_user.id, nota3, "nota3.pdf", "application/pdf", fake_pdf)

        notas = FiscalService.get_all_notas_fiscais(
            db_session,
            test_user.id,
            data_inicio=date(2024, 1, 1),
            data_fim=date(2024, 1, 31),
            categoria="Água Mineral"
        )
        
        assert len(notas) == 1
        assert notas[0].valor_total == 1000.0

    def test_filter_combined_empresa_valor(self, test_db, db_session, test_user, fake_pdf):
        nota1 = NotaFiscalCreate(
            valor_total=500.0,
            data=date(2024, 1, 1),
            empresa="Google Brasil"
        )
        nota2 = NotaFiscalCreate(
            valor_total=5000.0,
            data=date(2024, 1, 2),
            empresa="Google Brasil"
        )
        nota3 = NotaFiscalCreate(
            valor_total=2000.0,
            data=date(2024, 1, 3),
            empresa="Microsoft"
        )
        
        FiscalService.create_nota_fiscal_with_file(db_session, test_user.id, nota1, "nota1.pdf", "application/pdf", fake_pdf)
        FiscalService.create_nota_fiscal_with_file(db_session, test_user.id, nota2, "nota2.pdf", "application/pdf", fake_pdf)
        FiscalService.create_nota_fiscal_with_file(db_session, test_user.id, nota3, "nota3.pdf", "application/pdf", fake_pdf)

        notas = FiscalService.get_all_notas_fiscais(
            db_session,
            test_user.id,
            empresa="Google",
            valor_min=1000.0
        )
        
        assert len(notas) == 1
        assert notas[0].valor_total == 5000.0

    def test_count_notas_with_filters(self, test_db, db_session, test_user, fake_pdf):
        for i in range(5):
            nota_data = NotaFiscalCreate(
                valor_total=1000.0 * (i + 1),
                data=date(2024, 1, i + 1),
                empresa=f"Empresa {i}",
                categoria=CategoriaEnum.AGUA_MINERAL if i % 2 == 0 else CategoriaEnum.CALCADOS
            )
            FiscalService.create_nota_fiscal_with_file(
                db_session,
                test_user.id,
                nota_data,
                arquivo_nome=f"nota{i}.pdf",
                arquivo_tipo="application/pdf",
                arquivo_conteudo=fake_pdf
            )

        total = FiscalService.count_notas_fiscais(
            db_session,
            test_user.id,
            categoria="Água Mineral"
        )
        
        assert total == 3

    def test_calculate_and_update_metrics_single_nota(self, test_db, db_session, test_user, fake_pdf):
        nota_data = NotaFiscalCreate(
            valor_total=5000.00,
            data=date(datetime.now().year, 1, 15),
            empresa="Empresa Teste"
        )
        FiscalService.create_nota_fiscal_with_file(
            db_session,
            test_user.id,
            nota_data,
            arquivo_nome="nota.pdf",
            arquivo_tipo="application/pdf",
            arquivo_conteudo=fake_pdf
        )

        metrica = FiscalService.calculate_and_update_metrics(db_session, test_user.id)
        
        assert metrica.total_gasto == 5000.00

    def test_calculate_and_update_metrics_multiple_notas(self, test_db, db_session, test_user, fake_pdf):
        valores = [1000.00, 2000.00, 3000.00]
        for i, valor in enumerate(valores):
            nota_data = NotaFiscalCreate(
                valor_total=valor,
                data=date(datetime.now().year, 1, i + 1),
                empresa=f"Empresa {i}"
            )
            FiscalService.create_nota_fiscal_with_file(
                db_session,
                test_user.id,
                nota_data,
                arquivo_nome=f"nota{i}.pdf",
                arquivo_tipo="application/pdf",
                arquivo_conteudo=fake_pdf
            )

        metrica = FiscalService.calculate_and_update_metrics(db_session, test_user.id)
        
        assert metrica.total_gasto == 6000.00

    def test_calculate_and_update_metrics_only_current_year(self, test_db, db_session, test_user, fake_pdf):
        current_year = datetime.now().year
        
        nota_antiga = NotaFiscalCreate(
            valor_total=10000.00,
            data=date(current_year - 1, 12, 31),
            empresa="Empresa Antiga"
        )
        
        nota_atual = NotaFiscalCreate(
            valor_total=5000.00,
            data=date(current_year, 1, 15),
            empresa="Empresa Atual"
        )
        
        FiscalService.create_nota_fiscal_with_file(db_session, test_user.id, nota_antiga, "nota_antiga.pdf", "application/pdf", fake_pdf)
        FiscalService.create_nota_fiscal_with_file(db_session, test_user.id, nota_atual, "nota_atual.pdf", "application/pdf", fake_pdf)

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

    def test_create_nota_fiscal_with_file(self, test_db, db_session, test_user, fake_pdf):
        nota_data = NotaFiscalCreate(
            valor_total=15000.00,
            data=date(2024, 6, 15),
            empresa="Empresa Cliente LTDA"
        )

        nota = FiscalService.create_nota_fiscal_with_file(
            db_session,
            test_user.id,
            nota_data,
            arquivo_nome="nota_fiscal.pdf",
            arquivo_tipo="application/pdf",
            arquivo_conteudo=fake_pdf
        )

        assert nota.user_id == test_user.id
        assert nota.valor_total == 15000.00
        assert nota.data.date() == date(2024, 6, 15)
        assert nota.empresa == "Empresa Cliente LTDA"
        assert nota.arquivo_nome == "nota_fiscal.pdf"
        assert nota.arquivo_tipo == "application/pdf"
        assert nota.arquivo_tamanho == len(fake_pdf)
        assert nota.created_at is not None

    def test_create_nota_fiscal_inactive_user(self, test_db, db_session, test_user, fake_pdf):
        UserService.delete_user(db_session, test_user.id)

        nota_data = NotaFiscalCreate(
            valor_total=1000.00,
            data=date(2024, 1, 15),
            empresa="Empresa Teste"
        )
        
        with pytest.raises(HTTPException) as exc_info:
            FiscalService.create_nota_fiscal_with_file(
                db_session,
                test_user.id,
                nota_data,
                arquivo_nome="nota.pdf",
                arquivo_tipo="application/pdf",
                arquivo_conteudo=fake_pdf
            )
        
        assert exc_info.value.status_code == 400

    def test_create_nota_fiscal_updates_metrics(self, test_db, db_session, test_user, fake_pdf):
        nota_data = NotaFiscalCreate(
            valor_total=10000.00,
            data=date(datetime.now().year, 1, 15),
            empresa="Empresa Teste"
        )

        FiscalService.create_nota_fiscal_with_file(
            db_session,
            test_user.id,
            nota_data,
            arquivo_nome="nota.pdf",
            arquivo_tipo="application/pdf",
            arquivo_conteudo=fake_pdf
        )

        metrica = db_session.query(Metrica).filter(Metrica.user_id == test_user.id).first()
        assert metrica is not None
        assert metrica.total_gasto == 10000.00

    def test_update_nota_fiscal_success(self, test_db, db_session, test_user, fake_pdf):
        nota_data = NotaFiscalCreate(
            valor_total=5000.00,
            data=date(2024, 1, 15),
            empresa="Empresa Original"
        )
        created_nota = FiscalService.create_nota_fiscal_with_file(
            db_session,
            test_user.id,
            nota_data,
            arquivo_nome="nota_original.pdf",
            arquivo_tipo="application/pdf",
            arquivo_conteudo=fake_pdf
        )

        update_data = NotaFiscalUpdate(
            valor_total=7500.00,
            empresa="Empresa Atualizada"
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
        assert updated_nota.data.date() == date(2024, 1, 15)

    def test_update_nota_fiscal_nonexistent(self, test_db, db_session, test_user):
        update_data = NotaFiscalUpdate(valor_total=5000.00)
        result = FiscalService.update_nota_fiscal(db_session, 999, test_user.id, update_data)
        assert result is None

    def test_update_nota_fiscal_wrong_user(self, test_db, db_session, test_user, fake_pdf):
        other_user_data = UserCreate(
            email="other@example.com",
            name="Other User",
            password="password123"
        )
        other_user = UserService.create_user(db_session, other_user_data)

        nota_data = NotaFiscalCreate(
            valor_total=5000.00,
            data=date(2024, 1, 15),
            empresa="Empresa Teste"
        )
        created_nota = FiscalService.create_nota_fiscal_with_file(
            db_session,
            test_user.id,
            nota_data,
            arquivo_nome="nota.pdf",
            arquivo_tipo="application/pdf",
            arquivo_conteudo=fake_pdf
        )

        update_data = NotaFiscalUpdate(valor_total=7500.00)
        result = FiscalService.update_nota_fiscal(
            db_session, 
            created_nota.id, 
            other_user.id, 
            update_data
        )
        assert result is None

    def test_update_nota_fiscal_recalculates_metrics(self, test_db, db_session, test_user, fake_pdf):
        current_year = datetime.now().year
        
        nota_data = NotaFiscalCreate(
            valor_total=5000.00,
            data=date(current_year, 1, 15),
            empresa="Empresa Teste"
        )
        created_nota = FiscalService.create_nota_fiscal_with_file(
            db_session,
            test_user.id,
            nota_data,
            arquivo_nome="nota.pdf",
            arquivo_tipo="application/pdf",
            arquivo_conteudo=fake_pdf
        )

        update_data = NotaFiscalUpdate(valor_total=10000.00)
        FiscalService.update_nota_fiscal(db_session, created_nota.id, test_user.id, update_data)

        metrica = db_session.query(Metrica).filter(Metrica.user_id == test_user.id).first()
        assert metrica.total_gasto == 10000.00

    def test_delete_nota_fiscal_success(self, test_db, db_session, test_user, fake_pdf):
        nota_data = NotaFiscalCreate(
            valor_total=5000.00,
            data=date(2024, 1, 15),
            empresa="Empresa Teste"
        )
        created_nota = FiscalService.create_nota_fiscal_with_file(
            db_session,
            test_user.id,
            nota_data,
            arquivo_nome="nota.pdf",
            arquivo_tipo="application/pdf",
            arquivo_conteudo=fake_pdf
        )

        success = FiscalService.delete_nota_fiscal(db_session, created_nota.id, test_user.id)
        assert success is True

        nota = FiscalService.get_nota_fiscal_by_id(db_session, created_nota.id, test_user.id)
        assert nota is None

    def test_delete_nota_fiscal_nonexistent(self, test_db, db_session, test_user):
        success = FiscalService.delete_nota_fiscal(db_session, 999, test_user.id)
        assert success is False

    def test_delete_nota_fiscal_wrong_user(self, test_db, db_session, test_user, fake_pdf):
        other_user_data = UserCreate(
            email="other@example.com",
            name="Other User",
            password="password123"
        )
        other_user = UserService.create_user(db_session, other_user_data)

        nota_data = NotaFiscalCreate(
            valor_total=5000.00,
            data=date(2024, 1, 15),
            empresa="Empresa Teste"
        )
        created_nota = FiscalService.create_nota_fiscal_with_file(
            db_session,
            test_user.id,
            nota_data,
            arquivo_nome="nota.pdf",
            arquivo_tipo="application/pdf",
            arquivo_conteudo=fake_pdf
        )

        success = FiscalService.delete_nota_fiscal(db_session, created_nota.id, other_user.id)
        assert success is False

    def test_delete_nota_fiscal_recalculates_metrics(self, test_db, db_session, test_user, fake_pdf):
        current_year = datetime.now().year
        
        nota_data_1 = NotaFiscalCreate(
            valor_total=5000.00,
            data=date(current_year, 1, 15),
            empresa="Empresa A"
        )
        nota_data_2 = NotaFiscalCreate(
            valor_total=3000.00,
            data=date(current_year, 2, 15),
            empresa="Empresa B"
        )
        
        nota1 = FiscalService.create_nota_fiscal_with_file(db_session, test_user.id, nota_data_1, "nota1.pdf", "application/pdf", fake_pdf)
        FiscalService.create_nota_fiscal_with_file(db_session, test_user.id, nota_data_2, "nota2.pdf", "application/pdf", fake_pdf)

        metrica = db_session.query(Metrica).filter(Metrica.user_id == test_user.id).first()
        assert metrica.total_gasto == 8000.00

        FiscalService.delete_nota_fiscal(db_session, nota1.id, test_user.id)

        db_session.refresh(metrica)
        assert metrica.total_gasto == 3000.00
        
    def test_create_nota_fiscal_with_categoria(self, test_db, db_session, test_user, fake_pdf):
        nota_data = NotaFiscalCreate(
            valor_total=1500.00,
            data=date(2026, 2, 13),
            empresa="Amazon Web Services",
            categoria=CategoriaEnum.AGUA_MINERAL
        )
        
        nota = FiscalService.create_nota_fiscal_with_file(
            db_session,
            test_user.id,
            nota_data,
            arquivo_nome="nota.pdf",
            arquivo_tipo="application/pdf",
            arquivo_conteudo=fake_pdf
        )
        
        assert nota.categoria == "Água Mineral"
        assert nota.valor_total == 1500.00

    def test_create_nota_fiscal_without_categoria(self, test_db, db_session, test_user, fake_pdf):
        nota_data = NotaFiscalCreate(
            valor_total=800.00,
            data=date(2026, 2, 13),
            empresa="Padaria do João"
        )
        
        nota = FiscalService.create_nota_fiscal_with_file(
            db_session,
            test_user.id,
            nota_data,
            arquivo_nome="nota.pdf",
            arquivo_tipo="application/pdf",
            arquivo_conteudo=fake_pdf
        )
        
        assert nota.categoria is None
        assert nota.valor_total == 800.00

    def test_filter_notas_by_categoria(self, test_db, db_session, test_user, fake_pdf):
        nota1_data = NotaFiscalCreate(
            valor_total=1000.0,
            data=date(2026, 1, 15),
            empresa="Restaurante ABC",
            categoria=CategoriaEnum.AGUA_MINERAL
        )
        
        nota2_data = NotaFiscalCreate(
            valor_total=2000.0,
            data=date(2026, 1, 16),
            empresa="Uber",
            categoria=CategoriaEnum.BEBIDAS_ALCOOLICAS
        )
        
        nota3_data = NotaFiscalCreate(
            valor_total=1500.0,
            data=date(2026, 1, 17),
            empresa="Restaurante XYZ",
            categoria=CategoriaEnum.AGUA_MINERAL
        )
        
        FiscalService.create_nota_fiscal_with_file(db_session, test_user.id, nota1_data, "nota1.pdf", "application/pdf", fake_pdf)
        FiscalService.create_nota_fiscal_with_file(db_session, test_user.id, nota2_data, "nota2.pdf", "application/pdf", fake_pdf)
        FiscalService.create_nota_fiscal_with_file(db_session, test_user.id, nota3_data, "nota3.pdf", "application/pdf", fake_pdf)
        
        notas_alimentacao = FiscalService.get_all_notas_fiscais(
            db_session,
            test_user.id,
            categoria="Água Mineral"
        )
        
        assert len(notas_alimentacao) == 2
        assert all(nota.categoria == "Água Mineral" for nota in notas_alimentacao)
        
        notas_transporte = FiscalService.get_all_notas_fiscais(
            db_session,
            test_user.id,
            categoria="Bebidas Alcoólicas"
        )
        
        assert len(notas_transporte) == 1
        assert notas_transporte[0].categoria == "Bebidas Alcoólicas"

    def test_update_nota_fiscal_categoria(self, test_db, db_session, test_user, fake_pdf):
        nota_data = NotaFiscalCreate(
            valor_total=5000.00,
            data=date(2026, 1, 15),
            empresa="Empresa Original"
        )
        created_nota = FiscalService.create_nota_fiscal_with_file(
            db_session,
            test_user.id,
            nota_data,
            arquivo_nome="nota.pdf",
            arquivo_tipo="application/pdf",
            arquivo_conteudo=fake_pdf
        )
        assert created_nota.categoria is None
        
        update_data = NotaFiscalUpdate(
            categoria=CategoriaEnum.AGUA_MINERAL
        )
        
        updated_nota = FiscalService.update_nota_fiscal(
            db_session, 
            created_nota.id, 
            test_user.id, 
            update_data
        )
        
        assert updated_nota is not None
        assert updated_nota.categoria == "Água Mineral"
        assert updated_nota.valor_total == 5000.00

    def test_count_notas_by_categoria(self, test_db, db_session, test_user, fake_pdf):
        for i in range(3):
            nota_data = NotaFiscalCreate(
                valor_total=1000.00,
                data=date(2026, 1, i + 1),
                empresa=f"Empresa {i}",
                categoria=CategoriaEnum.AGUA_MINERAL
            )
            FiscalService.create_nota_fiscal_with_file(
                db_session,
                test_user.id,
                nota_data,
                arquivo_nome=f"nota{i}.pdf",
                arquivo_tipo="application/pdf",
                arquivo_conteudo=fake_pdf
            )
        
        total = FiscalService.count_notas_fiscais(
            db_session,
            test_user.id,
            categoria="Água Mineral"
        )
        
        assert total == 3
        
    def test_create_nota_fiscal_with_cnpj(self, test_db, db_session, test_user, fake_pdf):
        nota_data = NotaFiscalCreate(
            valor_total=5000.0,
            data=date(2026, 2, 13),
            empresa="Google Brasil LTDA",
            cnpj="06.990.590/0001-23"
        )
        
        nota = FiscalService.create_nota_fiscal_with_file(
            db_session,
            test_user.id,
            nota_data,
            arquivo_nome="nota.pdf",
            arquivo_tipo="application/pdf",
            arquivo_conteudo=fake_pdf
        )
        
        assert nota.cnpj == "06.990.590/0001-23"
        assert nota.empresa == "Google Brasil LTDA"

    def test_create_nota_fiscal_without_cnpj(self, test_db, db_session, test_user, fake_pdf):
        nota_data = NotaFiscalCreate(
            valor_total=1000.0,
            data=date(2026, 2, 13),
            empresa="Padaria do João"
        )
        
        nota = FiscalService.create_nota_fiscal_with_file(
            db_session,
            test_user.id,
            nota_data,
            arquivo_nome="nota.pdf",
            arquivo_tipo="application/pdf",
            arquivo_conteudo=fake_pdf
        )
        
        assert nota.cnpj is None
    
    def test_download_arquivo_nota_fiscal(self, test_db, db_session, test_user, fake_pdf):
        nota_data = NotaFiscalCreate(
            valor_total=1000.0,
            data=date(2026, 2, 16),
            empresa="Empresa Teste"
        )
        
        nota = FiscalService.create_nota_fiscal_with_file(
            db_session,
            test_user.id,
            nota_data,
            arquivo_nome="test.pdf",
            arquivo_tipo="application/pdf",
            arquivo_conteudo=fake_pdf
        )
        
        result = FiscalService.get_arquivo_nota_fiscal(db_session, nota.id, test_user.id)
        
        assert result is not None
        conteudo, nome, tipo = result
        assert conteudo == fake_pdf
        assert nome == "test.pdf"
        assert tipo == "application/pdf"

    def test_download_arquivo_wrong_user(self, test_db, db_session, test_user, fake_pdf):
        other_user_data = UserCreate(
            email="other@example.com",
            name="Other User",
            password="password123"
        )
        other_user = UserService.create_user(db_session, other_user_data)
        
        nota_data = NotaFiscalCreate(
            valor_total=1000.0,
            data=date(2026, 2, 16),
            empresa="Empresa Teste"
        )
        
        nota = FiscalService.create_nota_fiscal_with_file(
            db_session,
            test_user.id,
            nota_data,
            arquivo_nome="test.pdf",
            arquivo_tipo="application/pdf",
            arquivo_conteudo=fake_pdf
        )
        
        result = FiscalService.get_arquivo_nota_fiscal(db_session, nota.id, other_user.id)
        
        assert result is None

    def test_create_with_image_file(self, test_db, db_session, test_user, fake_image):
        nota_data = NotaFiscalCreate(
            valor_total=2000.0,
            data=date(2026, 2, 16),
            empresa="Empresa Teste"
        )
        
        nota = FiscalService.create_nota_fiscal_with_file(
            db_session,
            test_user.id,
            nota_data,
            arquivo_nome="nota.png",
            arquivo_tipo="image/png",
            arquivo_conteudo=fake_image
        )
        
        assert nota.arquivo_nome == "nota.png"
        assert nota.arquivo_tipo == "image/png"
        assert nota.arquivo_tamanho == len(fake_image)