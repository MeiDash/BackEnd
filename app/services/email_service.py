
import smtplib
from email.mime.text import MIMEText
from typing import List
import logging
import ssl 
from datetime import datetime

from app.models import User 
from app.core.config import settings 

# limiares de alerta em percentual. 
ALERT_THRESHOLDS: List[float] = [0.50, 0.70, 0.80, 0.90, 1.00] 


logging.basicConfig(level=logging.INFO)

class EmailService:
    @staticmethod
    def send_alert_email(
        user: User, 
        faturamento_total: float, 
        limite_anual: float, 
        percentual: float
    ):
        """
        Envia um e-mail de alerta real usando as configurações SMTP.
        """
        percentual_formatado = f"{percentual * 100:.2f}%"
        
        assunto = f"⚠️ Alerta MEI: Faturamento em {percentual_formatado} do limite!"
        
        corpo_html = f"""
        <html>
            <body>
                <p>Olá <strong>{user.name}</strong>,</p>
                
                <p>Identificamos que seu faturamento total acumulado atingiu <strong>{percentual_formatado}</strong> do limite anual do MEI (R$ {limite_anual:,.2f}).</p>
                
                <p>Seu faturamento atual é de <strong>R$ {faturamento_total:,.2f}</strong>.</p>
                
                <p><strong>🚨 Atenção!</strong> Você está se aproximando do teto. Planeje suas finanças para evitar o desenquadramento.</p>
                
                <p>Atenciosamente,<br>Equipe MeiDash</p>
                <br>
                <small>Enviado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</small>
            </body>
        </html>
        """
        
        msg = MIMEText(corpo_html, 'html', 'utf-8')
        msg['Subject'] = assunto
        msg['From'] = settings.EMAIL_SENDER
        msg['To'] = user.email

        try:
            # SSL/TLS para conexão segura
            context = ssl.create_default_context()
            
            with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
                server.starttls(context=context) 
                server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
                server.send_message(msg)
            
            logging.info(f"E-mail de alerta REAL enviado para {user.email}. Limiar: {percentual_formatado}")

        except smtplib.SMTPAuthenticationError:
            logging.error(f"Falha de Autenticação SMTP. Verifique Senha/App Password para {settings.SMTP_USERNAME}.")
            
        except Exception as e:
            logging.error(f"Falha geral ao enviar e-mail REAL para {user.email}: {e}")