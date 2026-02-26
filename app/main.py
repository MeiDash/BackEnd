"""
Aplicação principal do FastAPI
"""
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
from app.api import api_router
from app.db import Base, engine

# Criar as tabelas no banco de dados
Base.metadata.create_all(bind=engine)

# Criar aplicação FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Backend API para gerenciamento de usuários",
)

# Montar diretório de uploads
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir rotas
app.include_router(api_router)


@app.get("/")
async def root():
    """Endpoint raiz da API"""
    return {
        "message": "Bem-vindo ao Backend API",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "redoc": "/redoc",
    }


@app.get("/health")
async def health_check():
    """Health check da aplicação"""
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": "Erro interno do servidor",
            "detail": str(exc) if settings.ENVIRONMENT == "development" else "Internal Error",
        }
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    """Transforma erros de validação em mensagens mais amigáveis.

    Especificamente detecta validações relacionadas ao tamanho da senha
    (mais de 72 bytes) e retorna uma mensagem clara para o cliente.
    """
    errors = exc.errors()
    
    # Procurar por erro relacionado ao campo 'password' com indicação de 72 bytes
    for err in errors:
        msg = err.get("msg", "")
        loc = err.get("loc", [])
        if "password" in str(loc).lower() and "72 bytes" in str(msg).lower():
            content = {
                "detail": [
                    {
                        "loc": loc,
                        "msg": "A senha é muito longa: limite de 72 bytes (utf-8). Use uma senha mais curta.",
                        "type": "value_error.password_too_long",
                    }
                ]
            }
            return JSONResponse(status_code=HTTP_422_UNPROCESSABLE_ENTITY, content=content)
    
    # Processar erros para remover campos não serializáveis (como bytes)
    processed_errors = []
    for err in errors:
        processed_err = {
            "loc": err.get("loc", []),
            "msg": err.get("msg", ""),
            "type": err.get("type", ""),
        }
        # Converter input para string se for bytes
        if "input" in err:
            input_value = err["input"]
            if isinstance(input_value, bytes):
                processed_err["input"] = input_value.decode('utf-8', errors='replace')
            else:
                processed_err["input"] = str(input_value)
        
        processed_errors.append(processed_err)
    
    return JSONResponse(
        status_code=HTTP_422_UNPROCESSABLE_ENTITY, 
        content={"detail": processed_errors}
    )