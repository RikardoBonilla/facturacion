# 📊 Sistema de Facturación Electrónica Colombia

> 🇨🇴 Sistema completo de facturación electrónica para Colombia con integración DIAN

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green.svg)](https://fastapi.tiangolo.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue.svg)](https://postgresql.org)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://docker.com)

## 🚀 Inicio Rápido (5 minutos)

### 📋 Requisitos Previos

Solo necesitas tener instalado:
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (recomendado)
- O [Python 3.11+](https://python.org/downloads/) y [PostgreSQL](https://postgresql.org/download/)

### ⚡ Opción 1: Con Docker (Más Fácil)

```bash
# 1. Descargar el proyecto
git clone <URL-del-repositorio>
cd Facturacion

# 2. Iniciar todo con un comando
docker-compose up -d

# 3. ¡Listo! La API está funcionando
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