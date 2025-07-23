#!/usr/bin/env python3
"""
Script para crear facturas de prueba con sus detalles
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta
from decimal import Decimal
import random

# Add the backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, text
from app.core.config import settings
from app.models import *


async def create_sample_invoices():
    """Create sample invoices with details"""
    
    engine = create_async_engine(settings.DATABASE_URL)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        print("📄 Creating sample invoices...")
        
        # Get test company
        empresa_result = await session.execute(
            select(Empresa).where(Empresa.nit == "900123456-1")
        )
        empresa = empresa_result.scalar_one_or_none()
        
        if not empresa:
            print("❌ Test company not found. Run seed_data.py first.")
            return
        
        # Get clients
        clientes_result = await session.execute(
            select(Cliente).where(Cliente.empresa_id == empresa.id)
        )
        clientes = clientes_result.scalars().all()
        
        if not clientes:
            print("❌ No clients found. Run seed_data.py first.")
            return
        
        # Get products
        productos_result = await session.execute(
            select(Producto).where(Producto.empresa_id == empresa.id)
        )
        productos = productos_result.scalars().all()
        
        if not productos:
            print("❌ No products found. Run seed_data.py first.")
            return
        
        # Get admin user
        usuario_result = await session.execute(
            select(Usuario).where(
                Usuario.empresa_id == empresa.id,
                Usuario.email == "admin@empresatest.com"
            )
        )
        usuario = usuario_result.scalar_one_or_none()
        
        # Create sample invoices
        invoice_scenarios = [
            {
                "cliente": clientes[0] if len(clientes) > 0 else None,
                "productos": [
                    {"producto": productos[0], "cantidad": 2, "descuento": 0},
                    {"producto": productos[1], "cantidad": 1, "descuento": 5}
                ] if len(productos) > 1 else [],
                "forma_pago": "CONTADO",
                "metodo_pago": "EFECTIVO",
                "dias_vencimiento": 0
            },
            {
                "cliente": clientes[1] if len(clientes) > 1 else clientes[0],
                "productos": [
                    {"producto": productos[2], "cantidad": 5, "descuento": 0}
                ] if len(productos) > 2 else [{"producto": productos[0], "cantidad": 1, "descuento": 0}],
                "forma_pago": "CREDITO",
                "metodo_pago": "TRANSFERENCIA",
                "dias_vencimiento": 30
            },
            {
                "cliente": clientes[2] if len(clientes) > 2 else clientes[0],
                "productos": [
                    {"producto": productos[0], "cantidad": 8, "descuento": 10},
                    {"producto": productos[3], "cantidad": 2, "descuento": 0}
                ] if len(productos) > 3 else [{"producto": productos[0], "cantidad": 2, "descuento": 0}],
                "forma_pago": "CREDITO",
                "metodo_pago": "PSE",
                "dias_vencimiento": 15
            },
        ]
        
        for i, scenario in enumerate(invoice_scenarios, 1):
            if not scenario["cliente"] or not scenario["productos"]:
                continue
                
            fecha_emision = datetime.now() - timedelta(days=random.randint(1, 30))
            fecha_vencimiento = fecha_emision.date() + timedelta(days=scenario["dias_vencimiento"])
            
            # Calculate totals
            subtotal = Decimal('0')
            total_descuento = Decimal('0')
            
            for item in scenario["productos"]:
                producto = item["producto"]
                cantidad = Decimal(str(item["cantidad"]))
                descuento_pct = Decimal(str(item["descuento"]))
                
                precio_unitario = Decimal(str(producto.precio))
                subtotal_item = cantidad * precio_unitario
                descuento_item = subtotal_item * (descuento_pct / 100)
                
                subtotal += subtotal_item
                total_descuento += descuento_item
            
            base_gravable = subtotal - total_descuento
            total_iva = base_gravable * Decimal('0.19')  # Assuming 19% IVA
            total = base_gravable + total_iva
            
            # Create invoice
            numero_factura = i
            numero_completo = f"{empresa.prefijo_factura}{numero_factura:06d}"
            
            factura = Factura(
                empresa_id=empresa.id,
                tipo_documento="FV",
                prefijo=empresa.prefijo_factura,
                numero_factura=numero_factura,
                numero_completo=numero_completo,
                cliente_id=scenario["cliente"].id,
                fecha_emision=fecha_emision,
                fecha_vencimiento=fecha_vencimiento,
                subtotal=subtotal,
                descuento=total_descuento,
                base_gravable=base_gravable,
                total_iva=total_iva,
                total=total,
                estado="EMITIDA",
                forma_pago=scenario["forma_pago"],
                metodo_pago=scenario["metodo_pago"],
                usuario_id=usuario.id if usuario else None,
                observaciones=f"Factura de prueba #{i}"
            )
            session.add(factura)
            await session.flush()  # Get invoice ID
            
            # Create invoice details
            for item in scenario["productos"]:
                producto = item["producto"]
                cantidad = Decimal(str(item["cantidad"]))
                descuento_pct = Decimal(str(item["descuento"]))
                
                precio_unitario = Decimal(str(producto.precio))
                subtotal_item = cantidad * precio_unitario
                descuento_item = subtotal_item * (descuento_pct / 100)
                base_gravable_item = subtotal_item - descuento_item
                iva_item = base_gravable_item * (Decimal(str(producto.porcentaje_iva)) / 100)
                total_item = base_gravable_item + iva_item
                
                detalle = FacturaDetalle(
                    factura_id=factura.id,
                    producto_id=producto.id,
                    cantidad=cantidad,
                    precio_unitario=precio_unitario,
                    descuento_porcentaje=descuento_pct,
                    descuento_valor=descuento_item,
                    subtotal=subtotal_item,
                    base_gravable=base_gravable_item,
                    porcentaje_iva=Decimal(str(producto.porcentaje_iva)),
                    valor_iva=iva_item,
                    total=total_item
                )
                session.add(detalle)
                
                # Update product stock if applicable
                if producto.stock_actual is not None:
                    producto.stock_actual = max(0, producto.stock_actual - cantidad)
        
        await session.commit()
        print(f"✅ Created {len(invoice_scenarios)} sample invoices with details")
    
    await engine.dispose()


async def main():
    """Main function"""
    try:
        await create_sample_invoices()
        print("✅ Sample invoices created successfully")
    except Exception as e:
        print(f"❌ Error creating sample invoices: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())