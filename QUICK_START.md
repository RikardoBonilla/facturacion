# 🚀 Guía de Instalación Rápida

> ℹ️ Esta guía está diseñada para personas **sin experiencia en Python**. Siguiendo estos pasos tendrás el sistema funcionando en 10 minutos.

## 📋 Paso 1: Instalar Dependencias

### 🖥️ Windows

1. **Descargar Docker Desktop:**
   - Ve a: https://www.docker.com/products/docker-desktop/
   - Haz clic en "Download for Windows"
   - Instala y reinicia tu computadora cuando te lo pida

2. **Descargar Git:**
   - Ve a: https://git-scm.com/download/win
   - Descarga e instala

### 🍎 macOS

1. **Instalar Docker Desktop:**
   - Ve a: https://www.docker.com/products/docker-desktop/
   - Haz clic en "Download for Mac"
   - Arrastra Docker.app a Applications

2. **Git ya viene instalado** en macOS

### 🐧 Linux (Ubuntu/Debian)

```bash
# Instalar Docker
sudo apt update
sudo apt install docker.io docker-compose git
sudo usermod -aG docker $USER
# Cerrar sesión y volver a entrar
```

---

## 📥 Paso 2: Descargar el Proyecto

Abre una **terminal** (Command Prompt en Windows) y ejecuta:

```bash
# Descargar proyecto
git clone <URL-del-repositorio>
cd Facturacion

# Verificar que tienes los archivos
ls
```

Deberías ver archivos como: `docker-compose.yml`, `README.md`, `backend/`, etc.

---

## 🚀 Paso 3: Iniciar el Sistema

En la misma terminal, ejecuta **UN SOLO COMANDO**:

```bash
docker-compose up -d
```

**Esto tardará 2-3 minutos la primera vez** porque descarga las imágenes de Docker.

### ✅ Verificar que Funciona

Abre tu navegador y ve a:
- **API**: http://localhost:8000
- **Documentación**: http://localhost:8000/docs

Si ves una página con información de la API, ¡funciona! 🎉

---

## 🔑 Paso 4: Crear Datos de Prueba

En la terminal, ejecuta:

```bash
# Entrar al contenedor
docker-compose exec backend python scripts/seed_simple.py
```

Esto crea:
- ✅ Una empresa de prueba
- ✅ Un usuario administrador
- ✅ Algunos clientes y productos de ejemplo

---

## 🧪 Paso 5: Probar la API

### Opción A: Usar Swagger UI (Recomendado)

1. Ve a: http://localhost:8000/docs
2. Haz clic en **"Authorize"** (botón con candado 🔒)
3. Ingresa:
   - **username**: `admin@empresatest.com`
   - **password**: `admin123`
4. Haz clic en **"Authorize"** y luego **"Close"**
5. ¡Ahora puedes probar cualquier endpoint con "Try it out"!

### Opción B: Usar Scripts Automáticos

```bash
# Probar todos los endpoints automáticamente
docker-compose exec backend python scripts/test_endpoints.py
```

---

## 🆘 Si Algo Sale Mal

### 🔴 "Port already in use" o "puerto ya está en uso"

```bash
# En Windows (PowerShell como Administrador):
netstat -ano | findstr :8000
taskkill /PID <número-de-proceso> /F

# En macOS/Linux:
sudo lsof -ti :8000 | xargs kill -9
```

### 🔴 "Docker is not running"

1. Abre Docker Desktop manualmente
2. Espera a que aparezca el ícono en la barra de tareas
3. Intenta de nuevo

### 🔴 "No such file or directory"

```bash
# Verifica que estás en el directorio correcto
pwd
ls
# Deberías ver docker-compose.yml
```

### 🔴 Base de datos no responde

```bash
# Reiniciar todo
docker-compose down
docker-compose up -d
```

---

## 🛑 Cómo Parar el Sistema

Cuando termines de probar:

```bash
# Parar todos los servicios
docker-compose down

# Si quieres eliminar también los datos
docker-compose down -v
```

---

## 📱 Próximos Pasos

Una vez que tengas todo funcionando:

1. **Explora la documentación**: http://localhost:8000/docs
2. **Prueba crear clientes, productos y facturas**
3. **Lee el README.md completo** para funciones avanzadas
4. **Desarrolla tu frontend** conectándolo a la API

---

## 📞 ¿Necesitas Ayuda?

Si tienes problemas:

1. **Copia el error exacto** que aparece en la terminal
2. **Toma captura de pantalla** si es visual
3. **Indica tu sistema operativo** (Windows/Mac/Linux)
4. **Abre un issue** en GitHub con esa información

---

## ✅ Checklist Final

Marca ✅ cuando completes cada paso:

- [ ] Docker Desktop instalado y funcionando
- [ ] Proyecto descargado con `git clone`
- [ ] Sistema iniciado con `docker-compose up -d`
- [ ] API responde en http://localhost:8000
- [ ] Datos de prueba creados con `seed_simple.py`
- [ ] Swagger UI funciona con credenciales de prueba
- [ ] Probé al menos un endpoint (GET /clientes)

**¡Si tienes todos los ✅, tu sistema está listo para usar!** 🎉

---

<div align="center">

**🇨🇴 Sistema de Facturación Electrónica Colombia**

*Fácil de instalar, fácil de usar*

</div>