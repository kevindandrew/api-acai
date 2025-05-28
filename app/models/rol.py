from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base


class Rol(Base):
    __tablename__ = 'roles'  # SQLAlchemy recomienda usar nombres en plural

    id_rol: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
        name="id_rol"  # Mantenemos el naming original de la DB
    )
    nombre: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        unique=True,  # Mapeamos el UNIQUE constraint
        name="nombre"
    )
    descripcion: Mapped[str | None] = mapped_column(
        Text,
        name="descripcion"
    )

    # Relaciones (las añadiremos cuando veamos las tablas relacionadas)
    # empleados: Mapped[list["Empleado"]] = relationship(back_populates="rol")
    personal: Mapped[list["Personal"]] = relationship(back_populates="rol")
