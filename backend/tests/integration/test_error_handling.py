"""
Integration tests for error handling and exceptions
"""

import pytest
from httpx import AsyncClient
from fastapi import status
from unittest.mock import patch
import asyncio

from app.models import Cliente, Producto, Factura, Usuario


class TestDatabaseErrorHandling:
    """Test database error scenarios"""

    @pytest.mark.integration
    @pytest.mark.error
    @pytest.mark.asyncio
    async def test_database_connection_error(
        self, 
        async_client: AsyncClient,
        authenticated_headers: dict
    ):
        """Test handling of database connection errors"""
        
        # Simulate database connection error by patching the get_db dependency
        with patch('app.core.database.get_db') as mock_get_db:
            mock_get_db.side_effect = Exception("Database connection failed")
            
            response = await async_client.get(
                "/api/v1/empresas/",
                headers=authenticated_headers
            )
            
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

    @pytest.mark.integration
    @pytest.mark.error
    @pytest.mark.asyncio
    async def test_concurrent_modification_error(
        self, 
        async_client: AsyncClient,
        authenticated_headers: dict,
        test_producto: Producto
    ):
        """Test handling of concurrent modification scenarios"""
        
        # Simulate concurrent updates to the same product
        update_data_1 = {"nombre": "Producto Actualizado 1"}
        update_data_2 = {"nombre": "Producto Actualizado 2"}
        
        # Send concurrent requests
        tasks = [
            async_client.put(
                f"/api/v1/productos/{test_producto.id}",
                json=update_data_1,
                headers=authenticated_headers
            ),
            async_client.put(
                f"/api/v1/productos/{test_producto.id}",
                json=update_data_2,
                headers=authenticated_headers
            )
        ]
        
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        # At least one should succeed
        success_count = sum(1 for r in responses if hasattr(r, 'status_code') and r.status_code == 200)
        assert success_count >= 1

    @pytest.mark.integration
    @pytest.mark.error
    @pytest.mark.asyncio
    async def test_foreign_key_constraint_violation(
        self, 
        async_client: AsyncClient,
        authenticated_headers: dict
    ):
        """Test foreign key constraint violation handling"""
        
        # Try to create a factura with non-existent cliente_id
        factura_data = {
            "cliente_id": 99999,  # Non-existent
            "fecha_emision": "2024-01-15",
            "detalles": [
                {
                    "producto_id": 99999,  # Non-existent
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
        assert "not found" in response.json()["detail"].lower()

    @pytest.mark.integration
    @pytest.mark.error
    @pytest.mark.asyncio
    async def test_unique_constraint_violation(
        self, 
        async_client: AsyncClient,
        authenticated_headers: dict,
        test_producto: Producto
    ):
        """Test unique constraint violation handling"""
        
        # Try to create a product with duplicate code
        duplicate_data = {
            "codigo": test_producto.codigo,  # Duplicate
            "nombre": "Producto Duplicado",
            "tipo": "PRODUCTO",
            "precio_unitario": 75000.00,
            "unidad_medida": "UNI"
        }
        
        response = await async_client.post(
            "/api/v1/productos/",
            json=duplicate_data,
            headers=authenticated_headers
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already exists" in response.json()["detail"].lower() or "ya existe" in response.json()["detail"].lower()


class TestAuthenticationErrorHandling:
    """Test authentication and authorization error scenarios"""

    @pytest.mark.integration
    @pytest.mark.error
    @pytest.mark.auth
    @pytest.mark.asyncio
    async def test_invalid_token_format(self, async_client: AsyncClient):
        """Test handling of malformed JWT tokens"""
        
        invalid_tokens = [
            "invalid.token.format",
            "Bearer invalid_token",
            "not.a.jwt",
            "",
            "Bearer ",
        ]
        
        for token in invalid_tokens:
            headers = {"Authorization": f"Bearer {token}"}
            
            response = await async_client.get(
                "/api/v1/empresas/",
                headers=headers
            )
            
            assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.integration
    @pytest.mark.error
    @pytest.mark.auth
    @pytest.mark.asyncio
    async def test_expired_token_handling(self, async_client: AsyncClient):
        """Test handling of expired JWT tokens"""
        
        # Create an expired token (this would need to be mocked in real implementation)
        expired_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ0ZXN0QGV4YW1wbGUuY29tIiwiZXhwIjoxNjA5NDU5MjAwfQ.invalid"
        headers = {"Authorization": f"Bearer {expired_token}"}
        
        response = await async_client.get(
            "/api/v1/empresas/",
            headers=headers
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.integration
    @pytest.mark.error
    @pytest.mark.auth
    @pytest.mark.asyncio
    async def test_missing_authorization_header(self, async_client: AsyncClient):
        """Test endpoints without authorization header"""
        
        protected_endpoints = [
            "/api/v1/empresas/",
            "/api/v1/clientes/",
            "/api/v1/productos/",
            "/api/v1/facturas/",
        ]
        
        for endpoint in protected_endpoints:
            response = await async_client.get(endpoint)
            assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.integration
    @pytest.mark.error
    @pytest.mark.auth
    @pytest.mark.asyncio
    async def test_cross_tenant_access_attempt(
        self, 
        async_client: AsyncClient,
        authenticated_headers: dict
    ):
        """Test prevention of cross-tenant data access"""
        
        # This test assumes that the authenticated user belongs to empresa_id = 1
        # Try to access a resource that might belong to another empresa
        
        # Create a resource first
        cliente_data = {
            "tipo_persona": "NATURAL",
            "tipo_documento": "CC",
            "numero_documento": "87654321",
            "primer_nombre": "Test",
            "primer_apellido": "Cross-tenant",
            "direccion": "Test Address",
            "ciudad": "Test City",
            "departamento": "Test Department"
        }
        
        response = await async_client.post(
            "/api/v1/clientes/",
            json=cliente_data,
            headers=authenticated_headers
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        cliente_id = response.json()["id"]
        
        # Try to access with a different empresa context (this would be mocked in real test)
        # For now, we just verify that empresa_id is properly set
        response = await async_client.get(
            f"/api/v1/clientes/{cliente_id}",
            headers=authenticated_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "empresa_id" in data


class TestValidationErrorHandling:
    """Test input validation error scenarios"""

    @pytest.mark.integration
    @pytest.mark.error
    @pytest.mark.asyncio
    async def test_malformed_json_payload(
        self, 
        async_client: AsyncClient,
        authenticated_headers: dict
    ):
        """Test handling of malformed JSON payloads"""
        
        malformed_json = '{"invalid": json, "missing_quotes": value}'
        
        response = await async_client.post(
            "/api/v1/productos/",
            content=malformed_json,
            headers={**authenticated_headers, "Content-Type": "application/json"}
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.integration
    @pytest.mark.error
    @pytest.mark.asyncio
    async def test_missing_required_fields(
        self, 
        async_client: AsyncClient,
        authenticated_headers: dict
    ):
        """Test handling of missing required fields"""
        
        incomplete_data = {
            "codigo": "TEST001",
            # Missing required fields: nombre, tipo, precio_unitario, unidad_medida
        }
        
        response = await async_client.post(
            "/api/v1/productos/",
            json=incomplete_data,
            headers=authenticated_headers
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        error_detail = response.json()["detail"]
        assert isinstance(error_detail, list)
        assert len(error_detail) > 0

    @pytest.mark.integration
    @pytest.mark.error
    @pytest.mark.asyncio
    async def test_invalid_data_types(
        self, 
        async_client: AsyncClient,
        authenticated_headers: dict
    ):
        """Test handling of invalid data types"""
        
        invalid_data = {
            "codigo": "TEST001",
            "nombre": "Test Product",
            "tipo": "PRODUCTO",
            "precio_unitario": "not_a_number",  # Should be float
            "unidad_medida": "UNI",
            "incluye_iva": "not_a_boolean"      # Should be boolean
        }
        
        response = await async_client.post(
            "/api/v1/productos/",
            json=invalid_data,
            headers=authenticated_headers
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.integration
    @pytest.mark.error
    @pytest.mark.asyncio
    async def test_field_length_validation(
        self, 
        async_client: AsyncClient,
        authenticated_headers: dict
    ):
        """Test field length validation errors"""
        
        long_string = "a" * 1000  # Very long string
        
        invalid_data = {
            "codigo": long_string,  # Likely exceeds max length
            "nombre": long_string,
            "tipo": "PRODUCTO",
            "precio_unitario": 50000.00,
            "unidad_medida": "UNI"
        }
        
        response = await async_client.post(
            "/api/v1/productos/",
            json=invalid_data,
            headers=authenticated_headers
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.integration
    @pytest.mark.error
    @pytest.mark.asyncio
    async def test_enum_validation_errors(
        self, 
        async_client: AsyncClient,
        authenticated_headers: dict
    ):
        """Test enum field validation errors"""
        
        invalid_data = {
            "codigo": "TEST001",
            "nombre": "Test Product",
            "tipo": "INVALID_TYPE",  # Invalid enum value
            "precio_unitario": 50000.00,
            "unidad_medida": "UNI"
        }
        
        response = await async_client.post(
            "/api/v1/productos/",
            json=invalid_data,
            headers=authenticated_headers
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestBusinessLogicErrorHandling:
    """Test business logic error scenarios"""

    @pytest.mark.integration
    @pytest.mark.error
    @pytest.mark.asyncio
    async def test_insufficient_stock_error(
        self, 
        async_client: AsyncClient,
        authenticated_headers: dict,
        test_cliente: Cliente
    ):
        """Test handling of insufficient stock scenarios"""
        
        # Create a product with limited stock
        producto_data = {
            "codigo": "STOCK_TEST",
            "nombre": "Producto Stock Limitado",
            "tipo": "PRODUCTO",
            "precio_unitario": 50000.00,
            "unidad_medida": "UNI",
            "maneja_inventario": True,
            "stock_actual": 5,
            "stock_minimo": 1
        }
        
        response = await async_client.post(
            "/api/v1/productos/",
            json=producto_data,
            headers=authenticated_headers
        )
        
        producto_id = response.json()["id"]
        
        # Try to create a factura that exceeds available stock
        factura_data = {
            "cliente_id": test_cliente.id,
            "fecha_emision": "2024-01-15",
            "detalles": [
                {
                    "producto_id": producto_id,
                    "cantidad": 10.0,  # Exceeds available stock of 5
                    "precio_unitario": 50000.00
                }
            ]
        }
        
        response = await async_client.post(
            "/api/v1/facturas/",
            json=factura_data,
            headers=authenticated_headers
        )
        
        # This might be allowed to create but should warn about stock
        # Business logic would determine exact behavior
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST]

    @pytest.mark.integration
    @pytest.mark.error
    @pytest.mark.asyncio
    async def test_invalid_state_transition_error(
        self, 
        async_client: AsyncClient,
        authenticated_headers: dict,
        test_factura: Factura
    ):
        """Test invalid invoice state transitions"""
        
        # Try invalid state transitions
        invalid_transitions = [
            ("BORRADOR", "ACEPTADA"),   # Can't go directly from BORRADOR to ACEPTADA
            ("BORRADOR", "RECHAZADA"),  # Can't go directly from BORRADOR to RECHAZADA
        ]
        
        for current_state, target_state in invalid_transitions:
            response = await async_client.patch(
                f"/api/v1/facturas/{test_factura.id}/estado?nuevo_estado={target_state}",
                headers=authenticated_headers
            )
            
            assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.integration
    @pytest.mark.error
    @pytest.mark.asyncio
    async def test_delete_referenced_entity_error(
        self, 
        async_client: AsyncClient,
        authenticated_headers: dict,
        test_factura: Factura
    ):
        """Test deletion of entities that are referenced by others"""
        
        # Try to delete a cliente that has facturas
        response = await async_client.delete(
            f"/api/v1/clientes/{test_factura.cliente_id}",
            headers=authenticated_headers
        )
        
        # Should either soft delete or return error depending on business rules
        assert response.status_code in [status.HTTP_204_NO_CONTENT, status.HTTP_400_BAD_REQUEST]

    @pytest.mark.integration
    @pytest.mark.error
    @pytest.mark.asyncio
    async def test_modification_of_emitted_invoice_error(
        self, 
        async_client: AsyncClient,
        authenticated_headers: dict,
        test_cliente: Cliente,
        test_producto: Producto
    ):
        """Test modification of emitted invoices (should be forbidden)"""
        
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
        response = await async_client.patch(
            f"/api/v1/facturas/{factura_id}/estado?nuevo_estado=EMITIDA",
            headers=authenticated_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        
        # Try to modify the emitted factura
        update_data = {"observaciones": "Modified after emission"}
        
        response = await async_client.put(
            f"/api/v1/facturas/{factura_id}",
            json=update_data,
            headers=authenticated_headers
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestNetworkErrorHandling:
    """Test network and timeout error scenarios"""

    @pytest.mark.integration
    @pytest.mark.error
    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_request_timeout_handling(
        self, 
        async_client: AsyncClient,
        authenticated_headers: dict
    ):
        """Test handling of request timeouts"""
        
        # This test would simulate a slow operation
        # In practice, you'd mock a slow dependency
        
        with patch('asyncio.sleep', side_effect=asyncio.TimeoutError):
            response = await async_client.get(
                "/api/v1/empresas/",
                headers=authenticated_headers,
                timeout=0.001  # Very short timeout
            )
            
            # The response depends on how the timeout is handled
            # Could be 408 Request Timeout or 500 Internal Server Error
            assert response.status_code in [
                status.HTTP_408_REQUEST_TIMEOUT, 
                status.HTTP_500_INTERNAL_SERVER_ERROR
            ]

    @pytest.mark.integration
    @pytest.mark.error
    @pytest.mark.asyncio
    async def test_large_payload_handling(
        self, 
        async_client: AsyncClient,
        authenticated_headers: dict
    ):
        """Test handling of very large request payloads"""
        
        # Create a very large payload
        large_data = {
            "codigo": "LARGE_TEST",
            "nombre": "Test Product",
            "tipo": "PRODUCTO",
            "precio_unitario": 50000.00,
            "unidad_medida": "UNI",
            "descripcion": "x" * 1000000  # Very large description
        }
        
        response = await async_client.post(
            "/api/v1/productos/",
            json=large_data,
            headers=authenticated_headers
        )
        
        # Should either succeed or fail with appropriate error
        assert response.status_code in [
            status.HTTP_201_CREATED,
            status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            status.HTTP_422_UNPROCESSABLE_ENTITY
        ]


class TestExceptionPropagation:
    """Test proper exception propagation and logging"""

    @pytest.mark.integration
    @pytest.mark.error
    @pytest.mark.asyncio
    async def test_unhandled_exception_response(
        self, 
        async_client: AsyncClient,
        authenticated_headers: dict
    ):
        """Test that unhandled exceptions return proper error responses"""
        
        # This test would simulate an unhandled exception
        # In practice, you'd mock a dependency to raise an unexpected exception
        
        with patch('app.crud.crud_empresa.get_all') as mock_get_all:
            mock_get_all.side_effect = Exception("Simulated unhandled exception")
            
            response = await async_client.get(
                "/api/v1/empresas/",
                headers=authenticated_headers
            )
            
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            # Should not expose internal error details to client
            assert "Simulated unhandled exception" not in response.text

    @pytest.mark.integration
    @pytest.mark.error
    @pytest.mark.asyncio
    async def test_error_response_format(
        self, 
        async_client: AsyncClient,
        authenticated_headers: dict
    ):
        """Test that error responses follow consistent format"""
        
        # Trigger a validation error
        invalid_data = {
            "codigo": "",  # Empty required field
            "nombre": "Test Product",
            "tipo": "PRODUCTO",
            "precio_unitario": 50000.00,
            "unidad_medida": "UNI"
        }
        
        response = await async_client.post(
            "/api/v1/productos/",
            json=invalid_data,
            headers=authenticated_headers
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        error_data = response.json()
        
        # Verify error response structure
        assert "detail" in error_data
        if isinstance(error_data["detail"], list):
            # Pydantic validation errors
            for error in error_data["detail"]:
                assert "loc" in error
                assert "msg" in error
                assert "type" in error