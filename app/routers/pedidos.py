from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from decimal import Decimal
from datetime import datetime
from sqlalchemy import text  # Agrega esto al inicio de tu archivo
from app.database import get_db
from app.models import (
    Pedido,
    DetallePedido,
    ProductoPersonalizado,
    DetalleProductoPersonalizado,
    ProductoEstablecido,
    MateriaPrima,
    InventarioMateriaPrima,
    Sucursal,
    Personal,
    Cliente
)
from app.models.inventario_producto_establecido import InventarioProductoEstablecido
from app.schemas.pedidos import (
    DetallePedidoEstablecidoResponse,
    DetallePedidoPersonalizadoResponse,
    PedidoCreate,
    PedidoResponse,
    PedidoUpdate,
    EstadoPedido,
    MetodoPago
)
from app.dependencies import get_current_user

router = APIRouter(
    prefix="/pedidos",
    tags=["Pedidos"],
)

# --------------------------
# Endpoints para Pedidos
# --------------------------


@router.post("/", response_model=PedidoResponse, status_code=status.HTTP_201_CREATED)
def crear_pedido(
    pedido_data: PedidoCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Crea un nuevo pedido con sus detalles.
    Puede ser anónimo (sin id_cliente) o asociado a un cliente.
    """
    # Validar sucursal
    sucursal = db.query(Sucursal).get(pedido_data.id_sucursal)
    if not sucursal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sucursal no encontrada"
        )

    # Validar personal
    personal = db.query(Personal).get(pedido_data.id_personal)
    if not personal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Personal no encontrado"
        )

    # Validar cliente solo si se proporciona
    cliente = None
    if pedido_data.id_cliente is not None:  # Cambio importante aquí
        cliente = db.query(Cliente).get(pedido_data.id_cliente)
        if not cliente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cliente no encontrado"
            )

    # Crear el pedido
    pedido = Pedido(
        id_personal=pedido_data.id_personal,
        id_sucursal=pedido_data.id_sucursal,
        id_cliente=pedido_data.id_cliente,
        estado="Pendiente",
        metodo_pago=pedido_data.metodo_pago,
        total=Decimal('0')
    )
    db.add(pedido)
    db.flush()

    # Procesar detalles
    for detalle_data in pedido_data.detalles:
        if detalle_data.tipo_producto == "Establecido":
            producto = db.query(ProductoEstablecido).get(
                detalle_data.id_producto_establecido)
            if not producto:
                raise HTTPException(
                    status_code=404, detail="Producto no encontrado")

            detalle = DetallePedido(
                id_pedido=pedido.id_pedido,
                tipo_producto="Establecido",
                id_producto_establecido=detalle_data.id_producto_establecido,
                cantidad=detalle_data.cantidad,
                precio_unitario=producto.precio_unitario
            )
            db.add(detalle)

    # Actualizar el total usando text() para el SQL directo
    db.execute(
        text(
            "UPDATE pedido SET total = ("
            "SELECT COALESCE(SUM(subtotal), 0) FROM detalle_pedido "
            "WHERE id_pedido = :pedido_id"
            ") WHERE id_pedido = :pedido_id"
        ).bindparams(pedido_id=pedido.id_pedido)
    )

    # Alternativa más segura con parámetros nombrados:
    # db.execute(
    #     text("UPDATE pedido SET total = (SELECT COALESCE(SUM(subtotal), 0) FROM detalle_pedido WHERE id_pedido = :pid) WHERE id_pedido = :pid"),
    #     {"pid": pedido.id_pedido}
    # )

    db.refresh(pedido)
    db.commit()

    return obtener_pedido_completo(pedido.id_pedido, db)


@router.patch("/{pedido_id}", response_model=PedidoResponse)
def actualizar_pedido(
    pedido_id: int,
    pedido_update: PedidoUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Actualiza el estado o método de pago de un pedido.
    Si el estado cambia a 'Pagado', se descuenta del inventario.
    """
    pedido = db.query(Pedido).get(pedido_id)
    if not pedido:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pedido no encontrado"
        )

    # Actualizar estado si se proporciona
    if pedido_update.estado:
        if pedido_update.estado == EstadoPedido.PAGADO and pedido.estado != EstadoPedido.PAGADO.value:
            # Descontar del inventario solo cuando cambia a Pagado
            descontar_inventario(pedido, db)

        pedido.estado = pedido_update.estado.value

    # Actualizar método de pago si se proporciona
    if pedido_update.metodo_pago:
        pedido.metodo_pago = pedido_update.metodo_pago.value

    db.commit()
    return obtener_pedido_completo(pedido_id, db)


def descontar_inventario(pedido: Pedido, db: Session):
    """
    Descuenta del inventario los productos y materias primas utilizadas en el pedido.
    """
    for detalle in pedido.detalles:
        if detalle.tipo_producto == 'Establecido':
            # Descontar producto establecido
            inventario = db.query(InventarioProductoEstablecido).filter_by(
                id_sucursal=pedido.id_sucursal,
                id_producto_establecido=detalle.id_producto_establecido
            ).first()

            if not inventario or inventario.cantidad_disponible < detalle.cantidad:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Stock insuficiente para el producto {detalle.id_producto_establecido}"
                )

            inventario.cantidad_disponible -= detalle.cantidad

        elif detalle.tipo_producto == 'Personalizado':
            # Descontar materias primas del producto personalizado
            producto_personalizado = detalle.producto_personalizado
            for detalle_mp in producto_personalizado.detalles:
                inventario = db.query(InventarioMateriaPrima).filter_by(
                    id_sucursal=pedido.id_sucursal,
                    id_materia_prima=detalle_mp.id_materia_prima
                ).first()

                if not inventario or inventario.cantidad_stock < detalle_mp.cantidad:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Stock insuficiente para la materia prima {detalle_mp.id_materia_prima}"
                    )

                inventario.cantidad_stock -= detalle_mp.cantidad


@router.get("/{pedido_id}", response_model=PedidoResponse)
def obtener_pedido(
    pedido_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Obtiene un pedido completo con todos sus detalles.
    """
    return obtener_pedido_completo(pedido_id, db)


def obtener_pedido_completo(pedido_id: int, db: Session) -> PedidoResponse:
    pedido = db.query(Pedido).get(pedido_id)
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
     # Forzar el cálculo del total si es cero (como respaldo)
    if pedido.total == 0 and pedido.detalles:
        nuevo_total = sum(
            Decimal(detalle.subtotal) if detalle.subtotal else Decimal(0)
            for detalle in pedido.detalles
        )
        if nuevo_total > 0:
            pedido.total = nuevo_total
            db.commit()
            db.refresh(pedido)

    detalles_response = []
    for detalle in pedido.detalles:
        if detalle.tipo_producto == 'Establecido':
            producto = db.query(ProductoEstablecido).get(
                detalle.id_producto_establecido)
            detalle_data = {
                "id_detalle_pedido": detalle.id_detalle_pedido,
                "tipo_producto": "Establecido",
                "id_producto_establecido": detalle.id_producto_establecido,
                "nombre_producto": producto.nombre if producto else "Desconocido",
                "cantidad": detalle.cantidad,
                "precio_unitario": detalle.precio_unitario,
                "subtotal": detalle.subtotal
            }
            detalles_response.append(
                DetallePedidoEstablecidoResponse(**detalle_data))

        elif detalle.tipo_producto == 'Personalizado':
            producto_personalizado = detalle.producto_personalizado
            detalles_mp = []
            for detalle_mp in producto_personalizado.detalles:
                materia_prima = db.query(MateriaPrima).get(
                    detalle_mp.id_materia_prima)
                detalles_mp.append({
                    "id_materia_prima": detalle_mp.id_materia_prima,
                    "nombre_materia": materia_prima.nombre if materia_prima else "Desconocido",
                    "cantidad": detalle_mp.cantidad,
                    "precio_unitario": detalle_mp.precio_unitario,
                    "subtotal": detalle_mp.subtotal,
                    "unidad": materia_prima.unidad if materia_prima else "unidad"
                })

            detalle_data = {
                "id_detalle_pedido": detalle.id_detalle_pedido,
                "tipo_producto": "Personalizado",
                "id_producto_personalizado": detalle.id_producto_personalizado,
                "producto_personalizado": {
                    "id_producto_personalizado": producto_personalizado.id_producto_personalizado,
                    "nombre_personalizado": producto_personalizado.nombre_personalizado,
                    "detalles": detalles_mp
                },
                "cantidad": detalle.cantidad,
                "precio_unitario": detalle.precio_unitario,
                "subtotal": detalle.subtotal
            }
            detalles_response.append(
                DetallePedidoPersonalizadoResponse(**detalle_data))

    # Obtener nombres relacionados
    personal = db.query(Personal).get(pedido.id_personal)
    sucursal = db.query(Sucursal).get(pedido.id_sucursal)
    cliente = db.query(Cliente).get(
        pedido.id_cliente) if pedido.id_cliente else None

    return PedidoResponse(
        id_pedido=pedido.id_pedido,
        fecha_pedido=pedido.fecha_pedido,
        id_personal=pedido.id_personal,
        nombre_personal=personal.nombre if personal else "Desconocido",
        id_sucursal=pedido.id_sucursal,
        nombre_sucursal=sucursal.nombre if sucursal else "Desconocido",
        id_cliente=pedido.id_cliente,
        nombre_cliente=cliente.apellido if cliente else None,
        estado=pedido.estado,
        metodo_pago=pedido.metodo_pago,
        total=pedido.total,
        detalles=detalles_response
    )


@router.patch("/{pedido_id}/confirmar", response_model=PedidoResponse)
def confirmar_pedido(
    pedido_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Cambia el estado a 'Pagado' y descuenta del inventario"""
    pedido = db.query(Pedido).get(pedido_id)
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")

    if pedido.estado == EstadoPedido.PAGADO.value:
        raise HTTPException(status_code=400, detail="El pedido ya está pagado")

    if pedido.estado == EstadoPedido.CANCELADO.value:
        raise HTTPException(
            status_code=400, detail="Pedido cancelado no puede confirmarse")

    # Verificar y descontar inventario
    with db.begin_nested():
        for detalle in pedido.detalles:
            if detalle.tipo_producto == 'Establecido':
                # Descontar producto establecido
                inventario = db.query(InventarioProductoEstablecido).filter_by(
                    id_sucursal=pedido.id_sucursal,
                    id_producto_establecido=detalle.id_producto_establecido
                ).with_for_update().first()

                if not inventario or inventario.cantidad_disponible < detalle.cantidad:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Stock insuficiente para el producto {detalle.id_producto_establecido}"
                    )
                inventario.cantidad_disponible -= detalle.cantidad

            elif detalle.tipo_producto == 'Personalizado':
                # Descontar materias primas
                producto_personalizado = detalle.producto_personalizado
                for detalle_mp in producto_personalizado.detalles:
                    inventario = db.query(InventarioMateriaPrima).filter_by(
                        id_sucursal=pedido.id_sucursal,
                        id_materia_prima=detalle_mp.id_materia_prima
                    ).with_for_update().first()

                    if not inventario or inventario.cantidad_stock < detalle_mp.cantidad:
                        raise HTTPException(
                            status_code=400,
                            detail=f"Stock insuficiente para la materia prima {detalle_mp.id_materia_prima}"
                        )
                    inventario.cantidad_stock -= detalle_mp.cantidad

        # Cambiar estado
        pedido.estado = EstadoPedido.PAGADO.value
        db.commit()

    return obtener_pedido_completo(pedido_id, db)


@router.get("/sucursal/{sucursal_id}", response_model=List[PedidoResponse])
def listar_pedidos_sucursal(
    sucursal_id: int,
    estado: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Lista todos los pedidos de una sucursal, opcionalmente filtrados por estado.
    """
    # Verificar que la sucursal existe
    sucursal = db.query(Sucursal).get(sucursal_id)
    if not sucursal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sucursal no encontrada"
        )

    query = db.query(Pedido).filter_by(id_sucursal=sucursal_id)

    if estado:
        query = query.filter_by(estado=estado)

    pedidos = query.order_by(Pedido.fecha_pedido.desc()).all()

    return [obtener_pedido_completo(p.id_pedido, db) for p in pedidos]
