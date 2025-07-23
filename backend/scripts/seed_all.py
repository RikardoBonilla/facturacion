#!/usr/bin/env python3
"""
Script maestro para ejecutar todos los scripts de seeding
"""

import asyncio
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from seed_master_data import create_master_data
from seed_data import create_initial_data
from seed_companies import create_additional_companies
from seed_invoices import create_sample_invoices


async def seed_all():
    """Execute all seeding scripts in proper order"""
    
    print("🌱 Starting complete database seeding process...")
    print("=" * 60)
    
    try:
        # Step 1: Create master data (taxes, etc.)
        print("\n1️⃣ Creating master data...")
        await create_master_data()
        
        # Step 2: Create initial data (roles, permissions, test company)
        print("\n2️⃣ Creating initial data...")
        await create_initial_data()
        
        # Step 3: Create additional companies
        print("\n3️⃣ Creating additional companies...")
        await create_additional_companies()
        
        # Step 4: Create sample invoices
        print("\n4️⃣ Creating sample invoices...")
        await create_sample_invoices()
        
        print("\n" + "=" * 60)
        print("🎉 Complete database seeding finished successfully!")
        print("\n📋 Summary of created data:")
        print("   ✅ Colombian tax rates (IVA, INC, ICA)")
        print("   ✅ Roles and permissions system")
        print("   ✅ 3 test companies with multi-tenant setup")
        print("   ✅ Multiple users (admin and regular)")
        print("   ✅ Diverse client database")
        print("   ✅ Product/service catalog")
        print("   ✅ Sample invoices with details")
        
        print("\n🔑 Test credentials:")
        print("   Main Company (Empresa de Pruebas S.A.S.):")
        print("     Admin: admin@empresatest.com / admin123")
        print("     User:  usuario@empresatest.com / user123")
        print("   ")
        print("   TechDigital:")
        print("     Admin: admin@techdigital.com / tech123")
        print("   ")
        print("   Comercial Caribe:")
        print("     Admin: admin@comercialcaribe.com / caribe123")
        
        print("\n💡 You can now test the complete invoicing system!")
        
    except Exception as e:
        print(f"\n❌ Error during seeding process: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


async def main():
    """Main function"""
    await seed_all()


if __name__ == "__main__":
    asyncio.run(main())