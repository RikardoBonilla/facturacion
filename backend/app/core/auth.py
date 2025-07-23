"""
Middleware y dependencies de autenticación
"""

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models import Usuario
from app.services.auth_service import AuthService

# Security scheme para JWT Bearer token
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Usuario:
    """
    Dependency para obtener el usuario actual desde el token JWT
    """
    
    # Crear instancia del servicio de auth
    auth_service = AuthService(db)
    
    # Verificar token
    email = auth_service.verify_token(credentials.credentials)
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Obtener usuario
    user = await auth_service.get_user_by_email(email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.activo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario inactivo",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


async def get_current_active_user(
    current_user: Usuario = Depends(get_current_user)
) -> Usuario:
    """
    Dependency para obtener usuario activo
    """
    if not current_user.activo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario inactivo"
        )
    return current_user


def validate_empresa_access(user: Usuario, empresa_id: int) -> None:
    """
    Validar que el usuario tenga acceso a la empresa especificada
    """
    if user.empresa_id != empresa_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para acceder a esta empresa"
        )


async def get_empresa_id_from_user(
    current_user: Usuario = Depends(get_current_active_user)
) -> int:
    """
    Dependency para obtener el empresa_id del usuario autenticado
    """
    return current_user.empresa_id


def require_empresa_access(empresa_id: int):
    """
    Dependency factory para validar acceso a empresa específica
    """
    async def _validate_access(
        current_user: Usuario = Depends(get_current_active_user)
    ) -> Usuario:
        validate_empresa_access(current_user, empresa_id)
        return current_user
    
    return _validate_access