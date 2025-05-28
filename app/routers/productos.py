from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Literal, Optional
from decimal import Decimal
from app.database import get_db
from app.models import ProductoEstablecido, MateriaPrima
from app.schemas.productos import (
    ProductoEstablecidoCreate,
    ProductoEstablecidoResponse,
    MateriaPrimaCreate,
    MateriaPrimaResponse
)
from app.models.personal import Personal
from app.dependencies import require_admin, require_encargado

router = APIRouter(
    prefix="/productos",
    tags=["Productos"],
)

# --------------------------
# Endpoints para Productos Establecidos
# --------------------------


@router.post(
    "/establecidos",
    response_model=ProductoEstablecidoResponse,
    status_code=201,
)
def crear_producto(
    producto: ProductoEstablecidoCreate,
    db: Session = Depends(get_db),
    current_user: Personal = Depends(require_admin)
):
    """Crea un nuevo producto (helado o topping) - Solo admin"""
    db_producto = ProductoEstablecido(**producto.model_dump())
    db.add(db_producto)
    db.commit()
    db.refresh(db_producto)
    return db_producto


@router.get("/establecidos", response_model=List[ProductoEstablecidoResponse])
def listar_productos(
    tipo: Literal['helado', 'topping', 'todos'] = Query('todos'),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Personal = Depends(require_admin)
):
    """Lista productos con filtro por tipo"""
    query = db.query(ProductoEstablecido)

    if tipo != 'todos':
        es_helado = tipo == 'helado'
        query = query.filter(ProductoEstablecido.es_helado == es_helado)

    return query.offset(skip).limit(limit).all()


@router.put(
    "/establecidos/{producto_id}",
    response_model=ProductoEstablecidoResponse,

)
def actualizar_producto(
    producto_id: int,
    # Usamos Create como base para updates
    producto_data: ProductoEstablecidoCreate,
    db: Session = Depends(get_db),
    current_user: Personal = Depends(require_admin)
):
    """Actualiza un producto existente - Solo admin"""
    producto = db.query(ProductoEstablecido).get(producto_id)
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    for field, value in producto_data.model_dump().items():
        setattr(producto, field, value)

    db.commit()
    db.refresh(producto)
    return producto


@router.delete(
    "/establecidos/{producto_id}",
    status_code=204,
)
def eliminar_producto(
    producto_id: int,
    db: Session = Depends(get_db),
    current_user: Personal = Depends(require_admin)
):
    """Elimina un producto - Solo admin (validar que no esté en pedidos)"""
    producto = db.query(ProductoEstablecido).get(producto_id)
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    # Validar que no esté asociado a pedidos (ejemplo)
    if len(producto.inventarios) > 0:
        raise HTTPException(
            status_code=400,
            detail="No se puede eliminar: existe en inventarios"
        )

    db.delete(producto)
    db.commit()
    return None

# --------------------------
# Endpoints para Materias Primas
# --------------------------


@router.post(
    "/materias-primas",
    response_model=MateriaPrimaResponse,
    status_code=201,
)
def crear_materia_prima(
    materia: MateriaPrimaCreate,
    db: Session = Depends(get_db),
    current_user: Personal = Depends(require_admin)
):
    """Registra una nueva materia prima - Solo admin"""
    db_materia = MateriaPrima(**materia.model_dump())
    db.add(db_materia)
    db.commit()
    db.refresh(db_materia)
    return db_materia


@router.get("/materias-primas", response_model=List[MateriaPrimaResponse])
def listar_materias_primas(
    stock_min: Optional[Decimal] = Query(None, gt=0),
    db: Session = Depends(get_db),
    current_user: Personal = Depends(require_admin)
):
    """Lista materias primas con filtro por stock mínimo"""
    query = db.query(MateriaPrima)
    if stock_min is not None:
        query = query.filter(MateriaPrima.stock_minimo >= stock_min)
    return query.all()


@router.put(
    "/materias-primas/{materia_id}",
    response_model=MateriaPrimaResponse,
)
def actualizar_materia_prima(
    materia_id: int,
    materia_data: MateriaPrimaCreate,
    db: Session = Depends(get_db),
    current_user: Personal = Depends(require_admin)
):
    """Actualiza una materia prima - Solo admin"""
    materia = db.query(MateriaPrima).get(materia_id)
    if not materia:
        raise HTTPException(
            status_code=404, detail="Materia prima no encontrada")

    for field, value in materia_data.model_dump().items():
        setattr(materia, field, value)

    db.commit()
    db.refresh(materia)
    return materia


@router.delete(
    "/materias-primas/{materia_id}",
    status_code=204,
)
def eliminar_materia_prima(
    materia_id: int,
    db: Session = Depends(get_db),
    current_user: Personal = Depends(require_admin)
):
    """Elimina una materia prima - Solo admin (con validaciones)"""
    materia = db.query(MateriaPrima).get(materia_id)
    if not materia:
        raise HTTPException(
            status_code=404, detail="Materia prima no encontrada")

    # Validar que no esté en uso (ejemplo básico)
    if materia.detalles_productos or materia.inventarios:
        raise HTTPException(
            status_code=400,
            detail="No se puede eliminar: está en uso en productos o inventarios"
        )

    db.delete(materia)
    db.commit()
    return None
