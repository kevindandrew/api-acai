from datetime import datetime
from sqlalchemy import String, Integer, TIMESTAMP, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base


class ProductoPersonalizado(Base):
    __tablename__ = 'producto_personalizado'
    __table_args__ = {'comment': 'Helados personalizados con toppings'}

    id_producto_personalizado: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
        name="id_producto_personalizado"
    )
    id_pedido: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("pedido.id_pedido"),
        nullable=False,
        name="id_pedido"
    )
    nombre_personalizado: Mapped[str | None] = mapped_column(
        String(50),
        name="nombre_personalizado"
    )
    fecha_creacion: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default="CURRENT_TIMESTAMP",
        name="fecha_creacion"
    )

    # Relaciones
    pedido: Mapped["Pedido"] = relationship(
        back_populates="productos_personalizados")
    detalles: Mapped[list["DetalleProductoPersonalizado"]] = relationship(
        back_populates="producto_personalizado",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<ProductoPersonalizado(id={self.id_producto_personalizado}, nombre='{self.nombre_personalizado}')>"
