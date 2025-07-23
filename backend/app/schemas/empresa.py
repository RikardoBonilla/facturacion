"""
Schemas Pydantic para Empresa
"""

from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel, Field, EmailStr


class EmpresaBase(BaseModel):
    """Schema base para Empresa"""
    nit: str = Field(..., min_length=8, max_length=20, description="NIT de la empresa")
    razon_social: str = Field(..., min_length=2, max_length=200, description="Razón social")
    nombre_comercial: Optional[str] = Field(None, max_length=200, description="Nombre comercial")
    direccion: str = Field(..., min_length=5, description="Dirección de la empresa")
    ciudad: str = Field(..., min_length=2, max_length=100, description="Ciudad")
    departamento: str = Field(..., min_length=2, max_length=100, description="Departamento")
    telefono: Optional[str] = Field(None, max_length=20, description="Teléfono")
    email: EmailStr = Field(..., description="Email de la empresa")
    
    # Datos DIAN
    tipo_contribuyente: str = Field(..., regex="^(PERSONA_NATURAL|PERSONA_JURIDICA)$", description="Tipo de contribuyente")
    regimen_fiscal: str = Field(..., regex="^(SIMPLIFICADO|COMUN)$", description="Régimen fiscal")
    responsabilidades_fiscales: Optional[List[str]] = Field(None, description="Códigos de responsabilidades fiscales DIAN")
    
    # Configuración facturación electrónica
    ambiente_dian: str = Field(default="PRUEBAS", regex="^(PRUEBAS|PRODUCCION)$", description="Ambiente DIAN")
    prefijo_factura: Optional[str] = Field(None, max_length=10, description="Prefijo para facturas")
    resolucion_dian: Optional[str] = Field(None, max_length=50, description="Número de resolución DIAN")
    fecha_resolucion: Optional[date] = Field(None, description="Fecha de resolución DIAN")
    rango_autorizado_desde: Optional[int] = Field(None, ge=1, description="Rango autorizado desde")
    rango_autorizado_hasta: Optional[int] = Field(None, ge=1, description="Rango autorizado hasta")


class EmpresaCreate(EmpresaBase):
    """Schema para crear empresa"""
    pass


class EmpresaUpdate(BaseModel):
    """Schema para actualizar empresa"""
    razon_social: Optional[str] = Field(None, min_length=2, max_length=200)
    nombre_comercial: Optional[str] = Field(None, max_length=200)
    direccion: Optional[str] = Field(None, min_length=5)
    ciudad: Optional[str] = Field(None, min_length=2, max_length=100)
    departamento: Optional[str] = Field(None, min_length=2, max_length=100)
    telefono: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    tipo_contribuyente: Optional[str] = Field(None, regex="^(PERSONA_NATURAL|PERSONA_JURIDICA)$")
    regimen_fiscal: Optional[str] = Field(None, regex="^(SIMPLIFICADO|COMUN)$")
    responsabilidades_fiscales: Optional[List[str]] = None
    ambiente_dian: Optional[str] = Field(None, regex="^(PRUEBAS|PRODUCCION)$")
    prefijo_factura: Optional[str] = Field(None, max_length=10)
    resolucion_dian: Optional[str] = Field(None, max_length=50)
    fecha_resolucion: Optional[date] = None
    rango_autorizado_desde: Optional[int] = Field(None, ge=1)
    rango_autorizado_hasta: Optional[int] = Field(None, ge=1)


class Empresa(EmpresaBase):
    """Schema de respuesta para Empresa"""
    id: int
    activo: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class EmpresaList(BaseModel):
    """Schema para lista de empresas"""
    id: int
    nit: str
    razon_social: str
    nombre_comercial: Optional[str]
    ciudad: str
    departamento: str
    activo: bool

    class Config:
        from_attributes = True