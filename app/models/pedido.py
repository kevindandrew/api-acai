from datetime import datetime
from enum import Enum
from decimal import Decimal
from sqlalchemy import String, Integer, TIMESTAMP, ForeignKey, CheckConstraint, Numeric, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base


class EstadoPedido(str, Enum):
    PAGADO = 'Pagado'
    PENDIENTE = 'Pendiente'
    CANCELADO = 'Cancelado'


class MetodoPago(str, Enum):
    EFECTIVO = 'Efectivo'
    TARJETA = 'Tarjeta'
    TRANSFERENCIA = 'Transferencia'


class Pedido(Base):
    __tablename__ = 'pedido'
    __table_args__ = (
        CheckConstraint(
            "estado IN ('Pagado', 'Pendiente', 'Cancelado')",
            name="check_estado_valido"
        ),
        CheckConstraint(
            "metodo_pago IS NULL OR metodo_pago IN ('Efectivo', 'Tarjeta', 'Transferencia')",
            name="check_metodo_pago_valido"
        ),
    )

    id_pedido: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
        name="id_pedido"
    )
    fecha_pedido: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),  # pylint: disable=not-callable
        name="fecha_pedido"
    )
    id_personal: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("personal.id_personal"),
        nullable=False,
        name="id_personal"
    )
    id_sucursal: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("sucursal.id_sucursal"),
        nullable=False,
        name="id_sucursal"
    )
    id_cliente: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("cliente.id_cliente"),
        name="id_cliente",
        nullable=True
    )
    estado: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        name="estado"
    )
    metodo_pago: Mapped[str | None] = mapped_column(
        String(20),
        name="metodo_pago"
    )
    total: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        default=0,
        server_default='0',
        name="total"
    )

    # Relaciones
    personal: Mapped["Personal"] = relationship(back_populates="pedidos")
    sucursal: Mapped["Sucursal"] = relationship(back_populates="pedidos")
    cliente: Mapped["Cliente | None"] = relationship(back_populates="pedidos")
    productos_personalizados: Mapped[list["ProductoPersonalizado"]] = relationship(
        back_populates="pedido",
        cascade="all, delete-orphan"
    )
    detalles: Mapped[list["DetallePedido"]] = relationship(
        back_populates="pedido",
        cascade="all, delete-orphan"
    )

    def calcular_total(self):
        """Calcula el total del pedido sumando los subtotales de todos los detalles"""
        self.total = sum(
            Decimal(detalle.subtotal)
            for detalle in self.detalles
            if detalle.subtotal is not None
        )
        return self.total

    def actualizar_estado(self, nuevo_estado: EstadoPedido):
        """Actualiza el estado del pedido con validación"""
        if nuevo_estado in EstadoPedido:
            self.estado = nuevo_estado.value
            return True
        return False

    def __repr__(self) -> str:
        return f"<Pedido(id={self.id_pedido}, estado='{self.estado}', total={self.total}, fecha={self.fecha_pedido})>"
