"""
Unit tests for authentication system
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.auth_service import AuthService
from app.models import Usuario
from app.core.auth import get_current_user, validate_empresa_access


class TestAuthService:
    """Test cases for AuthService"""

    @pytest.mark.unit
    def test_password_hashing(self, auth_service: AuthService):
        """Test password hashing and verification"""
        password = "testpassword123"
        
        # Test hashing
        hashed = auth_service.get_password_hash(password)
        assert hashed != password
        assert len(hashed) > 50  # bcrypt hashes are long
        
        # Test verification
        assert auth_service.verify_password(password, hashed) is True
        assert auth_service.verify_password("wrongpassword", hashed) is False

    @pytest.mark.unit
    def test_create_access_token(self, auth_service: AuthService):
        """Test JWT token creation"""
        data = {"sub": "test@example.com"}
        token = auth_service.create_access_token(data)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 50  # JWT tokens are long

    @pytest.mark.unit
    def test_create_access_token_with_expiration(self, auth_service: AuthService):
        """Test JWT token creation with custom expiration"""
        data = {"sub": "test@example.com"}
        expires_delta = timedelta(minutes=5)
        token = auth_service.create_access_token(data, expires_delta)
        
        assert token is not None
        assert isinstance(token, str)

    @pytest.mark.unit
    def test_verify_token_valid(self, auth_service: AuthService):
        """Test token verification with valid token"""
        email = "test@example.com"
        data = {"sub": email}
        token = auth_service.create_access_token(data)
        
        verified_email = auth_service.verify_token(token)
        assert verified_email == email

    @pytest.mark.unit
    def test_verify_token_invalid(self, auth_service: AuthService):
        """Test token verification with invalid token"""
        invalid_token = "invalid.token.here"
        result = auth_service.verify_token(invalid_token)
        assert result is None

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_user_by_email_found(
        self, 
        db_session: AsyncSession, 
        test_usuario: Usuario,
        auth_service: AuthService
    ):
        """Test getting user by email when user exists"""
        await db_session.commit()  # Commit the test user
        
        user = await auth_service.get_user_by_email(test_usuario.email)
        assert user is not None
        assert user.email == test_usuario.email
        assert user.id == test_usuario.id

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_user_by_email_not_found(self, auth_service: AuthService):
        """Test getting user by email when user doesn't exist"""
        user = await auth_service.get_user_by_email("nonexistent@example.com")
        assert user is None

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_authenticate_user_success(
        self, 
        db_session: AsyncSession,
        test_usuario: Usuario,
        auth_service: AuthService
    ):
        """Test successful user authentication"""
        await db_session.commit()  # Commit the test user
        
        user = await auth_service.authenticate_user(test_usuario.email, "testpass123")
        assert user is not None
        assert user.email == test_usuario.email

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_authenticate_user_wrong_password(
        self, 
        db_session: AsyncSession,
        test_usuario: Usuario,
        auth_service: AuthService
    ):
        """Test authentication with wrong password"""
        await db_session.commit()  # Commit the test user
        
        user = await auth_service.authenticate_user(test_usuario.email, "wrongpassword")
        assert user is None

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_authenticate_user_nonexistent(self, auth_service: AuthService):
        """Test authentication with nonexistent user"""
        user = await auth_service.authenticate_user("nonexistent@example.com", "password")
        assert user is None


class TestAuthDependencies:
    """Test cases for authentication dependencies"""

    @pytest.mark.unit
    def test_validate_empresa_access_success(self, test_usuario: Usuario):
        """Test successful empresa access validation"""
        # Should not raise exception
        validate_empresa_access(test_usuario, test_usuario.empresa_id)

    @pytest.mark.unit
    def test_validate_empresa_access_forbidden(self, test_usuario: Usuario):
        """Test empresa access validation failure"""
        from fastapi import HTTPException
        
        with pytest.raises(HTTPException) as exc_info:
            validate_empresa_access(test_usuario, 999)  # Different empresa_id
        
        assert exc_info.value.status_code == 403
        assert "No tiene permisos" in str(exc_info.value.detail)


class TestPasswordSecurity:
    """Test cases for password security"""

    @pytest.mark.unit
    def test_password_hash_uniqueness(self, auth_service: AuthService):
        """Test that same password produces different hashes"""
        password = "samepassword"
        hash1 = auth_service.get_password_hash(password)
        hash2 = auth_service.get_password_hash(password)
        
        # Hashes should be different due to salt
        assert hash1 != hash2
        
        # But both should verify successfully
        assert auth_service.verify_password(password, hash1)
        assert auth_service.verify_password(password, hash2)

    @pytest.mark.unit
    def test_password_minimum_security(self, auth_service: AuthService):
        """Test password hashing works with various password types"""
        passwords = [
            "short",
            "verylongpasswordwithmanychars",
            "P@ssw0rd!",
            "12345678",
            "español_ñ_chars",
        ]
        
        for password in passwords:
            hashed = auth_service.get_password_hash(password)
            assert auth_service.verify_password(password, hashed)
            assert not auth_service.verify_password(password + "wrong", hashed)


class TestTokenSecurity:
    """Test cases for JWT token security"""

    @pytest.mark.unit
    def test_token_expiration(self, auth_service: AuthService):
        """Test that expired tokens are rejected"""
        # Create token that expires immediately
        data = {"sub": "test@example.com"}
        expires_delta = timedelta(seconds=-1)  # Already expired
        token = auth_service.create_access_token(data, expires_delta)
        
        # Should return None for expired token
        result = auth_service.verify_token(token)
        assert result is None

    @pytest.mark.unit
    def test_token_tampering(self, auth_service: AuthService):
        """Test that tampered tokens are rejected"""
        data = {"sub": "test@example.com"}
        token = auth_service.create_access_token(data)
        
        # Tamper with the token
        tampered_token = token[:-5] + "XXXXX"
        
        result = auth_service.verify_token(tampered_token)
        assert result is None

    @pytest.mark.unit
    def test_token_wrong_secret(self, auth_service: AuthService):
        """Test token verification with wrong secret"""
        from jose import jwt
        from app.core.config import settings
        
        data = {"sub": "test@example.com"}
        # Create token with wrong secret
        wrong_token = jwt.encode(data, "wrong-secret", algorithm=settings.ALGORITHM)
        
        result = auth_service.verify_token(wrong_token)
        assert result is None