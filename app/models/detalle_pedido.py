from decimal import Decimal
from sqlalchemy import String, Integer, Numeric, ForeignKey, CheckConstraint, Computed
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base


class DetallePedido(Base):
    __tablename__ = 'detalle_pedido'
    __table_args__ = (
        CheckConstraint(
            "tipo_producto IN ('Establecido', 'Personalizado')",
            name="check_tipo_producto_valido"
        ),
        CheckConstraint(
            "(tipo_producto = 'Establecido' AND id_producto_establecido IS NOT NULL AND id_producto_personalizado IS NULL) OR "
            "(tipo_producto = 'Personalizado' AND id_producto_personalizado IS NOT NULL AND id_producto_establecido IS NULL)",
            name="chk_tipo_producto"
        ),
    )

    id_detalle_pedido: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
        name="id_detalle_pedido"
    )
    id_pedido: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("pedido.id_pedido"),
        nullable=False,
        name="id_pedido"
    )
    tipo_producto: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        name="tipo_producto"
    )
    id_producto_establecido: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("producto_establecido.id_producto_establecido"),
        name="id_producto_establecido"
    )
    id_producto_personalizado: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("producto_personalizado.id_producto_personalizado"),
        name="id_producto_personalizado"
    )
    cantidad: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        name="cantidad"
    )
    precio_unitario: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        name="precio_unitario"
    )
    subtotal: Mapped[Decimal] = mapped_column(  # Nuevo campo computado
        Numeric(10, 2),
        Computed("cantidad * precio_unitario"),
        nullable=False,
        name="subtotal"
    )

    # Relaciones (se mantienen igual)
    pedido: Mapped["Pedido"] = relationship(back_populates="detalles")
    producto_establecido: Mapped["ProductoEstablecido"] = relationship()
    producto_personalizado: Mapped["ProductoPersonalizado"] = relationship()

    def __repr__(self) -> str:
        return (f"<DetallePedido(id={self.id_detalle_pedido}, "
                f"tipo={self.tipo_producto}, "
                f"cantidad={self.cantidad}, "
                f"subtotal={self.subtotal})>")  # Se agregó subtotal al repr
