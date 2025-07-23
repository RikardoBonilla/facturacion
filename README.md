# Sistema de Facturación Electrónica Colombia

Sistema profesional de facturación electrónica compatible con la DIAN de Colombia, desarrollado con tecnologías modernas para ser rápido, seguro y eficiente.

## 🚀 Tecnologías

### Backend
- **Python 3.11** - Lenguaje principal
- **FastAPI** - Framework web moderno y rápido
- **PostgreSQL** - Base de datos relacional
- **SQLAlchemy** - ORM con soporte async
- **Docker** - Contenedorización

### Frontend
- **Ionic** - Framework híbrido
- **Angular** - Framework TypeScript
- **Capacitor** - Para apps nativas

### DevOps
- **Docker Compose** - Orquestación de contenedores
- **Git** - Control de versiones

## 📋 Características

- ✅ Multi-tenant (múltiples empresas)
- ✅ Facturación electrónica DIAN
- ✅ Gestión de clientes y productos
- ✅ Cálculo automático de impuestos colombianos
- ✅ Autenticación JWT
- ✅ API RESTful documentada
- ✅ Base de datos PostgreSQL optimizada
- ✅ Dockerizado para desarrollo

## 🏗️ Arquitectura

```
facturacion/
├── backend/           # API Python con FastAPI
│   ├── app/
│   │   ├── api/       # Endpoints REST
│   │   ├── core/      # Configuración y DB
│   │   ├── models/    # Modelos SQLAlchemy
│   │   ├── schemas/   # Schemas Pydantic
│   │   ├── services/  # Lógica de negocio
│   │   └── utils/     # Utilidades
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/          # App Ionic/Angular
├── facturacion.sql    # Schema de base de datos
├── docker-compose.yml # Configuración Docker
└── README.md
```

## 🚦 Inicio Rápido

### Prerrequisitos
- Docker y Docker Compose
- Git

### 1. Clonar y configurar
```bash
git clone <repository>
cd facturacion

# Configurar variables de entorno
cp backend/.env.example backend/.env
# Editar backend/.env con tus configuraciones
```

### 2. Levantar servicios
```bash
# Levantar base de datos y backend
docker-compose up -d db backend

# Ver logs
docker-compose logs -f backend
```

### 3. Verificar instalación
```bash
# API documentación
http://localhost:8000/docs

# Health check
curl http://localhost:8000/health
```

## 📚 Documentación API

Una vez levantado el backend, la documentación interactiva está disponible en:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🗄️ Base de Datos

La base de datos incluye:
- Sistema multi-tenant
- Usuarios con roles y permisos
- Clientes con datos fiscales colombianos
- Productos con códigos UNSPSC
- Facturas con campos DIAN
- Impuestos colombianos (IVA, INC, ICA)
- Auditoría completa

## 🔐 Seguridad

- Autenticación JWT
- Hash de contraseñas con bcrypt
- Variables de entorno para secrets
- CORS configurado
- Validación con Pydantic

## 🧪 Testing

```bash
# Ejecutar tests
docker-compose exec backend pytest

# Con coverage
docker-compose exec backend pytest --cov=app
```

## 📦 Despliegue

Para producción:
1. Cambiar SECRET_KEY en variables de entorno
2. Configurar ALLOWED_HOSTS específicos
3. Usar PostgreSQL externo
4. Configurar certificados DIAN
5. Habilitar HTTPS

## 🤝 Contribución

1. Fork el proyecto
2. Crear feature branch
3. Commit cambios
4. Push al branch
5. Crear Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT.