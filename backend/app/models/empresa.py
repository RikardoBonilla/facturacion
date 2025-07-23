"""
Modelo SQLAlchemy para Empresa
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, ARRAY, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Empresa(Base):
    """Modelo de Empresa con configuración DIAN"""
    __tablename__ = "empresas"
    
    id = Column(Integer, primary_key=True, index=True)
    nit = Column(String(20), unique=True, index=True, nullable=False)
    razon_social = Column(String(200), nullable=False)
    nombre_comercial = Column(String(200), nullable=True)
    direccion = Column(Text, nullable=False)
    ciudad = Column(String(100), nullable=False)
    departamento = Column(String(100), nullable=False)
    telefono = Column(String(20), nullable=True)
    email = Column(String(100), nullable=False)
    
    # Datos DIAN
    tipo_contribuyente = Column(String(50), nullable=False)  # PERSONA_NATURAL, PERSONA_JURIDICA
    regimen_fiscal = Column(String(50), nullable=False)  # SIMPLIFICADO, COMUN
    responsabilidades_fiscales = Column(ARRAY(String), nullable=True)  # Array de códigos DIAN
    
    # Configuración facturación electrónica
    ambiente_dian = Column(String(20), default='PRUEBAS', nullable=False)  # PRUEBAS, PRODUCCION
    prefijo_factura = Column(String(10), nullable=True)
    resolucion_dian = Column(String(50), nullable=True)
    fecha_resolucion = Column(Date, nullable=True)
    rango_autorizado_desde = Column(Integer, nullable=True)
    rango_autorizado_hasta = Column(Integer, nullable=True)
    
    activo = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    usuarios = relationship("Usuario", back_populates="empresa")
    clientes = relationship("Cliente", back_populates="empresa")
    productos = relationship("Producto", back_populates="empresa")
    facturas = relationship("Factura", back_populates="empresa")
    
    def __repr__(self):
        return f"<Empresa(id={self.id}, nit='{self.nit}', razon_social='{self.razon_social}')>"