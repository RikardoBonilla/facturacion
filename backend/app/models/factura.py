"""
Modelos SQLAlchemy para Factura y relacionados
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Numeric, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Factura(Base):
    """Modelo de Factura con compliance DIAN"""
    __tablename__ = "facturas"
    
    id = Column(Integer, primary_key=True, index=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=False)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    
    # Numeración DIAN
    prefijo = Column(String(10), nullable=True)
    numero = Column(Integer, nullable=False)
    numero_completo = Column(String(20), nullable=False, index=True)  # Prefijo + Número
    
    # Fechas
    fecha_emision = Column(Date, nullable=False)
    fecha_vencimiento = Column(Date, nullable=True)
    
    # Datos DIAN
    cufe = Column(String(96), nullable=True, index=True)  # Código Único de Facturación Electrónica
    qr_code = Column(Text, nullable=True)  # QR code en base64
    xml_content = Column(Text, nullable=True)  # XML para DIAN
    estado_dian = Column(String(20), default='BORRADOR', nullable=False)  # BORRADOR, EMITIDA, ACEPTADA, RECHAZADA, ANULADA
    
    # Observaciones
    observaciones = Column(Text, nullable=True)
    notas = Column(Text, nullable=True)
    
    # Totales (calculados automáticamente)
    subtotal = Column(Numeric(15, 2), nullable=False, default=0)
    total_descuentos = Column(Numeric(15, 2), nullable=False, default=0)
    total_iva = Column(Numeric(15, 2), nullable=False, default=0)
    total_inc = Column(Numeric(15, 2), nullable=False, default=0)
    total_ica = Column(Numeric(15, 2), nullable=False, default=0)
    total_impuestos = Column(Numeric(15, 2), nullable=False, default=0)
    total_factura = Column(Numeric(15, 2), nullable=False, default=0)
    
    # Control
    activo = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    empresa = relationship("Empresa", back_populates="facturas")
    cliente = relationship("Cliente", back_populates="facturas")
    detalles = relationship("FacturaDetalle", back_populates="factura", cascade="all, delete-orphan")
    impuestos = relationship("FacturaImpuesto", back_populates="factura", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Factura(id={self.id}, numero='{self.numero_completo}', total={self.total_factura})>"


class FacturaDetalle(Base):
    """Modelo de detalle de factura (líneas de productos/servicios)"""
    __tablename__ = "factura_detalle"
    
    id = Column(Integer, primary_key=True, index=True)
    factura_id = Column(Integer, ForeignKey("facturas.id"), nullable=False)
    producto_id = Column(Integer, ForeignKey("productos.id"), nullable=False)
    
    # Datos del producto al momento de la factura
    codigo_producto = Column(String(50), nullable=False)
    nombre_producto = Column(String(200), nullable=False)
    descripcion = Column(Text, nullable=True)
    
    # Cantidades y precios
    cantidad = Column(Numeric(10, 3), nullable=False)
    precio_unitario = Column(Numeric(15, 2), nullable=False)
    descuento_porcentaje = Column(Numeric(5, 2), default=0, nullable=False)
    descuento_valor = Column(Numeric(15, 2), default=0, nullable=False)
    
    # Totales de línea
    subtotal_linea = Column(Numeric(15, 2), nullable=False)
    total_descuentos_linea = Column(Numeric(15, 2), nullable=False, default=0)
    total_impuestos_linea = Column(Numeric(15, 2), nullable=False, default=0)
    total_linea = Column(Numeric(15, 2), nullable=False)
    
    # Relationships
    factura = relationship("Factura", back_populates="detalles")
    producto = relationship("Producto", back_populates="detalles_factura")
    
    def __repr__(self):
        return f"<FacturaDetalle(id={self.id}, producto='{self.nombre_producto}', cantidad={self.cantidad})>"


class FacturaImpuesto(Base):
    """Modelo de impuestos por factura"""
    __tablename__ = "factura_impuestos"
    
    id = Column(Integer, primary_key=True, index=True)
    factura_id = Column(Integer, ForeignKey("facturas.id"), nullable=False)
    
    # Tipo de impuesto
    tipo_impuesto = Column(String(10), nullable=False)  # IVA, INC, ICA
    porcentaje = Column(Numeric(5, 2), nullable=False)
    
    # Base gravable y valor del impuesto
    base_gravable = Column(Numeric(15, 2), nullable=False)
    valor_impuesto = Column(Numeric(15, 2), nullable=False)
    
    # Relationships
    factura = relationship("Factura", back_populates="impuestos")
    
    def __repr__(self):
        return f"<FacturaImpuesto(tipo='{self.tipo_impuesto}', porcentaje={self.porcentaje}, valor={self.valor_impuesto})>"