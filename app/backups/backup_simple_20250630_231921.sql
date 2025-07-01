
-- Tabla: sucursal
CREATE TABLE sucursal (
  id_sucursal integer NOT NULL,
  nombre character varying(50) NOT NULL,
  direccion character varying(100) NOT NULL,
  telefono character varying(15),
  horario_apertura time without time zone,
  horario_cierre time without time zone,
  PRIMARY KEY (id_sucursal)
);

-- Datos para sucursal
INSERT INTO sucursal VALUES (1, 'Helados Paradise Centro', 'Av. Principal 123', '555-1001', '09:00:00', '21:00:00');
INSERT INTO sucursal VALUES (2, 'Sucursal Central', 'Av. Siempre Viva 742', '78945612', '08:00:00', '20:00:00');
INSERT INTO sucursal VALUES (3, 'Sucursal Norte', 'Calle Falsa 123', '78912345', '09:00:00', '21:00:00');

-- Tabla: personal
CREATE TABLE personal (
  id_personal integer NOT NULL,
  nombre character varying(50) NOT NULL,
  id_rol integer NOT NULL,
  id_sucursal integer,
  usuario character varying(30) NOT NULL,
  contraseña_hash character varying(512) NOT NULL,
  fecha_ultimo_login timestamp without time zone,
  PRIMARY KEY (id_personal)
);

-- Datos para personal
INSERT INTO personal VALUES (1, 'Admin Principal', 1, 1, 'admin', 'scrypt$ln=16,r=8,p=1$b2xkX3NhbHQ$...', NULL);
INSERT INTO personal VALUES (2, 'Gerente Ejemplo', 2, 1, 'gerente', 'scrypt$ln=16,r=8,p=1$b2xkX3NhbHQ$...', NULL);
INSERT INTO personal VALUES (3, 'Vendedor Demo', 3, 1, 'vendedor', 'scrypt$ln=16,r=8,p=1$b2xkX3NhbHQ$...', NULL);
INSERT INTO personal VALUES (5, 'Juan Pérez', 1, NULL, 'juan.admin', 'hash123', NULL);
INSERT INTO personal VALUES (6, 'Ana López', 2, 1, 'ana.cajera', 'hash456', NULL);
INSERT INTO personal VALUES (7, 'Carlos Gómez', 3, 2, 'carlos.heladero', 'hash789', NULL);
INSERT INTO personal VALUES (9, 'pepito sanchez', 3, 2, 'pepe123', '$2b$12$2wZlDW6DiGWFw2IsG8PIW..ORTencL0HTSXKtzDhjAQ0nkZoyb1R2', NULL);
INSERT INTO personal VALUES (8, 'Belen Segales', 1, NULL, 'belucita', '$2b$12$xyX2phe5dMNvId5GDN3vLOGZJQ41RtB1wIQm3FyEzVb0Ie4l9Z8mK', '2025-07-01T03:17:46.371257');

-- Tabla: roles
CREATE TABLE roles (
  id_rol integer NOT NULL,
  nombre character varying(20) NOT NULL,
  descripcion text,
  PRIMARY KEY (id_rol)
);

-- Datos para roles
INSERT INTO roles VALUES (1, 'Administrador', 'Acceso total al sistema');
INSERT INTO roles VALUES (2, 'Gerente Sucursal', 'Gestiona una sucursal');
INSERT INTO roles VALUES (3, 'Vendedor', 'Atención al cliente y ventas');

-- Tabla: inventario_productoestablecido
CREATE TABLE inventario_productoestablecido (
  id_sucursal integer NOT NULL,
  id_producto_establecido integer NOT NULL,
  cantidad_disponible integer NOT NULL,
  PRIMARY KEY (id_sucursal, id_producto_establecido)
);

-- Datos para inventario_productoestablecido
INSERT INTO inventario_productoestablecido VALUES (1, 2, 45);
INSERT INTO inventario_productoestablecido VALUES (1, 3, 100);
INSERT INTO inventario_productoestablecido VALUES (1, 1, 44);

-- Tabla: producto_establecido
CREATE TABLE producto_establecido (
  id_producto_establecido integer NOT NULL,
  nombre character varying(50) NOT NULL,
  descripcion text,
  precio_unitario numeric NOT NULL,
  es_helado boolean,
  PRIMARY KEY (id_producto_establecido)
);

-- Datos para producto_establecido
INSERT INTO producto_establecido VALUES (1, 'Clásico Vainilla', 'Helado de vainilla premium', '25.00', True);
INSERT INTO producto_establecido VALUES (2, 'Chocolate Intenso', 'Helado de chocolate belga', '28.00', True);
INSERT INTO producto_establecido VALUES (3, 'Topping Chispas', 'Chispas de chocolate', '5.00', False);
INSERT INTO producto_establecido VALUES (4, 'Cono de Vainilla', 'Helado tradicional de vainilla en cono', '10.00', True);
INSERT INTO producto_establecido VALUES (5, 'Brownie', 'Postre de chocolate', '12.00', False);

-- Tabla: inventario_materiaprima
CREATE TABLE inventario_materiaprima (
  id_sucursal integer NOT NULL,
  id_materia_prima integer NOT NULL,
  cantidad_stock numeric NOT NULL,
  PRIMARY KEY (id_sucursal, id_materia_prima)
);

-- Datos para inventario_materiaprima
INSERT INTO inventario_materiaprima VALUES (1, 1, '10.00');
INSERT INTO inventario_materiaprima VALUES (1, 2, '8.50');
INSERT INTO inventario_materiaprima VALUES (1, 3, '5.00');
INSERT INTO inventario_materiaprima VALUES (1, 4, '4.00');

-- Tabla: materia_prima
CREATE TABLE materia_prima (
  id_materia_prima integer NOT NULL,
  nombre character varying(50) NOT NULL,
  precio_unitario numeric NOT NULL,
  unidad character varying(10) NOT NULL,
  stock_minimo numeric,
  fecha_caducidad date,
  PRIMARY KEY (id_materia_prima)
);

-- Datos para materia_prima
INSERT INTO materia_prima VALUES (1, 'Vainilla', '15.50', 'litro', '5.00', NULL);
INSERT INTO materia_prima VALUES (2, 'Chocolate', '18.75', 'litro', '5.00', NULL);
INSERT INTO materia_prima VALUES (3, 'Chispas', '25.00', 'kg', '2.00', NULL);
INSERT INTO materia_prima VALUES (4, 'Caramelo', '30.00', 'litro', '3.00', NULL);
INSERT INTO materia_prima VALUES (5, 'Leche', '2.50', 'litro', '10.00', '2025-12-31');
INSERT INTO materia_prima VALUES (6, 'Chocolate', '3.00', 'kg', '5.00', '2025-10-15');
INSERT INTO materia_prima VALUES (7, 'Frutilla', '4.00', 'kg', '3.00', '2025-09-30');

-- Tabla: pedido
CREATE TABLE pedido (
  id_pedido integer NOT NULL,
  fecha_pedido timestamp without time zone,
  id_personal integer NOT NULL,
  id_sucursal integer NOT NULL,
  id_cliente integer,
  estado character varying(20) NOT NULL,
  metodo_pago character varying(20),
  total numeric NOT NULL,
  PRIMARY KEY (id_pedido)
);

-- Datos para pedido
INSERT INTO pedido VALUES (9, '2025-05-18T18:22:31.483874', 8, 1, NULL, 'Pendiente', 'Efectivo', '50.00');
INSERT INTO pedido VALUES (2, '2025-05-18T17:35:55.412019', 1, 1, NULL, 'Pendiente', NULL, '24.00');
INSERT INTO pedido VALUES (3, '2025-05-18T17:36:03.147835', 1, 1, NULL, 'Pagado', NULL, '50.00');
INSERT INTO pedido VALUES (4, '2025-05-18T17:36:05.251198', 1, 1, NULL, 'Pagado', NULL, '50.00');
INSERT INTO pedido VALUES (5, '2025-05-18T17:53:10.040301', 8, 1, NULL, 'Pagado', 'Efectivo', '50.00');
INSERT INTO pedido VALUES (6, '2025-05-18T18:05:50.845589', 8, 1, NULL, 'Pendiente', 'Efectivo', '75.00');
INSERT INTO pedido VALUES (7, '2025-05-18T18:07:25.411387', 8, 1, NULL, 'Pendiente', 'Efectivo', '56.00');
INSERT INTO pedido VALUES (10, '2025-06-12T09:30:10.793420', 3, 1, NULL, 'Pendiente', 'Efectivo', '0.00');
INSERT INTO pedido VALUES (11, '2025-06-12T10:01:59.447095', 3, 1, NULL, 'Pendiente', 'Efectivo', '48.76');
INSERT INTO pedido VALUES (12, '2025-06-12T10:02:05.559327', 3, 1, NULL, 'Pendiente', 'Efectivo', '48.76');
INSERT INTO pedido VALUES (16, '2025-06-13T00:58:21.035627', 1, 1, 1, 'Pendiente', 'Efectivo', '10.00');
INSERT INTO pedido VALUES (24, '2025-06-13T01:15:02.126514', 1, 1, NULL, 'Pendiente', 'Efectivo', '25.00');
INSERT INTO pedido VALUES (25, '2025-06-13T01:15:43.158091', 1, 1, 1, 'Pendiente', 'Efectivo', '78.00');
INSERT INTO pedido VALUES (26, '2025-06-13T01:20:26.211611', 1, 1, 1, 'Pendiente', 'Efectivo', '82.03');

-- Tabla: cliente
CREATE TABLE cliente (
  id_cliente integer NOT NULL,
  ci_nit character varying(20) NOT NULL,
  apellido character varying(50) NOT NULL,
  fecha_registro timestamp without time zone,
  PRIMARY KEY (id_cliente)
);

-- Datos para cliente
INSERT INTO cliente VALUES (1, '12345678', 'Gutiérrez', '2025-05-17T15:47:49.588211');
INSERT INTO cliente VALUES (2, '87654321', 'Mamani', '2025-05-17T15:47:49.588211');

-- Tabla: producto_personalizado
CREATE TABLE producto_personalizado (
  id_producto_personalizado integer NOT NULL,
  id_pedido integer NOT NULL,
  nombre_personalizado character varying(50),
  fecha_creacion timestamp without time zone,
  PRIMARY KEY (id_producto_personalizado)
);

-- Datos para producto_personalizado
INSERT INTO producto_personalizado VALUES (1, 11, 'kevingol', '2025-06-12T10:01:59.447095');
INSERT INTO producto_personalizado VALUES (2, 12, 'kevingol', '2025-06-12T10:02:05.559327');
INSERT INTO producto_personalizado VALUES (6, 16, 'Helado de Vainilla con Frutos Rojos', '2025-06-13T00:58:21.035627');
INSERT INTO producto_personalizado VALUES (11, 25, 'Mi Helado', '2025-06-13T01:15:43.158091');
INSERT INTO producto_personalizado VALUES (12, 26, 'Mi Helado', '2025-06-13T01:20:26.211611');

-- Tabla: detalle_productopersonalizado
CREATE TABLE detalle_productopersonalizado (
  id_producto_personalizado integer NOT NULL,
  id_materia_prima integer NOT NULL,
  cantidad numeric NOT NULL,
  precio_unitario numeric NOT NULL,
  subtotal numeric,
  PRIMARY KEY (id_producto_personalizado, id_materia_prima)
);

-- Datos para detalle_productopersonalizado
INSERT INTO detalle_productopersonalizado VALUES (1, 2, '1.00', '24.38', '24.38');
INSERT INTO detalle_productopersonalizado VALUES (2, 2, '1.00', '24.38', '24.38');
INSERT INTO detalle_productopersonalizado VALUES (6, 2, '0.20', '24.38', '4.88');
INSERT INTO detalle_productopersonalizado VALUES (6, 1, '0.10', '20.15', '2.02');
INSERT INTO detalle_productopersonalizado VALUES (11, 1, '0.20', '20.15', '4.03');
INSERT INTO detalle_productopersonalizado VALUES (12, 1, '0.20', '20.15', '4.03');

-- Tabla: detalle_pedido
CREATE TABLE detalle_pedido (
  id_detalle_pedido integer NOT NULL,
  id_pedido integer NOT NULL,
  tipo_producto character varying(20) NOT NULL,
  id_producto_establecido integer,
  id_producto_personalizado integer,
  cantidad integer NOT NULL,
  precio_unitario numeric NOT NULL,
  subtotal numeric,
  PRIMARY KEY (id_detalle_pedido)
);

-- Datos para detalle_pedido
INSERT INTO detalle_pedido VALUES (1, 2, 'Establecido', 5, NULL, 2, '12.00', '24.00');
INSERT INTO detalle_pedido VALUES (2, 3, 'Establecido', 1, NULL, 2, '25.00', '50.00');
INSERT INTO detalle_pedido VALUES (3, 4, 'Establecido', 1, NULL, 2, '25.00', '50.00');
INSERT INTO detalle_pedido VALUES (4, 5, 'Establecido', 1, NULL, 2, '25.00', '50.00');
INSERT INTO detalle_pedido VALUES (5, 6, 'Establecido', 1, NULL, 3, '25.00', '75.00');
INSERT INTO detalle_pedido VALUES (6, 7, 'Establecido', 2, NULL, 2, '28.00', '56.00');
INSERT INTO detalle_pedido VALUES (7, 9, 'Establecido', 1, NULL, 2, '25.00', '50.00');
INSERT INTO detalle_pedido VALUES (8, 11, 'Personalizado', NULL, 1, 2, '24.38', '48.76');
INSERT INTO detalle_pedido VALUES (9, 12, 'Personalizado', NULL, 2, 2, '24.38', '48.76');
INSERT INTO detalle_pedido VALUES (13, 16, 'Establecido', 3, NULL, 2, '5.00', '10.00');
INSERT INTO detalle_pedido VALUES (14, 16, 'Personalizado', NULL, 6, 1, '6.89', '6.89');
INSERT INTO detalle_pedido VALUES (15, 16, 'Establecido', 2, NULL, 1, '28.00', '28.00');
INSERT INTO detalle_pedido VALUES (28, 24, 'Establecido', 1, NULL, 1, '25.00', '25.00');
INSERT INTO detalle_pedido VALUES (29, 25, 'Establecido', 1, NULL, 2, '25.00', '50.00');
INSERT INTO detalle_pedido VALUES (30, 25, 'Establecido', 2, NULL, 1, '28.00', '28.00');
INSERT INTO detalle_pedido VALUES (31, 25, 'Personalizado', NULL, 11, 1, '4.03', '4.03');
INSERT INTO detalle_pedido VALUES (32, 26, 'Establecido', 1, NULL, 2, '25.00', '50.00');
INSERT INTO detalle_pedido VALUES (33, 26, 'Establecido', 2, NULL, 1, '28.00', '28.00');
INSERT INTO detalle_pedido VALUES (34, 26, 'Personalizado', NULL, 12, 1, '4.03', '4.03');
