from decimal import Decimal
from sqlalchemy import Numeric, Integer, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base


class InventarioMateriaPrima(Base):
    __tablename__ = 'inventario_materiaprima'
    __table_args__ = (
        PrimaryKeyConstraint(
            'id_sucursal',
            'id_materia_prima',
            name='pk_sucursal_materia'
        ),
    )

    id_sucursal: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("sucursal.id_sucursal"),
        nullable=False,
        name="id_sucursal"
    )
    id_materia_prima: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("materia_prima.id_materia_prima"),
        nullable=False,
        name="id_materia_prima"
    )
    cantidad_stock: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        name="cantidad_stock"
    )

    # Relaciones (se mantienen igual)
    sucursal: Mapped["Sucursal"] = relationship(
        back_populates="inventario_materias")
    materia_prima: Mapped["MateriaPrima"] = relationship(
        back_populates="inventarios")

    def __repr__(self) -> str:
        return f"<InventarioMateriaPrima(sucursal={self.id_sucursal}, materia={self.id_materia_prima}, stock={self.cantidad_stock})>"
