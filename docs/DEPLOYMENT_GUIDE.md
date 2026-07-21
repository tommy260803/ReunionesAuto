# GUÍA DE DESPLIEGUE - ZOOM2

**Versión:** 1.0  
**Fecha:** 2026-07-20  
**Sistema:** ReunionesAuto - Sistema de Gestión de Reuniones y Análisis Estadístico

---

## TABLA DE CONTENIDOS

1. [Requisitos Previos](#requisitos-previos)
2. [Configuración de Base de Datos](#configuración-de-base-de-datos)
3. [Configuración de Backend](#configuración-de-backend)
4. [Configuración de Frontend](#configuración-de-frontend)
5. [Configuración de Automatización (n8n)](#configuración-de-automatización-n8n)
6. [Despliegue Local](#despliegue-local)
7. [Despliegue en Producción](#despliegue-en-producción)
8. [Monitoreo y Mantenimiento](#monitoreo-y-mantenimiento)
9. [Solución de Problemas](#solución-de-problemas)

---

## REQUISITOS PREVIOS

### Software Requerido

**Backend:**
- Python 3.11+
- pip (gestor de paquetes Python)
- virtualenv (opcional, recomendado)

**Frontend:**
- Node.js 18+
- npm (gestor de paquetes Node.js)

**Base de Datos:**
- Cuenta de Supabase
- Acceso a SQL Editor de Supabase

**Automatización:**
- Instancia de n8n (local o en la nube)
- Credenciales de Zoom API

### Hardware Recomendado

**Mínimo:**
- 2 CPU cores
- 4 GB RAM
- 20 GB disco

**Recomendado:**
- 4 CPU cores
- 8 GB RAM
- 50 GB disco

---

## CONFIGURACIÓN DE BASE DE DATOS

### Crear Proyecto en Supabase

1. Inicie sesión en [Supabase](https://supabase.com)
2. Cree un nuevo proyecto
3. Anote las credenciales:
   - Project URL
   - Anon Key
   - Service Role Key

### Ejecutar Scripts SQL

Ejecute los scripts SQL en el siguiente orden en el SQL Editor de Supabase:

```sql
-- 1. Tablas principales
query1.txt
query2.txt
query3.txt
query4.txt

-- 2. Datos de prueba
insert_sample_tasks.sql

-- 3. Métricas
query5_metricas.txt
query6_reuniones_participantes.sql
query7_resumenes_modulo.sql
query8_metricas_inferenciales.sql

-- 4. Evaluación científica
query9_evaluacion_cientifica.sql

-- 5. Configuración de roles
query10_establecer_admin.sql

-- 6. Actualización de contraseñas
query11_actualizar_password.sql

-- 7. Persistencia de análisis
query12_persistencia_analisis.sql

-- 8. Mejoras RLS
query13_mejorar_rls_evaluacion.sql
```

### Configurar Variables de Entorno

Cree un archivo root `.env` en el proyecto:

```env
# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# n8n Webhooks
N8N_CALLBACK_SECRET=your-secret-key
N8N_WORKFLOW_VERSION=1.0

# Zoom API (opcional)
ZOOM_API_KEY=your-zoom-api-key
ZOOM_API_SECRET=your-zoom-api-secret
```

---

## CONFIGURACIÓN DE BACKEND

### Instalar Dependencias

```powershell
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.lock.txt
```

### Dependencias Opcionales

Para generación de reportes:

```powershell
pip install reportlab python-docx pandas openpyxl
```

Para análisis estadístico avanzado:

```powershell
pip install krippendorff
```

### Configurar Variables de Entorno

Cree `backend/.env`:

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
ADMIN_EMAIL=juanaureliodelacruzgamarra@gmail.com
```

### Ejecutar Pruebas

```powershell
python -m unittest discover -s tests -t . -v
```

### Iniciar Servidor de Desarrollo

```powershell
python -m uvicorn app.main:app --reload --port 8000
```

El servidor estará disponible en `http://localhost:8000`

---

## CONFIGURACIÓN DE FRONTEND

### Instalar Dependencias

```powershell
cd frontend
npm ci
```

### Configurar Variables de Entorno

Cree `frontend/.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
```

### Instalar Playwright (para pruebas E2E)

```powershell
npx playwright install
```

### Ejecutar Pruebas E2E

```powershell
npx playwright test
```

### Iniciar Servidor de Desarrollo

```powershell
npm run dev
```

El frontend estará disponible en `http://localhost:3000`

---

## CONFIGURACIÓN DE AUTOMATIZACIÓN (N8N)

### Importar Workflows

Importe los workflows JSON desde `json n8n/`:

1. Inicie sesión en su instancia de n8n
2. Navegue a "Workflows"
3. Haga clic en "Import from File"
4. Importe los siguientes workflows:
   - `zoom_meeting_creation.json`
   - `summary_generation.json`
   - `ai_execution_logging.json`

### Configurar Credenciales

Configure las siguientes credenciales en n8n:

**Supabase:**
- URL del proyecto
- Service Role Key

**Zoom API:**
- API Key
- API Secret

**OpenAI (opcional):**
- API Key

### Configurar Webhooks

Configure los webhooks en n8n:

1. Obtenga las URLs de los webhooks
2. Actualice las variables de entorno en el backend:
   ```env
   N8N_ZOOM_WEBHOOK=https://your-n8n-instance.com/webhook/zoom
   N8N_SUMMARY_WEBHOOK=https://your-n8n-instance.com/webhook/summary
   ```

---

## DESPLIEGUE LOCAL

### Iniciar Todos los Servicios

**Terminal 1 - Backend:**
```powershell
cd backend
.venv\Scripts\activate
python -m uvicorn app.main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```powershell
cd frontend
npm run dev
```

**Terminal 3 - n8n (opcional):**
```powershell
npx n8n
```

### Verificar Despliegue

1. Backend: `http://localhost:8000/docs` (documentación API)
2. Frontend: `http://localhost:3000` (aplicación web)
3. Health Check: `http://localhost:8000/health`

---

## DESPLIEGUE EN PRODUCCIÓN

### Opción 1: Docker Compose

Crear `docker-compose.yml`:

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_SERVICE_ROLE_KEY=${SUPABASE_SERVICE_ROLE_KEY}
    depends_on:
      - frontend

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=${API_URL}
      - NEXT_PUBLIC_SUPABASE_URL=${SUPABASE_URL}
      - NEXT_PUBLIC_SUPABASE_ANON_KEY=${SUPABASE_ANON_KEY}
```

Ejecutar:

```powershell
docker-compose up -d
```

### Opción 2: Vercel (Frontend) + Render (Backend)

**Frontend en Vercel:**

1. Conecte el repositorio a Vercel
2. Configure las variables de entorno
3. Deploy automáticamente en cada push

**Backend en Render:**

1. Conecte el repositorio a Render
2. Configure las variables de entorno
3. Deploy automáticamente en cada push

### Configurar Dominios Personalizados

**Frontend:**
1. Configure dominio en Vercel
2. Actualizar DNS con CNAME

**Backend:**
1. Configure dominio en Render
2. Actualizar DNS con CNAME

---

## MONITOREO Y MANTENIMIENTO

### Monitoreo de Servicios

**Backend:**
- Health check: `/health`
- Logs: Ver logs en la plataforma de hosting
- Métricas: Usar herramientas como Prometheus/Grafana

**Frontend:**
- Logs: Ver logs en Vercel
- Performance: Usar Vercel Analytics
- Errors: Usar Sentry para captura de errores

### Backups

**Base de Datos:**
- Supabase realiza backups automáticos diarios
- Configurar Point-in-Time Recovery si es necesario

**Archivos:**
- Backup de archivos de configuración
- Version control con Git

### Actualizaciones

**Backend:**
```powershell
cd backend
git pull
.venv\Scripts\activate
pip install -r requirements.lock.txt
```

**Frontend:**
```powershell
cd frontend
git pull
npm ci
npm run build
```

---

## SOLUCIÓN DE PROBLEMAS

### Problemas Comunes

**Backend no inicia:**
- Verificar que Python 3.+ está instalado
- Verificar que las dependencias están instaladas
- Verificar que las variables de entorno están configuradas

**Frontend no inicia:**
- Verificar que Node.js 18+ está instalado
- Verificar que las dependencias están instaladas
- Verificar que las variables de entorno están configuradas

**Error de conexión a base de datos:**
- Verificar que Supabase está accesible
- Verificar que las credenciales son correctas
- Verificar que las políticas RLS están configuradas

**Error de autenticación:**
- Verificar que el token JWT es válido
- Verificar que el usuario tiene el rol adecuado
- Verificar que las políticas RLS permiten el acceso

### Logs de Error

**Backend:**
- Ver logs en terminal o plataforma de hosting
- Buscar errores en `backend/app/main.py`

**Frontend:**
- Ver logs en terminal o Vercel
- Usar DevTools del navegador para errores de JavaScript

### Contacto de Soporte

Para problemas de despliegue:
- Email: devops@reunionesauto.com
- Documentación: https://docs.reunionesauto.com

---

## APÉNDICE

### Variables de Entorno Completas

**Backend (.env):**
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
ADMIN_EMAIL=juanaureliodelacruzgamarra@gmail.com
N8N_CALLBACK_SECRET=your-secret-key
N8N_WORKFLOW_VERSION=1.0
```

**Frontend (.env.local):**
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
```

### Puertos Utilizados

- Backend: 8000
- Frontend: 3000
- n8n: 5678 (default)

### URLs de Producción

- Frontend: `https://app.reunionesauto.com`
- Backend: `https://api.reunionesauto.com`
- API Docs: `https://api.reunionesauto.com/docs`

---

**Fin de la Guía de Despliegue**
