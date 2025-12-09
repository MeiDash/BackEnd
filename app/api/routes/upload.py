from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import os
import uuid
from pathlib import Path

router = APIRouter(
    prefix="/api",
    tags=["Uploads"],
)

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Faz upload de um arquivo e retorna a URL.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="Nome do arquivo inválido")

    # Verificar se é PDF (opcional, mas recomendado)
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Apenas arquivos PDF são permitidos")

    # Gerar nome único para o arquivo
    file_extension = Path(file.filename).suffix
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = UPLOAD_DIR / unique_filename

    try:
        # Salvar o arquivo
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        # Retornar a URL (assumindo localhost:8000)
        url = f"http://localhost:8000/uploads/{unique_filename}"
        return {"url": url}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao salvar arquivo: {str(e)}")