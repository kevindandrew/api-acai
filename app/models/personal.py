from datetime import datetime
from sqlalchemy import String, Integer, TIMESTAMP, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base


class Personal(Base):
    __tablename__ = 'personal'

    id_personal: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
        name="id_personal"
    )
    nombre: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        name="nombre"
    )
    id_rol: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("roles.id_rol"),
        nullable=False,
        name="id_rol"
    )
    id_sucursal: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("sucursal.id_sucursal"),
        nullable=True,
        name="id_sucursal"
    )
    usuario: Mapped[str] = mapped_column(
        String(30),
        unique=True,
        nullable=False,
        name="usuario"
    )
    contraseña_hash: Mapped[str] = mapped_column(
        String(512),
        nullable=False,
        name="contraseña_hash"
    )
    fecha_ultimo_login: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True),
        name="fecha_ultimo_login"
    )

    # Relaciones (se mantienen igual)
    rol: Mapped["Rol"] = relationship(back_populates="personal")
    sucursal: Mapped["Sucursal"] = relationship(back_populates="personal")
    pedidos: Mapped[list["Pedido"]] = relationship(back_populates="personal")
