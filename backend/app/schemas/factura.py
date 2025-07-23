"""
Schemas Pydantic para Factura
"""

from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, Field


class FacturaDetalleBase(BaseModel):
    """Schema base para detalle de factura"""
    producto_id: int = Field(..., description="ID del producto")
    cantidad: Decimal = Field(..., gt=0, description="Cantidad")
    precio_unitario: Decimal = Field(..., ge=0, description="Precio unitario")
    descuento_porcentaje: Decimal = Field(default=Decimal("0.00"), ge=0, le=100, description="Descuento en porcentaje")


class FacturaDetalleCreate(FacturaDetalleBase):
    """Schema para crear detalle de factura"""
    pass


class FacturaDetalle(FacturaDetalleBase):
    """Schema de respuesta para detalle de factura"""
    id: int
    factura_id: int
    codigo_producto: str
    nombre_producto: str
    descripcion: Optional[str]
    descuento_valor: Decimal
    subtotal_linea: Decimal
    total_descuentos_linea: Decimal
    total_impuestos_linea: Decimal
    total_linea: Decimal

    class Config:
        from_attributes = True


class FacturaImpuestoBase(BaseModel):
    """Schema base para impuesto de factura"""
    tipo_impuesto: str = Field(..., pattern="^(IVA|INC|ICA)$", description="Tipo de impuesto")
    porcentaje: Decimal = Field(..., ge=0, le=100, description="Porcentaje del impuesto")
    base_gravable: Decimal = Field(..., ge=0, description="Base gravable")
    valor_impuesto: Decimal = Field(..., ge=0, description="Valor del impuesto")


class FacturaImpuesto(FacturaImpuestoBase):
    """Schema de respuesta para impuesto de factura"""
    id: int
    factura_id: int

    class Config:
        from_attributes = True


class FacturaBase(BaseModel):
    """Schema base para Factura"""
    cliente_id: int = Field(..., description="ID del cliente")
    fecha_emision: date = Field(..., description="Fecha de emisión")
    fecha_vencimiento: Optional[date] = Field(None, description="Fecha de vencimiento")
    observaciones: Optional[str] = Field(None, description="Observaciones")
    notas: Optional[str] = Field(None, description="Notas adicionales")


class FacturaCreate(FacturaBase):
    """Schema para crear factura"""
    detalles: List[FacturaDetalleCreate] = Field(..., min_items=1, description="Detalles de la factura")


class FacturaUpdate(BaseModel):
    """Schema para actualizar factura"""
    cliente_id: Optional[int] = None
    fecha_emision: Optional[date] = None
    fecha_vencimiento: Optional[date] = None
    observaciones: Optional[str] = None
    notas: Optional[str] = None
    estado_dian: Optional[str] = Field(None, pattern="^(BORRADOR|EMITIDA|ACEPTADA|RECHAZADA|ANULADA)$")


class Factura(FacturaBase):
    """Schema de respuesta para Factura"""
    id: int
    empresa_id: int
    prefijo: Optional[str]
    numero: int
    numero_completo: str
    cufe: Optional[str]
    qr_code: Optional[str]
    estado_dian: str
    
    # Totales
    subtotal: Decimal
    total_descuentos: Decimal
    total_iva: Decimal
    total_inc: Decimal
    total_ica: Decimal
    total_impuestos: Decimal
    total_factura: Decimal
    
    activo: bool
    created_at: datetime
    updated_at: datetime
    
    # Relaciones
    detalles: List[FacturaDetalle] = []
    impuestos: List[FacturaImpuesto] = []

    class Config:
        from_attributes = True


class FacturaList(BaseModel):
    """Schema para lista de facturas"""
    id: int
    numero_completo: str
    fecha_emision: date
    cliente_nombre: str
    estado_dian: str
    total_factura: Decimal
    activo: bool

    class Config:
        from_attributes = True