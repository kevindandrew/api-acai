from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional


class ClienteBase(BaseModel):
    ci_nit: str = Field(..., min_length=3, max_length=20, example="1234567890")
    apellido: str = Field(..., min_length=2, max_length=50, example="Pérez")


class ClienteCreate(ClienteBase):
    pass


class ClienteResponse(ClienteBase):
    id_cliente: int
    fecha_registro: datetime

    class Config:
        from_attributes = True


class ClienteUpdate(BaseModel):
    ci_nit: Optional[str] = Field(None, min_length=3, max_length=20)
    apellido: Optional[str] = Field(None, min_length=2, max_length=50)
