"""
Integration tests for empresas endpoints
"""

import pytest
from httpx import AsyncClient
from fastapi import status

from app.models import Empresa, Usuario


class TestEmpresasEndpoints:
    """Test cases for empresas endpoints"""

    @pytest.mark.integration
    @pytest.mark.crud
    @pytest.mark.asyncio
    async def test_get_mi_empresa_success(
        self, 
        async_client: AsyncClient,
        authenticated_headers: dict,
        test_empresa: Empresa
    ):
        """Test getting my company information"""
        response = await async_client.get(
            "/api/v1/empresas/",
            headers=authenticated_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["id"] == test_empresa.id
        assert data["nit"] == test_empresa.nit
        assert data["razon_social"] == test_empresa.razon_social
        assert data["email"] == test_empresa.email
        assert data["tipo_contribuyente"] == test_empresa.tipo_contribuyente

    @pytest.mark.integration
    @pytest.mark.crud
    @pytest.mark.asyncio
    async def test_get_mi_empresa_unauthorized(self, async_client: AsyncClient):
        """Test getting company info without authentication"""
        response = await async_client.get("/api/v1/empresas/")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.integration
    @pytest.mark.crud
    @pytest.mark.asyncio
    async def test_update_mi_empresa_success(
        self, 
        async_client: AsyncClient,
        authenticated_headers: dict,
        test_empresa: Empresa
    ):
        """Test updating my company information"""
        update_data = {
            "nombre_comercial": "Updated Company Name",
            "telefono": "3009999999",
            "email": "updated@empresa.com"
        }
        
        response = await async_client.put(
            "/api/v1/empresas/",
            json=update_data,
            headers=authenticated_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["nombre_comercial"] == update_data["nombre_comercial"]
        assert data["telefono"] == update_data["telefono"]
        assert data["email"] == update_data["email"]
        # Other fields should remain unchanged
        assert data["nit"] == test_empresa.nit
        assert data["razon_social"] == test_empresa.razon_social

    @pytest.mark.integration
    @pytest.mark.crud
    @pytest.mark.asyncio
    async def test_update_mi_empresa_partial(
        self, 
        async_client: AsyncClient,
        authenticated_headers: dict,
        test_empresa: Empresa
    ):
        """Test partial update of company information"""
        update_data = {
            "telefono": "3001111111"
        }
        
        response = await async_client.put(
            "/api/v1/empresas/",
            json=update_data,
            headers=authenticated_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["telefono"] == update_data["telefono"]
        # Other fields should remain unchanged
        assert data["nit"] == test_empresa.nit
        assert data["razon_social"] == test_empresa.razon_social
        assert data["email"] == test_empresa.email

    @pytest.mark.integration
    @pytest.mark.crud
    @pytest.mark.asyncio
    async def test_update_mi_empresa_invalid_data(
        self, 
        async_client: AsyncClient,
        authenticated_headers: dict
    ):
        """Test updating company with invalid data"""
        update_data = {
            "email": "invalid-email",  # Invalid email format
            "tipo_contribuyente": "INVALID_TYPE"  # Invalid type
        }
        
        response = await async_client.put(
            "/api/v1/empresas/",
            json=update_data,
            headers=authenticated_headers
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.integration
    @pytest.mark.crud
    @pytest.mark.asyncio
    async def test_update_mi_empresa_unauthorized(self, async_client: AsyncClient):
        """Test updating company without authentication"""
        update_data = {
            "nombre_comercial": "Unauthorized Update"
        }
        
        response = await async_client.put(
            "/api/v1/empresas/",
            json=update_data
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.integration
    @pytest.mark.crud
    @pytest.mark.asyncio
    async def test_get_empresa_by_nit_success(
        self, 
        async_client: AsyncClient,
        authenticated_headers: dict,
        test_empresa: Empresa
    ):
        """Test getting company by NIT"""
        response = await async_client.get(
            f"/api/v1/empresas/nit/{test_empresa.nit}",
            headers=authenticated_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["nit"] == test_empresa.nit
        assert data["id"] == test_empresa.id

    @pytest.mark.integration
    @pytest.mark.crud
    @pytest.mark.asyncio
    async def test_get_empresa_by_nit_not_found(
        self, 
        async_client: AsyncClient,
        authenticated_headers: dict
    ):
        """Test getting company by non-existent NIT"""
        response = await async_client.get(
            "/api/v1/empresas/nit/999999999-9",
            headers=authenticated_headers
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestEmpresasValidation:
    """Test validation rules for empresas"""

    @pytest.mark.integration
    @pytest.mark.crud
    @pytest.mark.asyncio
    async def test_update_empresa_valid_tipos_contribuyente(
        self, 
        async_client: AsyncClient,
        authenticated_headers: dict
    ):
        """Test valid tipos de contribuyente"""
        valid_types = ["PERSONA_NATURAL", "PERSONA_JURIDICA"]
        
        for tipo in valid_types:
            update_data = {"tipo_contribuyente": tipo}
            
            response = await async_client.put(
                "/api/v1/empresas/",
                json=update_data,
                headers=authenticated_headers
            )
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["tipo_contribuyente"] == tipo

    @pytest.mark.integration
    @pytest.mark.crud
    @pytest.mark.asyncio
    async def test_update_empresa_valid_regimen_fiscal(
        self, 
        async_client: AsyncClient,
        authenticated_headers: dict
    ):
        """Test valid regímenes fiscales"""
        valid_regimens = ["SIMPLIFICADO", "COMUN"]
        
        for regimen in valid_regimens:
            update_data = {"regimen_fiscal": regimen}
            
            response = await async_client.put(
                "/api/v1/empresas/",
                json=update_data,
                headers=authenticated_headers
            )
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["regimen_fiscal"] == regimen

    @pytest.mark.integration
    @pytest.mark.crud
    @pytest.mark.asyncio
    async def test_update_empresa_valid_ambiente_dian(
        self, 
        async_client: AsyncClient,
        authenticated_headers: dict
    ):
        """Test valid ambientes DIAN"""
        valid_ambientes = ["PRUEBAS", "PRODUCCION"]
        
        for ambiente in valid_ambientes:
            update_data = {"ambiente_dian": ambiente}
            
            response = await async_client.put(
                "/api/v1/empresas/",
                json=update_data,
                headers=authenticated_headers
            )
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["ambiente_dian"] == ambiente

    @pytest.mark.integration
    @pytest.mark.crud
    @pytest.mark.asyncio
    async def test_update_empresa_responsabilidades_fiscales(
        self, 
        async_client: AsyncClient,
        authenticated_headers: dict
    ):
        """Test updating responsabilidades fiscales (array field)"""
        update_data = {
            "responsabilidades_fiscales": ["05", "09", "14"]
        }
        
        response = await async_client.put(
            "/api/v1/empresas/",
            json=update_data,
            headers=authenticated_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["responsabilidades_fiscales"] == update_data["responsabilidades_fiscales"]

    @pytest.mark.integration
    @pytest.mark.crud
    @pytest.mark.asyncio
    async def test_update_empresa_dian_configuration(
        self, 
        async_client: AsyncClient,
        authenticated_headers: dict
    ):
        """Test updating DIAN configuration"""
        from datetime import date
        
        update_data = {
            "prefijo_factura": "FE",
            "resolucion_dian": "18760000002",
            "fecha_resolucion": "2024-01-15",
            "rango_autorizado_desde": 1000,
            "rango_autorizado_hasta": 10000
        }
        
        response = await async_client.put(
            "/api/v1/empresas/",
            json=update_data,
            headers=authenticated_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["prefijo_factura"] == update_data["prefijo_factura"]
        assert data["resolucion_dian"] == update_data["resolucion_dian"]
        assert data["rango_autorizado_desde"] == update_data["rango_autorizado_desde"]
        assert data["rango_autorizado_hasta"] == update_data["rango_autorizado_hasta"]