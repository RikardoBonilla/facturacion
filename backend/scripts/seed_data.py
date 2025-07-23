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
from sqlalchemy import select
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
        
        # Get or create roles
        admin_role_result = await session.execute(
            select(Rol).where(Rol.nombre == "ADMINISTRADOR")
        )
        admin_role = admin_role_result.scalar_one_or_none()
        
        if not admin_role:
            admin_role = Rol(
                nombre="ADMINISTRADOR",
                descripcion="Administrador del sistema con todos los permisos"
            )
            session.add(admin_role)
        
        user_role_result = await session.execute(
            select(Rol).where(Rol.nombre == "USUARIO")
        )
        user_role = user_role_result.scalar_one_or_none()
        
        if not user_role:
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
            # Check if permission already exists
            existing_permission_result = await session.execute(
                select(Permiso).where(Permiso.modulo == modulo, Permiso.accion == accion)
            )
            existing_permission = existing_permission_result.scalar_one_or_none()
            if not existing_permission:
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
        
        # Create more test clients
        test_clientes = [
            {
                "tipo_persona": "NATURAL",
                "tipo_documento": "CC",
                "numero_documento": "98765432",
                "nombres": "Juan Carlos",
                "apellidos": "Pérez García",
                "email": "juan.perez@email.com",
                "telefono": "3012345678",
                "direccion": "Calle 15 # 10-20",
                "ciudad": "Bogotá",
                "departamento": "Cundinamarca",
                "regimen_fiscal": "SIMPLIFICADO"
            },
            {
                "tipo_persona": "JURIDICA",
                "tipo_documento": "NIT",
                "numero_documento": "800123456",
                "dv": "9",
                "razon_social": "Comercializadora ABC S.A.S.",
                "nombre_comercial": "Comercializadora ABC",
                "email": "facturacion@comercializadoraabc.com",
                "telefono": "6012345678",
                "direccion": "Carrera 7 # 45-67",
                "ciudad": "Medellín",
                "departamento": "Antioquia",
                "regimen_fiscal": "COMUN",
                "responsabilidades_fiscales": ["05", "09"]
            },
            {
                "tipo_persona": "NATURAL",
                "tipo_documento": "CC",
                "numero_documento": "45678901",
                "nombres": "María Elena",
                "apellidos": "Rodríguez López",
                "email": "maria.rodriguez@email.com",
                "telefono": "3098765432",
                "direccion": "Calle 22 # 30-45",
                "ciudad": "Cali",
                "departamento": "Valle del Cauca",
                "regimen_fiscal": "SIMPLIFICADO"
            },
            {
                "tipo_persona": "JURIDICA",
                "tipo_documento": "NIT",
                "numero_documento": "900987654",
                "dv": "3",
                "razon_social": "Distribuidora XYZ Ltda",
                "nombre_comercial": "Distribuidora XYZ",
                "email": "contabilidad@distribuidoraxyz.com",
                "telefono": "6019876543",
                "direccion": "Avenida 68 # 12-34",
                "ciudad": "Barranquilla",
                "departamento": "Atlántico",
                "regimen_fiscal": "COMUN",
                "responsabilidades_fiscales": ["05", "09", "48"]
            }
        ]
        
        for cliente_data in test_clientes:
            cliente = Cliente(
                empresa_id=test_empresa.id,
                **cliente_data
            )
            session.add(cliente)
        
        # Create diverse test products
        test_products = [
            {
                "codigo_interno": "SERV001",
                "nombre": "Consultoría en Sistemas",
                "descripcion": "Servicio profesional de consultoría en sistemas de información",
                "codigo_clasificacion": "81161500",
                "tipo": "SERVICIO",
                "precio": 150000,
                "unidad_medida": "HOR",
                "aplica_iva": True,
                "porcentaje_iva": 19.00
            },
            {
                "codigo_interno": "PROD001", 
                "nombre": "Computador Portátil",
                "descripcion": "Computador portátil Intel Core i5, 8GB RAM, 256GB SSD",
                "codigo_clasificacion": "43211508",
                "tipo": "PRODUCTO",
                "precio": 2500000,
                "costo": 2000000,
                "unidad_medida": "UND",
                "aplica_iva": True,
                "porcentaje_iva": 19.00,
                "stock_actual": 50,
                "stock_minimo": 5
            },
            {
                "codigo_interno": "PROD002",
                "nombre": "Mouse Inalámbrico",
                "descripcion": "Mouse óptico inalámbrico con receptor USB",
                "codigo_clasificacion": "43211714",
                "tipo": "PRODUCTO",
                "precio": 45000,
                "costo": 25000,
                "unidad_medida": "UND",
                "aplica_iva": True,
                "porcentaje_iva": 19.00,
                "stock_actual": 200,
                "stock_minimo": 20
            },
            {
                "codigo_interno": "SERV002",
                "nombre": "Soporte Técnico",
                "descripcion": "Servicio de soporte técnico especializado",
                "codigo_clasificacion": "81112200",
                "tipo": "SERVICIO",
                "precio": 80000,
                "unidad_medida": "HOR",
                "aplica_iva": True,
                "porcentaje_iva": 19.00
            },
            {
                "codigo_interno": "PROD003",
                "nombre": "Teclado Mecánico",
                "descripcion": "Teclado mecánico gaming retroiluminado",
                "codigo_clasificacion": "43211710",
                "tipo": "PRODUCTO",
                "precio": 320000,
                "costo": 200000,
                "unidad_medida": "UND",
                "aplica_iva": True,
                "porcentaje_iva": 19.00,
                "stock_actual": 30,
                "stock_minimo": 3
            },
            {
                "codigo_interno": "SERV003",
                "nombre": "Capacitación Empresarial",
                "descripcion": "Capacitación en herramientas empresariales",
                "codigo_clasificacion": "92111600",
                "tipo": "SERVICIO",
                "precio": 500000,
                "unidad_medida": "DIA",
                "aplica_iva": True,
                "porcentaje_iva": 19.00
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