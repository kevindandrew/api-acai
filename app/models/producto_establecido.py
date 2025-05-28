from decimal import Decimal
from sqlalchemy import Numeric, String, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base


class ProductoEstablecido(Base):
    __tablename__ = 'producto_establecido'

    id_producto_establecido: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
        name="id_producto_establecido"
    )
    nombre: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        name="nombre"
    )
    descripcion: Mapped[str | None] = mapped_column(
        Text,
        name="descripcion"
    )
    precio_unitario: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        name="precio_unitario"
    )
    es_helado: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        name="es_helado"
    )

    # Relación con Receta (la añadiremos después)
    # ingredientes: Mapped[list["Receta"]] = relationship(back_populates="producto")
    inventarios: Mapped[list["InventarioProductoEstablecido"]
                        ] = relationship(back_populates="producto")

    def __repr__(self) -> str:
        tipo = "Helado" if self.es_helado else "Topping/Adorno"
        return f"<ProductoEstablecido(id={self.id_producto_establecido}, nombre='{self.nombre}', tipo={tipo}, precio={self.precio_unitario})>"
