"""
Schemas para autenticación
"""

from pydantic import BaseModel, EmailStr
from typing import Optional


class Token(BaseModel):
    """Schema para respuesta de token"""
    access_token: str
    token_type: str
    user: dict


class TokenData(BaseModel):
    """Schema para datos del token"""
    email: Optional[str] = None


class UserLogin(BaseModel):
    """Schema para login de usuario"""
    email: EmailStr
    password: str


class UserInToken(BaseModel):
    """Schema para usuario en token"""
    id: int
    email: str
    nombre: str
    empresa_id: int