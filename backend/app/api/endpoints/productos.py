"""
Endpoints CRUD para Producto
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete

from app.core.database import get_db
from app.models import Producto
from app.schemas.producto import ProductoCreate, ProductoUpdate, Producto as ProductoSchema, ProductoList

router = APIRouter()


@router.post("/", response_model=ProductoSchema, status_code=status.HTTP_201_CREATED)
async def create_producto(
    producto_data: ProductoCreate,
    empresa_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Crear nuevo producto"""
    
    # Verificar que no exista otro producto con el mismo código en la empresa
    stmt = select(Producto).where(
        Producto.empresa_id == empresa_id,
        Producto.codigo == producto_data.codigo,
        Producto.activo == True
    )
    result = await db.execute(stmt)
    existing_producto = result.scalar_one_or_none()
    
    if existing_producto:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe un producto con código {producto_data.codigo}"
        )
    
    # Crear producto
    producto = Producto(**producto_data.model_dump(), empresa_id=empresa_id)
    db.add(producto)
    await db.commit()
    await db.refresh(producto)
    
    return producto


@router.get("/", response_model=List[ProductoList])
async def list_productos(
    empresa_id: int,
    skip: int = 0,
    limit: int = 100,
    activo: bool = True,
    tipo: str = None,
    db: AsyncSession = Depends(get_db)
):
    """Listar productos de una empresa"""
    
    stmt = select(Producto).where(
        Producto.empresa_id == empresa_id, 
        Producto.activo == activo
    )
    
    if tipo:
        stmt = stmt.where(Producto.tipo == tipo)
    
    stmt = stmt.offset(skip).limit(limit)
    result = await db.execute(stmt)
    productos = result.scalars().all()
    
    return productos


@router.get("/{producto_id}", response_model=ProductoSchema)
async def get_producto(
    producto_id: int,
    empresa_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Obtener producto por ID"""
    
    stmt = select(Producto).where(
        Producto.id == producto_id, 
        Producto.empresa_id == empresa_id
    )
    result = await db.execute(stmt)
    producto = result.scalar_one_or_none()
    
    if not producto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado"
        )
    
    return producto


@router.put("/{producto_id}", response_model=ProductoSchema)
async def update_producto(
    producto_id: int,
    empresa_id: int,
    producto_data: ProductoUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Actualizar producto"""
    
    # Verificar que existe
    stmt = select(Producto).where(
        Producto.id == producto_id, 
        Producto.empresa_id == empresa_id
    )
    result = await db.execute(stmt)
    producto = result.scalar_one_or_none()
    
    if not producto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado"
        )
    
    # Si se cambia el código, verificar que no exista otro producto con ese código
    if producto_data.codigo and producto_data.codigo != producto.codigo:
        stmt_check = select(Producto).where(
            Producto.empresa_id == empresa_id,
            Producto.codigo == producto_data.codigo,
            Producto.id != producto_id,
            Producto.activo == True
        )
        result_check = await db.execute(stmt_check)
        existing_producto = result_check.scalar_one_or_none()
        
        if existing_producto:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ya existe un producto con código {producto_data.codigo}"
            )
    
    # Actualizar solo campos proporcionados
    update_data = producto_data.model_dump(exclude_unset=True)
    if update_data:
        stmt = update(Producto).where(Producto.id == producto_id).values(**update_data)
        await db.execute(stmt)
        await db.commit()
        await db.refresh(producto)
    
    return producto


@router.delete("/{producto_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_producto(
    producto_id: int,
    empresa_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Eliminar producto (soft delete)"""
    
    stmt = select(Producto).where(
        Producto.id == producto_id, 
        Producto.empresa_id == empresa_id
    )
    result = await db.execute(stmt)
    producto = result.scalar_one_or_none()
    
    if not producto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado"
        )
    
    # Soft delete
    stmt = update(Producto).where(Producto.id == producto_id).values(activo=False)
    await db.execute(stmt)
    await db.commit()


@router.get("/codigo/{codigo}", response_model=ProductoSchema)
async def get_producto_by_codigo(
    codigo: str,
    empresa_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Obtener producto por código"""
    
    stmt = select(Producto).where(
        Producto.codigo == codigo,
        Producto.empresa_id == empresa_id,
        Producto.activo == True
    )
    result = await db.execute(stmt)
    producto = result.scalar_one_or_none()
    
    if not producto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado"
        )
    
    return producto


@router.patch("/{producto_id}/stock", response_model=ProductoSchema)
async def update_stock_producto(
    producto_id: int,
    empresa_id: int,
    nuevo_stock: int,
    db: AsyncSession = Depends(get_db)
):
    """Actualizar stock de producto"""
    
    # Verificar que existe y maneja inventario
    stmt = select(Producto).where(
        Producto.id == producto_id, 
        Producto.empresa_id == empresa_id,
        Producto.maneja_inventario == True
    )
    result = await db.execute(stmt)
    producto = result.scalar_one_or_none()
    
    if not producto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado o no maneja inventario"
        )
    
    # Actualizar stock
    stmt = update(Producto).where(Producto.id == producto_id).values(stock_actual=nuevo_stock)
    await db.execute(stmt)
    await db.commit()
    await db.refresh(producto)
    
    return producto