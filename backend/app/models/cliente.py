"""
Modelo SQLAlchemy para Cliente
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Cliente(Base):
    """Modelo de Cliente con datos fiscales colombianos"""
    __tablename__ = "clientes"
    
    id = Column(Integer, primary_key=True, index=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=False)
    
    # Información básica
    tipo_persona = Column(String(20), nullable=False)  # NATURAL, JURIDICA
    tipo_documento = Column(String(20), nullable=False)  # NIT, CC, CE, PASAPORTE
    numero_documento = Column(String(20), nullable=False, index=True)
    
    # Datos personales/empresariales
    razon_social = Column(String(200), nullable=True)  # Para personas jurídicas
    nombre_comercial = Column(String(200), nullable=True)
    primer_nombre = Column(String(50), nullable=True)  # Para personas naturales
    segundo_nombre = Column(String(50), nullable=True)
    primer_apellido = Column(String(50), nullable=True)
    segundo_apellido = Column(String(50), nullable=True)
    
    # Contacto
    email = Column(String(100), nullable=True)
    telefono = Column(String(20), nullable=True)
    celular = Column(String(20), nullable=True)
    
    # Dirección
    direccion = Column(Text, nullable=False)
    ciudad = Column(String(100), nullable=False)
    departamento = Column(String(100), nullable=False)
    codigo_postal = Column(String(10), nullable=True)
    
    # Datos fiscales
    regimen_fiscal = Column(String(50), nullable=True)  # SIMPLIFICADO, COMUN
    responsabilidad_tributaria = Column(String(10), nullable=True)  # Código DIAN
    
    # Control
    activo = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    empresa = relationship("Empresa", back_populates="clientes")
    facturas = relationship("Factura", back_populates="cliente")
    
    def __repr__(self):
        nombre_completo = self.get_nombre_completo()
        return f"<Cliente(id={self.id}, documento='{self.numero_documento}', nombre='{nombre_completo}')>"
    
    def get_nombre_completo(self):
        """Retorna el nombre completo según el tipo de persona"""
        if self.tipo_persona == "JURIDICA":
            return self.razon_social or self.nombre_comercial
        else:
            nombres = []
            if self.primer_nombre:
                nombres.append(self.primer_nombre)
            if self.segundo_nombre:
                nombres.append(self.segundo_nombre)
            if self.primer_apellido:
                nombres.append(self.primer_apellido)
            if self.segundo_apellido:
                nombres.append(self.segundo_apellido)
            return " ".join(nombres)