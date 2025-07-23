-- Base de datos para sistema de facturación electrónica Colombia
-- Motor: PostgreSQL
-- Compatibilidad: DIAN - Facturación Electrónica

-- =====================================================
-- MÓDULO DE SEGURIDAD Y USUARIOS
-- =====================================================

-- Tabla de empresas (multi-tenant)
CREATE TABLE empresas (
    id SERIAL PRIMARY KEY,
    nit VARCHAR(20) UNIQUE NOT NULL,
    razon_social VARCHAR(200) NOT NULL,
    nombre_comercial VARCHAR(200),
    direccion TEXT NOT NULL,
    ciudad VARCHAR(100) NOT NULL,
    departamento VARCHAR(100) NOT NULL,
    telefono VARCHAR(20),
    email VARCHAR(100) NOT NULL,
    -- Datos DIAN
    tipo_contribuyente VARCHAR(50) NOT NULL, -- PERSONA_NATURAL, PERSONA_JURIDICA
    regimen_fiscal VARCHAR(50) NOT NULL, -- SIMPLIFICADO, COMUN
    responsabilidades_fiscales TEXT[], -- Array de códigos DIAN
    -- Configuración facturación electrónica
    ambiente_dian VARCHAR(20) DEFAULT 'PRUEBAS', -- PRUEBAS, PRODUCCION
    prefijo_factura VARCHAR(10),
    resolucion_dian VARCHAR(50),
    fecha_resolucion DATE,
    rango_autorizado_desde INTEGER,
    rango_autorizado_hasta INTEGER,
    activo BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de roles
CREATE TABLE roles (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(50) UNIQUE NOT NULL,
    descripcion TEXT,
    activo BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de permisos
CREATE TABLE permisos (
    id SERIAL PRIMARY KEY,
    modulo VARCHAR(50) NOT NULL, -- FACTURAS, CLIENTES, PRODUCTOS, REPORTES, CONFIGURACION
    accion VARCHAR(50) NOT NULL, -- VER, CREAR, EDITAR, ELIMINAR, ANULAR
    descripcion TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(modulo, accion)
);

-- Tabla de relación roles-permisos
CREATE TABLE rol_permisos (
    rol_id INTEGER REFERENCES roles(id) ON DELETE CASCADE,
    permiso_id INTEGER REFERENCES permisos(id) ON DELETE CASCADE,
    PRIMARY KEY (rol_id, permiso_id)
);

-- Tabla de usuarios
CREATE TABLE usuarios (
    id SERIAL PRIMARY KEY,
    empresa_id INTEGER REFERENCES empresas(id),
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    tipo_documento VARCHAR(20) NOT NULL,
    numero_documento VARCHAR(20) NOT NULL,
    telefono VARCHAR(20),
    rol_id INTEGER REFERENCES roles(id),
    activo BOOLEAN DEFAULT true,
    ultimo_acceso TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de sesiones
CREATE TABLE sesiones (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER REFERENCES usuarios(id) ON DELETE CASCADE,
    token VARCHAR(255) UNIQUE NOT NULL,
    ip_address INET,
    user_agent TEXT,
    fecha_expiracion TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- MÓDULO DE FACTURACIÓN
-- =====================================================

-- Tabla de clientes mejorada para Colombia
CREATE TABLE clientes (
    id SERIAL PRIMARY KEY,
    empresa_id INTEGER REFERENCES empresas(id),
    tipo_persona VARCHAR(20) NOT NULL, -- NATURAL, JURIDICA
    tipo_documento VARCHAR(20) NOT NULL, -- NIT, CC, CE, PASAPORTE
    numero_documento VARCHAR(50) NOT NULL,
    dv CHAR(1), -- Dígito de verificación para NIT
    razon_social VARCHAR(200),
    nombres VARCHAR(100),
    apellidos VARCHAR(100),
    nombre_comercial VARCHAR(200),
    direccion TEXT NOT NULL,
    ciudad VARCHAR(100) NOT NULL,
    departamento VARCHAR(100) NOT NULL,
    codigo_postal VARCHAR(10),
    telefono VARCHAR(20),
    email VARCHAR(100),
    tipo_contribuyente VARCHAR(50),
    regimen_fiscal VARCHAR(50),
    responsabilidades_fiscales TEXT[],
    activo BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(empresa_id, tipo_documento, numero_documento)
);

-- Tabla de productos/servicios con códigos DIAN
CREATE TABLE productos (
    id SERIAL PRIMARY KEY,
    empresa_id INTEGER REFERENCES empresas(id),
    codigo_interno VARCHAR(50) NOT NULL,
    nombre VARCHAR(200) NOT NULL,
    descripcion TEXT,
    codigo_clasificacion VARCHAR(20), -- Código UNSPSC para DIAN
    precio DECIMAL(12,2) NOT NULL,
    costo DECIMAL(12,2) DEFAULT 0,
    unidad_medida VARCHAR(10) DEFAULT 'UND', -- Según estándar DIAN
    tipo VARCHAR(20) DEFAULT 'PRODUCTO', -- PRODUCTO o SERVICIO
    aplica_iva BOOLEAN DEFAULT true,
    porcentaje_iva DECIMAL(5,2) DEFAULT 19.00,
    stock_actual DECIMAL(10,2) DEFAULT 0,
    stock_minimo DECIMAL(10,2) DEFAULT 0,
    activo BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(empresa_id, codigo_interno)
);

-- Tabla de impuestos según normativa colombiana
CREATE TABLE impuestos (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(10) UNIQUE NOT NULL, -- 01=IVA, 02=IC, 03=ICA, 04=INC
    nombre VARCHAR(50) NOT NULL,
    porcentaje DECIMAL(5,2) NOT NULL,
    tipo VARCHAR(20) NOT NULL, -- NACIONAL, MUNICIPAL
    activo BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de facturas con campos DIAN
CREATE TABLE facturas (
    id SERIAL PRIMARY KEY,
    empresa_id INTEGER REFERENCES empresas(id),
    tipo_documento VARCHAR(20) NOT NULL, -- FV=Factura Venta, NC=Nota Crédito, ND=Nota Débito
    prefijo VARCHAR(10),
    numero_factura INTEGER NOT NULL,
    numero_completo VARCHAR(50) UNIQUE NOT NULL, -- PREFIJO+NUMERO
    cliente_id INTEGER NOT NULL REFERENCES clientes(id),
    fecha_emision TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_vencimiento DATE NOT NULL,
    -- Montos
    subtotal DECIMAL(12,2) NOT NULL DEFAULT 0,
    descuento DECIMAL(12,2) DEFAULT 0,
    base_gravable DECIMAL(12,2) NOT NULL DEFAULT 0,
    total_iva DECIMAL(12,2) NOT NULL DEFAULT 0,
    total_inc DECIMAL(12,2) DEFAULT 0,
    total_ica DECIMAL(12,2) DEFAULT 0,
    retencion_fuente DECIMAL(12,2) DEFAULT 0,
    total DECIMAL(12,2) NOT NULL DEFAULT 0,
    -- Estados
    estado VARCHAR(20) DEFAULT 'BORRADOR', -- BORRADOR, EMITIDA, ACEPTADA, RECHAZADA, ANULADA
    estado_dian VARCHAR(20), -- PENDIENTE, ENVIADA, ACEPTADA, RECHAZADA
    -- Datos DIAN
    cufe VARCHAR(100), -- Código Único de Factura Electrónica
    qr_code TEXT,
    xml_firmado TEXT,
    fecha_envio_dian TIMESTAMP,
    fecha_respuesta_dian TIMESTAMP,
    mensaje_dian TEXT,
    -- Pago
    forma_pago VARCHAR(20) NOT NULL, -- CONTADO, CREDITO
    metodo_pago VARCHAR(50), -- EFECTIVO, TRANSFERENCIA, TARJETA, PSE
    observaciones TEXT,
    -- Auditoría
    usuario_id INTEGER REFERENCES usuarios(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de detalle de facturas
CREATE TABLE factura_detalle (
    id SERIAL PRIMARY KEY,
    factura_id INTEGER NOT NULL REFERENCES facturas(id) ON DELETE CASCADE,
    producto_id INTEGER NOT NULL REFERENCES productos(id),
    cantidad DECIMAL(10,2) NOT NULL,
    precio_unitario DECIMAL(12,2) NOT NULL,
    descuento DECIMAL(12,2) DEFAULT 0,
    subtotal DECIMAL(12,2) NOT NULL,
    base_iva DECIMAL(12,2) NOT NULL,
    porcentaje_iva DECIMAL(5,2) NOT NULL,
    valor_iva DECIMAL(12,2) NOT NULL,
    total DECIMAL(12,2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de impuestos aplicados por factura
CREATE TABLE factura_impuestos (
    id SERIAL PRIMARY KEY,
    factura_id INTEGER NOT NULL REFERENCES facturas(id) ON DELETE CASCADE,
    impuesto_id INTEGER NOT NULL REFERENCES impuestos(id),
    base_imponible DECIMAL(12,2) NOT NULL,
    porcentaje DECIMAL(5,2) NOT NULL,
    monto DECIMAL(12,2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de pagos
CREATE TABLE pagos (
    id SERIAL PRIMARY KEY,
    factura_id INTEGER NOT NULL REFERENCES facturas(id),
    fecha_pago TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    monto DECIMAL(12,2) NOT NULL,
    metodo_pago VARCHAR(50) NOT NULL,
    banco VARCHAR(100),
    numero_transaccion VARCHAR(100),
    observaciones TEXT,
    usuario_id INTEGER REFERENCES usuarios(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla para logs de comunicación con DIAN
CREATE TABLE dian_logs (
    id SERIAL PRIMARY KEY,
    empresa_id INTEGER REFERENCES empresas(id),
    factura_id INTEGER REFERENCES facturas(id),
    tipo_operacion VARCHAR(50) NOT NULL, -- ENVIO_FACTURA, CONSULTA_ESTADO, ANULACION
    request_xml TEXT,
    response_xml TEXT,
    codigo_respuesta VARCHAR(10),
    mensaje_respuesta TEXT,
    exitoso BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de auditoría
CREATE TABLE auditoria (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER REFERENCES usuarios(id),
    tabla VARCHAR(50) NOT NULL,
    registro_id INTEGER NOT NULL,
    accion VARCHAR(20) NOT NULL, -- INSERT, UPDATE, DELETE
    datos_anteriores JSONB,
    datos_nuevos JSONB,
    ip_address INET,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- ÍNDICES PARA OPTIMIZACIÓN
-- =====================================================

CREATE INDEX idx_facturas_empresa ON facturas(empresa_id);
CREATE INDEX idx_facturas_cliente ON facturas(cliente_id);
CREATE INDEX idx_facturas_estado ON facturas(estado);
CREATE INDEX idx_facturas_estado_dian ON facturas(estado_dian);
CREATE INDEX idx_facturas_fecha ON facturas(fecha_emision);
CREATE INDEX idx_facturas_cufe ON facturas(cufe);
CREATE INDEX idx_clientes_documento ON clientes(tipo_documento, numero_documento);
CREATE INDEX idx_productos_codigo ON productos(empresa_id, codigo_interno);
CREATE INDEX idx_usuarios_email ON usuarios(email);
CREATE INDEX idx_sesiones_token ON sesiones(token);
CREATE INDEX idx_auditoria_usuario ON auditoria(usuario_id, created_at);

-- =====================================================
-- FUNCIONES Y TRIGGERS
-- =====================================================

-- Función para actualizar timestamps
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Aplicar trigger a todas las tablas con updated_at
CREATE TRIGGER update_empresas_updated_at BEFORE UPDATE ON empresas
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_usuarios_updated_at BEFORE UPDATE ON usuarios
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_clientes_updated_at BEFORE UPDATE ON clientes
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_productos_updated_at BEFORE UPDATE ON productos
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_facturas_updated_at BEFORE UPDATE ON facturas
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- Función para generar número de factura consecutivo
CREATE OR REPLACE FUNCTION generar_numero_factura(p_empresa_id INTEGER, p_tipo_documento VARCHAR)
RETURNS INTEGER AS $$
DECLARE
    v_ultimo_numero INTEGER;
BEGIN
    SELECT COALESCE(MAX(numero_factura), 0) + 1
    INTO v_ultimo_numero
    FROM facturas
    WHERE empresa_id = p_empresa_id
    AND tipo_documento = p_tipo_documento
    FOR UPDATE;
    
    RETURN v_ultimo_numero;
END;
$$ LANGUAGE plpgsql;

-- Función para auditoría automática
CREATE OR REPLACE FUNCTION fn_auditoria()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'DELETE' THEN
        INSERT INTO auditoria(usuario_id, tabla, registro_id, accion, datos_anteriores)
        VALUES (current_setting('app.current_user_id')::INTEGER, TG_TABLE_NAME, OLD.id, TG_OP, row_to_json(OLD));
        RETURN OLD;
    ELSIF TG_OP = 'UPDATE' THEN
        INSERT INTO auditoria(usuario_id, tabla, registro_id, accion, datos_anteriores, datos_nuevos)
        VALUES (current_setting('app.current_user_id')::INTEGER, TG_TABLE_NAME, NEW.id, TG_OP, row_to_json(OLD), row_to_json(NEW));
        RETURN NEW;
    ELSIF TG_OP = 'INSERT' THEN
        INSERT INTO auditoria(usuario_id, tabla, registro_id, accion, datos_nuevos)
        VALUES (current_setting('app.current_user_id')::INTEGER, TG_TABLE_NAME, NEW.id, TG_OP, row_to_json(NEW));
        RETURN NEW;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- VISTAS ÚTILES
-- =====================================================

-- Vista de facturas con información completa
CREATE VIEW v_facturas_completas AS
SELECT 
    f.id,
    f.numero_completo,
    f.tipo_documento,
    f.fecha_emision,
    f.fecha_vencimiento,
    f.estado,
    f.estado_dian,
    f.cufe,
    e.razon_social as empresa_nombre,
    e.nit as empresa_nit,
    c.numero_documento as cliente_documento,
    COALESCE(c.razon_social, c.nombres || ' ' || c.apellidos) as cliente_nombre,
    f.subtotal,
    f.total_iva,
    f.total,
    COALESCE(SUM(p.monto), 0) as total_pagado,
    f.total - COALESCE(SUM(p.monto), 0) as saldo_pendiente,
    u.nombre || ' ' || u.apellido as usuario_emisor
FROM facturas f
JOIN empresas e ON f.empresa_id = e.id
JOIN clientes c ON f.cliente_id = c.id
LEFT JOIN usuarios u ON f.usuario_id = u.id
LEFT JOIN pagos p ON f.id = p.factura_id
GROUP BY f.id, f.numero_completo, f.tipo_documento, f.fecha_emision, f.fecha_vencimiento,
         f.estado, f.estado_dian, f.cufe, e.razon_social, e.nit, c.numero_documento,
         c.razon_social, c.nombres, c.apellidos, f.subtotal, f.total_iva, f.total,
         u.nombre, u.apellido;

-- Vista de permisos por usuario
CREATE VIEW v_usuario_permisos AS
SELECT 
    u.id as usuario_id,
    u.email,
    u.nombre || ' ' || u.apellido as nombre_completo,
    r.nombre as rol,
    p.modulo,
    p.accion
FROM usuarios u
JOIN roles r ON u.rol_id = r.id
JOIN rol_permisos rp ON r.id = rp.rol_id
JOIN permisos p ON rp.permiso_id = p.id
WHERE u.activo = true AND r.activo = true;

-- =====================================================
-- DATOS INICIALES
-- =====================================================

-- Insertar roles básicos
INSERT INTO roles (nombre, descripcion) VALUES
('SUPER_ADMIN', 'Administrador del sistema con acceso total'),
('ADMIN', 'Administrador de empresa'),
('CONTADOR', 'Acceso a facturación y reportes'),
('VENDEDOR', 'Crear facturas y gestionar clientes'),
('CONSULTA', 'Solo lectura de información');

-- Insertar permisos básicos
INSERT INTO permisos (modulo, accion, descripcion) VALUES
-- Facturas
('FACTURAS', 'VER', 'Ver listado y detalle de facturas'),
('FACTURAS', 'CREAR', 'Crear nuevas facturas'),
('FACTURAS', 'EDITAR', 'Editar facturas en borrador'),
('FACTURAS', 'ANULAR', 'Anular facturas emitidas'),
('FACTURAS', 'ENVIAR_DIAN', 'Enviar facturas a la DIAN'),
-- Clientes
('CLIENTES', 'VER', 'Ver listado de clientes'),
('CLIENTES', 'CREAR', 'Crear nuevos clientes'),
('CLIENTES', 'EDITAR', 'Editar información de clientes'),
('CLIENTES', 'ELIMINAR', 'Eliminar clientes'),
-- Productos
('PRODUCTOS', 'VER', 'Ver catálogo de productos'),
('PRODUCTOS', 'CREAR', 'Crear nuevos productos'),
('PRODUCTOS', 'EDITAR', 'Editar productos existentes'),
('PRODUCTOS', 'ELIMINAR', 'Eliminar productos'),
-- Reportes
('REPORTES', 'VER', 'Ver reportes del sistema'),
('REPORTES', 'EXPORTAR', 'Exportar reportes'),
-- Configuración
('CONFIGURACION', 'VER', 'Ver configuración de la empresa'),
('CONFIGURACION', 'EDITAR', 'Editar configuración'),
('USUARIOS', 'VER', 'Ver usuarios del sistema'),
('USUARIOS', 'CREAR', 'Crear nuevos usuarios'),
('USUARIOS', 'EDITAR', 'Editar usuarios'),
('USUARIOS', 'ELIMINAR', 'Eliminar usuarios');

-- Insertar impuestos colombianos
INSERT INTO impuestos (codigo, nombre, porcentaje, tipo) VALUES
('01', 'IVA 19%', 19.00, 'NACIONAL'),
('02', 'IVA 5%', 5.00, 'NACIONAL'),
('03', 'IVA 0%', 0.00, 'NACIONAL'),
('04', 'INC 8%', 8.00, 'NACIONAL'),
('05', 'INC 4%', 4.00, 'NACIONAL'),
('06', 'ICA', 0.414, 'MUNICIPAL'); -- Tarifa ejemplo Bogotá