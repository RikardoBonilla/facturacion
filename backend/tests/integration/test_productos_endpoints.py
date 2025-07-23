"""
Integration tests for productos endpoints
"""

import pytest
from httpx import AsyncClient
from fastapi import status
from decimal import Decimal

from app.models import Producto, Usuario


class TestProductosEndpoints:
    """Test cases for productos endpoints"""

    @pytest.mark.integration
    @pytest.mark.crud
    @pytest.mark.asyncio
    async def test_create_producto_success(
        self, 
        async_client: AsyncClient,
        authenticated_headers: dict
    ):
        """Test creating a new product"""
        producto_data = {
            "codigo": "TEST001",
            "nombre": "Producto de Prueba",
            "descripcion": "Descripción del producto de prueba",
            "codigo_unspsc": "43211500",
            "tipo": "PRODUCTO",
            "precio_unitario": 50000.00,
            "unidad_medida": "UNI",
            "incluye_iva": True,
            "porcentaje_iva": 19.00,
            "maneja_inventario": True,
            "stock_actual": 100,
            "stock_minimo": 10
        }
        
        response = await async_client.post(
            "/api/v1/productos/",
            json=producto_data,
            headers=authenticated_headers
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        
        assert data["codigo"] == producto_data["codigo"]
        assert data["nombre"] == producto_data["nombre"]
        assert float(data["precio_unitario"]) == producto_data["precio_unitario"]
        assert data["tipo"] == producto_data["tipo"]
        assert "id" in data
        assert "empresa_id" in data

    @pytest.mark.integration
    @pytest.mark.crud
    @pytest.mark.asyncio
    async def test_create_producto_servicio(
        self, 
        async_client: AsyncClient,
        authenticated_headers: dict
    ):
        """Test creating a service product"""
        servicio_data = {
            "codigo": "SERV001",
            "nombre": "Servicio de Consultoría",
            "descripcion": "Servicios profesionales de consultoría",
            "codigo_unspsc": "81161500",
            "tipo": "SERVICIO",
            "precio_unitario": 200000.00,
            "unidad_medida": "HOR",
            "incluye_iva": True,
            "porcentaje_iva": 19.00,
            "incluye_inc": False,
            "maneja_inventario": False
        }
        
        response = await async_client.post(
            "/api/v1/productos/",
            json=servicio_data,
            headers=authenticated_headers
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        
        assert data["tipo"] == "SERVICIO"
        assert data["maneja_inventario"] is False
        assert data["stock_actual"] == 0

    @pytest.mark.integration
    @pytest.mark.crud
    @pytest.mark.asyncio
    async def test_create_producto_duplicate_codigo(
        self, 
        async_client: AsyncClient,
        authenticated_headers: dict,
        test_producto: Producto
    ):
        """Test creating product with duplicate code"""
        producto_data = {
            "codigo": test_producto.codigo,  # Duplicate code
            "nombre": "Otro Producto",
            "tipo": "PRODUCTO",
            "precio_unitario": 30000.00,
            "unidad_medida": "UNI"
        }
        
        response = await async_client.post(
            "/api/v1/productos/",
            json=producto_data,
            headers=authenticated_headers
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Ya existe un producto" in response.json()["detail"]

    @pytest.mark.integration
    @pytest.mark.crud
    @pytest.mark.asyncio
    async def test_list_productos_success(
        self, 
        async_client: AsyncClient,
        authenticated_headers: dict,
        test_producto: Producto
    ):
        """Test listing products"""
        response = await async_client.get(
            "/api/v1/productos/",
            headers=authenticated_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) >= 1
        
        # Check that test product is in the list
        product_codes = [producto["codigo"] for producto in data]
        assert test_producto.codigo in product_codes

    @pytest.mark.integration
    @pytest.mark.crud
    @pytest.mark.asyncio
    async def test_list_productos_filter_by_tipo(
        self, 
        async_client: AsyncClient,
        authenticated_headers: dict
    ):
        """Test listing products filtered by type"""
        
        # Create products of different types
        producto_data = {
            "codigo": "PROD_FILTER",
            "nombre": "Producto Filtro",
            "tipo": "PRODUCTO",
            "precio_unitario": 25000.00,
            "unidad_medida": "UNI"
        }
        
        await async_client.post(
            "/api/v1/productos/",
            json=producto_data,
            headers=authenticated_headers
        )
        
        servicio_data = {
            "codigo": "SERV_FILTER",
            "nombre": "Servicio Filtro",
            "tipo": "SERVICIO",
            "precio_unitario": 150000.00,
            "unidad_medida": "HOR"
        }
        
        await async_client.post(
            "/api/v1/productos/",
            json=servicio_data,
            headers=authenticated_headers
        )
        
        # Test filter by PRODUCTO
        response = await async_client.get(
            "/api/v1/productos/?tipo=PRODUCTO",
            headers=authenticated_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        for producto in data:
            assert producto["tipo"] == "PRODUCTO"

    @pytest.mark.integration
    @pytest.mark.crud
    @pytest.mark.asyncio
    async def test_get_producto_by_id(
        self, 
        async_client: AsyncClient,
        authenticated_headers: dict,
        test_producto: Producto
    ):
        """Test getting product by ID"""
        response = await async_client.get(
            f"/api/v1/productos/{test_producto.id}",
            headers=authenticated_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["id"] == test_producto.id
        assert data["codigo"] == test_producto.codigo
        assert data["nombre"] == test_producto.nombre

    @pytest.mark.integration
    @pytest.mark.crud
    @pytest.mark.asyncio
    async def test_get_producto_by_codigo(
        self, 
        async_client: AsyncClient,
        authenticated_headers: dict,
        test_producto: Producto
    ):
        """Test getting product by code"""
        response = await async_client.get(
            f"/api/v1/productos/codigo/{test_producto.codigo}",
            headers=authenticated_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["codigo"] == test_producto.codigo
        assert data["id"] == test_producto.id

    @pytest.mark.integration
    @pytest.mark.crud
    @pytest.mark.asyncio
    async def test_update_producto_success(
        self, 
        async_client: AsyncClient,
        authenticated_headers: dict,
        test_producto: Producto
    ):
        """Test updating product"""
        update_data = {
            "nombre": "Producto Actualizado",
            "precio_unitario": 75000.00,
            "descripcion": "Nueva descripción del producto",
            "porcentaje_iva": 19.00
        }
        
        response = await async_client.put(
            f"/api/v1/productos/{test_producto.id}",
            json=update_data,
            headers=authenticated_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["nombre"] == update_data["nombre"]
        assert float(data["precio_unitario"]) == update_data["precio_unitario"]
        assert data["descripcion"] == update_data["descripcion"]

    @pytest.mark.integration
    @pytest.mark.crud
    @pytest.mark.asyncio
    async def test_update_producto_codigo_duplicate(
        self, 
        async_client: AsyncClient,
        authenticated_headers: dict,
        test_producto: Producto
    ):
        """Test updating product with duplicate code"""
        
        # Create another product
        otro_producto_data = {
            "codigo": "OTRO001",
            "nombre": "Otro Producto",
            "tipo": "PRODUCTO",
            "precio_unitario": 30000.00,
            "unidad_medida": "UNI"
        }
        
        response = await async_client.post(
            "/api/v1/productos/",
            json=otro_producto_data,
            headers=authenticated_headers
        )
        
        otro_producto_id = response.json()["id"]
        
        # Try to update with existing code
        update_data = {
            "codigo": test_producto.codigo  # Duplicate code
        }
        
        response = await async_client.put(
            f"/api/v1/productos/{otro_producto_id}",
            json=update_data,
            headers=authenticated_headers
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.integration
    @pytest.mark.crud
    @pytest.mark.asyncio
    async def test_delete_producto_success(
        self, 
        async_client: AsyncClient,
        authenticated_headers: dict,
        test_producto: Producto
    ):
        """Test deleting product (soft delete)"""
        response = await async_client.delete(
            f"/api/v1/productos/{test_producto.id}",
            headers=authenticated_headers
        )
        
        assert response.status_code == status.HTTP_204_NO_CONTENT

    @pytest.mark.integration
    @pytest.mark.crud
    @pytest.mark.asyncio
    async def test_update_stock_producto(
        self, 
        async_client: AsyncClient,
        authenticated_headers: dict
    ):
        """Test updating product stock"""
        
        # Create product with inventory management
        producto_data = {
            "codigo": "STOCK001",
            "nombre": "Producto con Stock",
            "tipo": "PRODUCTO",
            "precio_unitario": 45000.00,
            "unidad_medida": "UNI",
            "maneja_inventario": True,
            "stock_actual": 50,
            "stock_minimo": 5
        }
        
        response = await async_client.post(
            "/api/v1/productos/",
            json=producto_data,
            headers=authenticated_headers
        )
        
        producto_id = response.json()["id"]
        
        # Update stock
        nuevo_stock = 75
        response = await async_client.patch(
            f"/api/v1/productos/{producto_id}/stock?nuevo_stock={nuevo_stock}",
            headers=authenticated_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["stock_actual"] == nuevo_stock

    @pytest.mark.integration
    @pytest.mark.crud
    @pytest.mark.asyncio
    async def test_update_stock_producto_no_inventario(
        self, 
        async_client: AsyncClient,
        authenticated_headers: dict,
        test_producto: Producto
    ):
        """Test updating stock of product that doesn't manage inventory"""
        
        nuevo_stock = 100
        response = await async_client.patch(
            f"/api/v1/productos/{test_producto.id}/stock?nuevo_stock={nuevo_stock}",
            headers=authenticated_headers
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestProductosValidation:
    """Test validation rules for productos"""

    @pytest.mark.integration
    @pytest.mark.crud
    @pytest.mark.asyncio
    async def test_create_producto_invalid_tipo(
        self, 
        async_client: AsyncClient,
        authenticated_headers: dict
    ):
        """Test creating product with invalid type"""
        producto_data = {
            "codigo": "INVALID001",
            "nombre": "Producto Inválido",
            "tipo": "INVALID_TYPE",  # Invalid
            "precio_unitario": 50000.00,
            "unidad_medida": "UNI"
        }
        
        response = await async_client.post(
            "/api/v1/productos/",
            json=producto_data,
            headers=authenticated_headers
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.integration
    @pytest.mark.crud
    @pytest.mark.asyncio
    async def test_create_producto_negative_price(
        self, 
        async_client: AsyncClient,
        authenticated_headers: dict
    ):
        """Test creating product with negative price"""
        producto_data = {
            "codigo": "NEG001",
            "nombre": "Producto Precio Negativo",
            "tipo": "PRODUCTO",
            "precio_unitario": -1000.00,  # Negative price
            "unidad_medida": "UNI"
        }
        
        response = await async_client.post(
            "/api/v1/productos/",
            json=producto_data,
            headers=authenticated_headers
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.integration
    @pytest.mark.crud
    @pytest.mark.asyncio
    async def test_create_producto_invalid_tax_percentage(
        self, 
        async_client: AsyncClient,
        authenticated_headers: dict
    ):
        """Test creating product with invalid tax percentage"""
        producto_data = {
            "codigo": "TAX001",
            "nombre": "Producto Impuesto Inválido",
            "tipo": "PRODUCTO",
            "precio_unitario": 50000.00,
            "unidad_medida": "UNI",
            "porcentaje_iva": 150.00  # Invalid percentage > 100
        }
        
        response = await async_client.post(
            "/api/v1/productos/",
            json=producto_data,
            headers=authenticated_headers
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.integration
    @pytest.mark.crud
    @pytest.mark.asyncio
    async def test_create_producto_missing_required_fields(
        self, 
        async_client: AsyncClient,
        authenticated_headers: dict
    ):
        """Test creating product with missing required fields"""
        producto_data = {
            "codigo": "MISSING001",
            # Missing nombre, tipo, precio_unitario, unidad_medida
        }
        
        response = await async_client.post(
            "/api/v1/productos/",
            json=producto_data,
            headers=authenticated_headers
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.integration
    @pytest.mark.crud
    @pytest.mark.asyncio
    async def test_create_producto_valid_tax_combinations(
        self, 
        async_client: AsyncClient,
        authenticated_headers: dict
    ):
        """Test creating products with different valid tax combinations"""
        
        tax_combinations = [
            {
                "codigo": "TAX_IVA",
                "incluye_iva": True,
                "porcentaje_iva": 19.00,
                "incluye_inc": False,
                "incluye_ica": False
            },
            {
                "codigo": "TAX_TODOS",
                "incluye_iva": True,
                "porcentaje_iva": 19.00,
                "incluye_inc": True,
                "porcentaje_inc": 8.00,
                "incluye_ica": True,
                "porcentaje_ica": 1.00
            },
            {
                "codigo": "TAX_NINGUNO",
                "incluye_iva": False,
                "incluye_inc": False,
                "incluye_ica": False
            }
        ]
        
        for i, tax_config in enumerate(tax_combinations):
            producto_data = {
                "nombre": f"Producto Impuestos {i}",
                "tipo": "PRODUCTO",
                "precio_unitario": 50000.00,
                "unidad_medida": "UNI",
                **tax_config
            }
            
            response = await async_client.post(
                "/api/v1/productos/",
                json=producto_data,
                headers=authenticated_headers
            )
            
            assert response.status_code == status.HTTP_201_CREATED
            data = response.json()
            
            assert data["incluye_iva"] == tax_config["incluye_iva"]
            if "porcentaje_iva" in tax_config:
                assert float(data["porcentaje_iva"]) == tax_config["porcentaje_iva"]


class TestProductosAuthorization:
    """Test authorization for productos endpoints"""

    @pytest.mark.integration
    @pytest.mark.auth
    @pytest.mark.asyncio
    async def test_productos_require_authentication(self, async_client: AsyncClient):
        """Test that all product endpoints require authentication"""
        endpoints = [
            ("GET", "/api/v1/productos/"),
            ("POST", "/api/v1/productos/"),
            ("GET", "/api/v1/productos/1"),
            ("PUT", "/api/v1/productos/1"),
            ("DELETE", "/api/v1/productos/1"),
            ("GET", "/api/v1/productos/codigo/TEST001"),
            ("PATCH", "/api/v1/productos/1/stock"),
        ]
        
        for method, url in endpoints:
            response = await async_client.request(method, url)
            assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.integration
    @pytest.mark.auth
    @pytest.mark.asyncio
    async def test_productos_empresa_isolation(
        self, 
        async_client: AsyncClient,
        authenticated_headers: dict
    ):
        """Test that products are isolated by empresa_id"""
        
        # Create product with authenticated user
        producto_data = {
            "codigo": "ISOLATION001",
            "nombre": "Producto Aislamiento",
            "tipo": "PRODUCTO",
            "precio_unitario": 50000.00,
            "unidad_medida": "UNI"
        }
        
        response = await async_client.post(
            "/api/v1/productos/",
            json=producto_data,
            headers=authenticated_headers
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        
        # Verify empresa_id is set correctly
        assert "empresa_id" in data
        assert data["empresa_id"] is not None