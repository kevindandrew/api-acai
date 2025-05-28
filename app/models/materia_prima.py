from datetime import date
from decimal import Decimal
from sqlalchemy import Numeric, String, Date, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base


class MateriaPrima(Base):
    __tablename__ = 'materia_prima'
    __table_args__ = (
        CheckConstraint(
            "unidad IN ('kg', 'litro', 'unidad', 'gramo')",
            name="check_unidad_valida"
        ),
    )

    id_materia_prima: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
        name="id_materia_prima"
    )
    nombre: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        name="nombre"
    )
    precio_unitario: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        name="precio_unitario"
    )
    unidad: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        name="unidad"
    )
    stock_minimo: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        default=Decimal('0'),
        name="stock_minimo"
    )
    fecha_caducidad: Mapped[date | None] = mapped_column(
        Date,
        name="fecha_caducidad"
    )

    inventarios: Mapped[list["InventarioMateriaPrima"]
                        ] = relationship(back_populates="materia_prima")
    detalles_productos: Mapped[list["DetalleProductoPersonalizado"]] = relationship(
        back_populates="materia_prima"
    )

    def __repr__(self) -> str:
        return f"<MateriaPrima(id={self.id_materia_prima}, nombre='{self.nombre}', unidad='{self.unidad}')>"
