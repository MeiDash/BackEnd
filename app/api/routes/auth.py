"""
Rotas de autenticação
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta

from app.db import get_db
from app.schemas import UserLogin, Token, UserResponse, ForgotPasswordRequest, MessageResponse, ResetPasswordRequest
from app.models.user import User
from app.services import UserService
from app.core.config import settings
from app.core.security import create_access_token
from app.utils import APIResponse


from pydantic import BaseModel, EmailStr


router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"],
    responses={404: {"description": "Not found"}},
)

@router.post("/login", response_model=Token, response_model_by_alias=False)
async def login(
    user_credentials: UserLogin,
    db: Session = Depends(get_db)
):
    """
    Autentica um usuário e retorna um token JWT
    """
    user = UserService.authenticate_user(
        db,
        email=user_credentials.email,
        password=user_credentials.password
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }


@router.post("/logout")
async def logout():
    """
    Logout do usuário (informativo, implementar blacklist de tokens se necessário)
    """
    return APIResponse.success(message="Logout realizado com sucesso")


@router.post("/forgot-password")
async def forgot_password(
    forgot_password_data: ForgotPasswordRequest,
    db: Session = Depends(get_db) 
):
    """
    Doc
    """
    generic_response = MessageResponse(
        message="Se o e-mail estiver cadastrado, você receberá as instruções em breve."
    )

    user = db.query(User).filter(User.email == forgot_password_data.email).first()  

    if not user:
        return generic_response 

    token = UserService.create_reset_token(email=user.email)

    try:
        UserService.send_reset_email(to_email=user.email, token=token)
    except smtplib.SMTPException as exc:
        print(f"[ERROR] Falha ao enviar e-mail para {user.email}: {exc}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Não foi possível enviar o e-mail. Tente novamente mais tarde.",
        )

    return generic_response

@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(
    reset_password_data: ResetPasswordRequest,
    db: Session = Depends(get_db)):
    success = UserService.reset_password(reset_password_data.token, reset_password_data.new_password, db)
    if not success:
        raise HTTPException(status_code=400, detail="Token inválido ou expirado.")
    return MessageResponse(message="Senha redefinida com sucesso.")