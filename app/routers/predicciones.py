from datetime import datetime, timedelta
from typing import List
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
import logging
from pydantic import BaseModel
from app.database import get_db
from app.models import Pedido, DetallePedido, ProductoEstablecido, MateriaPrima, InventarioMateriaPrima
from app.models.detalle_producto_personalizado import DetalleProductoPersonalizado
from app.models.producto_personalizado import ProductoPersonalizado
from app.dependencies import require_admin, require_vendedor
from app.models.personal import Personal
router = APIRouter(
    prefix="/predicciones",
    tags=["Predicciones"],
    responses={404: {"description": "No encontrado"}},
)

logger = logging.getLogger(__name__)

# -------------------------
# Modelos de Respuesta Simplificados
# -------------------------


class PrediccionTendenciaResponse(BaseModel):
    producto: str
    crecimiento: str
    ventas_recientes: int
    ventas_anteriores: int


class PrediccionDemandaResponse(BaseModel):
    producto: str
    demanda_proyectada: float
    unidad: str


class PrediccionStockResponse(BaseModel):
    materia_prima: str
    dias_restantes: float
    unidad: str

# -------------------------
# Endpoints Simplificados
# -------------------------


@router.get("/tendencias", response_model=List[PrediccionTendenciaResponse])
def predecir_tendencias(
    db: Session = Depends(get_db),
    current_user: Personal = Depends(require_admin),
    dias_analisis: int = Query(
        30, description="Días a analizar para detectar tendencias")
):
    """
    Predice tendencias comparando la primera mitad del período con la segunda mitad.
    Método simple: Comparación de ventas entre dos períodos iguales.
    """
    try:
        fecha_fin = datetime.now()
        fecha_medio = fecha_fin - timedelta(days=dias_analisis//2)
        fecha_inicio = fecha_fin - timedelta(days=dias_analisis)

        # Consulta para el período más reciente (segunda mitad)
        ventas_recientes = db.query(
            ProductoEstablecido.nombre,
            func.sum(DetallePedido.cantidad).label("ventas")
        ).join(DetallePedido).join(Pedido).filter(
            Pedido.fecha_pedido >= fecha_medio,
            Pedido.fecha_pedido <= fecha_fin,
            Pedido.estado == "Pagado"
        ).group_by(ProductoEstablecido.nombre).all()

        # Consulta para el período anterior (primera mitad)
        ventas_anteriores = db.query(
            ProductoEstablecido.nombre,
            func.sum(DetallePedido.cantidad).label("ventas")
        ).join(DetallePedido).join(Pedido).filter(
            Pedido.fecha_pedido >= fecha_inicio,
            Pedido.fecha_pedido < fecha_medio,
            Pedido.estado == "Pagado"
        ).group_by(ProductoEstablecido.nombre).all()

        # Convertir a diccionarios para fácil acceso
        ventas_recientes_dict = {
            nombre: ventas for nombre, ventas in ventas_recientes}
        ventas_anteriores_dict = {
            nombre: ventas for nombre, ventas in ventas_anteriores}

        # Calcular crecimiento para productos presentes en ambos períodos
        tendencias = []
        for producto in ventas_recientes_dict:
            if producto in ventas_anteriores_dict and ventas_anteriores_dict[producto] > 0:
                crecimiento = (
                    ventas_recientes_dict[producto] - ventas_anteriores_dict[producto]) / ventas_anteriores_dict[producto]
                tendencias.append({
                    "producto": producto,
                    "crecimiento": f"{crecimiento:.0%}",
                    "ventas_recientes": ventas_recientes_dict[producto],
                    "ventas_anteriores": ventas_anteriores_dict[producto]
                })

        # Ordenar por mayor crecimiento
        tendencias.sort(key=lambda x: float(
            x['crecimiento'].replace('%', '')), reverse=True)

        return tendencias[:10]  # Devolver solo las 10 principales tendencias

    except Exception as e:
        logger.error(f"Error en predicción de tendencias: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Error al calcular tendencias")


@router.get("/demanda/{producto_id}", response_model=PrediccionDemandaResponse)
def predecir_demanda(
    producto_id: int,
    dias_proyeccion: int = Query(7, description="Días a proyectar"),
    db: Session = Depends(get_db),
    current_user: Personal = Depends(require_admin)
):
    """
    Predice demanda usando promedio simple de ventas históricas.
    Método simple: Promedio de ventas diarias multiplicado por días a proyectar.
    """
    try:
        # Obtener nombre del producto
        producto = db.query(ProductoEstablecido.nombre).filter(
            ProductoEstablecido.id_producto_establecido == producto_id
        ).first()

        if not producto:
            raise HTTPException(
                status_code=404, detail="Producto no encontrado")

        # Calcular promedio de ventas diarias últimos 30 días
        ventas_totales = db.query(
            func.sum(DetallePedido.cantidad)
        ).join(Pedido).filter(
            DetallePedido.id_producto_establecido == producto_id,
            Pedido.fecha_pedido >= datetime.now() - timedelta(days=30),
            Pedido.estado == "Pagado"
        ).scalar() or 0

        promedio_diario = ventas_totales / 30
        demanda = promedio_diario * dias_proyeccion

        return {
            "producto": producto[0],
            "demanda_proyectada": round(demanda, 2),
            "unidad": "unidades"
        }

    except Exception as e:
        logger.error(f"Error en predicción de demanda: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Error al predecir demanda")


@router.get("/stock-riesgo", response_model=List[PrediccionStockResponse])
def predecir_stock_riesgo(
    db: Session = Depends(get_db),
    current_user: Personal = Depends(require_admin),
    umbral_dias: int = Query(
        7, description="Alertar si quedan menos de X días de stock")
):
    """
    Predice riesgo de faltante de materias primas.
    Método simple: Días restantes = Stock actual / Consumo promedio diario.
    """
    try:
        # Calcular consumo diario promedio de cada materia prima (últimos 30 días)
        consumo = db.query(
            MateriaPrima.nombre,
            MateriaPrima.unidad,
            func.sum(DetalleProductoPersonalizado.cantidad).label(
                "total_consumido")
        ).join(DetalleProductoPersonalizado).join(ProductoPersonalizado).join(Pedido).filter(
            Pedido.fecha_pedido >= datetime.now() - timedelta(days=30),
            Pedido.estado == "Pagado"
        ).group_by(MateriaPrima.nombre, MateriaPrima.unidad).all()

        # Calcular stock total por materia prima
        stock = db.query(
            MateriaPrima.nombre,
            func.sum(InventarioMateriaPrima.cantidad_stock).label(
                "total_stock")
        ).join(InventarioMateriaPrima).group_by(MateriaPrima.nombre).all()

        # Convertir a diccionarios
        consumo_dict = {nombre: (total/30, unidad)
                        for nombre, unidad, total in consumo}
        stock_dict = {nombre: total for nombre, total in stock}

        # Calcular días restantes para cada materia prima
        resultados = []
        for nombre in stock_dict:
            if nombre in consumo_dict and consumo_dict[nombre][0] > 0:
                dias_restantes = stock_dict[nombre] / consumo_dict[nombre][0]
                if dias_restantes <= umbral_dias:
                    resultados.append({
                        "materia_prima": nombre,
                        "dias_restantes": round(dias_restantes, 1),
                        "unidad": consumo_dict[nombre][1]
                    })

        # Ordenar por menor cantidad de días restantes
        resultados.sort(key=lambda x: x['dias_restantes'])

        return resultados

    except Exception as e:
        logger.error(f"Error en predicción de stock: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Error al predecir riesgo de stock")
