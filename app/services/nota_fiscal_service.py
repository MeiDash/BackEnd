

from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.nota_fiscal import NotaFiscal, Metrica
from app.models import User # Importa o modelo User
from app.schemas.nota_fiscal import NotaFiscalCreate
from app.services.email_service import EmailService, ALERT_THRESHOLDS
from typing import List
import logging
from datetime import datetime 

# Define a precisão dos limiares para comparação
COMPARISON_PRECISION = 0.0001 

class FiscalService:
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
            metrica = Metrica(user_id=user_id)
            db.add(metrica)
        
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
             raise Exception("Usuário não encontrado ou inativo.")
             
        db_nota = NotaFiscal(
            user_id=user_id,
            valor_total=nota_data.valor_total,
            data=nota_data.data,
            empresa=nota_data.empresa,
            url=nota_data.url,
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