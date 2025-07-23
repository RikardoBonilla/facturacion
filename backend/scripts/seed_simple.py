#!/usr/bin/env python3
"""
Script simplificado para poblar datos de prueba
"""

import asyncio
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from app.core.config import settings


async def create_simple_test_data():
    """Create simple test data without conflicts"""
    
    engine = create_async_engine(settings.DATABASE_URL)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        print("🌱 Creating simple test data...")
        
        # Create test company with conflict handling
        await session.execute(text("""
            INSERT INTO empresas (
                nit, razon_social, nombre_comercial, direccion, ciudad, departamento,
                telefono, email, tipo_contribuyente, regimen_fiscal, responsabilidades_fiscales,
                ambiente_dian, prefijo_factura, resolucion_dian, rango_autorizado_desde, rango_autorizado_hasta
            ) VALUES (
                '900123456-1', 'Empresa de Pruebas S.A.S.', 'Empresa Test', 
                'Carrera 10 # 20-30', 'Bogotá', 'Cundinamarca',
                '3001234567', 'admin@empresatest.com', 'PERSONA_JURIDICA', 'COMUN', 
                ARRAY['05', '09'], 'PRUEBAS', 'FT', '18760000001', 1, 5000
            ) ON CONFLICT (nit) DO NOTHING
        """))
        
        # Get empresa_id
        result = await session.execute(text("""
            SELECT id FROM empresas WHERE nit = '900123456-1'
        """))
        empresa_id = result.scalar()
        
        if not empresa_id:
            print("❌ Could not create or find test company")
            return
        
        # Create test client
        await session.execute(text("""
            INSERT INTO clientes (
                empresa_id, tipo_persona, tipo_documento, numero_documento,
                nombres, apellidos, email, telefono, direccion, ciudad, departamento, regimen_fiscal
            ) VALUES (
                :empresa_id, 'NATURAL', 'CC', '98765432',
                'Juan Carlos', 'Pérez García', 'juan.perez@email.com', '3012345678',
                'Calle 15 # 10-20', 'Bogotá', 'Cundinamarca', 'SIMPLIFICADO'
            ) ON CONFLICT (empresa_id, tipo_documento, numero_documento) DO NOTHING
        """), {"empresa_id": empresa_id})
        
        # Create test products
        products_sql = """
            INSERT INTO productos (
                empresa_id, codigo_interno, nombre, descripcion, codigo_clasificacion,
                precio, unidad_medida, tipo, aplica_iva, porcentaje_iva, stock_actual, stock_minimo
            ) VALUES 
            (:empresa_id, 'SERV001', 'Consultoría en Sistemas', 'Servicio profesional de consultoría', '81161500', 150000, 'HOR', 'SERVICIO', true, 19.00, 0, 0),
            (:empresa_id, 'PROD001', 'Computador Portátil', 'Computador portátil Intel Core i5', '43211508', 2500000, 'UND', 'PRODUCTO', true, 19.00, 50, 5),
            (:empresa_id, 'PROD002', 'Mouse Inalámbrico', 'Mouse óptico inalámbrico', '43211714', 45000, 'UND', 'PRODUCTO', true, 19.00, 200, 20)
            ON CONFLICT (empresa_id, codigo_interno) DO NOTHING
        """
        
        await session.execute(text(products_sql), {"empresa_id": empresa_id})
        
        await session.commit()
        print("✅ Simple test data created successfully")
        print(f"🏢 Company ID: {empresa_id}")
        print("📋 Test data includes:")
        print("   • 1 Test company (Empresa de Pruebas S.A.S.)")
        print("   • 1 Test client (Juan Carlos Pérez García)")
        print("   • 3 Test products/services")
        print("\n💡 You can now test basic functionality!")
    
    await engine.dispose()


async def main():
    """Main function"""
    try:
        await create_simple_test_data()
    except Exception as e:
        print(f"❌ Error creating simple test data: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())