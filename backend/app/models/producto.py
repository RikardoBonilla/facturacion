"""
Modelo SQLAlchemy para Producto
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Producto(Base):
    """Modelo de Producto con códigos UNSPSC"""
    __tablename__ = "productos"
    
    id = Column(Integer, primary_key=True, index=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=False)
    
    # Información básica
    codigo = Column(String(50), nullable=False, index=True)  # Código interno de la empresa
    nombre = Column(String(200), nullable=False)
    descripcion = Column(Text, nullable=True)
    
    # Clasificación UNSPSC (United Nations Standard Products and Services Code)
    codigo_unspsc = Column(String(20), nullable=True)  # Código estándar internacional
    
    # Tipo de producto/servicio
    tipo = Column(String(20), nullable=False)  # PRODUCTO, SERVICIO
    
    # Precios
    precio_unitario = Column(Numeric(15, 2), nullable=False)
    precio_compra = Column(Numeric(15, 2), nullable=True)
    
    # Unidades de medida
    unidad_medida = Column(String(20), nullable=False)  # UNI, KG, M, L, etc.
    
    # Impuestos
    incluye_iva = Column(Boolean, default=True, nullable=False)
    porcentaje_iva = Column(Numeric(5, 2), default=19.00, nullable=False)  # 0, 5, 19
    incluye_inc = Column(Boolean, default=False, nullable=False)  # Impuesto Nacional al Consumo
    porcentaje_inc = Column(Numeric(5, 2), default=0.00, nullable=False)
    incluye_ica = Column(Boolean, default=False, nullable=False)  # Impuesto de Industria y Comercio
    porcentaje_ica = Column(Numeric(5, 2), default=0.00, nullable=False)
    
    # Inventario (opcional)
    maneja_inventario = Column(Boolean, default=False, nullable=False)
    stock_actual = Column(Integer, default=0, nullable=True)
    stock_minimo = Column(Integer, default=0, nullable=True)
    
    # Control
    activo = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    empresa = relationship("Empresa", back_populates="productos")
    detalles_factura = relationship("FacturaDetalle", back_populates="producto")
    
    def __repr__(self):
        return f"<Producto(id={self.id}, codigo='{self.codigo}', nombre='{self.nombre}')>"
    
    def get_precio_con_impuestos(self):
        """Calcula el precio unitario incluyendo todos los impuestos"""
        precio_base = float(self.precio_unitario)
        
        if self.incluye_iva:
            precio_base *= (1 + float(self.porcentaje_iva) / 100)
        
        if self.incluye_inc:
            precio_base *= (1 + float(self.porcentaje_inc) / 100)
        
        if self.incluye_ica:
            precio_base *= (1 + float(self.porcentaje_ica) / 100)
        
        return round(precio_base, 2)