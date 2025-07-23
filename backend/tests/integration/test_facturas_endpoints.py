"""
Integration tests for facturas endpoints
"""

import pytest
from httpx import AsyncClient
from fastapi import status
from decimal import Decimal
from datetime import date, datetime

from app.models import Factura, FacturaDetalle, Cliente, Producto, Usuario


class TestFacturasEndpoints:
    """Test cases for facturas endpoints"""

    @pytest.mark.integration
    @pytest.mark.crud
    @pytest.mark.asyncio
    async def test_create_factura_success(
        self, 
        async_client: AsyncClient,
        authenticated_headers: dict,
        test_cliente: Cliente,
        test_producto: Producto
    ):
        """Test creating a new factura"""
        factura_data = {
            "cliente_id": test_cliente.id,
            "fecha_emision": "2024-01-15",
            "fecha_vencimiento": "2024-02-15",
            "observaciones": "Factura de prueba",
            "detalles": [
                {
                    "producto_id": test_producto.id,
                    "cantidad": 2.0,
                    "precio_unitario": 50000.00,
                    "descuento_porcentaje": 0.0
                }
            ]
        }
        
        response = await async_client.post(
            "/api/v1/facturas/",
            json=factura_data,
            headers=authenticated_headers
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        
        assert data["cliente_id"] == test_cliente.id
        assert data["estado_dian"] == "BORRADOR"
        assert "numero_completo" in data
        assert len(data["detalles"]) == 1
        assert "id" in data
        assert "empresa_id" in data

    @pytest.mark.integration
    @pytest.mark.crud
    @pytest.mark.asyncio
    async def test_create_factura_multiple_items(
        self, 
        async_client: AsyncClient,
        authenticated_headers: dict,
        test_cliente: Cliente,
        test_producto: Producto
    ):
        """Test creating factura with multiple items"""
        
        # Create another product
        producto2_data = {
            "codigo": "PROD002",
            "nombre": "Segundo Producto",
            "tipo": "PRODUCTO",
            "precio_unitario": 75000.00,
            "unidad_medida": "UNI"
        }
        
        response = await async_client.post(
            "/api/v1/productos/",
            json=producto2_data,
            headers=authenticated_headers
        )
        producto2_id = response.json()["id"]
        
        factura_data = {
            "cliente_id": test_cliente.id,
            "fecha_emision": "2024-01-15",
            "observaciones": "Factura con múltiples items",
            "detalles": [
                {
                    "producto_id": test_producto.id,
                    "cantidad": 1.0,
                    "precio_unitario": 50000.00,
                    "descuento_porcentaje": 0.0
                },
                {
                    "producto_id": producto2_id,
                    "cantidad": 2.0,
                    "precio_unitario": 75000.00,
                    "descuento_porcentaje": 10.0
                }
            ]
        }
        
        response = await async_client.post(
            "/api/v1/facturas/",
            json=factura_data,
            headers=authenticated_headers
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        
        assert len(data["detalles"]) == 2
        assert float(data["subtotal"]) > 0
        assert float(data["total_factura"]) > 0

    @pytest.mark.integration
    @pytest.mark.crud
    @pytest.mark.asyncio
    async def test_create_factura_with_discounts(
        self, 
        async_client: AsyncClient,
        authenticated_headers: dict,
        test_cliente: Cliente,
        test_producto: Producto
    ):
        """Test creating factura with discounts"""
        factura_data = {
            "cliente_id": test_cliente.id,
            "fecha_emision": "2024-01-15",
            "observaciones": "Factura con descuentos",
            "detalles": [
                {
                    "producto_id": test_producto.id,
                    "cantidad": 5.0,
                    "precio_unitario": 100000.00,
                    "descuento_porcentaje": 15.0
                }
            ]
        }
        
        response = await async_client.post(
            "/api/v1/facturas/",
            json=factura_data,
            headers=authenticated_headers
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        
        detalle = data["detalles"][0]
        assert float(detalle["descuento_porcentaje"]) == 15.0
        assert float(detalle["total_descuentos_linea"]) > 0
        assert float(data["total_descuentos"]) > 0

    @pytest.mark.integration
    @pytest.mark.crud
    @pytest.mark.asyncio
    async def test_create_factura_invalid_cliente(
        self, 
        async_client: AsyncClient,
        authenticated_headers: dict,
        test_producto: Producto
    ):
        """Test creating factura with invalid cliente_id"""
        factura_data = {
            "cliente_id": 99999,  # Non-existent cliente
            "fecha_emision": "2024-01-15",
            "detalles": [
                {
                    "producto_id": test_producto.id,
                    "cantidad": 1.0,
                    "precio_unitario": 50000.00
                }
            ]
        }
        
        response = await async_client.post(
            "/api/v1/facturas/",
            json=factura_data,
            headers=authenticated_headers
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.integration
    @pytest.mark.crud
    @pytest.mark.asyncio
    async def test_list_facturas_success(
        self, 
        async_client: AsyncClient,
        authenticated_headers: dict,
        test_factura: Factura
    ):
        """Test listing facturas"""
        response = await async_client.get(
            "/api/v1/facturas/",
            headers=authenticated_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) >= 1
        
        # Check that test factura is in the list
        factura_numbers = [factura["numero_completo"] for factura in data]
        assert test_factura.numero_completo in factura_numbers

    @pytest.mark.integration
    @pytest.mark.crud
    @pytest.mark.asyncio
    async def test_list_facturas_filter_by_estado(
        self, 
        async_client: AsyncClient,
        authenticated_headers: dict
    ):
        """Test listing facturas filtered by estado"""
        response = await async_client.get(
            "/api/v1/facturas/?estado_dian=BORRADOR",
            headers=authenticated_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        for factura in data:
            assert factura["estado_dian"] == "BORRADOR"

    @pytest.mark.integration
    @pytest.mark.crud
    @pytest.mark.asyncio
    async def test_list_facturas_filter_by_fecha(
        self, 
        async_client: AsyncClient,
        authenticated_headers: dict
    ):
        """Test listing facturas filtered by fecha range"""
        fecha_inicio = "2024-01-01"
        fecha_fin = "2024-12-31"
        
        response = await async_client.get(
            f"/api/v1/facturas/?fecha_inicio={fecha_inicio}&fecha_fin={fecha_fin}",
            headers=authenticated_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        for factura in data:
            fecha_emision = datetime.fromisoformat(factura["fecha_emision"].replace("Z", "+00:00")).date()
            assert date.fromisoformat(fecha_inicio) <= fecha_emision <= date.fromisoformat(fecha_fin)

    @pytest.mark.integration
    @pytest.mark.crud
    @pytest.mark.asyncio
    async def test_get_factura_by_id(
        self, 
        async_client: AsyncClient,
        authenticated_headers: dict,
        test_factura: Factura
    ):
        """Test getting factura by ID"""
        response = await async_client.get(
            f"/api/v1/facturas/{test_factura.id}",
            headers=authenticated_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["id"] == test_factura.id
        assert data["numero_completo"] == test_factura.numero_completo
        assert "detalles" in data
        assert "cliente" in data

    @pytest.mark.integration
    @pytest.mark.crud
    @pytest.mark.asyncio
    async def test_get_factura_by_numero(
        self, 
        async_client: AsyncClient,
        authenticated_headers: dict,
        test_factura: Factura
    ):
        """Test getting factura by numero_completo"""
        response = await async_client.get(
            f"/api/v1/facturas/numero/{test_factura.numero_completo}",
            headers=authenticated_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["numero_completo"] == test_factura.numero_completo
        assert data["id"] == test_factura.id

    @pytest.mark.integration
    @pytest.mark.crud
    @pytest.mark.asyncio
    async def test_update_factura_success(
        self, 
        async_client: AsyncClient,
        authenticated_headers: dict,
        test_factura: Factura
    ):
        """Test updating factura"""
        update_data = {
            "observaciones": "Observaciones actualizadas",
            "fecha_vencimiento": "2024-03-15"
        }
        
        response = await async_client.put(
            f"/api/v1/facturas/{test_factura.id}",
            json=update_data,
            headers=authenticated_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["observaciones"] == update_data["observaciones"]
        assert data["fecha_vencimiento"] == update_data["fecha_vencimiento"]

    @pytest.mark.integration
    @pytest.mark.crud
    @pytest.mark.asyncio
    async def test_update_factura_estado_emitida(
        self, 
        async_client: AsyncClient,
        authenticated_headers: dict,
        test_factura: Factura
    ):
        """Test updating factura estado to EMITIDA"""
        response = await async_client.patch(
            f"/api/v1/facturas/{test_factura.id}/estado?nuevo_estado=EMITIDA",
            headers=authenticated_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["estado_dian"] == "EMITIDA"
        # Should generate CUFE when emitted
        assert "cufe" in data

    @pytest.mark.integration
    @pytest.mark.crud
    @pytest.mark.asyncio
    async def test_update_factura_estado_invalid_transition(
        self, 
        async_client: AsyncClient,
        authenticated_headers: dict,
        test_factura: Factura
    ):
        """Test invalid estado transition"""
        # Try to go directly from BORRADOR to ACEPTADA (should fail)
        response = await async_client.patch(
            f"/api/v1/facturas/{test_factura.id}/estado?nuevo_estado=ACEPTADA",
            headers=authenticated_headers
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.integration
    @pytest.mark.crud
    @pytest.mark.asyncio
    async def test_delete_factura_borrador(
        self, 
        async_client: AsyncClient,
        authenticated_headers: dict,
        test_cliente: Cliente,
        test_producto: Producto
    ):
        """Test deleting factura in BORRADOR state"""
        
        # Create a factura to delete
        factura_data = {
            "cliente_id": test_cliente.id,
            "fecha_emision": "2024-01-15",
            "detalles": [
                {
                    "producto_id": test_producto.id,
                    "cantidad": 1.0,
                    "precio_unitario": 50000.00
                }
            ]
        }
        
        response = await async_client.post(
            "/api/v1/facturas/",
            json=factura_data,
            headers=authenticated_headers
        )
        
        factura_id = response.json()["id"]
        
        # Delete the factura
        response = await async_client.delete(
            f"/api/v1/facturas/{factura_id}",
            headers=authenticated_headers
        )
        
        assert response.status_code == status.HTTP_204_NO_CONTENT

    @pytest.mark.integration
    @pytest.mark.crud
    @pytest.mark.asyncio
    async def test_delete_factura_emitida_forbidden(
        self, 
        async_client: AsyncClient,
        authenticated_headers: dict,
        test_cliente: Cliente,
        test_producto: Producto
    ):
        """Test that emitted facturas cannot be deleted"""
        
        # Create and emit a factura
        factura_data = {
            "cliente_id": test_cliente.id,
            "fecha_emision": "2024-01-15",
            "detalles": [
                {
                    "producto_id": test_producto.id,
                    "cantidad": 1.0,
                    "precio_unitario": 50000.00
                }
            ]
        }
        
        response = await async_client.post(
            "/api/v1/facturas/",
            json=factura_data,
            headers=authenticated_headers
        )
        
        factura_id = response.json()["id"]
        
        # Emit the factura
        await async_client.patch(
            f"/api/v1/facturas/{factura_id}/estado?nuevo_estado=EMITIDA",
            headers=authenticated_headers
        )
        
        # Try to delete (should fail)
        response = await async_client.delete(
            f"/api/v1/facturas/{factura_id}",
            headers=authenticated_headers
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.integration
    @pytest.mark.crud
    @pytest.mark.asyncio
    async def test_generate_pdf_factura(
        self, 
        async_client: AsyncClient,
        authenticated_headers: dict,
        test_factura: Factura
    ):
        """Test generating PDF for factura"""
        
        # First emit the factura
        await async_client.patch(
            f"/api/v1/facturas/{test_factura.id}/estado?nuevo_estado=EMITIDA",
            headers=authenticated_headers
        )
        
        response = await async_client.get(
            f"/api/v1/facturas/{test_factura.id}/pdf",
            headers=authenticated_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert response.headers["content-type"] == "application/pdf"

    @pytest.mark.integration
    @pytest.mark.crud
    @pytest.mark.asyncio
    async def test_generate_xml_factura(
        self, 
        async_client: AsyncClient,
        authenticated_headers: dict,
        test_factura: Factura
    ):
        """Test generating XML for factura"""
        
        # First emit the factura
        await async_client.patch(
            f"/api/v1/facturas/{test_factura.id}/estado?nuevo_estado=EMITIDA",
            headers=authenticated_headers
        )
        
        response = await async_client.get(
            f"/api/v1/facturas/{test_factura.id}/xml",
            headers=authenticated_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert response.headers["content-type"] == "application/xml"


class TestFacturasValidation:
    """Test validation rules for facturas"""

    @pytest.mark.integration
    @pytest.mark.crud
    @pytest.mark.asyncio
    async def test_create_factura_empty_detalles(
        self, 
        async_client: AsyncClient,
        authenticated_headers: dict,
        test_cliente: Cliente
    ):
        """Test creating factura with empty detalles"""
        factura_data = {
            "cliente_id": test_cliente.id,
            "fecha_emision": "2024-01-15",
            "detalles": []  # Empty detalles
        }
        
        response = await async_client.post(
            "/api/v1/facturas/",
            json=factura_data,
            headers=authenticated_headers
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.integration
    @pytest.mark.crud
    @pytest.mark.asyncio
    async def test_create_factura_invalid_fecha(
        self, 
        async_client: AsyncClient,
        authenticated_headers: dict,
        test_cliente: Cliente,
        test_producto: Producto
    ):
        """Test creating factura with invalid fecha_emision"""
        factura_data = {
            "cliente_id": test_cliente.id,
            "fecha_emision": "invalid-date",
            "detalles": [
                {
                    "producto_id": test_producto.id,
                    "cantidad": 1.0,
                    "precio_unitario": 50000.00
                }
            ]
        }
        
        response = await async_client.post(
            "/api/v1/facturas/",
            json=factura_data,
            headers=authenticated_headers
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.integration
    @pytest.mark.crud
    @pytest.mark.asyncio
    async def test_create_factura_negative_cantidad(
        self, 
        async_client: AsyncClient,
        authenticated_headers: dict,
        test_cliente: Cliente,
        test_producto: Producto
    ):
        """Test creating factura with negative cantidad"""
        factura_data = {
            "cliente_id": test_cliente.id,
            "fecha_emision": "2024-01-15",
            "detalles": [
                {
                    "producto_id": test_producto.id,
                    "cantidad": -1.0,  # Negative quantity
                    "precio_unitario": 50000.00
                }
            ]
        }
        
        response = await async_client.post(
            "/api/v1/facturas/",
            json=factura_data,
            headers=authenticated_headers
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.integration
    @pytest.mark.crud
    @pytest.mark.asyncio
    async def test_create_factura_invalid_descuento(
        self, 
        async_client: AsyncClient,
        authenticated_headers: dict,
        test_cliente: Cliente,
        test_producto: Producto
    ):
        """Test creating factura with invalid descuento percentage"""
        factura_data = {
            "cliente_id": test_cliente.id,
            "fecha_emision": "2024-01-15",
            "detalles": [
                {
                    "producto_id": test_producto.id,
                    "cantidad": 1.0,
                    "precio_unitario": 50000.00,
                    "descuento_porcentaje": 150.0  # Invalid percentage > 100
                }
            ]
        }
        
        response = await async_client.post(
            "/api/v1/facturas/",
            json=factura_data,
            headers=authenticated_headers
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestFacturasAuthorization:
    """Test authorization for facturas endpoints"""

    @pytest.mark.integration
    @pytest.mark.auth
    @pytest.mark.asyncio
    async def test_facturas_require_authentication(self, async_client: AsyncClient):
        """Test that all factura endpoints require authentication"""
        endpoints = [
            ("GET", "/api/v1/facturas/"),
            ("POST", "/api/v1/facturas/"),
            ("GET", "/api/v1/facturas/1"),
            ("PUT", "/api/v1/facturas/1"),
            ("DELETE", "/api/v1/facturas/1"),
            ("GET", "/api/v1/facturas/numero/FT001"),
            ("PATCH", "/api/v1/facturas/1/estado"),
            ("GET", "/api/v1/facturas/1/pdf"),
            ("GET", "/api/v1/facturas/1/xml"),
        ]
        
        for method, url in endpoints:
            response = await async_client.request(method, url)
            assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.integration
    @pytest.mark.auth
    @pytest.mark.asyncio
    async def test_facturas_empresa_isolation(
        self, 
        async_client: AsyncClient,
        authenticated_headers: dict,
        test_cliente: Cliente,
        test_producto: Producto
    ):
        """Test that facturas are isolated by empresa_id"""
        
        # Create factura with authenticated user
        factura_data = {
            "cliente_id": test_cliente.id,
            "fecha_emision": "2024-01-15",
            "detalles": [
                {
                    "producto_id": test_producto.id,
                    "cantidad": 1.0,
                    "precio_unitario": 50000.00
                }
            ]
        }
        
        response = await async_client.post(
            "/api/v1/facturas/",
            json=factura_data,
            headers=authenticated_headers
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        
        # Verify empresa_id is set correctly
        assert "empresa_id" in data
        assert data["empresa_id"] is not None


class TestFacturasBusinessLogic:
    """Test business logic for facturas"""

    @pytest.mark.integration
    @pytest.mark.crud
    @pytest.mark.asyncio
    async def test_factura_calculation_accuracy(
        self, 
        async_client: AsyncClient,
        authenticated_headers: dict,
        test_cliente: Cliente,
        test_producto: Producto
    ):
        """Test that factura calculations are accurate"""
        
        # Known values for testing
        cantidad = Decimal("3.0")
        precio_unitario = Decimal("100000.00")
        descuento_porcentaje = Decimal("10.0")
        
        factura_data = {
            "cliente_id": test_cliente.id,
            "fecha_emision": "2024-01-15",
            "detalles": [
                {
                    "producto_id": test_producto.id,
                    "cantidad": float(cantidad),
                    "precio_unitario": float(precio_unitario),
                    "descuento_porcentaje": float(descuento_porcentaje)
                }
            ]
        }
        
        response = await async_client.post(
            "/api/v1/facturas/",
            json=factura_data,
            headers=authenticated_headers
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        
        # Calculate expected values
        subtotal_linea = cantidad * precio_unitario
        descuento_linea = subtotal_linea * (descuento_porcentaje / 100)
        base_iva = subtotal_linea - descuento_linea
        iva_linea = base_iva * Decimal("0.19")  # 19% IVA
        total_linea = base_iva + iva_linea
        
        detalle = data["detalles"][0]
        assert Decimal(str(detalle["subtotal_linea"])) == subtotal_linea
        assert Decimal(str(detalle["total_descuentos_linea"])) == descuento_linea
        assert Decimal(str(detalle["total_linea"])) == total_linea

    @pytest.mark.integration
    @pytest.mark.crud
    @pytest.mark.asyncio
    async def test_factura_numero_generation(
        self, 
        async_client: AsyncClient,
        authenticated_headers: dict,
        test_cliente: Cliente,
        test_producto: Producto
    ):
        """Test that factura numbers are generated consecutively"""
        
        factura_data = {
            "cliente_id": test_cliente.id,
            "fecha_emision": "2024-01-15",
            "detalles": [
                {
                    "producto_id": test_producto.id,
                    "cantidad": 1.0,
                    "precio_unitario": 50000.00
                }
            ]
        }
        
        # Create first factura
        response1 = await async_client.post(
            "/api/v1/facturas/",
            json=factura_data,
            headers=authenticated_headers
        )
        
        # Create second factura
        response2 = await async_client.post(
            "/api/v1/facturas/",
            json=factura_data,
            headers=authenticated_headers
        )
        
        assert response1.status_code == status.HTTP_201_CREATED
        assert response2.status_code == status.HTTP_201_CREATED
        
        data1 = response1.json()
        data2 = response2.json()
        
        # Numbers should be consecutive
        assert data2["numero"] == data1["numero"] + 1
        assert data1["numero_completo"] != data2["numero_completo"]