"""
Integration tests for clientes endpoints
"""

import pytest
from httpx import AsyncClient
from fastapi import status

from app.models import Cliente, Usuario


class TestClientesEndpoints:
    """Test cases for clientes endpoints"""

    @pytest.mark.integration
    @pytest.mark.crud
    @pytest.mark.asyncio
    async def test_create_cliente_success(
        self, 
        async_client: AsyncClient,
        authenticated_headers: dict
    ):
        """Test creating a new client"""
        cliente_data = {
            "tipo_persona": "NATURAL",
            "tipo_documento": "CC",
            "numero_documento": "11111111",
            "primer_nombre": "Juan",
            "primer_apellido": "Pérez",
            "email": "juan@email.com",
            "telefono": "3001234567",
            "direccion": "Calle 123 # 45-67",
            "ciudad": "Bogotá",
            "departamento": "Cundinamarca",
            "regimen_fiscal": "SIMPLIFICADO"
        }
        
        response = await async_client.post(
            "/api/v1/clientes/",
            json=cliente_data,
            headers=authenticated_headers
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        
        assert data["numero_documento"] == cliente_data["numero_documento"]
        assert data["primer_nombre"] == cliente_data["primer_nombre"]
        assert data["email"] == cliente_data["email"]
        assert "id" in data
        assert "empresa_id" in data

    @pytest.mark.integration
    @pytest.mark.crud
    @pytest.mark.asyncio
    async def test_create_cliente_juridica(
        self, 
        async_client: AsyncClient,
        authenticated_headers: dict
    ):
        """Test creating a juridical person client"""
        cliente_data = {
            "tipo_persona": "JURIDICA",
            "tipo_documento": "NIT",
            "numero_documento": "900123456-1",
            "razon_social": "Empresa Cliente S.A.S.",
            "nombre_comercial": "Cliente Corp",
            "email": "contacto@clientecorp.com",
            "telefono": "6015551234",
            "direccion": "Carrera 50 # 100-200",
            "ciudad": "Medellín",
            "departamento": "Antioquia",
            "regimen_fiscal": "COMUN"
        }
        
        response = await async_client.post(
            "/api/v1/clientes/",
            json=cliente_data,
            headers=authenticated_headers
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        
        assert data["tipo_persona"] == "JURIDICA"
        assert data["numero_documento"] == cliente_data["numero_documento"]
        assert data["razon_social"] == cliente_data["razon_social"]

    @pytest.mark.integration
    @pytest.mark.crud
    @pytest.mark.asyncio
    async def test_create_cliente_duplicate_documento(
        self, 
        async_client: AsyncClient,
        authenticated_headers: dict,
        test_cliente: Cliente
    ):
        """Test creating client with duplicate document number"""
        cliente_data = {
            "tipo_persona": "NATURAL",
            "tipo_documento": "CC",
            "numero_documento": test_cliente.numero_documento,  # Duplicate
            "primer_nombre": "Otro",
            "primer_apellido": "Cliente",
            "direccion": "Otra dirección",
            "ciudad": "Bogotá",
            "departamento": "Cundinamarca"
        }
        
        response = await async_client.post(
            "/api/v1/clientes/",
            json=cliente_data,
            headers=authenticated_headers
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Ya existe un cliente" in response.json()["detail"]

    @pytest.mark.integration
    @pytest.mark.crud
    @pytest.mark.asyncio
    async def test_list_clientes_success(
        self, 
        async_client: AsyncClient,
        authenticated_headers: dict,
        test_cliente: Cliente
    ):
        """Test listing clients"""
        response = await async_client.get(
            "/api/v1/clientes/",
            headers=authenticated_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) >= 1
        
        # Check that test client is in the list
        client_ids = [client["id"] for client in data]
        assert test_cliente.id in client_ids

    @pytest.mark.integration
    @pytest.mark.crud
    @pytest.mark.asyncio
    async def test_list_clientes_pagination(
        self, 
        async_client: AsyncClient,
        authenticated_headers: dict
    ):
        """Test client list pagination"""
        response = await async_client.get(
            "/api/v1/clientes/?skip=0&limit=10",
            headers=authenticated_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 10

    @pytest.mark.integration
    @pytest.mark.crud
    @pytest.mark.asyncio
    async def test_get_cliente_by_id(
        self, 
        async_client: AsyncClient,
        authenticated_headers: dict,
        test_cliente: Cliente
    ):
        """Test getting client by ID"""
        response = await async_client.get(
            f"/api/v1/clientes/{test_cliente.id}",
            headers=authenticated_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["id"] == test_cliente.id
        assert data["numero_documento"] == test_cliente.numero_documento

    @pytest.mark.integration
    @pytest.mark.crud
    @pytest.mark.asyncio
    async def test_get_cliente_not_found(
        self, 
        async_client: AsyncClient,
        authenticated_headers: dict
    ):
        """Test getting non-existent client"""
        response = await async_client.get(
            "/api/v1/clientes/99999",
            headers=authenticated_headers
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.integration
    @pytest.mark.crud
    @pytest.mark.asyncio
    async def test_update_cliente_success(
        self, 
        async_client: AsyncClient,
        authenticated_headers: dict,
        test_cliente: Cliente
    ):
        """Test updating client"""
        update_data = {
            "primer_nombre": "Juan Carlos",
            "email": "juan.carlos@newemail.com",
            "telefono": "3009999999"
        }
        
        response = await async_client.put(
            f"/api/v1/clientes/{test_cliente.id}",
            json=update_data,
            headers=authenticated_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["primer_nombre"] == update_data["primer_nombre"]
        assert data["email"] == update_data["email"]
        assert data["telefono"] == update_data["telefono"]

    @pytest.mark.integration
    @pytest.mark.crud
    @pytest.mark.asyncio
    async def test_delete_cliente_success(
        self, 
        async_client: AsyncClient,
        authenticated_headers: dict,
        test_cliente: Cliente
    ):
        """Test deleting client (soft delete)"""
        response = await async_client.delete(
            f"/api/v1/clientes/{test_cliente.id}",
            headers=authenticated_headers
        )
        
        assert response.status_code == status.HTTP_204_NO_CONTENT

    @pytest.mark.integration
    @pytest.mark.crud
    @pytest.mark.asyncio
    async def test_get_cliente_by_documento(
        self, 
        async_client: AsyncClient,
        authenticated_headers: dict,
        test_cliente: Cliente
    ):
        """Test getting client by document number"""
        response = await async_client.get(
            f"/api/v1/clientes/documento/{test_cliente.numero_documento}",
            headers=authenticated_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["numero_documento"] == test_cliente.numero_documento
        assert data["id"] == test_cliente.id


class TestClientesValidation:
    """Test validation rules for clientes"""

    @pytest.mark.integration
    @pytest.mark.crud
    @pytest.mark.asyncio
    async def test_create_cliente_invalid_tipo_persona(
        self, 
        async_client: AsyncClient,
        authenticated_headers: dict
    ):
        """Test creating client with invalid tipo_persona"""
        cliente_data = {
            "tipo_persona": "INVALID",  # Invalid
            "tipo_documento": "CC",
            "numero_documento": "22222222",
            "direccion": "Test address",
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
    @pytest.mark.crud
    @pytest.mark.asyncio
    async def test_create_cliente_invalid_tipo_documento(
        self, 
        async_client: AsyncClient,
        authenticated_headers: dict
    ):
        """Test creating client with invalid tipo_documento"""
        cliente_data = {
            "tipo_persona": "NATURAL",
            "tipo_documento": "INVALID",  # Invalid
            "numero_documento": "33333333",
            "direccion": "Test address",
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
    @pytest.mark.crud
    @pytest.mark.asyncio
    async def test_create_cliente_missing_required_fields(
        self, 
        async_client: AsyncClient,
        authenticated_headers: dict
    ):
        """Test creating client with missing required fields"""
        cliente_data = {
            "tipo_persona": "NATURAL",
            # Missing tipo_documento, numero_documento, direccion, etc.
        }
        
        response = await async_client.post(
            "/api/v1/clientes/",
            json=cliente_data,
            headers=authenticated_headers
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.integration
    @pytest.mark.crud
    @pytest.mark.asyncio
    async def test_create_cliente_invalid_email(
        self, 
        async_client: AsyncClient,
        authenticated_headers: dict
    ):
        """Test creating client with invalid email"""
        cliente_data = {
            "tipo_persona": "NATURAL",
            "tipo_documento": "CC",
            "numero_documento": "44444444",
            "primer_nombre": "Test",
            "primer_apellido": "User",
            "email": "invalid-email",  # Invalid email
            "direccion": "Test address",
            "ciudad": "Bogotá",
            "departamento": "Cundinamarca"
        }
        
        response = await async_client.post(
            "/api/v1/clientes/",
            json=cliente_data,
            headers=authenticated_headers
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestClientesAuthorization:
    """Test authorization for clientes endpoints"""

    @pytest.mark.integration
    @pytest.mark.auth
    @pytest.mark.asyncio
    async def test_clientes_require_authentication(self, async_client: AsyncClient):
        """Test that all client endpoints require authentication"""
        endpoints = [
            ("GET", "/api/v1/clientes/"),
            ("POST", "/api/v1/clientes/"),
            ("GET", "/api/v1/clientes/1"),
            ("PUT", "/api/v1/clientes/1"),
            ("DELETE", "/api/v1/clientes/1"),
        ]
        
        for method, url in endpoints:
            response = await async_client.request(method, url)
            assert response.status_code == status.HTTP_403_FORBIDDEN