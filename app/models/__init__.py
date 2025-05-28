# app/models/__init__.py
from .base import Base
from .sucursal import Sucursal
from .rol import Rol
from .personal import Personal
from .materia_prima import MateriaPrima
from .producto_establecido import ProductoEstablecido
from .inventario_materia_prima import InventarioMateriaPrima
from .inventario_producto_establecido import InventarioProductoEstablecido
from .pedido import Pedido
from .producto_personalizado import ProductoPersonalizado
from .detalle_producto_personalizado import DetalleProductoPersonalizado
from .detalle_pedido import DetallePedido
from .cliente import Cliente
# ...otros modelos


__all__ = ["Base", 'Personal', 'Pedido', 'Rol',
           'Sucursal', "InventarioMateriaPrima", "InventarioProductoEstablecido", "ProductoEstablecido",
           "Materia_Prima", "ProductoPersonalizado", "DetalleProductoPersonalizado", "DetallePedido", "MateriaPrima", "Cliente"
           ]
