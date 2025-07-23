"""
Integration tests for Colombian validation rules
"""

import pytest
from httpx import AsyncClient
from fastapi import status
from decimal import Decimal

from app.models import Cliente, Producto, Empresa


class TestDocumentValidation:
    """Test Colombian document type validation"""

    @pytest.mark.integration
    @pytest.mark.colombian
    @pytest.mark.asyncio
    async def test_create_cliente_valid_cc(
        self, 
        async_client: AsyncClient,
        authenticated_headers: dict
    ):
        """Test creating cliente with valid Cédula de Ciudadanía"""
        valid_cc_numbers = [
            "12345678",
            "1234567890",
            "87654321"
        ]
        
        for cc_number in valid_cc_numbers:
            cliente_data = {
                "tipo_persona": "NATURAL",
                "tipo_documento": "CC",
                "numero_documento": cc_number,
                "primer_nombre": "Juan",
                "primer_apellido": "Pérez",
                "direccion": "Calle 123",
                "ciudad": "Bogotá",
                "departamento": "Cundinamarca"
            }
            
            response = await async_client.post(
                "/api/v1/clientes/",
                json=cliente_data,
                headers=authenticated_headers
            )
            
            assert response.status_code == status.HTTP_201_CREATED
            data = response.json()
            assert data["numero_documento"] == cc_number

    @pytest.mark.integration
    @pytest.mark.colombian
    @pytest.mark.asyncio
    async def test_create_cliente_invalid_cc(
        self, 
        async_client: AsyncClient,
        authenticated_headers: dict
    ):
        """Test creating cliente with invalid Cédula de Ciudadanía"""
        invalid_cc_numbers = [
            "123",          # Too short
            "12345678901234",  # Too long
            "12345abc",     # Contains letters
            "",             # Empty
        ]
        
        for cc_number in invalid_cc_numbers:
            cliente_data = {
                "tipo_persona": "NATURAL",
                "tipo_documento": "CC",
                "numero_documento": cc_number,
                "primer_nombre": "Juan",
                "primer_apellido": "Pérez",
                "direccion": "Calle 123",
                "ciudad": "Bogotá",
                "departamento": "Cundinamarca"
            }
            
            response = await async_client.post(
                "/api/v1/clientes/",
                json=cliente_data,
                headers=authenticated_headers
            )
            
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.integration
    @pytest.mark.colombian
    @pytest.mark.asyncio
    async def test_create_cliente_valid_nit(
        self, 
        async_client: AsyncClient,
        authenticated_headers: dict
    ):
        """Test creating cliente with valid NIT"""
        valid_nit_numbers = [
            "900123456-1",
            "830000000-0",
            "900123456-9"
        ]
        
        for nit_number in valid_nit_numbers:
            cliente_data = {
                "tipo_persona": "JURIDICA",
                "tipo_documento": "NIT",
                "numero_documento": nit_number,
                "razon_social": "Empresa Test S.A.S.",
                "direccion": "Carrera 50",
                "ciudad": "Medellín",
                "departamento": "Antioquia"
            }
            
            response = await async_client.post(
                "/api/v1/clientes/",
                json=cliente_data,
                headers=authenticated_headers
            )
            
            assert response.status_code == status.HTTP_201_CREATED
            data = response.json()
            assert data["numero_documento"] == nit_number

    @pytest.mark.integration
    @pytest.mark.colombian
    @pytest.mark.asyncio
    async def test_create_cliente_invalid_nit(
        self, 
        async_client: AsyncClient,
        authenticated_headers: dict
    ):
        """Test creating cliente with invalid NIT"""
        invalid_nit_numbers = [
            "900123456",    # Missing verification digit
            "900123456-",   # Missing verification digit value
            "90012345-1",   # Too short
            "900123456-10", # Verification digit too long
            "90012345a-1",  # Contains letters
        ]
        
        for nit_number in invalid_nit_numbers:
            cliente_data = {
                "tipo_persona": "JURIDICA",
                "tipo_documento": "NIT",
                "numero_documento": nit_number,
                "razon_social": "Empresa Test S.A.S.",
                "direccion": "Carrera 50",
                "ciudad": "Medellín",
                "departamento": "Antioquia"
            }
            
            response = await async_client.post(
                "/api/v1/clientes/",
                json=cliente_data,
                headers=authenticated_headers
            )
            
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.integration
    @pytest.mark.colombian
    @pytest.mark.asyncio
    async def test_create_cliente_valid_ce(
        self, 
        async_client: AsyncClient,
        authenticated_headers: dict
    ):
        """Test creating cliente with valid Cédula de Extranjería"""
        valid_ce_numbers = [
            "123456789",
            "987654321012345"
        ]
        
        for ce_number in valid_ce_numbers:
            cliente_data = {
                "tipo_persona": "NATURAL",
                "tipo_documento": "CE",
                "numero_documento": ce_number,
                "primer_nombre": "John",
                "primer_apellido": "Smith",
                "direccion": "Calle 123",
                "ciudad": "Bogotá",
                "departamento": "Cundinamarca"
            }
            
            response = await async_client.post(
                "/api/v1/clientes/",
                json=cliente_data,
                headers=authenticated_headers
            )
            
            assert response.status_code == status.HTTP_201_CREATED

    @pytest.mark.integration
    @pytest.mark.colombian
    @pytest.mark.asyncio
    async def test_create_cliente_valid_pasaporte(
        self, 
        async_client: AsyncClient,
        authenticated_headers: dict
    ):
        """Test creating cliente with valid Pasaporte"""
        valid_passport_numbers = [
            "AB123456",
            "XY987654321",
            "PASSPORT123456789012"
        ]
        
        for passport_number in valid_passport_numbers:
            cliente_data = {
                "tipo_persona": "NATURAL",
                "tipo_documento": "PASAPORTE",
                "numero_documento": passport_number,
                "primer_nombre": "John",
                "primer_apellido": "Doe",
                "direccion": "Calle 123",
                "ciudad": "Bogotá",
                "departamento": "Cundinamarca"
            }
            
            response = await async_client.post(
                "/api/v1/clientes/",
                json=cliente_data,
                headers=authenticated_headers
            )
            
            assert response.status_code == status.HTTP_201_CREATED


class TestTaxValidation:
    """Test Colombian tax validation rules"""

    @pytest.mark.integration
    @pytest.mark.colombian
    @pytest.mark.asyncio
    async def test_create_producto_valid_iva_rates(
        self, 
        async_client: AsyncClient,
        authenticated_headers: dict
    ):
        """Test creating products with valid IVA rates"""
        valid_iva_rates = [0.0, 5.0, 19.0]
        
        for iva_rate in valid_iva_rates:
            producto_data = {
                "codigo": f"IVA{int(iva_rate)}_TEST",
                "nombre": f"Producto IVA {iva_rate}%",
                "tipo": "PRODUCTO",
                "precio_unitario": 100000.00,
                "unidad_medida": "UNI",
                "incluye_iva": True,
                "porcentaje_iva": iva_rate
            }
            
            response = await async_client.post(
                "/api/v1/productos/",
                json=producto_data,
                headers=authenticated_headers
            )
            
            assert response.status_code == status.HTTP_201_CREATED
            data = response.json()
            assert float(data["porcentaje_iva"]) == iva_rate

    @pytest.mark.integration
    @pytest.mark.colombian
    @pytest.mark.asyncio
    async def test_create_producto_invalid_iva_rates(
        self, 
        async_client: AsyncClient,
        authenticated_headers: dict
    ):
        """Test creating products with invalid IVA rates"""
        invalid_iva_rates = [-1.0, 20.0, 25.0, 100.0]
        
        for iva_rate in invalid_iva_rates:
            producto_data = {
                "codigo": f"INVALID_IVA{int(iva_rate)}",
                "nombre": f"Producto IVA Inválido {iva_rate}%",
                "tipo": "PRODUCTO",
                "precio_unitario": 100000.00,
                "unidad_medida": "UNI",
                "incluye_iva": True,
                "porcentaje_iva": iva_rate
            }
            
            response = await async_client.post(
                "/api/v1/productos/",
                json=producto_data,
                headers=authenticated_headers
            )
            
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.integration
    @pytest.mark.colombian
    @pytest.mark.asyncio
    async def test_create_producto_valid_inc_rates(
        self, 
        async_client: AsyncClient,
        authenticated_headers: dict
    ):
        """Test creating products with valid INC rates"""
        valid_inc_rates = [0.0, 8.0, 16.0]
        
        for inc_rate in valid_inc_rates:
            producto_data = {
                "codigo": f"INC{int(inc_rate)}_TEST",
                "nombre": f"Producto INC {inc_rate}%",
                "tipo": "PRODUCTO",
                "precio_unitario": 100000.00,
                "unidad_medida": "UNI",
                "incluye_inc": True,
                "porcentaje_inc": inc_rate
            }
            
            response = await async_client.post(
                "/api/v1/productos/",
                json=producto_data,
                headers=authenticated_headers
            )
            
            assert response.status_code == status.HTTP_201_CREATED
            data = response.json()
            assert float(data["porcentaje_inc"]) == inc_rate

    @pytest.mark.integration
    @pytest.mark.colombian
    @pytest.mark.asyncio
    async def test_create_producto_valid_ica_rates(
        self, 
        async_client: AsyncClient,
        authenticated_headers: dict
    ):
        """Test creating products with valid ICA rates"""
        valid_ica_rates = [0.0, 1.0, 2.0, 3.0]
        
        for ica_rate in valid_ica_rates:
            producto_data = {
                "codigo": f"ICA{int(ica_rate)}_TEST",
                "nombre": f"Producto ICA {ica_rate}%",
                "tipo": "PRODUCTO",
                "precio_unitario": 100000.00,
                "unidad_medida": "UNI",
                "incluye_ica": True,
                "porcentaje_ica": ica_rate
            }
            
            response = await async_client.post(
                "/api/v1/productos/",
                json=producto_data,
                headers=authenticated_headers
            )
            
            assert response.status_code == status.HTTP_201_CREATED
            data = response.json()
            assert float(data["porcentaje_ica"]) == ica_rate


class TestUNSPSCValidation:
    """Test UNSPSC code validation"""

    @pytest.mark.integration
    @pytest.mark.colombian
    @pytest.mark.asyncio
    async def test_create_producto_valid_unspsc(
        self, 
        async_client: AsyncClient,
        authenticated_headers: dict
    ):
        """Test creating products with valid UNSPSC codes"""
        valid_unspsc_codes = [
            "43211500",     # Office supplies
            "81161500",     # Consulting services
            "14111500",     # Food products
            "25101500",     # Chemical products
        ]
        
        for i, unspsc_code in enumerate(valid_unspsc_codes):
            producto_data = {
                "codigo": f"UNSPSC{i}",
                "nombre": f"Producto UNSPSC {i}",
                "codigo_unspsc": unspsc_code,
                "tipo": "PRODUCTO",
                "precio_unitario": 100000.00,
                "unidad_medida": "UNI"
            }
            
            response = await async_client.post(
                "/api/v1/productos/",
                json=producto_data,
                headers=authenticated_headers
            )
            
            assert response.status_code == status.HTTP_201_CREATED
            data = response.json()
            assert data["codigo_unspsc"] == unspsc_code

    @pytest.mark.integration
    @pytest.mark.colombian
    @pytest.mark.asyncio
    async def test_create_producto_invalid_unspsc(
        self, 
        async_client: AsyncClient,
        authenticated_headers: dict
    ):
        """Test creating products with invalid UNSPSC codes"""
        invalid_unspsc_codes = [
            "123",          # Too short
            "123456789",    # Too long
            "1234567a",     # Contains letters
            "",             # Empty
        ]
        
        for i, unspsc_code in enumerate(invalid_unspsc_codes):
            producto_data = {
                "codigo": f"INVALID_UNSPSC{i}",
                "nombre": f"Producto UNSPSC Inválido {i}",
                "codigo_unspsc": unspsc_code,
                "tipo": "PRODUCTO",
                "precio_unitario": 100000.00,
                "unidad_medida": "UNI"
            }
            
            response = await async_client.post(
                "/api/v1/productos/",
                json=producto_data,
                headers=authenticated_headers
            )
            
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestPersonTypeValidation:
    """Test persona type validation rules"""

    @pytest.mark.integration
    @pytest.mark.colombian
    @pytest.mark.asyncio
    async def test_create_cliente_natural_person_required_fields(
        self, 
        async_client: AsyncClient,
        authenticated_headers: dict
    ):
        """Test that natural persons require nombres and apellidos"""
        cliente_data = {
            "tipo_persona": "NATURAL",
            "tipo_documento": "CC",
            "numero_documento": "12345678",
            "primer_nombre": "Juan",
            "primer_apellido": "Pérez",
            "direccion": "Calle 123",
            "ciudad": "Bogotá",
            "departamento": "Cundinamarca"
        }
        
        response = await async_client.post(
            "/api/v1/clientes/",
            json=cliente_data,
            headers=authenticated_headers
        )
        
        assert response.status_code == status.HTTP_201_CREATED

    @pytest.mark.integration
    @pytest.mark.colombian
    @pytest.mark.asyncio
    async def test_create_cliente_natural_person_missing_nombre(
        self, 
        async_client: AsyncClient,
        authenticated_headers: dict
    ):
        """Test that natural persons cannot be created without primer_nombre"""
        cliente_data = {
            "tipo_persona": "NATURAL",
            "tipo_documento": "CC",
            "numero_documento": "12345678",
            # Missing primer_nombre
            "primer_apellido": "Pérez",
            "direccion": "Calle 123",
            "ciudad": "Bogotá",
            "departamento": "Cundinamarca"
        }
        
        response = await async_client.post(
            "/api/v1/clientes/",
            json=cliente_data,
            headers=authenticated_headers
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.integration
    @pytest.mark.colombian
    @pytest.mark.asyncio
    async def test_create_cliente_juridical_person_required_fields(
        self, 
        async_client: AsyncClient,
        authenticated_headers: dict
    ):
        """Test that juridical persons require razon_social"""
        cliente_data = {
            "tipo_persona": "JURIDICA",
            "tipo_documento": "NIT",
            "numero_documento": "900123456-1",
            "razon_social": "Empresa Test S.A.S.",
            "direccion": "Carrera 50",
            "ciudad": "Medellín",
            "departamento": "Antioquia"
        }
        
        response = await async_client.post(
            "/api/v1/clientes/",
            json=cliente_data,
            headers=authenticated_headers
        )
        
        assert response.status_code == status.HTTP_201_CREATED

    @pytest.mark.integration
    @pytest.mark.colombian
    @pytest.mark.asyncio
    async def test_create_cliente_juridical_person_missing_razon_social(
        self, 
        async_client: AsyncClient,
        authenticated_headers: dict
    ):
        """Test that juridical persons cannot be created without razon_social"""
        cliente_data = {
            "tipo_persona": "JURIDICA",
            "tipo_documento": "NIT",
            "numero_documento": "900123456-1",
            # Missing razon_social
            "direccion": "Carrera 50",
            "ciudad": "Medellín",
            "departamento": "Antioquia"
        }
        
        response = await async_client.post(
            "/api/v1/clientes/",
            json=cliente_data,
            headers=authenticated_headers
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestGeographicValidation:
    """Test Colombian geographic validation"""

    @pytest.mark.integration
    @pytest.mark.colombian
    @pytest.mark.asyncio
    async def test_create_cliente_valid_departments(
        self, 
        async_client: AsyncClient,
        authenticated_headers: dict
    ):
        """Test creating clients with valid Colombian departments"""
        valid_departments = [
            "Cundinamarca",
            "Antioquia",
            "Valle del Cauca",
            "Atlántico",
            "Bolívar",
            "Santander"
        ]
        
        for i, departamento in enumerate(valid_departments):
            cliente_data = {
                "tipo_persona": "NATURAL",
                "tipo_documento": "CC",
                "numero_documento": f"1234567{i}",
                "primer_nombre": "Juan",
                "primer_apellido": "Pérez",
                "direccion": "Calle 123",
                "ciudad": "Ciudad Test",
                "departamento": departamento
            }
            
            response = await async_client.post(
                "/api/v1/clientes/",
                json=cliente_data,
                headers=authenticated_headers
            )
            
            assert response.status_code == status.HTTP_201_CREATED
            data = response.json()
            assert data["departamento"] == departamento

    @pytest.mark.integration
    @pytest.mark.colombian
    @pytest.mark.asyncio
    async def test_create_cliente_valid_cities(
        self, 
        async_client: AsyncClient,
        authenticated_headers: dict
    ):
        """Test creating clients with valid Colombian cities"""
        valid_cities = [
            "Bogotá",
            "Medellín",
            "Cali",
            "Barranquilla",
            "Cartagena",
            "Bucaramanga"
        ]
        
        for i, ciudad in enumerate(valid_cities):
            cliente_data = {
                "tipo_persona": "NATURAL",
                "tipo_documento": "CC",
                "numero_documento": f"8765432{i}",
                "primer_nombre": "María",
                "primer_apellido": "García",
                "direccion": "Carrera 456",
                "ciudad": ciudad,
                "departamento": "Cundinamarca"
            }
            
            response = await async_client.post(
                "/api/v1/clientes/",
                json=cliente_data,
                headers=authenticated_headers
            )
            
            assert response.status_code == status.HTTP_201_CREATED
            data = response.json()
            assert data["ciudad"] == ciudad


class TestEmpresaValidation:
    """Test empresa validation rules"""

    @pytest.mark.integration
    @pytest.mark.colombian
    @pytest.mark.asyncio
    async def test_create_empresa_valid_regimen_fiscal(
        self, 
        async_client: AsyncClient,
        authenticated_headers: dict
    ):
        """Test creating empresa with valid regimen fiscal"""
        valid_regimenes = ["SIMPLIFICADO", "COMUN"]
        
        for i, regimen in enumerate(valid_regimenes):
            empresa_data = {
                "nit": f"90012345{i}-1",
                "razon_social": f"Empresa {regimen} S.A.S.",
                "direccion": "Calle Principal 123",
                "ciudad": "Bogotá",
                "departamento": "Cundinamarca",
                "email": f"contacto{i}@empresa.com",
                "telefono": "3001234567",
                "tipo_contribuyente": "PERSONA_JURIDICA",
                "regimen_fiscal": regimen
            }
            
            response = await async_client.post(
                "/api/v1/empresas/",
                json=empresa_data,
                headers=authenticated_headers
            )
            
            assert response.status_code == status.HTTP_201_CREATED
            data = response.json()
            assert data["regimen_fiscal"] == regimen

    @pytest.mark.integration
    @pytest.mark.colombian
    @pytest.mark.asyncio
    async def test_create_empresa_valid_tipo_contribuyente(
        self, 
        async_client: AsyncClient,
        authenticated_headers: dict
    ):
        """Test creating empresa with valid tipo contribuyente"""
        valid_tipos = ["PERSONA_NATURAL", "PERSONA_JURIDICA"]
        
        for i, tipo in enumerate(valid_tipos):
            empresa_data = {
                "nit": f"80012345{i}-1",
                "razon_social": f"Empresa {tipo} S.A.S.",
                "direccion": "Avenida Principal 456",
                "ciudad": "Medellín",
                "departamento": "Antioquia",
                "email": f"info{i}@empresa.com",
                "telefono": "3009876543",
                "tipo_contribuyente": tipo,
                "regimen_fiscal": "COMUN"
            }
            
            response = await async_client.post(
                "/api/v1/empresas/",
                json=empresa_data,
                headers=authenticated_headers
            )
            
            assert response.status_code == status.HTTP_201_CREATED
            data = response.json()
            assert data["tipo_contribuyente"] == tipo

    @pytest.mark.integration
    @pytest.mark.colombian
    @pytest.mark.asyncio
    async def test_create_empresa_valid_ambiente_dian(
        self, 
        async_client: AsyncClient,
        authenticated_headers: dict
    ):
        """Test creating empresa with valid ambiente DIAN"""
        valid_ambientes = ["PRUEBAS", "PRODUCCION"]
        
        for i, ambiente in enumerate(valid_ambientes):
            empresa_data = {
                "nit": f"70012345{i}-1",
                "razon_social": f"Empresa {ambiente} S.A.S.",
                "direccion": "Diagonal Principal 789",
                "ciudad": "Cali",
                "departamento": "Valle del Cauca",
                "email": f"admin{i}@empresa.com",
                "telefono": "3005551234",
                "tipo_contribuyente": "PERSONA_JURIDICA",
                "regimen_fiscal": "COMUN",
                "ambiente_dian": ambiente
            }
            
            response = await async_client.post(
                "/api/v1/empresas/",
                json=empresa_data,
                headers=authenticated_headers
            )
            
            assert response.status_code == status.HTTP_201_CREATED
            data = response.json()
            assert data["ambiente_dian"] == ambiente


class TestCurrencyValidation:
    """Test Colombian peso currency validation"""

    @pytest.mark.integration
    @pytest.mark.colombian
    @pytest.mark.asyncio
    async def test_create_producto_valid_peso_amounts(
        self, 
        async_client: AsyncClient,
        authenticated_headers: dict
    ):
        """Test creating products with valid peso amounts"""
        valid_amounts = [
            1.00,           # Minimum peso
            100.00,         # Small amount
            50000.00,       # Medium amount
            1000000.00,     # Large amount
            9999999.99      # Very large amount
        ]
        
        for i, amount in enumerate(valid_amounts):
            producto_data = {
                "codigo": f"PESO{i}",
                "nombre": f"Producto Peso {amount}",
                "tipo": "PRODUCTO",
                "precio_unitario": amount,
                "unidad_medida": "UNI"
            }
            
            response = await async_client.post(
                "/api/v1/productos/",
                json=producto_data,
                headers=authenticated_headers
            )
            
            assert response.status_code == status.HTTP_201_CREATED
            data = response.json()
            assert float(data["precio_unitario"]) == amount

    @pytest.mark.integration
    @pytest.mark.colombian
    @pytest.mark.asyncio
    async def test_create_producto_invalid_peso_amounts(
        self, 
        async_client: AsyncClient,
        authenticated_headers: dict
    ):
        """Test creating products with invalid peso amounts"""
        invalid_amounts = [
            0.00,           # Zero amount
            -100.00,        # Negative amount
            0.001           # Too many decimals
        ]
        
        for i, amount in enumerate(invalid_amounts):
            producto_data = {
                "codigo": f"INVALID_PESO{i}",
                "nombre": f"Producto Peso Inválido {amount}",
                "tipo": "PRODUCTO",
                "precio_unitario": amount,
                "unidad_medida": "UNI"
            }
            
            response = await async_client.post(
                "/api/v1/productos/",
                json=producto_data,
                headers=authenticated_headers
            )
            
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY