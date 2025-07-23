# 📊 Sistema de Facturación Electrónica Colombia

> 🇨🇴 API REST completa para facturación electrónica colombiana con cumplimiento DIAN

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green.svg)](https://fastapi.tiangolo.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue.svg)](https://postgresql.org)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://docker.com)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**🔗 Repositorio:** https://github.com/RikardoBonilla/facturacion.git

## 🚀 Inicio Rápido (5 minutos)

### 📋 Requisitos Previos

Solo necesitas tener instalado:
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (recomendado)
- O [Python 3.11+](https://python.org/downloads/) y [PostgreSQL](https://postgresql.org/download/)

### ⚡ Opción 1: Con Docker (Más Fácil)

```bash
# 1. Clonar el repositorio
git clone https://github.com/RikardoBonilla/facturacion.git
cd facturacion

# 2. Iniciar todos los servicios
docker-compose up -d

# 3. Crear datos de prueba
docker-compose exec backend python scripts/seed_simple.py

# 4. ¡Listo! La API está funcionando
```

**🌐 URLs disponibles:**
- API: http://localhost:8000
- Documentación: http://localhost:8000/docs
- Base de datos: localhost:5432

### ⚡ Opción 2: Instalación Manual

```bash
# 1. Ir al directorio backend
cd backend

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Configurar base de datos (archivo .env)
cp .env.example .env
# Editar .env con tus datos

# 4. Iniciar servidor
python -m uvicorn app.main:app --reload
```

---

## 🏗️ Arquitectura del Sistema

### 📊 Stack Tecnológico

**Backend:**
- **FastAPI 0.104** - Framework web asíncrono moderno
- **Python 3.11** - Lenguaje de programación
- **PostgreSQL 15** - Base de datos relacional
- **SQLAlchemy 2.0** - ORM con soporte async/await
- **Alembic** - Migraciones de base de datos
- **Pydantic** - Validación de datos y serialización
- **JWT** - Autenticación stateless
- **Docker** - Contenedorización

**DevOps & Tools:**
- **Docker Compose** - Orquestación de contenedores
- **pytest** - Framework de testing
- **pre-commit** - Hooks de código
- **mypy** - Type checking
- **black/isort** - Formateo de código

### 🔄 Arquitectura de Capas

```
┌─────────────────────────────────────────────────────┐
│                  CLIENTE (Frontend)                 │
└─────────────────────┬───────────────────────────────┘
                      │ HTTP/REST API
┌─────────────────────▼───────────────────────────────┐
│                 API LAYER (FastAPI)                 │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐   │
│  │  Endpoints  │ │ Middleware  │ │ Auth Guard  │   │
│  └─────────────┘ └─────────────┘ └─────────────┘   │
└─────────────────────┬───────────────────────────────┘
                      │ Pydantic Schemas
┌─────────────────────▼───────────────────────────────┐
│               SERVICE LAYER                         │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐   │
│  │ Auth Service│ │CRUD Services│ │DIAN Services│   │
│  └─────────────┘ └─────────────┘ └─────────────┘   │
└─────────────────────┬───────────────────────────────┘
                      │ SQLAlchemy Models
┌─────────────────────▼───────────────────────────────┐
│               DATA LAYER                            │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐   │
│  │ PostgreSQL  │ │   Models    │ │ Migrations  │   │
│  └─────────────┘ └─────────────┘ └─────────────┘   │
└─────────────────────────────────────────────────────┘
```

### 🗂️ Estructura del Proyecto

```
facturacion/
├── 📁 backend/                     # API Backend
│   ├── 📁 app/
│   │   ├── 📁 api/                 # API Routes
│   │   │   ├── __init__.py         # Router principal
│   │   │   └── endpoints/          # Endpoints por módulo
│   │   │       ├── auth.py         # Autenticación
│   │   │       ├── empresas.py     # Gestión empresas
│   │   │       ├── clientes.py     # Gestión clientes
│   │   │       ├── productos.py    # Catálogo productos
│   │   │       ├── facturas.py     # Facturación
│   │   │       └── usuarios.py     # Gestión usuarios
│   │   ├── 📁 core/                # Configuración base
│   │   │   ├── auth.py             # Seguridad JWT
│   │   │   ├── config.py           # Variables entorno
│   │   │   └── database.py         # Conexión DB
│   │   ├── 📁 models/              # Modelos SQLAlchemy
│   │   │   ├── usuario.py          # Modelo Usuario
│   │   │   ├── empresa.py          # Modelo Empresa
│   │   │   ├── cliente.py          # Modelo Cliente
│   │   │   ├── producto.py         # Modelo Producto
│   │   │   ├── factura.py          # Modelo Factura
│   │   │   └── rol.py              # Modelo Roles/Permisos
│   │   ├── 📁 schemas/             # Esquemas Pydantic
│   │   │   ├── auth.py             # Schemas autenticación
│   │   │   ├── empresa.py          # Schemas empresa
│   │   │   ├── cliente.py          # Schemas cliente
│   │   │   ├── producto.py         # Schemas producto
│   │   │   └── factura.py          # Schemas factura
│   │   ├── 📁 services/            # Lógica de negocio
│   │   │   └── auth_service.py     # Servicio autenticación
│   │   └── main.py                 # Aplicación principal
│   ├── 📁 migrations/              # Migraciones Alembic
│   ├── 📁 scripts/                 # Scripts utilidades
│   │   ├── seed_simple.py          # Datos básicos
│   │   ├── seed_all.py             # Datos completos
│   │   ├── test_endpoints.py       # Testing automático
│   │   └── test_swagger_demo.py    # Demo Swagger
│   ├── 📁 tests/                   # Tests automatizados
│   │   ├── unit/                   # Tests unitarios
│   │   ├── integration/            # Tests integración
│   │   └── conftest.py             # Configuración pytest
│   ├── .env.example                # Variables entorno ejemplo
│   ├── requirements.txt            # Dependencias producción
│   ├── requirements-dev.txt        # Dependencias desarrollo
│   ├── Dockerfile                  # Imagen Docker
│   └── alembic.ini                 # Configuración migraciones
├── 🐳 docker-compose.yml           # Orquestación contenedores
├── 🗄️ facturacion.sql              # Schema base de datos
├── 📖 README.md                    # Documentación principal
├── 🚀 QUICK_START.md               # Guía instalación rápida
└── 📋 TESTING_RESULTS.md           # Resultados testing
```

---

## ⚡ Instalación y Configuración Detallada

### 🔧 Opción 1: Desarrollo con Docker (Recomendado)

```bash
# 1. Clonar repositorio
git clone https://github.com/RikardoBonilla/facturacion.git
cd facturacion

# 2. Configurar variables de entorno
cp backend/.env.example backend/.env
# Editar backend/.env si es necesario

# 3. Construir y levantar servicios
docker-compose up --build -d

# 4. Verificar servicios activos
docker-compose ps

# 5. Ver logs
docker-compose logs -f backend

# 6. Crear datos de prueba
docker-compose exec backend python scripts/seed_simple.py

# 7. Ejecutar tests
docker-compose exec backend pytest
```

### 🔧 Opción 2: Desarrollo Local

```bash
# 1. Clonar repositorio
git clone https://github.com/RikardoBonilla/facturacion.git
cd facturacion/backend

# 2. Crear entorno virtual
python3.11 -m venv venv

# En Linux/macOS:
source venv/bin/activate

# En Windows:
venv\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 4. Configurar variables de entorno
cp .env.example .env
# Editar .env con configuración local

# 5. Configurar base de datos PostgreSQL
# Crear base de datos 'facturacion'
createdb facturacion

# 6. Ejecutar migraciones
alembic upgrade head

# 7. Crear datos de prueba
python scripts/seed_simple.py

# 8. Iniciar servidor de desarrollo
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 🗄️ Configuración de Base de Datos

**Con Docker (automático):**
- PostgreSQL 15 se configura automáticamente
- Datos persistentes en volume `postgres_data`
- Schema aplicado desde `facturacion.sql`

**Instalación manual:**
```sql
-- Crear base de datos
CREATE DATABASE facturacion;
CREATE USER facturacion_user WITH PASSWORD 'tu_password';
GRANT ALL PRIVILEGES ON DATABASE facturacion TO facturacion_user;

-- Aplicar schema
psql -U facturacion_user -d facturacion -f facturacion.sql
```

---

## 🔑 Credenciales de Prueba

Una vez iniciado el sistema, usa estas credenciales para probar:

```
📧 Email:    admin@empresatest.com
🔒 Password: admin123
🏢 Empresa:  Empresa de Pruebas S.A.S.
```

---

## 📚 Cómo Usar la API

### 1️⃣ Abrir la Documentación

Ve a: http://localhost:8000/docs

![Swagger UI Interface](https://fastapi.tiangolo.com/img/index/index-03-swagger-02.png)

### 2️⃣ Autenticarse

1. Haz clic en el botón **"Authorize"** 🔒
2. Ingresa las credenciales de prueba
3. Haz clic en **"Authorize"** y luego **"Close"**

### 3️⃣ Probar Endpoints

Ahora puedes probar cualquier endpoint:
- 👥 **Clientes**: Crear y gestionar clientes
- 📦 **Productos**: Catálogo de productos/servicios  
- 🧾 **Facturas**: Crear facturas electrónicas
- 🏢 **Empresas**: Gestión multi-empresa

### 4️⃣ Ejemplos de Uso

**Listar clientes:**
```http
GET /api/v1/clientes
Authorization: Bearer <tu-token>
```

**Crear un cliente:**
```http
POST /api/v1/clientes
Content-Type: application/json
Authorization: Bearer <tu-token>

{
  "tipo_persona": "NATURAL",
  "tipo_documento": "CC",
  "numero_documento": "12345678",
  "nombres": "Juan",
  "apellidos": "Pérez",
  "email": "juan@email.com",
  "telefono": "3001234567",
  "direccion": "Calle 123 #45-67",
  "ciudad": "Bogotá",
  "departamento": "Cundinamarca",
  "regimen_fiscal": "SIMPLIFICADO"
}
```

---

## 🛠️ Scripts Útiles

El proyecto incluye scripts para facilitar el uso:

```bash
# Crear datos de prueba
python scripts/seed_simple.py

# Crear datos completos (empresas, clientes, productos, facturas)
python scripts/seed_all.py

# Probar todos los endpoints automáticamente
python scripts/test_endpoints.py

# Demostración de Swagger UI
python scripts/test_swagger_demo.py
```

---

## 📁 Estructura del Proyecto

```
Facturacion/
├── 📁 backend/                 # API FastAPI
│   ├── 📁 app/
│   │   ├── 📁 api/endpoints/   # Rutas de la API
│   │   ├── 📁 models/          # Modelos de base de datos
│   │   ├── 📁 schemas/         # Validación de datos
│   │   └── 📁 services/        # Lógica de negocio
│   ├── 📁 scripts/             # Scripts útiles
│   └── 📁 tests/               # Pruebas automatizadas
├── 📁 frontend/                # Interface web (opcional)
├── 🐳 docker-compose.yml       # Configuración Docker
├── 🗄️ facturacion.sql          # Esquema de base de datos
└── 📖 README.md                # Este archivo
```

---

## 🇨🇴 Características Colombianas

### ✅ Cumplimiento DIAN
- 📋 Tipos de documento: NIT, CC, CE, PASAPORTE
- 💰 Impuestos: IVA (0%, 5%, 19%), INC, ICA
- 📊 Códigos UNSPSC para productos
- 🏢 Regímenes fiscales: SIMPLIFICADO, COMÚN
- 📄 Estados DIAN: BORRADOR, EMITIDA, ACEPTADA, RECHAZADA

### 📊 Funcionalidades
- 🔐 **Autenticación JWT** - Seguridad empresarial
- 🏢 **Multi-empresa** - Múltiples empresas en una instalación
- 👥 **Gestión de clientes** - Personas naturales y jurídicas
- 📦 **Catálogo de productos** - Con códigos UNSPSC
- 🧾 **Facturación completa** - Con cálculos automáticos
- 📊 **Reportes** - Información financiera y fiscal
- 🔄 **API REST** - Integración con otros sistemas

---

## 🆘 Solución de Problemas

### ❓ Problemas Comunes

**🔴 "Address already in use"**
```bash
# Matar procesos en puerto 8000
sudo lsof -ti :8000 | xargs kill -9
```

**🔴 "Database connection error"**
```bash
# Verificar que PostgreSQL esté corriendo
docker-compose ps
# O reiniciar base de datos
docker-compose restart db
```

**🔴 "Module not found"**
```bash
# Instalar dependencias
pip install -r requirements.txt
```

**🔴 "Permission denied"**
```bash
# En scripts, dar permisos de ejecución
chmod +x scripts/*.py
```

### 📞 Obtener Ayuda

1. **Revisa los logs:**
   ```bash
   docker-compose logs backend
   ```

2. **Verifica el estado:**
   ```bash
   curl http://localhost:8000/health
   ```

3. **Recrear base de datos:**
   ```bash
   docker-compose down -v
   docker-compose up -d
   python scripts/seed_simple.py
   ```

---

## 🧪 Testing

### Pruebas Automáticas
```bash
# Ejecutar todas las pruebas
pytest

# Pruebas con cobertura
pytest --cov=app

# Pruebas de endpoints
python scripts/test_endpoints.py
```

### Pruebas Manuales
1. Abrir http://localhost:8000/docs
2. Usar credenciales de prueba
3. Probar endpoints con "Try it out"

---

## 🔧 Configuración Avanzada

### Variables de Entorno (.env)
```bash
# Base de datos
DATABASE_URL=postgresql+asyncpg://admin:admin123@localhost:5432/facturacion

# Seguridad
SECRET_KEY=tu-clave-super-secreta

# DIAN
DIAN_AMBIENTE=PRUEBAS
```

### Personalización
- **Puerto:** Cambiar en `docker-compose.yml` o comando uvicorn
- **Base de datos:** Modificar credenciales en `.env`
- **CORS:** Ajustar `ALLOWED_HOSTS` en configuración

---

## 🛠️ Comandos de Desarrollo

### 📦 Gestión de Dependencias

```bash
# Ver dependencias instaladas
pip list

# Actualizar requirements.txt
pip freeze > requirements.txt

# Instalar nueva dependencia
pip install nueva-dependencia
echo "nueva-dependencia==version" >> requirements.txt
```

### 🗄️ Gestión de Base de Datos

```bash
# Crear nueva migración
alembic revision --autogenerate -m "Descripción del cambio"

# Aplicar migraciones
alembic upgrade head

# Ver historial de migraciones
alembic history

# Revertir migración
alembic downgrade -1

# Ver SQL de migración sin ejecutar
alembic upgrade head --sql
```

### 🧪 Testing y Calidad de Código

```bash
# Ejecutar todos los tests
pytest

# Tests con cobertura
pytest --cov=app --cov-report=html

# Tests específicos
pytest tests/unit/test_auth.py

# Tests con output detallado
pytest -v -s

# Linting y formateo
black app/
isort app/
mypy app/

# Pre-commit hooks
pre-commit run --all-files
```

### 🐳 Comandos Docker

```bash
# Ver logs específicos
docker-compose logs backend
docker-compose logs db

# Ejecutar comandos en contenedor
docker-compose exec backend bash
docker-compose exec backend python scripts/seed_all.py

# Rebuilding services
docker-compose up --build backend

# Limpiar volúmenes
docker-compose down -v

# Verificar recursos
docker system df
docker system prune
```

### 🔧 Scripts Útiles

```bash
# Crear datos básicos de prueba
python scripts/seed_simple.py

# Crear datos completos (empresas, clientes, productos, facturas)
python scripts/seed_all.py

# Crear solo datos maestros (impuestos, roles)
python scripts/seed_master_data.py

# Testing completo de endpoints
python scripts/test_endpoints.py

# Demo de Swagger UI
python scripts/test_swagger_demo.py

# Linting automático
python scripts/lint.py
```

---

## 🎯 Decisiones de Desarrollo

### 🏗️ Arquitectura

**1. Clean Architecture:**
- Separación clara entre capas (API, Service, Data)
- Dependencias unidireccionales
- Fácil testeo y mantenimiento

**2. Async/Await:**
- SQLAlchemy 2.0 con soporte async
- FastAPI asíncrono por defecto
- Mejor performance y concurrencia

**3. Multi-tenancy:**
- Aislamiento por `empresa_id`
- Una base de datos, múltiples empresas
- Seguridad a nivel de datos

### 🔒 Seguridad

**1. Autenticación JWT:**
- Tokens stateless
- Expiration configurable
- Bearer token authentication

**2. Autorización RBAC:**
- Roles y permisos granulares
- Middleware de autorización
- Scopes por empresa

**3. Validación:**
- Pydantic schemas en todos los endpoints
- Validación de datos colombianos
- Sanitización automática

### 🗄️ Base de Datos

**1. PostgreSQL:**
- ACID compliance
- JSON fields para flexibilidad
- Excellent performance

**2. SQLAlchemy 2.0:**
- Type hints completos
- Async queries
- Lazy loading optimizado

**3. Migraciones:**
- Alembic para versionado
- Rollback capabilities
- Schema consistency

### 🇨🇴 Cumplimiento Colombia

**1. Tipos de Documento:**
- NIT con dígito verificador
- CC, CE, PASAPORTE
- Validación específica

**2. Impuestos:**
- IVA (0%, 5%, 19%)
- INC por categorías
- ICA municipal

**3. DIAN Integration:**
- Estados de factura
- Códigos UNSPSC
- XML structure ready

---

## ➕ Agregar Nuevos Endpoints

### 📋 Paso a Paso

#### 1️⃣ Crear el Modelo (si es necesario)

```python
# backend/app/models/nuevo_modelo.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class NuevoModelo(Base):
    __tablename__ = "nuevo_modelo"
    
    id = Column(Integer, primary_key=True, index=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=False)
    nombre = Column(String(200), nullable=False)
    created_at = Column(DateTime, default=func.now())
    
    # Relaciones
    empresa = relationship("Empresa", back_populates="nuevo_modelos")
```

#### 2️⃣ Crear Schemas Pydantic

```python
# backend/app/schemas/nuevo_modelo.py
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class NuevoModeloBase(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=200)

class NuevoModeloCreate(NuevoModeloBase):
    pass

class NuevoModeloUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=2, max_length=200)

class NuevoModelo(NuevoModeloBase):
    id: int
    empresa_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True
```

#### 3️⃣ Crear Endpoints

```python
# backend/app/api/endpoints/nuevo_modelo.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.nuevo_modelo import NuevoModelo
from app.schemas.nuevo_modelo import (
    NuevoModelo as NuevoModeloSchema,
    NuevoModeloCreate,
    NuevoModeloUpdate
)

router = APIRouter()

@router.get("/", response_model=List[NuevoModeloSchema])
async def list_nuevo_modelos(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Listar todos los elementos del nuevo modelo"""
    query = select(NuevoModelo).where(
        NuevoModelo.empresa_id == current_user.empresa_id
    ).offset(skip).limit(limit)
    
    result = await db.execute(query)
    return result.scalars().all()

@router.post("/", response_model=NuevoModeloSchema)
async def create_nuevo_modelo(
    nuevo_modelo: NuevoModeloCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Crear nuevo elemento"""
    db_nuevo_modelo = NuevoModelo(
        **nuevo_modelo.dict(),
        empresa_id=current_user.empresa_id
    )
    
    db.add(db_nuevo_modelo)
    await db.commit()
    await db.refresh(db_nuevo_modelo)
    
    return db_nuevo_modelo

@router.get("/{nuevo_modelo_id}", response_model=NuevoModeloSchema)
async def get_nuevo_modelo(
    nuevo_modelo_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Obtener elemento por ID"""
    query = select(NuevoModelo).where(
        NuevoModelo.id == nuevo_modelo_id,
        NuevoModelo.empresa_id == current_user.empresa_id
    )
    
    result = await db.execute(query)
    nuevo_modelo = result.scalar_one_or_none()
    
    if not nuevo_modelo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Elemento no encontrado"
        )
    
    return nuevo_modelo

@router.put("/{nuevo_modelo_id}", response_model=NuevoModeloSchema)
async def update_nuevo_modelo(
    nuevo_modelo_id: int,
    nuevo_modelo_update: NuevoModeloUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Actualizar elemento"""
    # Obtener elemento existente
    query = select(NuevoModelo).where(
        NuevoModelo.id == nuevo_modelo_id,
        NuevoModelo.empresa_id == current_user.empresa_id
    )
    
    result = await db.execute(query)
    db_nuevo_modelo = result.scalar_one_or_none()
    
    if not db_nuevo_modelo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Elemento no encontrado"
        )
    
    # Actualizar campos
    update_data = nuevo_modelo_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_nuevo_modelo, field, value)
    
    await db.commit()
    await db.refresh(db_nuevo_modelo)
    
    return db_nuevo_modelo

@router.delete("/{nuevo_modelo_id}")
async def delete_nuevo_modelo(
    nuevo_modelo_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Eliminar elemento"""
    # Obtener elemento
    query = select(NuevoModelo).where(
        NuevoModelo.id == nuevo_modelo_id,
        NuevoModelo.empresa_id == current_user.empresa_id
    )
    
    result = await db.execute(query)
    db_nuevo_modelo = result.scalar_one_or_none()
    
    if not db_nuevo_modelo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Elemento no encontrado"
        )
    
    await db.delete(db_nuevo_modelo)
    await db.commit()
    
    return {"message": "Elemento eliminado exitosamente"}
```

#### 4️⃣ Registrar en Router Principal

```python
# backend/app/api/__init__.py
from fastapi import APIRouter
from app.api.endpoints import (
    auth, empresas, clientes, productos, 
    facturas, usuarios, nuevo_modelo  # Agregar import
)

api_router = APIRouter()

# Incluir rutas existentes...
api_router.include_router(
    nuevo_modelo.router, 
    prefix="/nuevo-modelo", 
    tags=["nuevo-modelo"]
)
```

#### 5️⃣ Crear Migración

```bash
# Generar migración automática
alembic revision --autogenerate -m "Add nuevo_modelo table"

# Aplicar migración
alembic upgrade head
```

#### 6️⃣ Agregar Tests

```python
# backend/tests/integration/test_nuevo_modelo_endpoints.py
import pytest
from httpx import AsyncClient

class TestNuevoModeloEndpoints:
    
    async def test_create_nuevo_modelo(self, client: AsyncClient, auth_headers):
        """Test crear nuevo modelo"""
        data = {
            "nombre": "Test Modelo"
        }
        
        response = await client.post(
            "/api/v1/nuevo-modelo/",
            json=data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        assert response.json()["nombre"] == "Test Modelo"
    
    async def test_list_nuevo_modelos(self, client: AsyncClient, auth_headers):
        """Test listar modelos"""
        response = await client.get(
            "/api/v1/nuevo-modelo/",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        assert isinstance(response.json(), list)
```

#### 7️⃣ Actualizar Modelos Relacionados

```python
# Si hay relaciones, actualizar modelos existentes
# backend/app/models/empresa.py

class Empresa(Base):
    # ... campos existentes ...
    
    # Agregar relación
    nuevo_modelos = relationship("NuevoModelo", back_populates="empresa")
```

#### 8️⃣ Documentar en Swagger

```python
# Los decoradores FastAPI generan automáticamente la documentación
# Pero puedes agregar más detalles:

@router.post(
    "/",
    response_model=NuevoModeloSchema,
    summary="Crear nuevo elemento",
    description="Crea un nuevo elemento en el sistema con validaciones específicas",
    responses={
        201: {"description": "Elemento creado exitosamente"},
        400: {"description": "Datos inválidos"},
        401: {"description": "No autorizado"},
    }
)
```

### ✅ Checklist para Nuevos Endpoints

- [ ] Modelo SQLAlchemy creado
- [ ] Schemas Pydantic definidos
- [ ] Endpoints CRUD implementados
- [ ] Autenticación y autorización agregada
- [ ] Multi-tenancy por empresa_id
- [ ] Router registrado en API principal
- [ ] Migración de base de datos creada y aplicada
- [ ] Tests unitarios e integración escritos
- [ ] Documentación Swagger actualizada
- [ ] Validaciones de datos colombianos (si aplica)

---

## 📊 API Reference

### 🔐 Autenticación

**POST** `/api/v1/auth/login`
- **Body:** `username` (email), `password`
- **Response:** JWT token + user info
- **Usage:** OAuth2PasswordRequestForm

**GET** `/api/v1/auth/me`
- **Headers:** `Authorization: Bearer <token>`
- **Response:** Current user information

### 🏢 Empresas

**GET** `/api/v1/empresas` - Listar empresas
**POST** `/api/v1/empresas` - Crear empresa
**GET** `/api/v1/empresas/{id}` - Obtener empresa
**PUT** `/api/v1/empresas/{id}` - Actualizar empresa
**DELETE** `/api/v1/empresas/{id}` - Eliminar empresa

### 👥 Clientes

**GET** `/api/v1/clientes` - Listar clientes
**POST** `/api/v1/clientes` - Crear cliente
**GET** `/api/v1/clientes/{id}` - Obtener cliente
**PUT** `/api/v1/clientes/{id}` - Actualizar cliente
**DELETE** `/api/v1/clientes/{id}` - Eliminar cliente

### 📦 Productos

**GET** `/api/v1/productos` - Listar productos
**POST** `/api/v1/productos` - Crear producto
**GET** `/api/v1/productos/{id}` - Obtener producto
**PUT** `/api/v1/productos/{id}` - Actualizar producto
**DELETE** `/api/v1/productos/{id}` - Eliminar producto

### 🧾 Facturas

**GET** `/api/v1/facturas` - Listar facturas
**POST** `/api/v1/facturas` - Crear factura
**GET** `/api/v1/facturas/{id}` - Obtener factura
**PUT** `/api/v1/facturas/{id}` - Actualizar factura
**DELETE** `/api/v1/facturas/{id}` - Anular factura

> 📖 **Documentación completa:** http://localhost:8000/docs

---

## 📈 Próximos Pasos

Una vez tengas la API funcionando:

1. **📱 Frontend:** Desarrollar interface web con React/Angular/Vue
2. **🔌 Integraciones:** Conectar con sistemas contables
3. **📊 Reportes:** Implementar dashboards y análisis
4. **🌐 Producción:** Desplegar en servidor cloud
5. **📋 DIAN:** Configurar certificados y ambiente productivo

---

## 🤝 Contribuir

¿Quieres mejorar el proyecto?

1. Fork el repositorio
2. Crea una rama: `git checkout -b mi-nueva-funcionalidad`
3. Haz commit: `git commit -am 'Agregar nueva funcionalidad'`
4. Push: `git push origin mi-nueva-funcionalidad`
5. Crea un Pull Request

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver archivo `LICENSE` para más detalles.

---

## 📞 Soporte

- 📧 **Email:** [tu-email@ejemplo.com]
- 💬 **Issues:** [GitHub Issues](link-a-issues)
- 📖 **Documentación:** http://localhost:8000/docs
- 🌐 **Demo:** [Link a demo online]

---

<div align="center">

**🇨🇴 Hecho con ❤️ para Colombia**

[![Mira la documentación en vivo](https://img.shields.io/badge/Ver%20Docs-En%20Vivo-brightgreen.svg)](http://localhost:8000/docs)

</div>