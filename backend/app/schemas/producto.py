"""
Schemas Pydantic para Producto
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field


class ProductoBase(BaseModel):
    """Schema base para Producto"""
    codigo: str = Field(..., min_length=1, max_length=50, description="Código interno del producto")
    nombre: str = Field(..., min_length=2, max_length=200, description="Nombre del producto")
    descripcion: Optional[str] = Field(None, description="Descripción del producto")
    codigo_unspsc: Optional[str] = Field(None, max_length=20, description="Código UNSPSC")
    tipo: str = Field(..., pattern="^(PRODUCTO|SERVICIO)$", description="Tipo de producto/servicio")
    
    # Precios
    precio_unitario: Decimal = Field(..., ge=0, description="Precio unitario")
    precio_compra: Optional[Decimal] = Field(None, ge=0, description="Precio de compra")
    
    # Unidades
    unidad_medida: str = Field(..., max_length=20, description="Unidad de medida")
    
    # Impuestos
    incluye_iva: bool = Field(default=True, description="¿Incluye IVA?")
    porcentaje_iva: Decimal = Field(default=Decimal("19.00"), ge=0, le=100, description="Porcentaje de IVA")
    incluye_inc: bool = Field(default=False, description="¿Incluye INC?")
    porcentaje_inc: Decimal = Field(default=Decimal("0.00"), ge=0, le=100, description="Porcentaje de INC")
    incluye_ica: bool = Field(default=False, description="¿Incluye ICA?")
    porcentaje_ica: Decimal = Field(default=Decimal("0.00"), ge=0, le=100, description="Porcentaje de ICA")
    
    # Inventario
    maneja_inventario: bool = Field(default=False, description="¿Maneja inventario?")
    stock_actual: Optional[int] = Field(None, ge=0, description="Stock actual")
    stock_minimo: Optional[int] = Field(None, ge=0, description="Stock mínimo")


class ProductoCreate(ProductoBase):
    """Schema para crear producto"""
    pass


class ProductoUpdate(BaseModel):
    """Schema para actualizar producto"""
    codigo: Optional[str] = Field(None, min_length=1, max_length=50)
    nombre: Optional[str] = Field(None, min_length=2, max_length=200)
    descripcion: Optional[str] = None
    codigo_unspsc: Optional[str] = Field(None, max_length=20)
    tipo: Optional[str] = Field(None, pattern="^(PRODUCTO|SERVICIO)$")
    precio_unitario: Optional[Decimal] = Field(None, ge=0)
    precio_compra: Optional[Decimal] = Field(None, ge=0)
    unidad_medida: Optional[str] = Field(None, max_length=20)
    incluye_iva: Optional[bool] = None
    porcentaje_iva: Optional[Decimal] = Field(None, ge=0, le=100)
    incluye_inc: Optional[bool] = None
    porcentaje_inc: Optional[Decimal] = Field(None, ge=0, le=100)
    incluye_ica: Optional[bool] = None
    porcentaje_ica: Optional[Decimal] = Field(None, ge=0, le=100)
    maneja_inventario: Optional[bool] = None
    stock_actual: Optional[int] = Field(None, ge=0)
    stock_minimo: Optional[int] = Field(None, ge=0)


class Producto(ProductoBase):
    """Schema de respuesta para Producto"""
    id: int
    empresa_id: int
    activo: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProductoList(BaseModel):
    """Schema para lista de productos"""
    id: int
    codigo: str
    nombre: str
    tipo: str
    precio_unitario: Decimal
    unidad_medida: str
    stock_actual: Optional[int]
    activo: bool

    class Config:
        from_attributes = True