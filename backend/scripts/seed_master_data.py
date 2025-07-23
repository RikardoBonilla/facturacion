#!/usr/bin/env python3
"""
Script para poblar datos maestros del sistema
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


async def create_master_data():
    """Create master data for the Colombian invoicing system"""
    
    engine = create_async_engine(settings.DATABASE_URL)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        print("🏛️ Creating master data...")
        
        # Create Colombian taxes (impuestos)
        impuestos_data = [
            # IVA rates
            ("01", "IVA 0%", 0.00, "NACIONAL"),
            ("02", "IVA 5%", 5.00, "NACIONAL"),
            ("03", "IVA 19%", 19.00, "NACIONAL"), 
            # INC (Impuesto Nacional al Consumo)
            ("04", "INC 4%", 4.00, "NACIONAL"),
            ("05", "INC 8%", 8.00, "NACIONAL"),
            ("06", "INC 16%", 16.00, "NACIONAL"),
            # ICA (Impuesto de Industria y Comercio)
            ("07", "ICA 0.2%", 0.20, "MUNICIPAL"),
            ("08", "ICA 0.3%", 0.30, "MUNICIPAL"),
            ("09", "ICA 0.4%", 0.40, "MUNICIPAL"),
            ("10", "ICA 0.5%", 0.50, "MUNICIPAL"),
            ("11", "ICA 0.6%", 0.60, "MUNICIPAL"),
            ("12", "ICA 0.7%", 0.70, "MUNICIPAL"),
            ("13", "ICA 1.0%", 1.00, "MUNICIPAL"),
        ]
        
        for codigo, nombre, porcentaje, tipo in impuestos_data:
            await session.execute(
                text("""
                    INSERT INTO impuestos (codigo, nombre, porcentaje, tipo, activo) 
                    VALUES (:codigo, :nombre, :porcentaje, :tipo, true)
                    ON CONFLICT (codigo) DO UPDATE SET
                        nombre = EXCLUDED.nombre,
                        porcentaje = EXCLUDED.porcentaje,
                        tipo = EXCLUDED.tipo,
                        activo = EXCLUDED.activo
                """),
                {
                    "codigo": codigo,
                    "nombre": nombre,
                    "porcentaje": porcentaje,
                    "tipo": tipo
                }
            )
        
        await session.commit()
        print("💰 Colombian tax rates created successfully")
    
    await engine.dispose()


async def main():
    """Main function"""
    try:
        await create_master_data()
        print("✅ Master data created successfully")
    except Exception as e:
        print(f"❌ Error creating master data: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())