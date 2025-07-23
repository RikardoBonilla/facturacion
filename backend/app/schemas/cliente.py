"""
Schemas Pydantic para Cliente
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, EmailStr


class ClienteBase(BaseModel):
    """Schema base para Cliente"""
    tipo_persona: str = Field(..., regex="^(NATURAL|JURIDICA)$", description="Tipo de persona")
    tipo_documento: str = Field(..., regex="^(NIT|CC|CE|PASAPORTE)$", description="Tipo de documento")
    numero_documento: str = Field(..., min_length=6, max_length=20, description="Número de documento")
    
    # Datos personales/empresariales
    razon_social: Optional[str] = Field(None, max_length=200, description="Razón social (personas jurídicas)")
    nombre_comercial: Optional[str] = Field(None, max_length=200, description="Nombre comercial")
    primer_nombre: Optional[str] = Field(None, max_length=50, description="Primer nombre (personas naturales)")
    segundo_nombre: Optional[str] = Field(None, max_length=50, description="Segundo nombre")
    primer_apellido: Optional[str] = Field(None, max_length=50, description="Primer apellido")
    segundo_apellido: Optional[str] = Field(None, max_length=50, description="Segundo apellido")
    
    # Contacto
    email: Optional[EmailStr] = Field(None, description="Email del cliente")
    telefono: Optional[str] = Field(None, max_length=20, description="Teléfono")
    celular: Optional[str] = Field(None, max_length=20, description="Celular")
    
    # Dirección
    direccion: str = Field(..., min_length=5, description="Dirección")
    ciudad: str = Field(..., min_length=2, max_length=100, description="Ciudad")
    departamento: str = Field(..., min_length=2, max_length=100, description="Departamento")
    codigo_postal: Optional[str] = Field(None, max_length=10, description="Código postal")
    
    # Datos fiscales
    regimen_fiscal: Optional[str] = Field(None, regex="^(SIMPLIFICADO|COMUN)$", description="Régimen fiscal")
    responsabilidad_tributaria: Optional[str] = Field(None, max_length=10, description="Código responsabilidad tributaria DIAN")


class ClienteCreate(ClienteBase):
    """Schema para crear cliente"""
    pass


class ClienteUpdate(BaseModel):
    """Schema para actualizar cliente"""
    tipo_persona: Optional[str] = Field(None, regex="^(NATURAL|JURIDICA)$")
    tipo_documento: Optional[str] = Field(None, regex="^(NIT|CC|CE|PASAPORTE)$")
    numero_documento: Optional[str] = Field(None, min_length=6, max_length=20)
    razon_social: Optional[str] = Field(None, max_length=200)
    nombre_comercial: Optional[str] = Field(None, max_length=200)
    primer_nombre: Optional[str] = Field(None, max_length=50)
    segundo_nombre: Optional[str] = Field(None, max_length=50)
    primer_apellido: Optional[str] = Field(None, max_length=50)
    segundo_apellido: Optional[str] = Field(None, max_length=50)
    email: Optional[EmailStr] = None
    telefono: Optional[str] = Field(None, max_length=20)
    celular: Optional[str] = Field(None, max_length=20)
    direccion: Optional[str] = Field(None, min_length=5)
    ciudad: Optional[str] = Field(None, min_length=2, max_length=100)
    departamento: Optional[str] = Field(None, min_length=2, max_length=100)
    codigo_postal: Optional[str] = Field(None, max_length=10)
    regimen_fiscal: Optional[str] = Field(None, regex="^(SIMPLIFICADO|COMUN)$")
    responsabilidad_tributaria: Optional[str] = Field(None, max_length=10)


class Cliente(ClienteBase):
    """Schema de respuesta para Cliente"""
    id: int
    empresa_id: int
    activo: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ClienteList(BaseModel):
    """Schema para lista de clientes"""
    id: int
    tipo_documento: str
    numero_documento: str
    nombre_completo: str
    email: Optional[str]
    telefono: Optional[str]
    ciudad: str
    activo: bool

    class Config:
        from_attributes = True