from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from decimal import Decimal
from datetime import date
from app.models.personal import Personal
from app.database import get_db
from app.models import (
    InventarioMateriaPrima,
    InventarioProductoEstablecido,
    Sucursal,
    MateriaPrima,
    ProductoEstablecido
)
from app.schemas.inventario import (
    InventarioMateriaResponse,
    InventarioProductoResponse,
    AjusteMateriaStock,
    AjusteProductoStock,
    TransferenciaProductos,
    AlertaStockResponse,
    AsignarMateriaPrimaSucursal,
    AsignarProductoSucursal
)
from app.dependencies import get_current_user, require_encargado, require_admin_or_encargado, require_admin

router = APIRouter(
    prefix="/inventario",
    tags=["Inventario"],
)

# --------------------------
# Endpoints para Materias Primas
# --------------------------


@router.post("/materias-primas/asignar")
def asignar_materia_prima_sucursal(
    asignacion: AsignarMateriaPrimaSucursal,
    db: Session = Depends(get_db),
    current_user: Personal = Depends(require_admin_or_encargado)
):
    """
    Asigna una materia prima a una sucursal con cantidad inicial (solo admin o encargado)
    """
    # Verificar si la materia prima existe
    materia = db.query(MateriaPrima).get(asignacion.id_materia_prima)
    if not materia:
        raise HTTPException(
            status_code=404, detail="Materia prima no encontrada")

    # Verificar si la sucursal existe
    sucursal = db.query(Sucursal).get(asignacion.id_sucursal)
    if not sucursal:
        raise HTTPException(status_code=404, detail="Sucursal no encontrada")

    # Verificar si ya existe registro
    existente = db.query(InventarioMateriaPrima).filter_by(
        id_sucursal=asignacion.id_sucursal,
        id_materia_prima=asignacion.id_materia_prima
    ).first()

    if existente:
        raise HTTPException(
            status_code=400,
            detail="Esta materia prima ya está asignada a la sucursal. Use el endpoint de ajuste para modificar el stock."
        )

    # Crear nuevo registro de inventario
    nuevo_inventario = InventarioMateriaPrima(
        id_sucursal=asignacion.id_sucursal,
        id_materia_prima=asignacion.id_materia_prima,
        cantidad_stock=asignacion.cantidad_inicial
    )

    db.add(nuevo_inventario)
    db.commit()

    return {
        "message": "Materia prima asignada a sucursal exitosamente",
        "id_sucursal": nuevo_inventario.id_sucursal,
        "id_materia_prima": nuevo_inventario.id_materia_prima,
        "stock_inicial": nuevo_inventario.cantidad_stock
    }


@router.get("/materias-primas/sucursal/{sucursal_id}", response_model=List[InventarioMateriaResponse])
def obtener_inventario_materias(
    sucursal_id: int,
    bajo_stock: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: Personal = Depends(get_current_user)
):
    """Obtiene el inventario de materias primas de una sucursal"""
    # Verificar existencia de sucursal
    if not db.query(Sucursal).filter_by(id_sucursal=sucursal_id).first():
        raise HTTPException(status_code=404, detail="Sucursal no encontrada")

    query = db.query(
        InventarioMateriaPrima,
        MateriaPrima.nombre,
        MateriaPrima.unidad,
        MateriaPrima.precio_unitario,
        MateriaPrima.stock_minimo,
        MateriaPrima.fecha_caducidad
    ).join(
        MateriaPrima,
        InventarioMateriaPrima.id_materia_prima == MateriaPrima.id_materia_prima
    ).filter(
        InventarioMateriaPrima.id_sucursal == sucursal_id
    )

    if bajo_stock is not None:
        if bajo_stock:
            query = query.filter(
                InventarioMateriaPrima.cantidad_stock < MateriaPrima.stock_minimo)
        else:
            query = query.filter(
                InventarioMateriaPrima.cantidad_stock >= MateriaPrima.stock_minimo)

    inventario = query.all()

    return [{
        "id_sucursal": item.InventarioMateriaPrima.id_sucursal,
        "id_materia_prima": item.InventarioMateriaPrima.id_materia_prima,
        "cantidad_stock": item.InventarioMateriaPrima.cantidad_stock,
        "nombre": item.nombre,
        "unidad": item.unidad,
        "precio_unitario": item.precio_unitario,
        "stock_minimo": item.stock_minimo,
        "fecha_caducidad": item.fecha_caducidad,
        "bajo_stock": item.InventarioMateriaPrima.cantidad_stock < item.stock_minimo
    } for item in inventario]


@router.patch("/materias-primas/ajustar")
def ajustar_stock_materia(
    id_sucursal: int,
    id_materia: int,
    ajuste: AjusteMateriaStock,
    db: Session = Depends(get_db),
    current_user: Personal = Depends(require_admin_or_encargado)
):
    """Ajusta el stock de una materia prima (solo admin o encargado)"""
    inventario = db.query(InventarioMateriaPrima).filter_by(
        id_sucursal=id_sucursal,
        id_materia_prima=id_materia
    ).first()

    if not inventario:
        raise HTTPException(
            status_code=404, detail="Registro de inventario no encontrado")

    materia = db.query(MateriaPrima).get(id_materia)
    if not materia:
        raise HTTPException(
            status_code=404, detail="Materia prima no encontrada")

    inventario.cantidad_stock = ajuste.cantidad
    db.commit()

    return {
        "message": "Stock actualizado",
        "bajo_stock": inventario.cantidad_stock < materia.stock_minimo,
        "nuevo_stock": inventario.cantidad_stock
    }

# --------------------------
# Endpoints para Productos
# --------------------------


@router.post("/productos/asignar")
def asignar_producto_sucursal(
    asignacion: AsignarProductoSucursal,
    db: Session = Depends(get_db),
    current_user: Personal = Depends(require_admin_or_encargado)
):
    """
    Asigna un producto a una sucursal con cantidad inicial (solo admin o encargado)
    """
    # Verificar si el producto existe
    producto = db.query(ProductoEstablecido).get(
        asignacion.id_producto_establecido)
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    # Verificar si la sucursal existe
    sucursal = db.query(Sucursal).get(asignacion.id_sucursal)
    if not sucursal:
        raise HTTPException(status_code=404, detail="Sucursal no encontrada")

    # Verificar si ya existe registro
    existente = db.query(InventarioProductoEstablecido).filter_by(
        id_sucursal=asignacion.id_sucursal,
        id_producto_establecido=asignacion.id_producto_establecido
    ).first()

    if existente:
        raise HTTPException(
            status_code=400,
            detail="Este producto ya está asignado a la sucursal. Use el endpoint de ajuste para modificar el stock."
        )

    # Crear nuevo registro de inventario
    nuevo_inventario = InventarioProductoEstablecido(
        id_sucursal=asignacion.id_sucursal,
        id_producto_establecido=asignacion.id_producto_establecido,
        cantidad_disponible=asignacion.cantidad_inicial
    )

    db.add(nuevo_inventario)
    db.commit()

    return {
        "message": "Producto asignado a sucursal exitosamente",
        "id_sucursal": nuevo_inventario.id_sucursal,
        "id_producto_establecido": nuevo_inventario.id_producto_establecido,
        "stock_inicial": nuevo_inventario.cantidad_disponible
    }


@router.get("/productos/sucursal/{sucursal_id}", response_model=List[InventarioProductoResponse])
def obtener_inventario_productos(
    sucursal_id: int,
    db: Session = Depends(get_db),
    current_user: Personal = Depends(get_current_user)
):
    """Obtiene el inventario de productos establecidos de una sucursal"""
    # Verificar existencia de sucursal
    if not db.query(Sucursal).filter_by(id_sucursal=sucursal_id).first():
        raise HTTPException(status_code=404, detail="Sucursal no encontrada")

    inventario = db.query(
        InventarioProductoEstablecido,
        ProductoEstablecido.nombre,
        ProductoEstablecido.es_helado
    ).join(
        ProductoEstablecido,
        InventarioProductoEstablecido.id_producto_establecido == ProductoEstablecido.id_producto_establecido
    ).filter(
        InventarioProductoEstablecido.id_sucursal == sucursal_id
    ).all()

    return [{
        "id_sucursal": item.InventarioProductoEstablecido.id_sucursal,
        "id_producto_establecido": item.InventarioProductoEstablecido.id_producto_establecido,
        "cantidad_disponible": item.InventarioProductoEstablecido.cantidad_disponible,
        "nombre": item.nombre,
        "es_helado": item.es_helado
    } for item in inventario]

# ... (los demás endpoints permanecen iguales, solo cambiando unidad_medida por unidad donde sea necesario)


@router.patch("/productos/ajustar")
def ajustar_stock_producto(
    id_sucursal: int,
    id_producto: int,
    ajuste: AjusteProductoStock,
    db: Session = Depends(get_db),
    current_user: Personal = Depends(require_admin_or_encargado)
):
    """Ajusta el stock de un producto (solo admin o encargado)"""
    inventario = db.query(InventarioProductoEstablecido).filter_by(
        id_sucursal=id_sucursal,
        id_producto_establecido=id_producto
    ).first()

    if not inventario:
        raise HTTPException(
            status_code=404, detail="Registro de inventario no encontrado")

    inventario.cantidad_disponible = ajuste.cantidad
    db.commit()

    return {
        "message": "Stock actualizado",
        "nuevo_stock": inventario.cantidad_disponible
    }


@router.post("/productos/transferir")
def transferir_productos(
    transferencia: TransferenciaProductos,
    db: Session = Depends(get_db),
    current_user: Personal = Depends(require_admin_or_encargado)
):
    """Transfiere productos entre sucursales (solo admin o encargado)"""
    # Validaciones básicas
    if transferencia.id_sucursal_origen == transferencia.id_sucursal_destino:
        raise HTTPException(
            status_code=400, detail="No se puede transferir a la misma sucursal")

    if transferencia.cantidad <= 0:
        raise HTTPException(
            status_code=400, detail="La cantidad debe ser mayor a cero")

    # Verificar sucursales
    sucursal_origen = db.query(Sucursal).get(transferencia.id_sucursal_origen)
    sucursal_destino = db.query(Sucursal).get(
        transferencia.id_sucursal_destino)

    if not sucursal_origen or not sucursal_destino:
        raise HTTPException(status_code=404, detail="Sucursal no encontrada")

    # Verificar producto en origen
    inventario_origen = db.query(InventarioProductoEstablecido).filter_by(
        id_sucursal=transferencia.id_sucursal_origen,
        id_producto_establecido=transferencia.id_producto_establecido
    ).first()

    if not inventario_origen:
        raise HTTPException(
            status_code=404, detail="Producto no encontrado en sucursal origen")

    # Verificar stock suficiente
    if inventario_origen.cantidad_disponible < transferencia.cantidad:
        raise HTTPException(
            status_code=400,
            detail=f"Stock insuficiente. Disponible: {inventario_origen.cantidad_disponible}, Solicitado: {transferencia.cantidad}"
        )

    # Buscar o crear registro en destino
    inventario_destino = db.query(InventarioProductoEstablecido).filter_by(
        id_sucursal=transferencia.id_sucursal_destino,
        id_producto_establecido=transferencia.id_producto_establecido
    ).first()

    if not inventario_destino:
        inventario_destino = InventarioProductoEstablecido(
            id_sucursal=transferencia.id_sucursal_destino,
            id_producto_establecido=transferencia.id_producto_establecido,
            cantidad_disponible=0
        )
        db.add(inventario_destino)

    # Realizar transferencia
    inventario_origen.cantidad_disponible -= transferencia.cantidad
    inventario_destino.cantidad_disponible += transferencia.cantidad

    db.commit()

    return {
        "message": "Transferencia completada",
        "stock_origen_actualizado": inventario_origen.cantidad_disponible,
        "stock_destino_actualizado": inventario_destino.cantidad_disponible
    }


@router.get("/alertas/sucursal/{sucursal_id}", response_model=List[AlertaStockResponse])
def obtener_alertas_stock(
    sucursal_id: int,
    db: Session = Depends(get_db),
    current_user: Personal = Depends(get_current_user)
):
    """Obtiene alertas de stock bajo para una sucursal"""
    # Verificar sucursal
    sucursal = db.query(Sucursal).get(sucursal_id)
    if not sucursal:
        raise HTTPException(status_code=404, detail="Sucursal no encontrada")

    # Materias primas con stock bajo
    materias_bajas = db.query(
        InventarioMateriaPrima,
        MateriaPrima.nombre,
        MateriaPrima.unidad,
        MateriaPrima.stock_minimo,
        MateriaPrima.fecha_caducidad
    ).join(
        MateriaPrima
    ).filter(
        InventarioMateriaPrima.id_sucursal == sucursal_id,
        InventarioMateriaPrima.cantidad_stock < MateriaPrima.stock_minimo
    ).all()

    alertas = [{
        "tipo": "materia_prima",
        "id_item": item.InventarioMateriaPrima.id_materia_prima,
        "nombre": item.nombre,
        "unidad": item.unidad,
        "stock_actual": item.InventarioMateriaPrima.cantidad_stock,
        "stock_minimo": item.stock_minimo,
        "diferencia": item.stock_minimo - item.InventarioMateriaPrima.cantidad_stock,
        "sucursal_id": sucursal_id,
        "sucursal_nombre": sucursal.nombre,
        "fecha_caducidad": item.fecha_caducidad
    } for item in materias_bajas]

    return alertas
