"""
Configuración de la base de datos usando SQLAlchemy con AsyncPG
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from typing import AsyncGenerator

from app.core.config import settings

# Crear engine asíncrono
engine = create_async_engine(
    settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"),
    echo=settings.DEBUG,  # Mostrar queries SQL en modo debug
    pool_pre_ping=True,
    pool_recycle=300,
)

# Crear sessionmaker asíncrono
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Base para modelos
Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency para obtener una sesión de base de datos
    Se usa como dependency injection en FastAPI
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """Inicializar base de datos - crear tablas si no existen"""
    async with engine.begin() as conn:
        # En desarrollo, puedes usar esto para crear tablas automáticamente
        # En producción, usar Alembic para migraciones
        await conn.run_sync(Base.metadata.create_all)