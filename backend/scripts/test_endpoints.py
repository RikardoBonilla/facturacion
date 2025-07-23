#!/usr/bin/env python3
"""
Script para probar todos los endpoints de la API
Incluye autenticación y operaciones CRUD completas
"""

import asyncio
import json
import sys
from pathlib import Path

import httpx

# Base URL de la API
BASE_URL = "http://localhost:8000/api/v1"

# Credenciales de prueba (del seeding script)
TEST_CREDENTIALS = {
    "username": "admin@empresatest.com",  # OAuth2 usa 'username' field
    "password": "admin123"
}

class APITester:
    def __init__(self):
        self.client = httpx.AsyncClient()
        self.token = None
        self.headers = {}
        self.empresa_id = None
        self.test_resources = {}
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    def print_response(self, method, url, response, description=""):
        """Print formatted response information"""
        status_color = "🟢" if response.status_code < 400 else "🔴"
        print(f"\n{status_color} {method} {url}")
        if description:
            print(f"   📝 {description}")
        print(f"   📊 Status: {response.status_code}")
        
        try:
            json_data = response.json()
            if isinstance(json_data, dict) and len(json_data) <= 5:
                print(f"   📋 Response: {json.dumps(json_data, indent=2, ensure_ascii=False)}")
            elif isinstance(json_data, list) and len(json_data) <= 3:
                print(f"   📋 Response: {len(json_data)} items")
                if json_data:
                    print(f"   🔍 First item: {json.dumps(json_data[0], indent=2, ensure_ascii=False)}")
            else:
                print(f"   📋 Response: {type(json_data).__name__} with {len(json_data) if hasattr(json_data, '__len__') else 'N/A'} items")
        except:
            print(f"   📋 Response: {response.text[:200]}...")
    
    async def test_authentication(self):
        """Test authentication endpoints"""
        print("\n" + "="*60)
        print("🔐 TESTING AUTHENTICATION")
        print("="*60)
        
        # Test login
        login_data = TEST_CREDENTIALS
        response = await self.client.post(
            f"{BASE_URL}/auth/login",
            data=login_data,  # OAuth2PasswordRequestForm expects form data
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        self.print_response("POST", "/auth/login", response, "User login")
        
        if response.status_code == 200:
            data = response.json()
            self.token = data["access_token"]
            self.empresa_id = data["user"]["empresa_id"]
            self.headers = {"Authorization": f"Bearer {self.token}"}
            print(f"   ✅ Token obtained successfully")
            print(f"   🏢 Company ID: {self.empresa_id}")
        else:
            print("   ❌ Authentication failed")
            return False
        
        # Test get current user info
        response = await self.client.get(
            f"{BASE_URL}/auth/me",
            headers=self.headers
        )
        self.print_response("GET", "/auth/me", response, "Get current user info")
        
        # Test logout
        response = await self.client.post(
            f"{BASE_URL}/auth/logout",
            headers=self.headers
        )
        self.print_response("POST", "/auth/logout", response, "User logout")
        
        return True
    
    async def test_empresas_endpoints(self):
        """Test empresas (companies) endpoints"""
        print("\n" + "="*60)
        print("🏢 TESTING EMPRESAS ENDPOINTS")
        print("="*60)
        
        # GET - List companies
        response = await self.client.get(
            f"{BASE_URL}/empresas",
            headers=self.headers
        )
        self.print_response("GET", "/empresas", response, "List all companies")
        
        # GET - Get specific company
        if self.empresa_id:
            response = await self.client.get(
                f"{BASE_URL}/empresas/{self.empresa_id}",
                headers=self.headers
            )
            self.print_response("GET", f"/empresas/{self.empresa_id}", response, "Get company by ID")
        
        # POST - Create new company
        new_company_data = {
            "nit": "900999888-7",
            "razon_social": "Nueva Empresa Test S.A.S.",
            "nombre_comercial": "Nueva Empresa Test",
            "direccion": "Calle Test # 123-45",
            "ciudad": "Medellín",
            "departamento": "Antioquia",
            "telefono": "3001112233",
            "email": "test@nuevaempresa.com",
            "tipo_contribuyente": "PERSONA_JURIDICA",
            "regimen_fiscal": "COMUN",
            "responsabilidades_fiscales": ["05", "09"],
            "ambiente_dian": "PRUEBAS",
            "prefijo_factura": "NE",
            "resolucion_dian": "18760000999",
            "rango_autorizado_desde": 1,
            "rango_autorizado_hasta": 1000
        }
        
        response = await self.client.post(
            f"{BASE_URL}/empresas",
            json=new_company_data,
            headers=self.headers
        )
        self.print_response("POST", "/empresas", response, "Create new company")
        
        if response.status_code in [200, 201]:
            created_company = response.json()
            self.test_resources["empresa_id"] = created_company["id"]
            
            # PUT - Update company
            update_data = {
                "telefono": "3009998877",
                "email": "updated@nuevaempresa.com"
            }
            
            response = await self.client.put(
                f"{BASE_URL}/empresas/{created_company['id']}",
                json=update_data,
                headers=self.headers
            )
            self.print_response("PUT", f"/empresas/{created_company['id']}", response, "Update company")
        
    async def test_clientes_endpoints(self):
        """Test clientes (customers) endpoints"""
        print("\n" + "="*60)
        print("👥 TESTING CLIENTES ENDPOINTS")
        print("="*60)
        
        # GET - List clients
        response = await self.client.get(
            f"{BASE_URL}/clientes",
            headers=self.headers
        )
        self.print_response("GET", "/clientes", response, "List all clients")
        
        # POST - Create new client
        new_client_data = {
            "tipo_persona": "NATURAL",
            "tipo_documento": "CC",
            "numero_documento": "12345678",
            "nombres": "Test Cliente",
            "apellidos": "API Testing",
            "email": "testcliente@email.com",
            "telefono": "3001234567",
            "direccion": "Calle Cliente # 456-78",
            "ciudad": "Bogotá",
            "departamento": "Cundinamarca",
            "regimen_fiscal": "SIMPLIFICADO"
        }
        
        response = await self.client.post(
            f"{BASE_URL}/clientes",
            json=new_client_data,
            headers=self.headers
        )
        self.print_response("POST", "/clientes", response, "Create new client")
        
        if response.status_code in [200, 201]:
            created_client = response.json()
            client_id = created_client["id"]
            self.test_resources["client_id"] = client_id
            
            # GET - Get specific client
            response = await self.client.get(
                f"{BASE_URL}/clientes/{client_id}",
                headers=self.headers
            )
            self.print_response("GET", f"/clientes/{client_id}", response, "Get client by ID")
            
            # PUT - Update client
            update_data = {
                "telefono": "3009876543",
                "email": "updated@email.com"
            }
            
            response = await self.client.put(
                f"{BASE_URL}/clientes/{client_id}",
                json=update_data,
                headers=self.headers
            )
            self.print_response("PUT", f"/clientes/{client_id}", response, "Update client")
    
    async def test_productos_endpoints(self):
        """Test productos (products) endpoints"""
        print("\n" + "="*60)
        print("📦 TESTING PRODUCTOS ENDPOINTS")
        print("="*60)
        
        # GET - List products
        response = await self.client.get(
            f"{BASE_URL}/productos",
            headers=self.headers
        )
        self.print_response("GET", "/productos", response, "List all products")
        
        # POST - Create new product
        new_product_data = {
            "codigo_interno": "TEST001",
            "nombre": "Producto Test API",
            "descripcion": "Producto creado para testing de API",
            "codigo_clasificacion": "12345678",
            "tipo": "PRODUCTO",
            "precio": 100000,
            "costo": 80000,
            "unidad_medida": "UND",
            "aplica_iva": True,
            "porcentaje_iva": 19.00,
            "stock_actual": 100,
            "stock_minimo": 10
        }
        
        response = await self.client.post(
            f"{BASE_URL}/productos",
            json=new_product_data,
            headers=self.headers
        )
        self.print_response("POST", "/productos", response, "Create new product")
        
        if response.status_code in [200, 201]:
            created_product = response.json()
            product_id = created_product["id"]
            self.test_resources["product_id"] = product_id
            
            # GET - Get specific product
            response = await self.client.get(
                f"{BASE_URL}/productos/{product_id}",
                headers=self.headers
            )
            self.print_response("GET", f"/productos/{product_id}", response, "Get product by ID")
            
            # PUT - Update product
            update_data = {
                "precio": 120000,
                "descripcion": "Producto actualizado via API"
            }
            
            response = await self.client.put(
                f"{BASE_URL}/productos/{product_id}",
                json=update_data,
                headers=self.headers
            )
            self.print_response("PUT", f"/productos/{product_id}", response, "Update product")
    
    async def test_facturas_endpoints(self):
        """Test facturas (invoices) endpoints"""
        print("\n" + "="*60)
        print("🧾 TESTING FACTURAS ENDPOINTS")
        print("="*60)
        
        # GET - List invoices
        response = await self.client.get(
            f"{BASE_URL}/facturas",
            headers=self.headers
        )
        self.print_response("GET", "/facturas", response, "List all invoices")
        
        # For creating invoice, we need existing client and product IDs
        if "client_id" in self.test_resources and "product_id" in self.test_resources:
            # POST - Create new invoice
            new_invoice_data = {
                "cliente_id": self.test_resources["client_id"],
                "fecha_vencimiento": "2024-12-31",
                "forma_pago": "CREDITO",
                "observaciones": "Factura de prueba API",
                "detalles": [
                    {
                        "producto_id": self.test_resources["product_id"],
                        "cantidad": 2,
                        "precio_unitario": 100000,
                        "descuento_porcentaje": 5.0
                    }
                ]
            }
            
            response = await self.client.post(
                f"{BASE_URL}/facturas",
                json=new_invoice_data,
                headers=self.headers
            )
            self.print_response("POST", "/facturas", response, "Create new invoice")
            
            if response.status_code in [200, 201]:
                created_invoice = response.json()
                invoice_id = created_invoice["id"]
                self.test_resources["invoice_id"] = invoice_id
                
                # GET - Get specific invoice
                response = await self.client.get(
                    f"{BASE_URL}/facturas/{invoice_id}",
                    headers=self.headers
                )
                self.print_response("GET", f"/facturas/{invoice_id}", response, "Get invoice by ID")
    
    async def test_delete_operations(self):
        """Test DELETE operations for created resources"""
        print("\n" + "="*60)
        print("🗑️ TESTING DELETE OPERATIONS")
        print("="*60)
        
        # Delete in reverse order to avoid foreign key constraints
        delete_order = [
            ("invoice_id", "facturas", "invoice"),
            ("product_id", "productos", "product"),
            ("client_id", "clientes", "client"),
            ("empresa_id", "empresas", "company")
        ]
        
        for resource_key, endpoint, name in delete_order:
            if resource_key in self.test_resources:
                resource_id = self.test_resources[resource_key]
                response = await self.client.delete(
                    f"{BASE_URL}/{endpoint}/{resource_id}",
                    headers=self.headers
                )
                self.print_response("DELETE", f"/{endpoint}/{resource_id}", response, f"Delete {name}")
    
    async def run_all_tests(self):
        """Run all API tests"""
        print("🚀 STARTING COMPREHENSIVE API TESTING")
        print("="*60)
        
        # Test authentication first
        if not await self.test_authentication():
            print("❌ Authentication failed, stopping tests")
            return
        
        # Test all CRUD endpoints
        await self.test_empresas_endpoints()
        await self.test_clientes_endpoints()
        await self.test_productos_endpoints()
        await self.test_facturas_endpoints()
        
        # Test delete operations
        await self.test_delete_operations()
        
        print("\n" + "="*60)
        print("✅ ALL TESTS COMPLETED")
        print("="*60)
        print("📋 Summary:")
        print("   🔐 Authentication: Tested login, user info, logout")
        print("   🏢 Companies: GET, POST, PUT operations")
        print("   👥 Clients: GET, POST, PUT operations")
        print("   📦 Products: GET, POST, PUT operations")  
        print("   🧾 Invoices: GET, POST operations")
        print("   🗑️ Delete: All created resources cleaned up")
        print(f"\n💡 Swagger UI available at: http://localhost:8000/docs")
        print(f"📖 ReDoc available at: http://localhost:8000/redoc")


async def main():
    """Main function to run all tests"""
    try:
        async with APITester() as tester:
            await tester.run_all_tests()
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())