"""
Serviço de usuário com lógica de negócio
"""
import ssl
from app.core.config import settings
from app.schemas.user import UserUpdatePassword
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models import User
from app.schemas import UserCreate, UserUpdate, UserResponse
from app.schemas import UserLogin, Token, UserResponse, ForgotPasswordRequest, MessageResponse
from app.core.security import hash_password, verify_password, pwd_context
from typing import Optional, List
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from passlib.context import CryptContext
from jose import JWTError, jwt
import os
from dotenv import load_dotenv
import smtplib
from datetime import datetime, timezone, timedelta

class UserService:
    """Serviço para operações de usuário"""
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """Obtém usuário por email"""
        return db.query(User).filter(User.email == email).first()
    
    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[User]:
        """Obtém usuário por username"""
        return db.query(User).filter(User.name == username).first()
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        """Obtém usuário por ID"""
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def get_all_users(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None
    ) -> List[User]:
        """Obtém todos os usuários com paginação"""
        query = db.query(User)
        
        if is_active is not None:
            query = query.filter(User.is_active == is_active)
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def create_user(db: Session, user_data: UserCreate) -> User:
        """Cria um novo usuário"""
        db_user = User(
            email=user_data.email,
            name=user_data.name,
            nome_empresa=getattr(user_data, "nome_empresa", None),
            cnpj=getattr(user_data, "cnpj", None),
            occupation=getattr(user_data, "occupation", None),
            hashed_password=hash_password(user_data.password),
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    
    @staticmethod
    def update_user(
        db: Session,
        user_id: int,
        user_data: UserUpdate
    ) -> Optional[User]:
        """Atualiza um usuário existente"""
        db_user = db.query(User).filter(User.id == user_id).first()
        
        if not db_user:
            return None
        
        update_data = user_data.model_dump(exclude_unset=True)
        
        # Hash da nova senha se fornecida
        if "password" in update_data:
            update_data["hashed_password"] = hash_password(update_data.pop("password"))
        
        for field, value in update_data.items():
            setattr(db_user, field, value)
        
        db.commit()
        db.refresh(db_user)
        return db_user
    
    @staticmethod
    def delete_user(db: Session, user_id: int) -> bool:
        """Deleta um usuário (soft delete)"""
        db_user = db.query(User).filter(User.id == user_id).first()
        
        if not db_user:
            return False
        
        db_user.is_active = False
        db.commit()
        return True
    
    @staticmethod
    def authenticate_user(
        db: Session,
        email: str,
        password: str
    ) -> Optional[User]:
        """Autentica um usuário com email e senha"""
        print(f"🔐 authenticate_user: buscando usuário com email: {email}")
        user = UserService.get_user_by_email(db, email)
        
        if not user:
            print(f"❌ authenticate_user: usuário não encontrado com email: {email}")
            return None
        
        print(f"✅ authenticate_user: usuário encontrado")
        print(f"   Email: {user.email}")
        print(f"   Ativo: {user.is_active}")
        print(f"   Hash armazenado: {user.hashed_password[:50]}...")
        
        if not user.is_active:
            print(f"❌ authenticate_user: usuário inativo")
            return None
        
        print(f"🔐 authenticate_user: verificando senha...")
        password_valid = verify_password(password, user.hashed_password)
        print(f"🔐 authenticate_user: resultado da verificação: {password_valid}")
        
        if not password_valid:
            print(f"❌ authenticate_user: senha inválida para {email}")
            return None
        

        print(f"✅ authenticate_user: autenticação bem-sucedida para {email}")

        return user
    
    @staticmethod
    def user_exists(db: Session, email: str = None, username: str = None) -> bool:
        """Verifica se um usuário já existe"""
        query = db.query(User)
        
        filters = []
        if email:
            filters.append(User.email == email)
        if username:
            filters.append(User.name == username)
        
        if not filters:
            return False
        
        return query.filter(or_(*filters)).first() is not None

    @staticmethod
    def update_password(db: Session, user_id: int, passwords: UserUpdatePassword) -> bool:
        """
        Verifica a senha atual e atualiza para a nova senha
        """
        db_user = db.query(User).filter(User.id == user_id).first()
        
        if not db_user:
            return False
            
        if not verify_password(passwords.current_password, db_user.hashed_password):
            return False
            
        db_user.hashed_password = hash_password(passwords.new_password)
        db.commit()
        return True

    @staticmethod
    def send_reset_email(to_email: str, token: str) -> None:
        reset_link = f"{settings.FRONTEND_URL}/recuperar-senha?token={token}"

        html = f"""
        <html><body>
        <p>Você solicitou a redefinição de senha.</p>
        <p><a href="{reset_link}">Clique aqui para redefinir sua senha</a></p>
        <p><small>O link expira em {settings.RESET_TOKEN_EXPIRE_MINUTES} minutos.
            Se não foi você, ignore este e-mail.</small></p>
        </body></html>
        """

        msg = MIMEText(html, "html", "utf-8")
        msg["Subject"] = "Redefinição de senha"
        msg["From"] = settings.EMAIL_SENDER
        msg["To"] = to_email

        context = ssl.create_default_context()  # ← isso faltava

        with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
            server.starttls(context=context)    # ← passando o context
            server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            server.send_message(msg)            # ← igual ao seu EmailService

    @staticmethod
    def create_reset_token(email: str) -> str:
        """Gera um JWT de reset com expiração e 'purpose' para evitar reutilização."""
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.RESET_TOKEN_EXPIRE_MINUTES)
        payload = {
            "sub": email,
            "purpose": "password_reset",  # impede uso de tokens de outros fluxos
            "exp": expire,
        }
        return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    @staticmethod
    def decode_reset_token(token: str) -> str | None:
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            if payload.get("purpose") != "password_reset":
                return None
            return payload.get("sub")  # o email
        except JWTError:
            return None
        
    @staticmethod
    def reset_password(token: str, new_password: str, db: Session) -> bool:
        email = UserService.decode_reset_token(token)
        if not email:
            return False

        user = db.query(User).filter(User.email == email).first()
        if not user:
            return False

        user.hashed_password = hash_password(new_password)
        db.commit()
        return True