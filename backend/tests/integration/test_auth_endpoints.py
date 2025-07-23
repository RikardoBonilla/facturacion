"""
Integration tests for authentication endpoints
"""

import pytest
from httpx import AsyncClient
from fastapi import status

from app.models import Usuario


class TestAuthEndpoints:
    """Test cases for authentication endpoints"""

    @pytest.mark.integration
    @pytest.mark.auth
    @pytest.mark.asyncio
    async def test_login_success(
        self, 
        async_client: AsyncClient,
        test_usuario: Usuario
    ):
        """Test successful login"""
        login_data = {
            "username": test_usuario.email,  # OAuth2PasswordRequestForm uses 'username'
            "password": "testpass123"
        }
        
        response = await async_client.post(
            "/api/v1/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
        assert "user" in data
        assert data["user"]["email"] == test_usuario.email
        assert data["user"]["empresa_id"] == test_usuario.empresa_id

    @pytest.mark.integration
    @pytest.mark.auth
    @pytest.mark.asyncio
    async def test_login_wrong_password(
        self, 
        async_client: AsyncClient,
        test_usuario: Usuario
    ):
        """Test login with wrong password"""
        login_data = {
            "username": test_usuario.email,
            "password": "wrongpassword"
        }
        
        response = await async_client.post(
            "/api/v1/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert "Credenciales incorrectas" in data["detail"]

    @pytest.mark.integration
    @pytest.mark.auth
    @pytest.mark.asyncio
    async def test_login_nonexistent_user(self, async_client: AsyncClient):
        """Test login with nonexistent user"""
        login_data = {
            "username": "nonexistent@example.com",
            "password": "password"
        }
        
        response = await async_client.post(
            "/api/v1/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.integration
    @pytest.mark.auth
    @pytest.mark.asyncio
    async def test_login_inactive_user(
        self, 
        async_client: AsyncClient,
        test_usuario: Usuario,
        db_session
    ):
        """Test login with inactive user"""
        # Deactivate user
        test_usuario.activo = False
        await db_session.commit()
        
        login_data = {
            "username": test_usuario.email,
            "password": "testpass123"
        }
        
        response = await async_client.post(
            "/api/v1/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.integration
    @pytest.mark.auth
    @pytest.mark.asyncio
    async def test_get_current_user_success(
        self, 
        async_client: AsyncClient,
        authenticated_headers: dict
    ):
        """Test getting current user information"""
        response = await async_client.get(
            "/api/v1/auth/me",
            headers=authenticated_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert "id" in data
        assert "email" in data
        assert "nombre" in data
        assert "empresa_id" in data
        assert "activo" in data
        assert "rol_id" in data

    @pytest.mark.integration
    @pytest.mark.auth
    @pytest.mark.asyncio
    async def test_get_current_user_no_token(self, async_client: AsyncClient):
        """Test getting current user without token"""
        response = await async_client.get("/api/v1/auth/me")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.integration
    @pytest.mark.auth
    @pytest.mark.asyncio
    async def test_get_current_user_invalid_token(self, async_client: AsyncClient):
        """Test getting current user with invalid token"""
        headers = {"Authorization": "Bearer invalid-token"}
        response = await async_client.get(
            "/api/v1/auth/me",
            headers=headers
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.integration
    @pytest.mark.auth
    @pytest.mark.asyncio
    async def test_logout(self, async_client: AsyncClient):
        """Test logout endpoint"""
        response = await async_client.post("/api/v1/auth/logout")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "mensaje" in data["message"] or "Sesión cerrada" in data["message"]

    @pytest.mark.integration
    @pytest.mark.auth
    @pytest.mark.asyncio
    async def test_protected_endpoint_without_auth(self, async_client: AsyncClient):
        """Test accessing protected endpoint without authentication"""
        response = await async_client.get("/api/v1/empresas/")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.integration
    @pytest.mark.auth
    @pytest.mark.asyncio
    async def test_protected_endpoint_with_auth(
        self, 
        async_client: AsyncClient,
        authenticated_headers: dict
    ):
        """Test accessing protected endpoint with authentication"""
        response = await async_client.get(
            "/api/v1/empresas/",
            headers=authenticated_headers
        )
        
        # Should not be forbidden (might be 404 if no empresa data, but not 403)
        assert response.status_code != status.HTTP_403_FORBIDDEN

    @pytest.mark.integration
    @pytest.mark.auth
    @pytest.mark.asyncio
    async def test_token_format_validation(self, async_client: AsyncClient):
        """Test various invalid token formats"""
        invalid_tokens = [
            "Bearer",  # No token
            "invalid-token",  # No Bearer prefix
            "Bearer ",  # Empty token
            "Bearer token-without-dots",  # Invalid JWT format
        ]
        
        for token in invalid_tokens:
            headers = {"Authorization": token}
            response = await async_client.get(
                "/api/v1/auth/me",
                headers=headers
            )
            assert response.status_code in [
                status.HTTP_401_UNAUTHORIZED, 
                status.HTTP_403_FORBIDDEN
            ]


class TestAuthFlow:
    """Test complete authentication flow"""

    @pytest.mark.integration
    @pytest.mark.auth
    @pytest.mark.asyncio
    async def test_complete_auth_flow(
        self, 
        async_client: AsyncClient,
        test_usuario: Usuario
    ):
        """Test complete authentication flow from login to accessing protected resource"""
        
        # Step 1: Login
        login_data = {
            "username": test_usuario.email,
            "password": "testpass123"
        }
        
        login_response = await async_client.post(
            "/api/v1/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        assert login_response.status_code == status.HTTP_200_OK
        token_data = login_response.json()
        access_token = token_data["access_token"]
        
        # Step 2: Access protected endpoint
        headers = {"Authorization": f"Bearer {access_token}"}
        me_response = await async_client.get(
            "/api/v1/auth/me",
            headers=headers
        )
        
        assert me_response.status_code == status.HTTP_200_OK
        user_data = me_response.json()
        assert user_data["email"] == test_usuario.email
        
        # Step 3: Access another protected endpoint
        empresas_response = await async_client.get(
            "/api/v1/empresas/",
            headers=headers
        )
        
        # Should not be forbidden
        assert empresas_response.status_code != status.HTTP_403_FORBIDDEN