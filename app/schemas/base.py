# app/schemas/base.py (NOVO ARQUIVO)

from pydantic import BaseModel
from typing import Optional

def to_camel(string: str) -> str:
    parts = string.split("_")
    return parts[0] + "".join(p.title() for p in parts[1:])


class CamelModel(BaseModel):
    """BaseModel que converte nomes snake_case em camelCase para aliases."""
    model_config = {
        "alias_generator": to_camel,
        "populate_by_name": True,
    }

# Você também pode mover outros schemas base ou helpers para cá, se tiver.