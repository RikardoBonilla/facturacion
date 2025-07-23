"""
API Router configuration
"""

from fastapi import APIRouter

from app.api.endpoints import auth, empresas, clientes, productos, facturas, usuarios

api_router = APIRouter()

# Incluir rutas de endpoints
api_router.include_router(auth.router, prefix="/auth", tags=["autenticación"])
api_router.include_router(empresas.router, prefix="/empresas", tags=["empresas"])
api_router.include_router(usuarios.router, prefix="/usuarios", tags=["usuarios"])
api_router.include_router(clientes.router, prefix="/clientes", tags=["clientes"])
api_router.include_router(productos.router, prefix="/productos", tags=["productos"])
api_router.include_router(facturas.router, prefix="/facturas", tags=["facturas"])