#!/usr/bin/env python3
"""
Script para poblar la base de datos con datos iniciales
"""

import asyncio
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models import *
from app.services.auth_service import AuthService


async def create_initial_data():
    """Create initial data for the system"""
    
    # Create async engine and session
    engine = create_async_engine(settings.DATABASE_URL)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        auth_service = AuthService(session)
        
        print("🌱 Creating initial data...")
        
        # Create roles
        admin_role = Rol(
            nombre="ADMINISTRADOR",
            descripcion="Administrador del sistema con todos los permisos"
        )
        session.add(admin_role)
        
        user_role = Rol(
            nombre="USUARIO",
            descripcion="Usuario estándar con permisos básicos"
        )
        session.add(user_role)
        
        await session.flush()  # Get IDs
        
        # Create permissions
        permissions = [
            ("FACTURAS", "VER", "Ver facturas"),
            ("FACTURAS", "CREAR", "Crear facturas"),
            ("FACTURAS", "EDITAR", "Editar facturas"),
            ("FACTURAS", "ELIMINAR", "Eliminar facturas"),
            ("FACTURAS", "ANULAR", "Anular facturas"),
            ("CLIENTES", "VER", "Ver clientes"),
            ("CLIENTES", "CREAR", "Crear clientes"),
            ("CLIENTES", "EDITAR", "Editar clientes"),
            ("CLIENTES", "ELIMINAR", "Eliminar clientes"),
            ("PRODUCTOS", "VER", "Ver productos"),
            ("PRODUCTOS", "CREAR", "Crear productos"),
            ("PRODUCTOS", "EDITAR", "Editar productos"),
            ("PRODUCTOS", "ELIMINAR", "Eliminar productos"),
            ("REPORTES", "VER", "Ver reportes"),
            ("CONFIGURACION", "VER", "Ver configuración"),
            ("CONFIGURACION", "EDITAR", "Editar configuración"),
        ]
        
        for modulo, accion, descripcion in permissions:
            permiso = Permiso(
                modulo=modulo,
                accion=accion,
                descripcion=descripcion
            )
            session.add(permiso)
        
        await session.flush()
        
        # Assign all permissions to admin role
        permisos = await session.execute(select(Permiso))
        all_permissions = permisos.scalars().all()
        
        for permiso in all_permissions:
            admin_role.permisos.append(permiso)
        
        # Assign basic permissions to user role
        basic_permissions = ["FACTURAS:VER", "CLIENTES:VER", "PRODUCTOS:VER", "REPORTES:VER"]
        for permission_key in basic_permissions:
            modulo, accion = permission_key.split(":")
            permiso = await session.execute(
                select(Permiso).where(Permiso.modulo == modulo, Permiso.accion == accion)
            )
            permission = permiso.scalar_one_or_none()
            if permission:
                user_role.permisos.append(permission)
        
        # Create test company
        test_empresa = Empresa(
            nit="900123456-1",
            razon_social="Empresa de Pruebas S.A.S.",
            nombre_comercial="Empresa Test",
            direccion="Carrera 10 # 20-30",
            ciudad="Bogotá",
            departamento="Cundinamarca",
            telefono="3001234567",
            email="admin@empresatest.com",
            tipo_contribuyente="PERSONA_JURIDICA",
            regimen_fiscal="COMUN",
            responsabilidades_fiscales=["05", "09"],
            ambiente_dian="PRUEBAS",
            prefijo_factura="FT",
            resolucion_dian="18760000001",
            rango_autorizado_desde=1,
            rango_autorizado_hasta=5000
        )
        session.add(test_empresa)
        await session.flush()
        
        # Create admin user
        admin_user = Usuario(
            empresa_id=test_empresa.id,
            email="admin@empresatest.com",
            password_hash=auth_service.get_password_hash("admin123"),
            nombre="Administrador",
            apellido="Sistema",
            tipo_documento="CC",
            numero_documento="12345678",
            telefono="3001234567",
            rol_id=admin_role.id,
            activo=True
        )
        session.add(admin_user)
        
        # Create test user
        test_user = Usuario(
            empresa_id=test_empresa.id,
            email="usuario@empresatest.com",
            password_hash=auth_service.get_password_hash("user123"),
            nombre="Usuario",
            apellido="Prueba",
            tipo_documento="CC",
            numero_documento="87654321",
            telefono="3009876543",
            rol_id=user_role.id,
            activo=True
        )
        session.add(test_user)
        
        # Create test client
        test_cliente = Cliente(
            empresa_id=test_empresa.id,
            tipo_persona="NATURAL",
            tipo_documento="CC",
            numero_documento="98765432",
            primer_nombre="Juan",
            primer_apellido="Pérez",
            email="juan.perez@email.com",
            telefono="3012345678",
            direccion="Calle 15 # 10-20",
            ciudad="Bogotá",
            departamento="Cundinamarca",
            regimen_fiscal="SIMPLIFICADO"
        )
        session.add(test_cliente)
        
        # Create test products
        test_products = [
            {
                "codigo": "PROD001",
                "nombre": "Servicio de Consultoría",
                "descripcion": "Servicio profesional de consultoría",
                "codigo_unspsc": "81161500",
                "tipo": "SERVICIO",
                "precio_unitario": 100000,
                "unidad_medida": "UNI",
                "incluye_iva": True,
                "porcentaje_iva": 19.00
            },
            {
                "codigo": "PROD002", 
                "nombre": "Producto Físico",
                "descripcion": "Producto físico de ejemplo",
                "codigo_unspsc": "43211500",
                "tipo": "PRODUCTO",
                "precio_unitario": 50000,
                "unidad_medida": "UNI",
                "incluye_iva": True,
                "porcentaje_iva": 19.00,
                "maneja_inventario": True,
                "stock_actual": 100,
                "stock_minimo": 10
            }
        ]
        
        for product_data in test_products:
            producto = Producto(
                empresa_id=test_empresa.id,
                **product_data
            )
            session.add(producto)
        
        await session.commit()
        print("✅ Initial data created successfully")
        print("\n📋 Test credentials:")
        print("   Admin: admin@empresatest.com / admin123")
        print("   User:  usuario@empresatest.com / user123")
        print(f"   Company: {test_empresa.razon_social} (NIT: {test_empresa.nit})")
    
    await engine.dispose()


async def main():
    """Main function"""
    try:
        await create_initial_data()
    except Exception as e:
        print(f"❌ Error creating initial data: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())