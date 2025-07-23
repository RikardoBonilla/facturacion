"""
Sistema de Facturación Electrónica Colombia
FastAPI Main Application
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.core.config import settings
from app.api import api_router

# Configurar logger
logger.add("logs/app.log", rotation="1 day", retention="30 days", level="INFO")

# Crear aplicación FastAPI
app = FastAPI(
    title="Sistema de Facturación Electrónica",
    description="API REST para facturación electrónica en Colombia con integración DIAN",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir rutas de la API
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/")
async def root():
    """Endpoint raíz de la API"""
    return {
        "message": "Sistema de Facturación Electrónica Colombia",
        "version": "1.0.0",
        "status": "active",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Endpoint para verificar el estado de la API"""
    return {"status": "healthy", "version": "1.0.0"}


# Event handlers
@app.on_event("startup")
async def startup_event():
    """Eventos al iniciar la aplicación"""
    logger.info("🚀 Iniciando Sistema de Facturación Electrónica")
    logger.info(f"🔧 Modo Debug: {settings.DEBUG}")
    logger.info(f"📊 Base de datos: {settings.DATABASE_URL.split('@')[1] if '@' in settings.DATABASE_URL else 'configurada'}")


@app.on_event("shutdown")
async def shutdown_event():
    """Eventos al cerrar la aplicación"""
    logger.info("🛑 Cerrando Sistema de Facturación Electrónica")