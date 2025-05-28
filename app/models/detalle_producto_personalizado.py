from decimal import Decimal
from sqlalchemy import Numeric, ForeignKey, Computed
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base


class DetalleProductoPersonalizado(Base):
    __tablename__ = 'detalle_productopersonalizado'
    __table_args__ = (
        {'comment': 'Componentes/ingredientes de helados personalizados'},
    )

    id_producto_personalizado: Mapped[int] = mapped_column(
        ForeignKey("producto_personalizado.id_producto_personalizado"),
        primary_key=True,
        name="id_producto_personalizado"
    )
    id_materia_prima: Mapped[int] = mapped_column(
        ForeignKey("materia_prima.id_materia_prima"),
        primary_key=True,
        name="id_materia_prima"
    )
    cantidad: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        nullable=False,
        name="cantidad"
    )
    precio_unitario: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        name="precio_unitario"
    )
    subtotal: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        Computed("cantidad * precio_unitario"),
        name="subtotal"
    )

    # Relaciones
    producto_personalizado: Mapped["ProductoPersonalizado"] = relationship(
        back_populates="detalles"
    )
    materia_prima: Mapped["MateriaPrima"] = relationship(
        back_populates="detalles_productos"
    )

    def __repr__(self) -> str:
        return (f"<DetalleProducto(producto={self.id_producto_personalizado}, "
                f"materia={self.id_materia_prima}, "
                f"cantidad={self.cantidad})>")
