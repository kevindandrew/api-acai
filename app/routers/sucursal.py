from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.inventario_materia_prima import InventarioMateriaPrima
from app.models.inventario_producto_establecido import InventarioProductoEstablecido
from app.models.personal import Personal
from app.models.sucursal import Sucursal
from app.schemas.sucursal import (
    SucursalCreate,
    SucursalResponse,
    SucursalUpdate
)
from app.dependencies import require_admin, require_encargado

router = APIRouter(
    prefix="/sucursales",
    tags=["Sucursales"],
)


@router.post(
    "/",
    response_model=SucursalResponse,
    status_code=status.HTTP_201_CREATED,
)
def crear_sucursal(
    sucursal: SucursalCreate,
    db: Session = Depends(get_db),
    current_user: Personal = Depends(require_admin)
):
    """Crea una nueva sucursal (solo admin)"""
    db_sucursal = Sucursal(**sucursal.model_dump())
    db.add(db_sucursal)
    db.commit()
    db.refresh(db_sucursal)
    return db_sucursal


@router.get("/", response_model=List[SucursalResponse])
def listar_sucursales(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Personal = Depends(require_admin)
):
    """Lista todas las sucursales (paginado)"""
    return db.query(Sucursal).offset(skip).limit(limit).all()


@router.get("/{sucursal_id}", response_model=SucursalResponse)
def obtener_sucursal(
    sucursal_id: int,
    db: Session = Depends(get_db),
    current_user: Personal = Depends(require_admin)
):
    """Obtiene los detalles de una sucursal específica"""
    sucursal = db.query(Sucursal).get(sucursal_id)
    if not sucursal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sucursal no encontrada"
        )
    return sucursal


@router.put("/{sucursal_id}", response_model=SucursalResponse)
def actualizar_sucursal(
    sucursal_id: int,
    sucursal_data: SucursalUpdate,
    db: Session = Depends(get_db),
    current_user: Personal = Depends(require_admin)
):
    """Actualiza los datos de una sucursal"""
    sucursal = db.query(Sucursal).get(sucursal_id)
    if not sucursal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sucursal no encontrada"
        )

    update_data = sucursal_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(sucursal, field, value)

    db.commit()
    db.refresh(sucursal)
    return sucursal


@router.get("/{sucursal_id}/inventario")
def obtener_inventario_sucursal(
    sucursal_id: int,
    db: Session = Depends(get_db),
    current_user: Personal = Depends(require_admin)
):
    """Obtiene el inventario completo de una sucursal"""
    sucursal = db.query(Sucursal).get(sucursal_id)
    if not sucursal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sucursal no encontrada"
        )

    return {
        "sucursal": sucursal,
        "inventario_materias": sucursal.inventario_materias,
        "inventario_productos": sucursal.inventario_productos
    }


@router.delete(
    "/{sucursal_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def eliminar_sucursal(
    sucursal_id: int,
    db: Session = Depends(get_db),
    current_user: Personal = Depends(require_admin)
):
    """
    Elimina una sucursal (solo administradores).
    - Verifica que no tenga personal asignado
    - Verifica que no tenga inventario registrado
    - Eliminación física (opcional: puedes cambiar a eliminación lógica)
    """
    sucursal = db.query(Sucursal).get(sucursal_id)

    if not sucursal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sucursal no encontrada"
        )

    # Verificar si tiene personal asignado
    personal_count = db.query(Personal).filter(
        Personal.id_sucursal == sucursal_id).count()
    if personal_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No se puede eliminar: {personal_count} empleados asignados"
        )

    # Verificar inventario de materias primas
    inventario_materias = db.query(InventarioMateriaPrima).filter(
        InventarioMateriaPrima.id_sucursal == sucursal_id
    ).count()

    if inventario_materias > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede eliminar: existe inventario de materias primas"
        )

    # Verificar inventario de productos
    inventario_productos = db.query(InventarioProductoEstablecido).filter(
        InventarioProductoEstablecido.id_sucursal == sucursal_id
    ).count()

    if inventario_productos > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede eliminar: existe inventario de productos"
        )

    # Si pasa todas las validaciones, eliminar
    db.delete(sucursal)
    db.commit()

    return None  # 204 No Content
