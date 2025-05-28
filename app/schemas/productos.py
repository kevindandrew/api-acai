from decimal import Decimal
from datetime import date
from pydantic import BaseModel, Field
from typing import Optional, Literal

UnidadMedida = Literal['kg', 'litro', 'unidad', 'gramo']

# --------------------------
# Esquemas para Productos Establecidos
# --------------------------


class ProductoEstablecidoBase(BaseModel):
    nombre: str = Field(..., max_length=50, example="Helado de Vainilla")
    descripcion: Optional[str] = Field(
        None, example="Delicioso helado de vainilla artesanal")
    precio_unitario: Decimal = Field(..., gt=0,
                                     decimal_places=2, example=15.50)
    es_helado: bool = Field(default=True, example=True)


class ProductoEstablecidoCreate(ProductoEstablecidoBase):
    pass


class ProductoEstablecidoResponse(ProductoEstablecidoBase):
    id_producto_establecido: int

    class Config:
        from_attributes = True

# --------------------------
# Esquemas para Materias Primas
# --------------------------


class MateriaPrimaBase(BaseModel):
    nombre: str = Field(..., max_length=50, example="Vainilla")
    precio_unitario: Decimal = Field(..., gt=0, decimal_places=2, example=5.75)
    unidad: UnidadMedida = Field(..., example="kg")
    stock_minimo: Decimal = Field(default=0, decimal_places=2, example=2.5)
    fecha_caducidad: Optional[date] = Field(None, example="2023-12-31")


class MateriaPrimaCreate(MateriaPrimaBase):
    pass


class MateriaPrimaResponse(MateriaPrimaBase):
    id_materia_prima: int

    class Config:
        from_attributes = True
