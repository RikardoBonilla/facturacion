"""
Endpoints CRUD para Factura
"""

from typing import List
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.auth import get_current_active_user
from app.models import Factura, FacturaDetalle, FacturaImpuesto, Producto, Cliente, Empresa, Usuario
from app.schemas.factura import (
    FacturaCreate, FacturaUpdate, Factura as FacturaSchema, FacturaList
)

router = APIRouter()


async def calculate_factura_totals(factura_id: int, db: AsyncSession):
    """Calcular totales de la factura"""
    
    # Obtener detalles de la factura
    stmt = select(FacturaDetalle).where(FacturaDetalle.factura_id == factura_id)
    result = await db.execute(stmt)
    detalles = result.scalars().all()
    
    subtotal = Decimal("0.00")
    total_descuentos = Decimal("0.00")
    total_iva = Decimal("0.00")
    total_inc = Decimal("0.00")
    total_ica = Decimal("0.00")
    
    for detalle in detalles:
        # Calcular subtotal de línea
        subtotal_linea = detalle.cantidad * detalle.precio_unitario
        descuento_linea = subtotal_linea * (detalle.descuento_porcentaje / 100)
        base_gravable_linea = subtotal_linea - descuento_linea
        
        # Obtener producto para calcular impuestos
        stmt_producto = select(Producto).where(Producto.id == detalle.producto_id)
        result_producto = await db.execute(stmt_producto)
        producto = result_producto.scalar_one()
        
        # Calcular impuestos de línea
        impuestos_linea = Decimal("0.00")
        if producto.incluye_iva:
            iva_linea = base_gravable_linea * (producto.porcentaje_iva / 100)
            total_iva += iva_linea
            impuestos_linea += iva_linea
        
        if producto.incluye_inc:
            inc_linea = base_gravable_linea * (producto.porcentaje_inc / 100)
            total_inc += inc_linea
            impuestos_linea += inc_linea
        
        if producto.incluye_ica:
            ica_linea = base_gravable_linea * (producto.porcentaje_ica / 100)
            total_ica += ica_linea
            impuestos_linea += ica_linea
        
        # Actualizar detalle
        detalle.subtotal_linea = subtotal_linea
        detalle.total_descuentos_linea = descuento_linea
        detalle.total_impuestos_linea = impuestos_linea
        detalle.total_linea = base_gravable_linea + impuestos_linea
        
        subtotal += base_gravable_linea
        total_descuentos += descuento_linea
    
    total_impuestos = total_iva + total_inc + total_ica
    total_factura = subtotal + total_impuestos
    
    # Actualizar factura
    stmt_update = update(Factura).where(Factura.id == factura_id).values(
        subtotal=subtotal,
        total_descuentos=total_descuentos,
        total_iva=total_iva,
        total_inc=total_inc,
        total_ica=total_ica,
        total_impuestos=total_impuestos,
        total_factura=total_factura
    )
    await db.execute(stmt_update)
    
    # Crear registros de impuestos
    await db.execute(delete(FacturaImpuesto).where(FacturaImpuesto.factura_id == factura_id))
    
    if total_iva > 0:
        impuesto_iva = FacturaImpuesto(
            factura_id=factura_id,
            tipo_impuesto="IVA",
            porcentaje=Decimal("19.00"),  # Podría ser dinámico
            base_gravable=subtotal,
            valor_impuesto=total_iva
        )
        db.add(impuesto_iva)
    
    if total_inc > 0:
        impuesto_inc = FacturaImpuesto(
            factura_id=factura_id,
            tipo_impuesto="INC",
            porcentaje=Decimal("8.00"),  # Podría ser dinámico
            base_gravable=subtotal,
            valor_impuesto=total_inc
        )
        db.add(impuesto_inc)
    
    if total_ica > 0:
        impuesto_ica = FacturaImpuesto(
            factura_id=factura_id,
            tipo_impuesto="ICA",
            porcentaje=Decimal("1.00"),  # Podría ser dinámico
            base_gravable=subtotal,
            valor_impuesto=total_ica
        )
        db.add(impuesto_ica)


@router.post("/", response_model=FacturaSchema, status_code=status.HTTP_201_CREATED)
async def create_factura(
    factura_data: FacturaCreate,
    current_user: Usuario = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Crear nueva factura"""
    
    empresa_id = current_user.empresa_id
    
    # Verificar que el cliente existe
    stmt_cliente = select(Cliente).where(
        Cliente.id == factura_data.cliente_id,
        Cliente.empresa_id == empresa_id,
        Cliente.activo == True
    )
    result_cliente = await db.execute(stmt_cliente)
    cliente = result_cliente.scalar_one_or_none()
    
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente no encontrado"
        )
    
    # Obtener configuración de empresa para numeración
    stmt_empresa = select(Empresa).where(Empresa.id == empresa_id)
    result_empresa = await db.execute(stmt_empresa)
    empresa = result_empresa.scalar_one()
    
    # Generar número de factura (simplificado)
    stmt_last = select(Factura).where(Factura.empresa_id == empresa_id).order_by(Factura.numero.desc()).limit(1)
    result_last = await db.execute(stmt_last)
    last_factura = result_last.scalar_one_or_none()
    
    numero = 1 if not last_factura else last_factura.numero + 1
    numero_completo = f"{empresa.prefijo_factura or ''}{numero}"
    
    # Crear factura
    factura = Factura(
        **factura_data.model_dump(exclude={"detalles"}),
        empresa_id=empresa_id,
        numero=numero,
        numero_completo=numero_completo,
        prefijo=empresa.prefijo_factura
    )
    db.add(factura)
    await db.flush()  # Para obtener el ID
    
    # Crear detalles
    for detalle_data in factura_data.detalles:
        # Verificar que el producto existe
        stmt_producto = select(Producto).where(
            Producto.id == detalle_data.producto_id,
            Producto.empresa_id == empresa_id,
            Producto.activo == True
        )
        result_producto = await db.execute(stmt_producto)
        producto = result_producto.scalar_one_or_none()
        
        if not producto:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Producto con ID {detalle_data.producto_id} no encontrado"
            )
        
        # Crear detalle
        detalle = FacturaDetalle(
            factura_id=factura.id,
            producto_id=detalle_data.producto_id,
            codigo_producto=producto.codigo,
            nombre_producto=producto.nombre,
            descripcion=producto.descripcion,
            cantidad=detalle_data.cantidad,
            precio_unitario=detalle_data.precio_unitario,
            descuento_porcentaje=detalle_data.descuento_porcentaje,
            descuento_valor=Decimal("0.00"),  # Se calculará
            subtotal_linea=Decimal("0.00"),  # Se calculará
            total_descuentos_linea=Decimal("0.00"),  # Se calculará
            total_impuestos_linea=Decimal("0.00"),  # Se calculará
            total_linea=Decimal("0.00")  # Se calculará
        )
        db.add(detalle)
    
    await db.commit()
    
    # Calcular totales
    await calculate_factura_totals(factura.id, db)
    await db.commit()
    
    # Recargar factura con relaciones
    await db.refresh(factura)
    return factura


@router.get("/", response_model=List[FacturaList])
async def list_facturas(
    skip: int = 0,
    limit: int = 100,
    activo: bool = True,
    estado_dian: str = None,
    current_user: Usuario = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Listar facturas de mi empresa"""
    
    empresa_id = current_user.empresa_id
    
    stmt = (
        select(Factura, Cliente.razon_social, Cliente.primer_nombre, Cliente.primer_apellido)
        .join(Cliente, Factura.cliente_id == Cliente.id)
        .where(Factura.empresa_id == empresa_id, Factura.activo == activo)
    )
    
    if estado_dian:
        stmt = stmt.where(Factura.estado_dian == estado_dian)
    
    stmt = stmt.offset(skip).limit(limit).order_by(Factura.created_at.desc())
    result = await db.execute(stmt)
    rows = result.all()
    
    # Construir response
    facturas_list = []
    for row in rows:
        factura, razon_social, primer_nombre, primer_apellido = row
        cliente_nombre = razon_social or f"{primer_nombre or ''} {primer_apellido or ''}".strip()
        
        factura_dict = {
            "id": factura.id,
            "numero_completo": factura.numero_completo,
            "fecha_emision": factura.fecha_emision,
            "cliente_nombre": cliente_nombre,
            "estado_dian": factura.estado_dian,
            "total_factura": factura.total_factura,
            "activo": factura.activo
        }
        facturas_list.append(FacturaList(**factura_dict))
    
    return facturas_list


@router.get("/{factura_id}", response_model=FacturaSchema)
async def get_factura(
    factura_id: int,
    empresa_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Obtener factura por ID"""
    
    stmt = (
        select(Factura)
        .options(
            selectinload(Factura.detalles),
            selectinload(Factura.impuestos)
        )
        .where(Factura.id == factura_id, Factura.empresa_id == empresa_id)
    )
    result = await db.execute(stmt)
    factura = result.scalar_one_or_none()
    
    if not factura:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Factura no encontrada"
        )
    
    return factura


@router.put("/{factura_id}", response_model=FacturaSchema)
async def update_factura(
    factura_id: int,
    empresa_id: int,
    factura_data: FacturaUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Actualizar factura (solo facturas en borrador)"""
    
    # Verificar que existe y está en borrador
    stmt = select(Factura).where(
        Factura.id == factura_id, 
        Factura.empresa_id == empresa_id,
        Factura.estado_dian == "BORRADOR"
    )
    result = await db.execute(stmt)
    factura = result.scalar_one_or_none()
    
    if not factura:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Factura no encontrada o no se puede modificar"
        )
    
    # Actualizar solo campos proporcionados
    update_data = factura_data.model_dump(exclude_unset=True)
    if update_data:
        stmt = update(Factura).where(Factura.id == factura_id).values(**update_data)
        await db.execute(stmt)
        await db.commit()
        await db.refresh(factura)
    
    return factura


@router.delete("/{factura_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_factura(
    factura_id: int,
    empresa_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Anular factura"""
    
    stmt = select(Factura).where(
        Factura.id == factura_id, 
        Factura.empresa_id == empresa_id
    )
    result = await db.execute(stmt)
    factura = result.scalar_one_or_none()
    
    if not factura:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Factura no encontrada"
        )
    
    # Anular factura
    stmt = update(Factura).where(Factura.id == factura_id).values(
        estado_dian="ANULADA",
        activo=False
    )
    await db.execute(stmt)
    await db.commit()


@router.patch("/{factura_id}/emitir", response_model=FacturaSchema)
async def emitir_factura(
    factura_id: int,
    empresa_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Emitir factura (cambiar estado a EMITIDA)"""
    
    stmt = select(Factura).where(
        Factura.id == factura_id, 
        Factura.empresa_id == empresa_id,
        Factura.estado_dian == "BORRADOR"
    )
    result = await db.execute(stmt)
    factura = result.scalar_one_or_none()
    
    if not factura:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Factura no encontrada o no se puede emitir"
        )
    
    # Aquí iría la lógica de generación CUFE, XML, QR, etc.
    cufe = f"CUFE-{factura_id}-{factura.numero_completo}"  # Simplificado
    
    # Actualizar estado
    stmt = update(Factura).where(Factura.id == factura_id).values(
        estado_dian="EMITIDA",
        cufe=cufe
    )
    await db.execute(stmt)
    await db.commit()
    await db.refresh(factura)
    
    return factura