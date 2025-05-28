from datetime import datetime
from pydantic import BaseModel, Field, EmailStr
from typing import Optional

# Esquemas comunes


class PersonalBase(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=50, example="Juan Pérez")
    usuario: str = Field(..., min_length=3, max_length=30,
                         example="juan_perez")
    id_rol: int = Field(..., gt=0, example=1)
    # Opcional pero positivo si existe
    id_sucursal: Optional[int] = Field(None, gt=0)

# Para creación (incluye contraseña)


class PersonalCreate(PersonalBase):
    contraseña: str = Field(..., min_length=6, example="secret123")

# Para respuesta (excluye contraseña)


class PersonalResponse(PersonalBase):
    id_personal: int
    id_sucursal: Optional[int] = None  # Cambiado a opcional
    fecha_ultimo_login: Optional[datetime] = None

    class Config:
        from_attributes = True  # Habilita la conversión desde ORM

# Para actualización (todos los campos opcionales)


class PersonalUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=2, max_length=50)
    usuario: Optional[str] = Field(None, min_length=3, max_length=30)
    contraseña: Optional[str] = Field(None, min_length=6)
    id_rol: Optional[int] = Field(None, gt=0)
    id_sucursal: Optional[int] = Field(None, gt=0)
