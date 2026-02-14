"""
Testes unitários para o serviço de notas fiscais
"""
import pytest
from datetime import date, datetime
from sqlalchemy.orm import Session
from app.models import User
from app.models.nota_fiscal import NotaFiscal, Metrica
from app.schemas import UserCreate
from app.schemas.nota_fiscal import NotaFiscalCreate, NotaFiscalUpdate
from app.services.user_service import UserService
from app.services.nota_fiscal_service import FiscalService


class TestFiscalService:
    """Testes para FiscalService"""

    @pytest.fixture
    def test_user(self, test_db, db_session):
        """Cria um usuário de teste"""
        user_data = UserCreate(
            email="testuser@example.com",
            name="Test User",
            password="password123"
        )
        return UserService.create_user(db_session, user_data)

    def test_get_nota_fiscal_by_id_existing(self, test_db, db_session, test_user):
        """Testa obtenção de nota fiscal por ID existente"""
        # Criar nota fiscal de teste
        nota_data = NotaFiscalCreate(
            valor_total=1000.00,
            data=date(2024, 1, 15),
            empresa="Empresa Teste LTDA",
            url="https://example.com/nota1.pdf"
        )
        created_nota = FiscalService.create_nota_fiscal(db_session, test_user.id, nota_data)

        # Buscar por ID
        nota = FiscalService.get_nota_fiscal_by_id(db_session, created_nota.id, test_user.id)
        assert nota is not None
        assert nota.id == created_nota.id
        assert nota.valor_total == 1000.00
        assert nota.empresa == "Empresa Teste LTDA"

    def test_get_nota_fiscal_by_id_nonexistent(self, test_db, db_session, test_user):
        """Testa obtenção de nota fiscal por ID inexistente"""
        nota = FiscalService.get_nota_fiscal_by_id(db_session, 999, test_user.id)
        assert nota is None

    def test_get_nota_fiscal_by_id_wrong_user(self, test_db, db_session, test_user):
        """Testa obtenção de nota fiscal de outro usuário"""
        # Criar outro usuário
        other_user_data = UserCreate(
            email="other@example.com",
            name="Other User",
            password="password123"
        )
        other_user = UserService.create_user(db_session, other_user_data)

        # Criar nota fiscal para o primeiro usuário
        nota_data = NotaFiscalCreate(
            valor_total=1000.00,
            data=date(2024, 1, 15),
            empresa="Empresa Teste LTDA",
            url="https://example.com/nota1.pdf"
        )
        created_nota = FiscalService.create_nota_fiscal(db_session, test_user.id, nota_data)

        # Tentar buscar com outro usuário
        nota = FiscalService.get_nota_fiscal_by_id(db_session, created_nota.id, other_user.id)
        assert nota is None

    def test_get_all_notas_fiscais_empty(self, test_db, db_session, test_user):
        """Testa obtenção de todas as notas fiscais quando vazio"""
        notas = FiscalService.get_all_notas_fiscais(db_session, test_user.id)
        assert notas == []

    def test_get_all_notas_fiscais_with_data(self, test_db, db_session, test_user):
        """Testa obtenção de todas as notas fiscais com dados"""
        # Criar notas fiscais de teste
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
        """Testa paginação na obtenção de notas fiscais"""
        # Criar 5 notas fiscais
        for i in range(5):
            nota_data = NotaFiscalCreate(
                valor_total=1000.00,
                data=date(2024, 1, i + 1),
                empresa=f"Empresa {i} LTDA",
                url=f"https://example.com/nota{i}.pdf"
            )
            FiscalService.create_nota_fiscal(db_session, test_user.id, nota_data)

        # Testar paginação
        notas = FiscalService.get_all_notas_fiscais(db_session, test_user.id, skip=2, limit=2)
        assert len(notas) == 2

    def test_get_all_notas_fiscais_ordered_by_date(self, test_db, db_session, test_user):
        """Testa ordenação por data (mais recentes primeiro)"""
        # Criar notas com datas diferentes
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
        
        # Deve estar ordenado por data decrescente
        assert notas[0].data.date() == date(2024, 1, 15)
        assert notas[1].data.date() == date(2024, 1, 10)
        assert notas[2].data.date() == date(2024, 1, 1)


    def test_calculate_and_update_metrics_single_nota(self, test_db, db_session, test_user):
        """Testa cálculo de métricas com uma nota fiscal"""
        # Criar nota fiscal do ano corrente
        nota_data = NotaFiscalCreate(
            valor_total=5000.00,
            data=date(datetime.now().year, 1, 15),
            empresa="Empresa Teste",
            url="https://example.com/nota.pdf"
        )
        FiscalService.create_nota_fiscal(db_session, test_user.id, nota_data)

        # Calcular métricas
        metrica = FiscalService.calculate_and_update_metrics(db_session, test_user.id)
        
        assert metrica.total_gasto == 5000.00

    def test_calculate_and_update_metrics_multiple_notas(self, test_db, db_session, test_user):
        """Testa cálculo de métricas com múltiplas notas fiscais"""
        # Criar várias notas fiscais do ano corrente
        valores = [1000.00, 2000.00, 3000.00]
        for i, valor in enumerate(valores):
            nota_data = NotaFiscalCreate(
                valor_total=valor,
                data=date(datetime.now().year, 1, i + 1),
                empresa=f"Empresa {i}",
                url=f"https://example.com/nota{i}.pdf"
            )
            FiscalService.create_nota_fiscal(db_session, test_user.id, nota_data)

        # Calcular métricas
        metrica = FiscalService.calculate_and_update_metrics(db_session, test_user.id)
        
        assert metrica.total_gasto == 6000.00  # Soma de todos os valores

    def test_calculate_and_update_metrics_only_current_year(self, test_db, db_session, test_user):
        """Testa que métricas calculam apenas notas do ano corrente"""
        current_year = datetime.now().year
        
        # Criar nota do ano passado
        nota_antiga = NotaFiscalCreate(
            valor_total=10000.00,
            data=date(current_year - 1, 12, 31),
            empresa="Empresa Antiga",
            url="https://example.com/nota_antiga.pdf"
        )
        
        # Criar nota do ano corrente
        nota_atual = NotaFiscalCreate(
            valor_total=5000.00,
            data=date(current_year, 1, 15),
            empresa="Empresa Atual",
            url="https://example.com/nota_atual.pdf"
        )
        
        FiscalService.create_nota_fiscal(db_session, test_user.id, nota_antiga)
        FiscalService.create_nota_fiscal(db_session, test_user.id, nota_atual)

        # Calcular métricas
        metrica = FiscalService.calculate_and_update_metrics(db_session, test_user.id)
        
        # Deve contar apenas a nota do ano corrente
        assert metrica.total_gasto == 5000.00

    def test_calculate_and_update_metrics_reset_alert(self, test_db, db_session, test_user):
        """Testa reset do alerta quando faturamento volta a zero"""
        # Criar métrica com alerta já enviado
        metrica = Metrica(
            user_id=test_user.id,
            total_gasto=50000.00,
            ultimo_alerta_percentual=0.80
        )
        db_session.add(metrica)
        db_session.commit()

        # Recalcular sem notas (simula início de novo ano)
        metrica_atualizada = FiscalService.calculate_and_update_metrics(db_session, test_user.id)
        
        assert metrica_atualizada.total_gasto == 0.0
        assert metrica_atualizada.ultimo_alerta_percentual == 0.0

    def test_create_nota_fiscal_success(self, test_db, db_session, test_user):
        """Testa criação de nota fiscal com sucesso"""
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
        """Testa criação de nota fiscal com usuário inativo"""
        # Desativar usuário
        UserService.delete_user(db_session, test_user.id)

        nota_data = NotaFiscalCreate(
            valor_total=1000.00,
            data=date(2024, 1, 15),
            empresa="Empresa Teste",
            url="https://example.com/nota.pdf"
        )

        # Deve lançar exceção
        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc_info:
            FiscalService.create_nota_fiscal(db_session, test_user.id, nota_data)
        
        assert exc_info.value.status_code == 400

    def test_create_nota_fiscal_updates_metrics(self, test_db, db_session, test_user):
        """Testa que criação de nota fiscal atualiza métricas"""
        nota_data = NotaFiscalCreate(
            valor_total=10000.00,
            data=date(datetime.now().year, 1, 15),
            empresa="Empresa Teste",
            url="https://example.com/nota.pdf"
        )

        FiscalService.create_nota_fiscal(db_session, test_user.id, nota_data)

        # Verificar métrica
        metrica = db_session.query(Metrica).filter(Metrica.user_id == test_user.id).first()
        assert metrica is not None
        assert metrica.total_gasto == 10000.00

    def test_update_nota_fiscal_success(self, test_db, db_session, test_user):
        """Testa atualização de nota fiscal com sucesso"""
        # Criar nota fiscal
        nota_data = NotaFiscalCreate(
            valor_total=5000.00,
            data=date(2024, 1, 15),
            empresa="Empresa Original",
            url="https://example.com/nota_original.pdf"
        )
        created_nota = FiscalService.create_nota_fiscal(db_session, test_user.id, nota_data)

        # Atualizar dados
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
        assert updated_nota.data.date() == date(2024, 1, 15)  # Não alterado

    def test_update_nota_fiscal_nonexistent(self, test_db, db_session, test_user):
        """Testa atualização de nota fiscal inexistente"""
        update_data = NotaFiscalUpdate(valor_total=5000.00)
        result = FiscalService.update_nota_fiscal(db_session, 999, test_user.id, update_data)
        assert result is None

    def test_update_nota_fiscal_wrong_user(self, test_db, db_session, test_user):
        """Testa atualização de nota fiscal de outro usuário"""
        # Criar outro usuário
        other_user_data = UserCreate(
            email="other@example.com",
            name="Other User",
            password="password123"
        )
        other_user = UserService.create_user(db_session, other_user_data)

        # Criar nota para o primeiro usuário
        nota_data = NotaFiscalCreate(
            valor_total=5000.00,
            data=date(2024, 1, 15),
            empresa="Empresa Teste",
            url="https://example.com/nota.pdf"
        )
        created_nota = FiscalService.create_nota_fiscal(db_session, test_user.id, nota_data)

        # Tentar atualizar com outro usuário
        update_data = NotaFiscalUpdate(valor_total=7500.00)
        result = FiscalService.update_nota_fiscal(
            db_session, 
            created_nota.id, 
            other_user.id, 
            update_data
        )
        assert result is None

    def test_update_nota_fiscal_recalculates_metrics(self, test_db, db_session, test_user):
        """Testa que atualização recalcula métricas"""
        current_year = datetime.now().year
        
        # Criar nota fiscal
        nota_data = NotaFiscalCreate(
            valor_total=5000.00,
            data=date(current_year, 1, 15),
            empresa="Empresa Teste",
            url="https://example.com/nota.pdf"
        )
        created_nota = FiscalService.create_nota_fiscal(db_session, test_user.id, nota_data)

        # Atualizar valor
        update_data = NotaFiscalUpdate(valor_total=10000.00)
        FiscalService.update_nota_fiscal(db_session, created_nota.id, test_user.id, update_data)

        # Verificar métrica atualizada
        metrica = db_session.query(Metrica).filter(Metrica.user_id == test_user.id).first()
        assert metrica.total_gasto == 10000.00

    def test_delete_nota_fiscal_success(self, test_db, db_session, test_user):
        """Testa exclusão de nota fiscal com sucesso"""
        # Criar nota fiscal
        nota_data = NotaFiscalCreate(
            valor_total=5000.00,
            data=date(2024, 1, 15),
            empresa="Empresa Teste",
            url="https://example.com/nota.pdf"
        )
        created_nota = FiscalService.create_nota_fiscal(db_session, test_user.id, nota_data)

        # Deletar
        success = FiscalService.delete_nota_fiscal(db_session, created_nota.id, test_user.id)
        assert success is True

        # Verificar se foi realmente deletado
        nota = FiscalService.get_nota_fiscal_by_id(db_session, created_nota.id, test_user.id)
        assert nota is None

    def test_delete_nota_fiscal_nonexistent(self, test_db, db_session, test_user):
        """Testa exclusão de nota fiscal inexistente"""
        success = FiscalService.delete_nota_fiscal(db_session, 999, test_user.id)
        assert success is False

    def test_delete_nota_fiscal_wrong_user(self, test_db, db_session, test_user):
        """Testa exclusão de nota fiscal de outro usuário"""
        # Criar outro usuário
        other_user_data = UserCreate(
            email="other@example.com",
            name="Other User",
            password="password123"
        )
        other_user = UserService.create_user(db_session, other_user_data)

        # Criar nota para o primeiro usuário
        nota_data = NotaFiscalCreate(
            valor_total=5000.00,
            data=date(2024, 1, 15),
            empresa="Empresa Teste",
            url="https://example.com/nota.pdf"
        )
        created_nota = FiscalService.create_nota_fiscal(db_session, test_user.id, nota_data)

        # Tentar deletar com outro usuário
        success = FiscalService.delete_nota_fiscal(db_session, created_nota.id, other_user.id)
        assert success is False

    def test_delete_nota_fiscal_recalculates_metrics(self, test_db, db_session, test_user):
        """Testa que exclusão recalcula métricas"""
        current_year = datetime.now().year
        
        # Criar duas notas fiscais
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

        # Verificar métrica inicial
        metrica = db_session.query(Metrica).filter(Metrica.user_id == test_user.id).first()
        assert metrica.total_gasto == 8000.00

        # Deletar uma nota
        FiscalService.delete_nota_fiscal(db_session, nota1.id, test_user.id)

        # Verificar métrica atualizada
        db_session.refresh(metrica)
        assert metrica.total_gasto == 3000.00
        
        
    def test_create_nota_fiscal_with_categoria(self, test_db, db_session, test_user):
        """Testa criação de nota fiscal com categoria"""
        from app.schemas.nota_fiscal import CategoriaEnum
        
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
        """Testa criação de nota fiscal sem categoria (opcional)"""
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
        """Testa filtro por categoria"""
        from app.schemas.nota_fiscal import CategoriaEnum
        
        # Criar notas com diferentes categorias
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
        
        # Filtrar por categoria "Alimentação"
        notas_alimentacao = FiscalService.get_all_notas_fiscais(
            db_session,
            test_user.id,
            categoria="Alimentação"
        )
        
        assert len(notas_alimentacao) == 2
        assert all(nota.categoria == "Alimentação" for nota in notas_alimentacao)
        
        # Filtrar por categoria "Transporte"
        notas_transporte = FiscalService.get_all_notas_fiscais(
            db_session,
            test_user.id,
            categoria="Transporte"
        )
        
        assert len(notas_transporte) == 1
        assert notas_transporte[0].categoria == "Transporte"


    def test_update_nota_fiscal_categoria(self, test_db, db_session, test_user):
        """Testa atualização de categoria de nota fiscal"""
        from app.schemas.nota_fiscal import CategoriaEnum
        
        # Criar nota fiscal sem categoria
        nota_data = NotaFiscalCreate(
            valor_total=5000.00,
            data=date(2026, 1, 15),
            empresa="Empresa Original",
            url="https://example.com/nota.pdf"
        )
        created_nota = FiscalService.create_nota_fiscal(db_session, test_user.id, nota_data)
        assert created_nota.categoria is None
        
        # Atualizar para adicionar categoria
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
        assert updated_nota.valor_total == 5000.00  # Não alterado


    def test_count_notas_by_categoria(self, test_db, db_session, test_user):
        """Testa contagem de notas por categoria"""
        from app.schemas.nota_fiscal import CategoriaEnum
        
        # Criar notas com categorias
        for i in range(3):
            nota_data = NotaFiscalCreate(
                valor_total=1000.00,
                data=date(2026, 1, i + 1),
                empresa=f"Empresa {i}",
                url=f"https://example.com/nota{i}.pdf",
                categoria=CategoriaEnum.SERVICOS_DIGITAIS
            )
            FiscalService.create_nota_fiscal(db_session, test_user.id, nota_data)
        
        # Contar notas da categoria "Serviços Digitais"
        total = FiscalService.count_notas_fiscais(
            db_session,
            test_user.id,
            categoria="Serviços Digitais"
        )
        
        assert total == 3