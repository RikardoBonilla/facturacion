"""
Modelo SQLAlchemy para Rol
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Table, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


# Tabla de asociación para roles y permisos
rol_permisos = Table(
    'rol_permisos',
    Base.metadata,
    Column('rol_id', Integer, ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True),
    Column('permiso_id', Integer, ForeignKey('permisos.id', ondelete='CASCADE'), primary_key=True)
)


class Rol(Base):
    """Modelo de Rol"""
    __tablename__ = "roles"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), unique=True, nullable=False)
    descripcion = Column(String, nullable=True)
    activo = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    usuarios = relationship("Usuario", back_populates="rol")
    permisos = relationship("Permiso", secondary=rol_permisos, back_populates="roles")
    
    def __repr__(self):
        return f"<Rol(id={self.id}, nombre='{self.nombre}')>"


class Permiso(Base):
    """Modelo de Permiso"""
    __tablename__ = "permisos"
    
    id = Column(Integer, primary_key=True, index=True)
    modulo = Column(String(50), nullable=False)
    accion = Column(String(50), nullable=False)
    descripcion = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    roles = relationship("Rol", secondary=rol_permisos, back_populates="permisos")
    
    def __repr__(self):
        return f"<Permiso(id={self.id}, modulo='{self.modulo}', accion='{self.accion}')>"


class Sesion(Base):
    """Modelo de Sesión"""
    __tablename__ = "sesiones"
    
    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    token = Column(String(255), unique=True, nullable=False)
    ip_address = Column(String, nullable=True)  # INET type for PostgreSQL
    user_agent = Column(String, nullable=True)
    fecha_expiracion = Column(DateTime, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    usuario = relationship("Usuario", back_populates="sesiones")
    
    def __repr__(self):
        return f"<Sesion(id={self.id}, usuario_id={self.usuario_id}, token='{self.token[:20]}...')>"