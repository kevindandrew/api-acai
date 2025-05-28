from datetime import datetime
from decimal import Decimal
from typing import Literal, Optional, List
from pydantic import BaseModel, Field, validator
from typing import Optional, Union
from enum import Enum


class EstadoPedido(str, Enum):
    PAGADO = 'Pagado'
    PENDIENTE = 'Pendiente'
    CANCELADO = 'Cancelado'


class MetodoPago(str, Enum):
    EFECTIVO = 'Efectivo'
    TARJETA = 'Tarjeta'
    TRANSFERENCIA = 'Transferencia'


class DetalleProductoPersonalizadoCreate(BaseModel):
    id_materia_prima: int
    cantidad: Decimal


class ProductoPersonalizadoCreate(BaseModel):
    nombre_personalizado: Optional[str] = None
    detalles: List[DetalleProductoPersonalizadoCreate]
    margen: Optional[Decimal] = Field(
        Decimal('0.30'), gt=0, description="Margen de ganancia (ej. 0.30 = 30%)")


class DetallePedidoCreate(BaseModel):
    tipo_producto: str  # 'Establecido' o 'Personalizado'
    id_producto_establecido: Optional[int] = None
    producto_personalizado: Optional[ProductoPersonalizadoCreate] = None
    cantidad: int

    @validator('tipo_producto')
    @classmethod
    def validate_tipo_producto(cls, v):
        if v not in ['Establecido', 'Personalizado']:
            raise ValueError(
                "Tipo de producto debe ser 'Establecido' o 'Personalizado'")
        return v

    @validator('id_producto_establecido')
    @classmethod
    def validate_producto_establecido(cls, v, values):
        if values.get('tipo_producto') == 'Establecido' and v is None:
            raise ValueError(
                "id_producto_establecido es requerido para productos establecidos")
        return v

    @validator('producto_personalizado')
    @classmethod
    def validate_producto_personalizado(cls, v, values):
        if values.get('tipo_producto') == 'Personalizado' and v is None:
            raise ValueError(
                "producto_personalizado es requerido para productos personalizados")
        return v


class PedidoCreate(BaseModel):
    id_personal: int
    id_sucursal: int
    id_cliente: Optional[int] = Field(
        None,
        description="Opcional. Si no se proporciona, se considera pedido anónimo"
    )
    metodo_pago: Optional[MetodoPago] = None
    detalles: List[DetallePedidoCreate]

    @validator('id_cliente')
    @classmethod
    def validate_cliente(cls, v):
        # Permitir None para pedidos anónimos
        return v


class PedidoUpdate(BaseModel):
    estado: Optional[EstadoPedido] = None
    metodo_pago: Optional[MetodoPago] = None


class DetalleProductoPersonalizadoResponse(BaseModel):
    id_materia_prima: int
    nombre_materia: str
    cantidad: Decimal
    precio_unitario: Decimal
    subtotal: Decimal
    unidad: str


class ProductoPersonalizadoResponse(BaseModel):
    id_producto_personalizado: int
    nombre_personalizado: Optional[str]
    detalles: List[DetalleProductoPersonalizadoResponse]


class DetallePedidoEstablecidoResponse(BaseModel):
    id_detalle_pedido: int
    tipo_producto: Literal['Establecido']
    id_producto_establecido: int
    nombre_producto: str
    cantidad: int
    precio_unitario: Decimal
    subtotal: Decimal


class DetallePedidoPersonalizadoResponse(BaseModel):
    id_detalle_pedido: int
    tipo_producto: Literal['Personalizado']
    id_producto_personalizado: int
    producto_personalizado: ProductoPersonalizadoResponse
    cantidad: int
    precio_unitario: Decimal
    subtotal: Decimal


DetallePedidoResponse = Union[DetallePedidoEstablecidoResponse,
                              DetallePedidoPersonalizadoResponse]

""" class DetallePedidoResponse(BaseModel):
    id_detalle_pedido: int
    tipo_producto: str
    id_producto_establecido: Optional[int]
    nombre_producto: Optional[str]
    producto_personalizado: Optional[ProductoPersonalizadoResponse]
    cantidad: int
    precio_unitario: Decimal
    subtotal: Decimal
 """


class PedidoResponse(BaseModel):
    id_pedido: int
    fecha_pedido: datetime
    id_personal: int
    nombre_personal: str
    id_sucursal: int
    nombre_sucursal: str
    id_cliente: Optional[int]
    nombre_cliente: Optional[str]
    estado: str
    metodo_pago: Optional[str]
    total: Decimal
    detalles: List[DetallePedidoResponse]
