from sqlalchemy import Time, String
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base  # Importamos la base declarativa común
from sqlalchemy.orm import relationship


class Sucursal(Base):
    __tablename__ = 'sucursal'  # SQLAlchemy por defecto usa lowercase

    id_sucursal: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
        name="id_sucursal"  # Para mantener el nombre exacto de la columna
    )
    nombre: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        name="nombre"
    )
    direccion: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        name="direccion"
    )
    telefono: Mapped[str | None] = mapped_column(
        String(15),
        name="telefono"
    )
    horario_apertura: Mapped[Time | None] = mapped_column(
        Time,
        name="horario_apertura"
    )
    horario_cierre: Mapped[Time | None] = mapped_column(
        Time,
        name="horario_cierre"
    )

    # Relaciones (las añadiremos cuando me pases las tablas relacionadas)
    # empleados: Mapped[list["Empleado"]] = relationship(back_populates="sucursal")
    personal: Mapped[list["Personal"]] = relationship(
        back_populates="sucursal")
    inventario_materias: Mapped[list["InventarioMateriaPrima"]] = relationship(
        back_populates="sucursal")
    inventario_productos: Mapped[list["InventarioProductoEstablecido"]] = relationship(
        back_populates="sucursal")

    # Añade esta relación
    # En sucursal.py
    # Usa el nombre del modelo como string
    pedidos = relationship("Pedido", back_populates="sucursal", lazy="dynamic")
