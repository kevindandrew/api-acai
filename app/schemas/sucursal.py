from pydantic import BaseModel, Field
from datetime import time
from typing import Optional


class SucursalBase(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=50,
                        example="Sucursal Centro")
    direccion: str = Field(..., min_length=5,
                           max_length=100, example="Av. Principal 123")
    telefono: Optional[str] = Field(
        None, min_length=7, max_length=15, example="+59171234567")
    horario_apertura: Optional[time] = Field(None, example="08:00:00")
    horario_cierre: Optional[time] = Field(None, example="22:00:00")


class SucursalCreate(SucursalBase):
    pass


class SucursalResponse(SucursalBase):
    id_sucursal: int

    class Config:
        from_attributes = True  # Para Pydantic v2 (antes orm_mode=True)


class SucursalUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=2, max_length=50)
    direccion: Optional[str] = Field(None, min_length=5, max_length=100)
    telefono: Optional[str] = Field(None, min_length=7, max_length=15)
    horario_apertura: Optional[time] = None
    horario_cierre: Optional[time] = None
