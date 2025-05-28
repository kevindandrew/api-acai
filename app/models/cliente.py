from datetime import datetime
from sqlalchemy import String, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base


class Cliente(Base):
    __tablename__ = 'cliente'

    id_cliente: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
        name="id_cliente"
    )
    ci_nit: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        nullable=False,
        name="ci_nit"
    )
    apellido: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        name="apellido"
    )
    fecha_registro: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default="CURRENT_TIMESTAMP",
        name="fecha_registro"
    )

    # Relación con Pedidos (opcional, la agregaremos cuando hagamos Pedido)
    pedidos: Mapped[list["Pedido"]] = relationship(back_populates="cliente")
