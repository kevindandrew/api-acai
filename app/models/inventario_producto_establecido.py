from decimal import Decimal
from sqlalchemy import Integer, Numeric, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base


class InventarioProductoEstablecido(Base):
    __tablename__ = 'inventario_productoestablecido'
    __table_args__ = {
        'comment': 'Inventario de productos terminados por sucursal'}

    # Clave primaria compuesta (se mantiene igual)
    id_sucursal: Mapped[int] = mapped_column(
        ForeignKey("sucursal.id_sucursal"),
        primary_key=True,
        name="id_sucursal"
    )
    id_producto_establecido: Mapped[int] = mapped_column(
        ForeignKey("producto_establecido.id_producto_establecido"),
        primary_key=True,
        name="id_producto_establecido"
    )

    cantidad_disponible: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        name="cantidad_disponible"
    )
    # Se eliminó precio_ajustado (ya no existe en la nueva versión)

    # Relaciones (se mantienen igual)
    sucursal: Mapped["Sucursal"] = relationship(
        back_populates="inventario_productos")
    producto: Mapped["ProductoEstablecido"] = relationship(
        back_populates="inventarios")

    def __repr__(self) -> str:
        return (f"<InventarioProducto(sucursal={self.id_sucursal}, "
                f"producto={self.id_producto_establecido}, "
                f"stock={self.cantidad_disponible})>")
