from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from typing import List, Optional
from app.database import get_db
from app.models import (
    Pedido,
    DetallePedido,
    ProductoEstablecido,
    Sucursal,
    InventarioMateriaPrima,
    DetalleProductoPersonalizado,
    ProductoPersonalizado,
    MateriaPrima,
    Cliente
)
from sqlalchemy import func, text, and_, or_
from sqlalchemy.exc import SQLAlchemyError
import logging
from pydantic import BaseModel
from typing import Dict, Any
from app.models.personal import Personal
from app.dependencies import require_admin, require_vendedor
router = APIRouter(
    prefix="/reportes",
    tags=["Reportes"],
    responses={404: {"description": "No encontrado"}},
)
logger = logging.getLogger(__name__)
# Modelos Pydantic para respuestas estructuradas


class ProductoVendido(BaseModel):
    producto: str
    unidades_vendidas: int
    ingresos: float
    ingreso_promedio: float


class SucursalVentas(BaseModel):
    sucursal: str
    total_pedidos: int
    ventas_totales: float
    promedio_por_pedido: float


class MateriaUtilizada(BaseModel):
    materia_prima: str
    total_utilizado: float
    unidad: str
    porcentaje_pedidos: Optional[float] = None


class ReporteResponse(BaseModel):
    meta: Dict[str, Any]
    data: List[Any]

# 1. Reporte de Productos Más Vendidos


# 1. Reporte de Productos Más Vendidos - VERSIÓN CORREGIDA
@router.get("/productos-mas-vendidos", response_model=ReporteResponse)
def productos_mas_vendidos(
    dias: int = Query(30, description="Período en días"),
    db: Session = Depends(get_db),
    current_user: Personal = Depends(require_admin)
):
    """
    Versión simplificada del reporte de productos más vendidos.
    Devuelve solo productos establecidos ordenados por cantidad vendida.
    """
    try:
        fecha_inicio = datetime.now() - timedelta(days=dias)

        # Consulta básica sin joins complejos
        resultados = db.execute(text("""
            SELECT 
                pe.nombre AS producto,
                SUM(dp.cantidad) AS unidades_vendidas,
                SUM(dp.subtotal) AS ingresos
            FROM detalle_pedido dp
            JOIN producto_establecido pe ON dp.id_producto_establecido = pe.id_producto_establecido
            JOIN pedido p ON dp.id_pedido = p.id_pedido
            WHERE p.estado = 'Pagado'
            AND p.fecha_pedido >= :fecha_inicio
            GROUP BY pe.nombre
            ORDER BY unidades_vendidas DESC
        """), {"fecha_inicio": fecha_inicio}).fetchall()

        datos = [{
            "producto": producto,
            "unidades_vendidas": int(unidades),
            "ingresos": float(ingresos)
        } for producto, unidades, ingresos in resultados]

        return {
            "meta": {
                "dias_analizados": dias,
                "fecha_inicio": fecha_inicio.isoformat(),
                "total_productos": len(datos)
            },
            "data": datos
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al generar reporte: {str(e)}"
        )
# 2. Reporte de Sucursales con Más Ventas


@router.get("/sucursales-top", response_model=ReporteResponse)
def sucursales_top(
    dias: int = Query(30, ge=1, le=365, description="Período en días (1-365)"),
    ordenar_por: str = Query(
        "ventas", description="Criterio de orden (ventas|pedidos)"),
    db: Session = Depends(get_db),
    current_user: Personal = Depends(require_admin)
):
    """
    Compara el desempeño de las sucursales por volumen de ventas o cantidad de pedidos.
    """
    try:
        fecha_inicio = datetime.now(timezone.utc) - timedelta(days=dias)

        query = db.query(
            Sucursal.nombre.label("sucursal"),
            func.count(Pedido.id_pedido).label("total_pedidos"),
            func.sum(Pedido.total).label("ventas_totales"),
            (func.sum(Pedido.total) / func.count(Pedido.id_pedido)
             ).label("promedio_por_pedido")
        ).join(
            Pedido,
            Pedido.id_sucursal == Sucursal.id_sucursal
        ).filter(
            Pedido.estado == "Pagado",
            Pedido.fecha_pedido >= fecha_inicio
        ).group_by(
            Sucursal.nombre
        )

        # Ordenar según criterio
        if ordenar_por == "pedidos":
            query = query.order_by(func.count(Pedido.id_pedido).desc())
        else:  # default por ventas
            query = query.order_by(func.sum(Pedido.total).desc())

        resultados = query.all()

        return {
            "meta": {
                "dias_analizados": dias,
                "criterio_orden": ordenar_por,
                "total_sucursales": len(resultados),
                "fecha_inicio": fecha_inicio.isoformat(),
                "fecha_fin": datetime.now(timezone.utc).isoformat()
            },
            "data": [
                {
                    "sucursal": nombre,
                    "total_pedidos": int(pedidos),
                    "ventas_totales": float(ventas),
                    "promedio_por_pedido": float(promedio) if pedidos > 0 else 0
                } for nombre, pedidos, ventas, promedio in resultados
            ]
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al generar reporte de sucursales: {str(e)}"
        )

# 3. Materias Primas Más Utilizadas


@router.get("/materias-mas-usadas", response_model=ReporteResponse)
def materias_mas_usadas(
    dias: int = Query(30, description="Período en días"),
    db: Session = Depends(get_db),
    current_user: Personal = Depends(require_admin)
):
    """
    Reporte de materias primas más utilizadas en productos personalizados.
    Devuelve las materias primas ordenadas por cantidad utilizada.
    """
    try:
        fecha_inicio = datetime.now() - timedelta(days=dias)

        # Consulta corregida con el nombre exacto de la tabla
        resultados = db.execute(text("""
            SELECT 
                mp.nombre AS materia_prima,
                SUM(dpp.cantidad) AS total_utilizado,
                mp.unidad
            FROM detalle_productopersonalizado dpp
            JOIN materia_prima mp ON dpp.id_materia_prima = mp.id_materia_prima
            JOIN producto_personalizado pp ON dpp.id_producto_personalizado = pp.id_producto_personalizado
            JOIN pedido p ON pp.id_pedido = p.id_pedido
            WHERE p.fecha_pedido >= :fecha_inicio
            AND p.estado = 'Pagado'  
            GROUP BY mp.nombre, mp.unidad
            ORDER BY total_utilizado DESC
            LIMIT 10
        """), {"fecha_inicio": fecha_inicio}).fetchall()

        datos = [{
            "materia_prima": nombre,
            "total_utilizado": float(cantidad),
            "unidad": unidad
        } for nombre, cantidad, unidad in resultados]

        return {
            "meta": {
                "dias_analizados": dias,
                "fecha_inicio": fecha_inicio.isoformat(),
                "total_materias": len(datos)
            },
            "data": datos
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al generar reporte: {str(e)}"
        )
# 4. Reporte de Fidelización de Clientes


@router.get("/clientes-frecuentes", response_model=ReporteResponse)
def clientes_frecuentes(
    top: int = Query(
        10, ge=1, le=50, description="Número de clientes a listar"),
    dias: int = Query(90, ge=1, le=365, description="Período en días (1-365)"),
    sucursal_id: Optional[int] = Query(
        None, description="Filtrar por ID de sucursal"),
    db: Session = Depends(get_db),
    current_user: Personal = Depends(require_admin)
):
    """
    Identifica los clientes más frecuentes por cantidad de pedidos y monto gastado.
    """
    try:
        fecha_inicio = datetime.now(timezone.utc) - timedelta(days=dias)

        query = db.query(
            Cliente.id_cliente,
            Cliente.ci_nit,
            Cliente.apellido,
            func.count(Pedido.id_pedido).label("total_pedidos"),
            func.sum(Pedido.total).label("total_gastado"),
            (func.sum(Pedido.total) / func.count(Pedido.id_pedido)
             ).label("promedio_por_pedido")
        ).join(
            Pedido,
            Pedido.id_cliente == Cliente.id_cliente
        ).filter(
            Pedido.estado == "Pagado",
            Pedido.fecha_pedido >= fecha_inicio,
            Pedido.id_cliente.isnot(None)
        ).group_by(
            Cliente.id_cliente,
            Cliente.ci_nit,
            Cliente.apellido
        ).order_by(
            func.sum(Pedido.total).desc()
        ).limit(top)

        if sucursal_id:
            query = query.filter(Pedido.id_sucursal == sucursal_id)

        resultados = query.all()

        return {
            "meta": {
                "dias_analizados": dias,
                "sucursal_id": sucursal_id,
                "total_clientes": len(resultados),
                "fecha_inicio": fecha_inicio.isoformat(),
                "fecha_fin": datetime.now(timezone.utc).isoformat()
            },
            "data": [
                {
                    "id_cliente": id_cliente,
                    "ci_nit": ci_nit,
                    "apellido": apellido,
                    "total_pedidos": int(pedidos),
                    "total_gastado": float(gastado),
                    "promedio_por_pedido": float(promedio) if pedidos > 0 else 0
                } for id_cliente, ci_nit, apellido, pedidos, gastado, promedio in resultados
            ]
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al generar reporte de clientes frecuentes: {str(e)}"
        )

# 5. Reporte de Ventas por Horario


@router.get("/ventas-por-horario", response_model=ReporteResponse)
def ventas_por_horario(
    dias: int = Query(7, ge=1, le=30, description="Período en días (1-30)"),
    sucursal_id: Optional[int] = Query(
        None, description="Filtrar por ID de sucursal"),
    db: Session = Depends(get_db),
    current_user: Personal = Depends(require_admin)
):
    """
    Analiza las ventas por franja horaria para identificar horas pico.
    """
    try:
        fecha_inicio = datetime.now(timezone.utc) - timedelta(days=dias)

        query = db.query(
            func.extract('hour', Pedido.fecha_pedido).label("hora"),
            func.count(Pedido.id_pedido).label("total_pedidos"),
            func.sum(Pedido.total).label("ventas_totales"),
            func.avg(Pedido.total).label("ticket_promedio")
        ).filter(
            Pedido.estado == "Pagado",
            Pedido.fecha_pedido >= fecha_inicio
        ).group_by(
            func.extract('hour', Pedido.fecha_pedido)
        ).order_by(
            func.extract('hour', Pedido.fecha_pedido)
        )

        if sucursal_id:
            query = query.filter(Pedido.id_sucursal == sucursal_id)

        resultados = query.all()

        # Formatear horas
        datos = []
        for hora, pedidos, ventas, ticket in resultados:
            hora_str = f"{int(hora):02d}:00 - {int(hora)+1:02d}:00"
            datos.append({
                "franja_horaria": hora_str,
                "total_pedidos": int(pedidos),
                "ventas_totales": float(ventas),
                "ticket_promedio": float(ticket) if pedidos > 0 else 0,
                "hora": int(hora)
            })

        return {
            "meta": {
                "dias_analizados": dias,
                "sucursal_id": sucursal_id,
                "total_franjas": len(datos),
                "fecha_inicio": fecha_inicio.isoformat(),
                "fecha_fin": datetime.now(timezone.utc).isoformat()
            },
            "data": sorted(datos, key=lambda x: x['hora'])
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al generar reporte de ventas por horario: {str(e)}"
        )
