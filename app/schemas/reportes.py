from pydantic import BaseModel
from typing import List, Optional


class ReporteProductosResponse(BaseModel):
    producto: str
    ventas: int
    porcentaje: float


class ReporteSucursalResponse(BaseModel):
    sucursal: str
    ventas_totales: float
    pedidos_atendidos: int


class RecomendacionResponse(BaseModel):
    producto_id: int
    nombre: str
    veces_vendido: int
    imagen_url: Optional[str]
