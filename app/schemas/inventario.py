from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal
from datetime import date


class InventarioMateriaBase(BaseModel):
    id_sucursal: int
    id_materia_prima: int
    cantidad_stock: Decimal = Field(max_digits=10, decimal_places=2)


class InventarioMateriaCreate(InventarioMateriaBase):
    pass


class InventarioMateriaResponse(InventarioMateriaBase):
    nombre: Optional[str] = None
    unidad: Optional[str] = None
    precio_unitario: Optional[Decimal] = None
    stock_minimo: Optional[Decimal] = None
    fecha_caducidad: Optional[date] = None
    bajo_stock: Optional[bool] = None

    class Config:
        from_attributes = True


class InventarioProductoBase(BaseModel):
    id_sucursal: int
    id_producto_establecido: int
    cantidad_disponible: int


class InventarioProductoCreate(InventarioProductoBase):
    pass


class InventarioProductoResponse(InventarioProductoBase):
    nombre: Optional[str] = None
    es_helado: Optional[bool] = None

    class Config:
        from_attributes = True


class AjusteMateriaStock(BaseModel):
    cantidad: Decimal = Field(max_digits=10, decimal_places=2)
    motivo: Optional[str] = None


class AjusteProductoStock(BaseModel):
    cantidad: int
    motivo: Optional[str] = None


class TransferenciaProductos(BaseModel):
    id_sucursal_origen: int
    id_sucursal_destino: int
    id_producto_establecido: int
    cantidad: int
    motivo: Optional[str] = None


class AlertaStockResponse(BaseModel):
    tipo: str  # 'materia_prima' o 'producto'
    id_item: int
    nombre: str
    unidad: Optional[str] = None
    stock_actual: Decimal
    stock_minimo: Optional[Decimal] = None
    diferencia: Optional[Decimal] = None
    sucursal_id: int
    sucursal_nombre: Optional[str] = None
    fecha_caducidad: Optional[date] = None

# ... (los schemas anteriores permanecen igual)


class AsignarMateriaPrimaSucursal(BaseModel):
    id_materia_prima: int
    id_sucursal: int
    cantidad_inicial: Decimal = Field(max_digits=10, decimal_places=2)


class AsignarProductoSucursal(BaseModel):
    id_producto_establecido: int
    id_sucursal: int
    cantidad_inicial: int
