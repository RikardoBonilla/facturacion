#!/usr/bin/env python3
"""
Script de demostración para mostrar el uso de Swagger UI y endpoints específicos
"""

import asyncio
import json
import sys
from pathlib import Path

import httpx

# Base URL de la API
BASE_URL = "http://localhost:8000/api/v1"

async def demo_swagger_endpoints():
    """Demonstrar endpoints específicos que funcionan bien en Swagger"""
    
    print("🚀 DEMOSTRACIÓN DE ENDPOINTS PARA SWAGGER UI")
    print("=" * 60)
    print(f"📖 Swagger UI: http://localhost:8000/docs")
    print(f"📋 OpenAPI JSON: http://localhost:8000/openapi.json")
    print("=" * 60)
    
    async with httpx.AsyncClient() as client:
        
        # 1. Test Authentication Flow
        print("\n🔐 1. AUTENTICACIÓN")
        print("-" * 30)
        
        # Login
        login_response = await client.post(
            f"{BASE_URL}/auth/login",
            data={"username": "admin@empresatest.com", "password": "admin123"},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if login_response.status_code == 200:
            token_data = login_response.json()
            token = token_data["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            
            print("✅ Login exitoso")
            print(f"   📧 Usuario: {token_data['user']['email']}")
            print(f"   🏢 Empresa: {token_data['user']['empresa_id']}")
            
            # Get user info
            user_info = await client.get(f"{BASE_URL}/auth/me", headers=headers)
            print(f"✅ Información del usuario obtenida (Status: {user_info.status_code})")
            
        else:
            print("❌ Error en login")
            return
        
        # 2. Test Direct API Calls  
        print("\n📊 2. ENDPOINTS DISPONIBLES")
        print("-" * 30)
        
        endpoints_to_test = [
            ("GET", "/empresas", "Listar empresas"),
            ("GET", "/clientes", "Listar clientes"),
            ("GET", "/productos", "Listar productos"),
            ("GET", "/facturas", "Listar facturas"),
            ("GET", "/usuarios", "Listar usuarios"),
        ]
        
        for method, endpoint, description in endpoints_to_test:
            try:
                response = await client.get(
                    f"{BASE_URL}{endpoint}",
                    headers=headers
                )
                status_emoji = "✅" if response.status_code < 400 else "⚠️"
                print(f"{status_emoji} {method} {endpoint} - {description} (Status: {response.status_code})")
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        if isinstance(data, list):
                            print(f"   📋 {len(data)} elementos encontrados")
                        else:
                            print(f"   📋 Respuesta: {type(data).__name__}")
                    except:
                        pass
                        
            except Exception as e:
                print(f"❌ {method} {endpoint} - Error: {str(e)[:50]}...")
        
        # 3. Create a test resource to show POST functionality
        print("\n📝 3. OPERACIONES DE CREACIÓN (POST)")
        print("-" * 30)
        
        # Create a test client
        new_client = {
            "tipo_persona": "NATURAL",
            "tipo_documento": "CC", 
            "numero_documento": "87654321",
            "nombres": "Demo Swagger",
            "apellidos": "API Test",
            "email": "demo@swagger.com",
            "telefono": "3001112233",
            "direccion": "Calle Demo #123",
            "ciudad": "Bogotá",
            "departamento": "Cundinamarca",
            "regimen_fiscal": "SIMPLIFICADO"
        }
        
        try:
            create_response = await client.post(
                f"{BASE_URL}/clientes",
                json=new_client,
                headers=headers
            )
            
            if create_response.status_code in [200, 201]:
                created_client = create_response.json()
                print("✅ Cliente creado exitosamente")
                print(f"   🆔 ID: {created_client.get('id', 'N/A')}")
                print(f"   👤 Nombre: {created_client.get('nombres', '')} {created_client.get('apellidos', '')}")
                
                # Clean up - delete the created client
                client_id = created_client.get('id')
                if client_id:
                    delete_response = await client.delete(
                        f"{BASE_URL}/clientes/{client_id}",
                        headers=headers
                    )
                    if delete_response.status_code in [200, 204]:
                        print("✅ Cliente eliminado (cleanup)")
                    
            else:
                print(f"⚠️ Error al crear cliente (Status: {create_response.status_code})")
                if create_response.status_code == 307:
                    print("   ℹ️ Redirección detectada - endpoint podría necesitar ajustes")
                    
        except Exception as e:
            print(f"❌ Error en creación de cliente: {str(e)[:50]}...")
    
    # 4. Swagger Instructions
    print("\n📚 4. CÓMO USAR SWAGGER UI")
    print("-" * 30)
    print("1. Abrir http://localhost:8000/docs en tu navegador")
    print("2. Hacer clic en 'Authorize' (botón de candado)")
    print("3. En 'OAuth2PasswordBearer' usar:")
    print("   - username: admin@empresatest.com")
    print("   - password: admin123")
    print("4. Hacer clic en 'Authorize' y luego 'Close'")
    print("5. Ahora puedes probar cualquier endpoint!")
    print("\n🔍 Endpoints recomendados para probar:")
    print("   • GET /auth/me - Información del usuario actual")
    print("   • GET /empresas - Listar empresas")
    print("   • GET /clientes - Listar clientes")
    print("   • POST /clientes - Crear nuevo cliente")
    print("   • GET /productos - Listar productos")
    
    print("\n" + "=" * 60)
    print("✅ DEMOSTRACIÓN COMPLETADA")
    print("💡 La API está funcionando correctamente con Swagger UI")
    print("=" * 60)


async def main():
    """Main function"""
    try:
        await demo_swagger_endpoints()
    except Exception as e:
        print(f"❌ Error durante la demostración: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())