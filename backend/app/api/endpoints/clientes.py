"""
Endpoints CRUD para Cliente
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete

from app.core.database import get_db
from app.core.auth import get_current_active_user, get_empresa_id_from_user
from app.models import Cliente, Usuario
from app.schemas.cliente import ClienteCreate, ClienteUpdate, Cliente as ClienteSchema, ClienteList

router = APIRouter()


@router.post("/", response_model=ClienteSchema, status_code=status.HTTP_201_CREATED)
async def create_cliente(
    cliente_data: ClienteCreate,
    current_user: Usuario = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Crear nuevo cliente"""
    
    empresa_id = current_user.empresa_id
    
    # Verificar que no exista otro cliente con el mismo documento en la empresa
    stmt = select(Cliente).where(
        Cliente.empresa_id == empresa_id,
        Cliente.numero_documento == cliente_data.numero_documento,
        Cliente.activo == True
    )
    result = await db.execute(stmt)
    existing_cliente = result.scalar_one_or_none()
    
    if existing_cliente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe un cliente con documento {cliente_data.numero_documento}"
        )
    
    # Crear cliente
    cliente = Cliente(**cliente_data.model_dump(), empresa_id=empresa_id)
    db.add(cliente)
    await db.commit()
    await db.refresh(cliente)
    
    return cliente


@router.get("/", response_model=List[ClienteList])
async def list_clientes(
    skip: int = 0,
    limit: int = 100,
    activo: bool = True,
    current_user: Usuario = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Listar clientes de mi empresa"""
    
    empresa_id = current_user.empresa_id
    
    stmt = (
        select(Cliente)
        .where(Cliente.empresa_id == empresa_id, Cliente.activo == activo)
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    clientes = result.scalars().all()
    
    # Agregar nombre completo para el response
    response_clientes = []
    for cliente in clientes:
        cliente_dict = {
            "id": cliente.id,
            "tipo_documento": cliente.tipo_documento,
            "numero_documento": cliente.numero_documento,
            "nombre_completo": cliente.get_nombre_completo(),
            "email": cliente.email,
            "telefono": cliente.telefono,
            "ciudad": cliente.ciudad,
            "activo": cliente.activo
        }
        response_clientes.append(ClienteList(**cliente_dict))
    
    return response_clientes


@router.get("/{cliente_id}", response_model=ClienteSchema)
async def get_cliente(
    cliente_id: int,
    current_user: Usuario = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Obtener cliente por ID"""
    
    stmt = select(Cliente).where(
        Cliente.id == cliente_id, 
        Cliente.empresa_id == current_user.empresa_id
    )
    result = await db.execute(stmt)
    cliente = result.scalar_one_or_none()
    
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente no encontrado"
        )
    
    return cliente


@router.put("/{cliente_id}", response_model=ClienteSchema)
async def update_cliente(
    cliente_id: int,
    cliente_data: ClienteUpdate,
    current_user: Usuario = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Actualizar cliente"""
    
    # Verificar que existe
    stmt = select(Cliente).where(
        Cliente.id == cliente_id, 
        Cliente.empresa_id == current_user.empresa_id
    )
    result = await db.execute(stmt)
    cliente = result.scalar_one_or_none()
    
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente no encontrado"
        )
    
    # Si se cambia el documento, verificar que no exista otro cliente con ese documento
    if cliente_data.numero_documento and cliente_data.numero_documento != cliente.numero_documento:
        stmt_check = select(Cliente).where(
            Cliente.empresa_id == current_user.empresa_id,
            Cliente.numero_documento == cliente_data.numero_documento,
            Cliente.id != cliente_id,
            Cliente.activo == True
        )
        result_check = await db.execute(stmt_check)
        existing_cliente = result_check.scalar_one_or_none()
        
        if existing_cliente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ya existe un cliente con documento {cliente_data.numero_documento}"
            )
    
    # Actualizar solo campos proporcionados
    update_data = cliente_data.model_dump(exclude_unset=True)
    if update_data:
        stmt = update(Cliente).where(Cliente.id == cliente_id).values(**update_data)
        await db.execute(stmt)
        await db.commit()
        await db.refresh(cliente)
    
    return cliente


@router.delete("/{cliente_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_cliente(
    cliente_id: int,
    current_user: Usuario = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Eliminar cliente (soft delete)"""
    
    stmt = select(Cliente).where(
        Cliente.id == cliente_id, 
        Cliente.empresa_id == current_user.empresa_id
    )
    result = await db.execute(stmt)
    cliente = result.scalar_one_or_none()
    
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente no encontrado"
        )
    
    # Soft delete
    stmt = update(Cliente).where(Cliente.id == cliente_id).values(activo=False)
    await db.execute(stmt)
    await db.commit()


@router.get("/documento/{numero_documento}", response_model=ClienteSchema)
async def get_cliente_by_documento(
    numero_documento: str,
    current_user: Usuario = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Obtener cliente por número de documento"""
    
    stmt = select(Cliente).where(
        Cliente.numero_documento == numero_documento,
        Cliente.empresa_id == current_user.empresa_id,
        Cliente.activo == True
    )
    result = await db.execute(stmt)
    cliente = result.scalar_one_or_none()
    
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente no encontrado"
        )
    
    return cliente