"""
Endpoints CRUD para Empresa
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete

from app.core.database import get_db
from app.models import Empresa
from app.schemas.empresa import EmpresaCreate, EmpresaUpdate, Empresa as EmpresaSchema, EmpresaList

router = APIRouter()


@router.post("/", response_model=EmpresaSchema, status_code=status.HTTP_201_CREATED)
async def create_empresa(
    empresa_data: EmpresaCreate,
    db: AsyncSession = Depends(get_db)
):
    """Crear nueva empresa"""
    
    # Verificar que el NIT no exista
    stmt = select(Empresa).where(Empresa.nit == empresa_data.nit)
    result = await db.execute(stmt)
    existing_empresa = result.scalar_one_or_none()
    
    if existing_empresa:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe una empresa con NIT {empresa_data.nit}"
        )
    
    # Crear empresa
    empresa = Empresa(**empresa_data.model_dump())
    db.add(empresa)
    await db.commit()
    await db.refresh(empresa)
    
    return empresa


@router.get("/", response_model=List[EmpresaList])
async def list_empresas(
    skip: int = 0,
    limit: int = 100,
    activo: bool = True,
    db: AsyncSession = Depends(get_db)
):
    """Listar empresas"""
    
    stmt = select(Empresa).where(Empresa.activo == activo).offset(skip).limit(limit)
    result = await db.execute(stmt)
    empresas = result.scalars().all()
    
    return empresas


@router.get("/{empresa_id}", response_model=EmpresaSchema)
async def get_empresa(
    empresa_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Obtener empresa por ID"""
    
    stmt = select(Empresa).where(Empresa.id == empresa_id)
    result = await db.execute(stmt)
    empresa = result.scalar_one_or_none()
    
    if not empresa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Empresa no encontrada"
        )
    
    return empresa


@router.put("/{empresa_id}", response_model=EmpresaSchema)
async def update_empresa(
    empresa_id: int,
    empresa_data: EmpresaUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Actualizar empresa"""
    
    # Verificar que existe
    stmt = select(Empresa).where(Empresa.id == empresa_id)
    result = await db.execute(stmt)
    empresa = result.scalar_one_or_none()
    
    if not empresa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Empresa no encontrada"
        )
    
    # Actualizar solo campos proporcionados
    update_data = empresa_data.model_dump(exclude_unset=True)
    if update_data:
        stmt = update(Empresa).where(Empresa.id == empresa_id).values(**update_data)
        await db.execute(stmt)
        await db.commit()
        await db.refresh(empresa)
    
    return empresa


@router.delete("/{empresa_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_empresa(
    empresa_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Eliminar empresa (soft delete)"""
    
    stmt = select(Empresa).where(Empresa.id == empresa_id)
    result = await db.execute(stmt)
    empresa = result.scalar_one_or_none()
    
    if not empresa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Empresa no encontrada"
        )
    
    # Soft delete
    stmt = update(Empresa).where(Empresa.id == empresa_id).values(activo=False)
    await db.execute(stmt)
    await db.commit()


@router.get("/nit/{nit}", response_model=EmpresaSchema)
async def get_empresa_by_nit(
    nit: str,
    db: AsyncSession = Depends(get_db)
):
    """Obtener empresa por NIT"""
    
    stmt = select(Empresa).where(Empresa.nit == nit, Empresa.activo == True)
    result = await db.execute(stmt)
    empresa = result.scalar_one_or_none()
    
    if not empresa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Empresa no encontrada"
        )
    
    return empresa