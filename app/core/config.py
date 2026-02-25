"""
Configurações da aplicação
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Configurações da aplicação"""
    
    # Aplicação
    APP_NAME: str = "Backend API"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    
    # Banco de dados
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/your_db_name"
    
    # Segurança
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:5173"
    
    # CONFIGURAÇÕES PARA E-MAIL
    SMTP_SERVER: str 
    SMTP_PORT: int
    SMTP_USERNAME: str
    SMTP_PASSWORD: str
    EMAIL_SENDER: str
    
    REPORT_LOGO_PATH: str

    class Config:
        env_file = ".env"
        case_sensitive = True
    
    @property
    def allowed_origins_list(self) -> List[str]:
        """Converte string ALLOWED_ORIGINS em lista"""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]


settings = Settings()
