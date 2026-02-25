from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.nota_fiscal import NotaFiscal, Metrica
from app.models import User 
from app.schemas.nota_fiscal import NotaFiscalCreate, MetricaResponse, NotaFiscalUpdate
from app.services.email_service import EmailService, ALERT_THRESHOLDS
from typing import List
from typing import List, Optional
import logging
from datetime import date, datetime, time 
from fastapi import HTTPException

# Define a precisão dos limiares para comparação
COMPARISON_PRECISION = 0.0001 

class FiscalService:
    
    """Serviço para operações de Nota Fiscal"""
    
    @staticmethod
    def get_nota_fiscal_by_id(
        db: Session, 
        nota_id: int, 
        user_id: int
    ) -> Optional[NotaFiscal]:
        """Obtém nota fiscal por ID (apenas do usuário autenticado)"""
        return db.query(NotaFiscal).filter(
            NotaFiscal.id == nota_id,
            NotaFiscal.user_id == user_id
        ).first()
    
    @staticmethod
    def get_all_notas_fiscais(
        db: Session,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        data_inicio: Optional[date] = None,
        data_fim: Optional[date] = None,
        empresa: Optional[str] = None,
        valor_min: Optional[float] = None,
        valor_max: Optional[float] = None,
        categoria: Optional[str] = None 
    ) -> List[NotaFiscal]:
        """Obtém todas as notas fiscais do usuário com paginação e filtros opcionais"""
        query = db.query(NotaFiscal).filter(
            NotaFiscal.user_id == user_id
        )
        
        if data_inicio:
            query = query.filter(NotaFiscal.data >= data_inicio)
        
        if data_fim:
            data_fim_completa = datetime.combine(data_fim, time(23, 59, 59))
            query = query.filter(NotaFiscal.data <= data_fim_completa)
        
        if empresa:
            query = query.filter(NotaFiscal.empresa.ilike(f"%{empresa}%"))
        
        if valor_min is not None:
            query = query.filter(NotaFiscal.valor_total >= valor_min)
        
        if valor_max is not None:
            query = query.filter(NotaFiscal.valor_total <= valor_max)
        
        if categoria:
            query = query.filter(NotaFiscal.categoria == categoria)
        
        return query.order_by(
            NotaFiscal.data.desc()
        ).offset(skip).limit(limit).all()


    @staticmethod
    def count_notas_fiscais(
        db: Session,
        user_id: int,
        data_inicio: Optional[date] = None,
        data_fim: Optional[date] = None,
        empresa: Optional[str] = None,
        valor_min: Optional[float] = None,
        valor_max: Optional[float] = None,
        categoria: Optional[str] = None  
    ) -> int:
        """Conta o total de notas fiscais que atendem aos filtros"""
        query = db.query(func.count(NotaFiscal.id)).filter(
            NotaFiscal.user_id == user_id
        )
        
        if data_inicio:
            query = query.filter(NotaFiscal.data >= data_inicio)
        
        if data_fim:
            data_fim_completa = datetime.combine(data_fim, time(23, 59, 59))
            query = query.filter(NotaFiscal.data <= data_fim_completa)
        
        if empresa:
            query = query.filter(NotaFiscal.empresa.ilike(f"%{empresa}%"))
        
        if valor_min is not None:
            query = query.filter(NotaFiscal.valor_total >= valor_min)
        
        if valor_max is not None:
            query = query.filter(NotaFiscal.valor_total <= valor_max)
        
        if categoria:
            query = query.filter(NotaFiscal.categoria == categoria)
        
        return query.scalar()
    
    
    
    
    @staticmethod
    def calculate_and_update_metrics(db: Session, user_id: int):
        """
        Calcula o faturamento total (total_gasto) a partir das Notas Fiscais 
        emitidas no ANO CORRENTE e atualiza o registro Metrica do usuário.
        """
        
        # determina o primeiro dia do ano corrente (Filtro Anual)
        today = datetime.now()
        start_of_year = datetime(today.year, 1, 1)
        logging.info(f"CALCULO: Filtrando notas a partir de: {start_of_year}")
        
        # sOMA DOS VALORES: Filtra por user_id E PELA DATA (Filtro Anual)
        faturamento_total = db.query(func.sum(NotaFiscal.valor_total)).filter(
            NotaFiscal.user_id == user_id,
            # apenas notas deste ano
            NotaFiscal.data >= start_of_year 
        ).scalar() or 0.0

        # busca/cria a metrica
        metrica: Optional[Metrica] = db.query(Metrica).filter(Metrica.user_id == user_id).first()
        if not metrica:
            metrica = Metrica(
                user_id=user_id,
                limite=0,
                total_gasto=0.0,
                ultimo_alerta_percentual=0.0
            )
            db.add(metrica)
            
            metrica.total_gasto = 0.0
            metrica.limite = 81000.00
            metrica.ultimo_alerta_percentual = 0.0
        else:
            
            if metrica.limite is None:
                metrica.limite = 81000.00
            if metrica.ultimo_alerta_percentual is None:
                metrica.ultimo_alerta_percentual = 0.0
        
        # Lógica de RESET ANUAL do alerta (Se o faturamento deste ano for 0 e antes era > 0, reseta o alerta)
        if faturamento_total == 0 and metrica.total_gasto > 0:
             metrica.ultimo_alerta_percentual = 0.0
             logging.info(f"Metrica de {user_id} RESETADA. O ciclo de alerta anual recomeça.")
        
        # Atualiza o campo total_gasto com o faturamento ANUAL
        metrica.total_gasto = faturamento_total
        
        db.commit()
        db.refresh(metrica)
        
        return metrica

    @staticmethod
    def check_limit_and_notify(db: Session, metrica: Metrica, user: User):
        if metrica.limite is None or metrica.limite <= 0:
            return
        
        if metrica.ultimo_alerta_percentual is None:
            metrica.ultimo_alerta_percentual = 0.0
        
        limite = metrica.limite
        faturamento = metrica.total_gasto
        
        if limite == 0:
            return 

        percentual_atual = faturamento / limite
        
        for threshold in sorted(ALERT_THRESHOLDS):
            is_threshold_reached = percentual_atual >= (threshold - COMPARISON_PRECISION)
            is_alert_not_sent = metrica.ultimo_alerta_percentual < (threshold - COMPARISON_PRECISION)
            
            if is_threshold_reached and is_alert_not_sent:
                EmailService.send_alert_email(user, faturamento, limite, percentual_atual)
                metrica.ultimo_alerta_percentual = threshold
                db.add(metrica)
                db.commit()
                db.refresh(metrica)
                
                logging.info(f"Alerta enviado para {user.email}: Limiar {threshold*100:.0f}% atingido.")

    @staticmethod
    def create_nota_fiscal(db: Session, user_id: int, nota_data: NotaFiscalCreate) -> NotaFiscal:
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.is_active:  
            raise HTTPException(status_code=400, detail="Usuário não encontrado ou inativo.")
            
        db_nota = NotaFiscal(
            user_id=user_id,
            valor_total=nota_data.valor_total,
            data=nota_data.data,
            empresa=nota_data.empresa,
            cnpj=nota_data.cnpj,
            url=nota_data.url,
            categoria=nota_data.categoria.value if nota_data.categoria else None,  
        )
        
        db.add(db_nota)
        db.commit()
        db.refresh(db_nota)
        
        metrica = FiscalService.calculate_and_update_metrics(db, user_id)
        FiscalService.check_limit_and_notify(db, metrica, user)
        
        return db_nota

    @staticmethod
    def get_notas_fiscais_by_user(db: Session, user_id: int) -> List[NotaFiscal]:
        """
        Retorna todas as notas fiscais do usuário.
        """
        return db.query(NotaFiscal).filter(NotaFiscal.user_id == user_id).all()

    @staticmethod
    def get_user_metrics(db: Session, user_id: int):
        """
        Retorna as métricas do usuário, calculando se necessário.
        """
        metrica = FiscalService.calculate_and_update_metrics(db, user_id)
        percentual_atingido = (metrica.total_gasto / metrica.limite) * 100 if metrica.limite and metrica.limite > 0 else 0.0
        return MetricaResponse(
            user_id=metrica.user_id,
            total_gasto=metrica.total_gasto,
            limite=metrica.limite,
            updated_at=metrica.updated_at,
            percentual_atingido=percentual_atingido
        )
    
    @staticmethod
    def update_nota_fiscal(
        db: Session,
        nota_id: int,
        user_id: int,
        nota_data: NotaFiscalUpdate
    ) -> Optional[NotaFiscal]:
        """Atualiza uma nota fiscal existente"""
        db_nota = db.query(NotaFiscal).filter(
            NotaFiscal.id == nota_id,
            NotaFiscal.user_id == user_id
        ).first()
        
        if not db_nota:
            return None
        
        update_data = nota_data.model_dump(exclude_unset=True)
        
        if 'categoria' in update_data and update_data['categoria'] is not None:
            if hasattr(update_data['categoria'], 'value'):
                update_data['categoria'] = update_data['categoria'].value
        
        for field, value in update_data.items():
            setattr(db_nota, field, value)
        
        db.commit()
        db.refresh(db_nota)
        
        # Recalcula métricas após atualização
        user = db.query(User).filter(User.id == user_id).first()
        metrica = FiscalService.calculate_and_update_metrics(db, user_id)
        FiscalService.check_limit_and_notify(db, metrica, user)
        
        return db_nota
    
    @staticmethod
    def delete_nota_fiscal(db: Session, nota_id: int, user_id: int) -> bool:
        """Deleta uma nota fiscal (hard delete)"""
        db_nota = db.query(NotaFiscal).filter(
            NotaFiscal.id == nota_id,
            NotaFiscal.user_id == user_id
        ).first()
        
        if not db_nota:
            return False
        
        db.delete(db_nota)
        db.commit()
        
        # Recalcula métricas após deleção
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            metrica = FiscalService.calculate_and_update_metrics(db, user_id)
            FiscalService.check_limit_and_notify(db, metrica, user)
        
        return True
    
    @staticmethod
    def update_user_limit(db: Session, user_id: int, new_limit: float) -> Metrica:
        """Atualiza o limite customizado do usuário e recalcula o percentual"""
        metrica = db.query(Metrica).filter(Metrica.user_id == user_id).first()
        
        if not metrica:
            # Se não existe, cria com o novo limite
            metrica = Metrica(user_id=user_id, limite=new_limit, total_gasto=0.0)
            db.add(metrica)
        else:
            metrica.limite = new_limit
            
        db.commit()
        db.refresh(metrica)
        return metrica