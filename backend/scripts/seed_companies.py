#!/usr/bin/env python3
"""
Script para crear empresas adicionales de prueba (multi-tenant)
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


async def create_additional_companies():
    """Create additional test companies"""
    
    engine = create_async_engine(settings.DATABASE_URL)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        auth_service = AuthService(session)
        
        print("🏢 Creating additional test companies...")
        
        # Get existing roles
        admin_role_result = await session.execute(
            select(Rol).where(Rol.nombre == "ADMINISTRADOR")
        )
        admin_role = admin_role_result.scalar_one_or_none()
        
        user_role_result = await session.execute(
            select(Rol).where(Rol.nombre == "USUARIO")
        )
        user_role = user_role_result.scalar_one_or_none()
        
        if not admin_role or not user_role:
            print("❌ Roles not found. Run seed_data.py first.")
            return
        
        # Additional companies data
        companies_data = [
            {
                "empresa": {
                    "nit": "800987654-3",
                    "razon_social": "Tecnología Digital S.A.S.",
                    "nombre_comercial": "TechDigital",
                    "direccion": "Carrera 15 # 93-47",
                    "ciudad": "Bogotá",
                    "departamento": "Cundinamarca",
                    "telefono": "6017894561",
                    "email": "admin@techdigital.com",
                    "tipo_contribuyente": "PERSONA_JURIDICA",
                    "regimen_fiscal": "COMUN",
                    "responsabilidades_fiscales": ["05", "09"],
                    "ambiente_dian": "PRUEBAS",
                    "prefijo_factura": "TD",
                    "resolucion_dian": "18760000002",
                    "rango_autorizado_desde": 1,
                    "rango_autorizado_hasta": 10000
                },
                "admin": {
                    "email": "admin@techdigital.com",
                    "password": "tech123",
                    "nombre": "Carlos",
                    "apellido": "Mendoza",
                    "tipo_documento": "CC",
                    "numero_documento": "79123456",
                    "telefono": "3201234567"
                },
                "clientes": [
                    {
                        "tipo_persona": "JURIDICA",
                        "tipo_documento": "NIT",
                        "numero_documento": "830123456",
                        "dv": "7",
                        "razon_social": "Soluciones Empresariales Ltda",
                        "email": "facturacion@solempresariales.com",
                        "telefono": "6015551234",
                        "direccion": "Calle 26 # 13-45",
                        "ciudad": "Bogotá",
                        "departamento": "Cundinamarca",
                        "regimen_fiscal": "COMUN"
                    }
                ],
                "productos": [
                    {
                        "codigo_interno": "SOFT001",
                        "nombre": "Licencia Software ERP",
                        "descripcion": "Licencia anual software ERP empresarial",
                        "codigo_clasificacion": "81112201",
                        "tipo": "SERVICIO",
                        "precio": 1200000,
                        "unidad_medida": "LIC",
                        "aplica_iva": True,
                        "porcentaje_iva": 19.00
                    },
                    {
                        "codigo_interno": "SOFT002",
                        "nombre": "Desarrollo Web",
                        "descripcion": "Desarrollo de aplicación web personalizada",
                        "codigo_clasificacion": "81112202",
                        "tipo": "SERVICIO",
                        "precio": 350000,
                        "unidad_medida": "HOR",
                        "aplica_iva": True,
                        "porcentaje_iva": 19.00
                    }
                ]
            },
            {
                "empresa": {
                    "nit": "900555333-1",
                    "razon_social": "Comercial del Caribe S.A.S.",
                    "nombre_comercial": "Comercial Caribe",
                    "direccion": "Carrera 43 # 52-165",
                    "ciudad": "Barranquilla",
                    "departamento": "Atlántico",
                    "telefono": "6053334455",
                    "email": "admin@comercialcaribe.com",
                    "tipo_contribuyente": "PERSONA_JURIDICA",
                    "regimen_fiscal": "COMUN",
                    "responsabilidades_fiscales": ["05", "09", "48"],
                    "ambiente_dian": "PRUEBAS",
                    "prefijo_factura": "CC",
                    "resolucion_dian": "18760000003",
                    "rango_autorizado_desde": 1,
                    "rango_autorizado_hasta": 15000
                },
                "admin": {
                    "email": "admin@comercialcaribe.com",
                    "password": "caribe123",
                    "nombre": "Ana María",
                    "apellido": "Vargas",
                    "tipo_documento": "CC",
                    "numero_documento": "32654987",
                    "telefono": "3159876543"
                },
                "clientes": [
                    {
                        "tipo_persona": "NATURAL",
                        "tipo_documento": "CC",
                        "numero_documento": "72456789",
                        "nombres": "Roberto",
                        "apellidos": "Silva Martínez",
                        "email": "roberto.silva@email.com",
                        "telefono": "3008765432",
                        "direccion": "Calle 84 # 50-23",
                        "ciudad": "Barranquilla",
                        "departamento": "Atlántico",
                        "regimen_fiscal": "SIMPLIFICADO"
                    }
                ],
                "productos": [
                    {
                        "codigo_interno": "ELEC001",
                        "nombre": "Televisor LED 55\"",
                        "descripcion": "Televisor LED 55 pulgadas 4K Smart TV",
                        "codigo_clasificacion": "52161517",
                        "tipo": "PRODUCTO",
                        "precio": 1800000,
                        "costo": 1300000,
                        "unidad_medida": "UND",
                        "aplica_iva": True,
                        "porcentaje_iva": 19.00,
                        "stock_actual": 25,
                        "stock_minimo": 3
                    },
                    {
                        "codigo_interno": "ELEC002",
                        "nombre": "Nevera 350L",
                        "descripcion": "Nevera no frost 350 litros",
                        "codigo_clasificacion": "52141500",
                        "tipo": "PRODUCTO",
                        "precio": 1200000,
                        "costo": 900000,
                        "unidad_medida": "UND",
                        "aplica_iva": True,
                        "porcentaje_iva": 19.00,
                        "stock_actual": 15,
                        "stock_minimo": 2
                    }
                ]
            }
        ]
        
        for company_data in companies_data:
            # Create company
            empresa = Empresa(**company_data["empresa"])
            session.add(empresa)
            await session.flush()
            
            # Create admin user
            admin_data = company_data["admin"]
            admin_user = Usuario(
                empresa_id=empresa.id,
                email=admin_data["email"],
                password_hash=auth_service.get_password_hash(admin_data["password"]),
                nombre=admin_data["nombre"],
                apellido=admin_data["apellido"],
                tipo_documento=admin_data["tipo_documento"],
                numero_documento=admin_data["numero_documento"],
                telefono=admin_data["telefono"],
                rol_id=admin_role.id,
                activo=True
            )
            session.add(admin_user)
            
            # Create clients
            for cliente_data in company_data["clientes"]:
                cliente = Cliente(
                    empresa_id=empresa.id,
                    **cliente_data
                )
                session.add(cliente)
            
            # Create products
            for producto_data in company_data["productos"]:
                producto = Producto(
                    empresa_id=empresa.id,
                    **producto_data
                )
                session.add(producto)
            
            print(f"✅ Created company: {empresa.razon_social}")
        
        await session.commit()
        print(f"🏢 Created {len(companies_data)} additional companies successfully")
        
        # Print credentials
        print("\n📋 Additional company credentials:")
        for company_data in companies_data:
            empresa_info = company_data["empresa"]
            admin_info = company_data["admin"]
            print(f"   {empresa_info['razon_social']}:")
            print(f"     Email: {admin_info['email']}")
            print(f"     Password: {admin_info['password']}")
            print(f"     NIT: {empresa_info['nit']}")
    
    await engine.dispose()


async def main():
    """Main function"""
    try:
        await create_additional_companies()
        print("✅ Additional companies created successfully")
    except Exception as e:
        print(f"❌ Error creating additional companies: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())