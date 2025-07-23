"""
Pytest configuration and shared fixtures
"""

import asyncio
import os
import pytest
import pytest_asyncio
from typing import AsyncGenerator, Generator
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

# Add the backend directory to Python path
import sys
from pathlib import Path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.main import app
from app.core.database import Base, get_db
from app.core.config import settings
from app.models import *
from app.services.auth_service import AuthService


# Test database URL
TEST_DATABASE_URL = "postgresql+asyncpg://admin:admin123@localhost:5432/facturacion_test"


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def test_engine():
    """Create test database engine."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
        echo=False,
    )
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Drop all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a fresh database session for each test."""
    async_session = async_sessionmaker(
        test_engine, 
        class_=AsyncSession, 
        expire_on_commit=False
    )
    
    async with async_session() as session:
        # Start a transaction
        await session.begin()
        
        try:
            yield session
        finally:
            # Rollback transaction to clean up
            await session.rollback()
            await session.close()


@pytest.fixture
def override_get_db(db_session: AsyncSession):
    """Override the get_db dependency for testing."""
    async def _override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = _override_get_db
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def client(override_get_db) -> TestClient:
    """Create test client."""
    return TestClient(app)


@pytest_asyncio.fixture
async def async_client(override_get_db) -> AsyncGenerator[AsyncClient, None]:
    """Create async test client."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def auth_service(db_session: AsyncSession) -> AuthService:
    """Create auth service instance."""
    return AuthService(db_session)


# Data fixtures
@pytest_asyncio.fixture
async def test_empresa(db_session: AsyncSession) -> Empresa:
    """Create test company."""
    empresa = Empresa(
        nit="900123456-1",
        razon_social="Empresa Test S.A.S.",
        nombre_comercial="Test Company",
        direccion="Carrera 10 # 20-30",
        ciudad="Bogotá",
        departamento="Cundinamarca",
        telefono="3001234567",
        email="test@empresa.com",
        tipo_contribuyente="PERSONA_JURIDICA",
        regimen_fiscal="COMUN",
        responsabilidades_fiscales=["05", "09"],
        ambiente_dian="PRUEBAS",
        prefijo_factura="FT",
        resolucion_dian="18760000001",
        rango_autorizado_desde=1,
        rango_autorizado_hasta=5000
    )
    db_session.add(empresa)
    await db_session.flush()
    return empresa


@pytest_asyncio.fixture
async def test_rol(db_session: AsyncSession) -> Rol:
    """Create test role."""
    rol = Rol(
        nombre="TEST_ADMIN",
        descripcion="Test administrator role",
        activo=True
    )
    db_session.add(rol)
    await db_session.flush()
    return rol


@pytest_asyncio.fixture
async def test_usuario(
    db_session: AsyncSession, 
    test_empresa: Empresa, 
    test_rol: Rol,
    auth_service: AuthService
) -> Usuario:
    """Create test user."""
    usuario = Usuario(
        empresa_id=test_empresa.id,
        email="test@empresa.com",
        password_hash=auth_service.get_password_hash("testpass123"),
        nombre="Test",
        apellido="User",
        tipo_documento="CC",
        numero_documento="12345678",
        telefono="3001234567",
        rol_id=test_rol.id,
        activo=True
    )
    db_session.add(usuario)
    await db_session.flush()
    return usuario


@pytest_asyncio.fixture
async def test_cliente(db_session: AsyncSession, test_empresa: Empresa) -> Cliente:
    """Create test client."""
    cliente = Cliente(
        empresa_id=test_empresa.id,
        tipo_persona="NATURAL",
        tipo_documento="CC",
        numero_documento="98765432",
        primer_nombre="Juan",
        primer_apellido="Pérez",
        email="juan.perez@email.com",
        telefono="3012345678",
        direccion="Calle 15 # 10-20",
        ciudad="Bogotá",
        departamento="Cundinamarca",
        regimen_fiscal="SIMPLIFICADO"
    )
    db_session.add(cliente)
    await db_session.flush()
    return cliente


@pytest_asyncio.fixture
async def test_producto(db_session: AsyncSession, test_empresa: Empresa) -> Producto:
    """Create test product."""
    producto = Producto(
        empresa_id=test_empresa.id,
        codigo="TEST001",
        nombre="Producto de Prueba",
        descripcion="Producto para testing",
        codigo_unspsc="43211500",
        tipo="PRODUCTO",
        precio_unitario=50000,
        unidad_medida="UNI",
        incluye_iva=True,
        porcentaje_iva=19.00
    )
    db_session.add(producto)
    await db_session.flush()
    return producto


@pytest_asyncio.fixture
async def authenticated_headers(
    auth_service: AuthService,
    test_usuario: Usuario
) -> dict:
    """Create authentication headers for test requests."""
    from datetime import timedelta
    
    access_token = auth_service.create_access_token(
        data={"sub": test_usuario.email},
        expires_delta=timedelta(minutes=30)
    )
    
    return {"Authorization": f"Bearer {access_token}"}


# Utility fixtures
@pytest.fixture
def mock_settings():
    """Mock settings for testing."""
    class MockSettings:
        SECRET_KEY = "test-secret-key"
        ALGORITHM = "HS256"
        ACCESS_TOKEN_EXPIRE_MINUTES = 30
        DATABASE_URL = TEST_DATABASE_URL
        DEBUG = True
        API_V1_STR = "/api/v1"
    
    return MockSettings()


# Parametrized fixtures for different test scenarios
@pytest.fixture(params=["NATURAL", "JURIDICA"])
def tipo_persona(request):
    """Parametrized fixture for person types."""
    return request.param


@pytest.fixture(params=["CC", "NIT", "CE", "PASAPORTE"])
def tipo_documento(request):
    """Parametrized fixture for document types."""
    return request.param


@pytest.fixture(params=["PRODUCTO", "SERVICIO"])
def tipo_producto(request):
    """Parametrized fixture for product types."""
    return request.param