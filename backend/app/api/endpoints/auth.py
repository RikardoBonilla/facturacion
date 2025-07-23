"""
Endpoints de autenticación
"""

from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.auth import get_current_user
from app.schemas.auth import Token, UserLogin
from app.services.auth_service import AuthService

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """
    Endpoint para autenticación de usuarios
    """
    auth_service = AuthService(db)
    
    user = await auth_service.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth_service.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "nombre": f"{user.nombre} {user.apellido}",
            "empresa_id": user.empresa_id
        }
    }


@router.get("/me", response_model=dict)
async def get_current_user_info(
    current_user = Depends(get_current_user)
):
    """
    Obtener información del usuario actual
    """
    return {
        "id": current_user.id,
        "email": current_user.email,
        "nombre": f"{current_user.nombre} {current_user.apellido}",
        "empresa_id": current_user.empresa_id,
        "activo": current_user.activo,
        "rol_id": current_user.rol_id
    }


@router.post("/logout")
async def logout():
    """
    Endpoint para cerrar sesión
    En JWT stateless, el logout se maneja del lado del cliente eliminando el token
    """
    return {"message": "Sesión cerrada exitosamente"}