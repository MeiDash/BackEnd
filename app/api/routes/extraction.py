from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session
from app.db import get_db
from app.schemas import UserCreate, UserUpdate, UserResponse
from app.services import ExtractionService 
from app.utils import APIResponse, PaginationParams

router = APIRouter(
    prefix="/api/documents",
    tags=["Extração de entidades"],
    responses={404: {"description": "Not found"}}
)

@router.post("", status_code=status.HTTP_201_CREATED)
async def extract_total_value(
    image: UploadFile = File(...), 
    db: Session = Depends(get_db),
    ):
    try:

        content = await image.read()
    
        result = ExtractionService.extract(content)
        return result

    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err))
    
