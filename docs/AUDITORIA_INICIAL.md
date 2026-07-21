# Auditoría Inicial del Proyecto Zoom2

**Fecha:** 2026-07-20  
**Objetivo:** Evaluar el estado actual del sistema antes de implementar el módulo de evaluación científica y estadística.

---

## 1. Arquitectura Encontrada

### 1.1. Stack Tecnológico

**Backend (FastAPI):**
- Python 3.12.10
- FastAPI 0.139.0
- Cliente REST personalizado para Supabase (requests)
- Autenticación JWT con bcrypt (passlib)
- ReportLab para generación de PDF
- NumPy, SciPy para cálculos estadísticos

**Frontend (Next.js):**
- Next.js 16.2.10 (App Router)
- React 19.2.4
- TypeScript
- Tailwind CSS 4
- Axios para llamadas HTTP
- Recharts para gráficos
- Lucide React para iconos

**Base de Datos:**
- Supabase PostgreSQL
- Cliente REST sin SDK oficial
- Row Level Security (RLS) implementado
- Scripts SQL versionados en `querys para supabase/`

**Automatización:**
- n8n para workflows
- Zoom API para reuniones
- Integración mediante webhooks

### 1.2. Estructura de Directorios

```
ReunionesAuto/
├── backend/
│   ├── app/
│   │   ├── auth/          # Autenticación JWT
│   │   ├── automation/    # Integración n8n
│   │   ├── core/          # Config, seguridad, cliente Supabase
│   │   ├── meetings/      # Gestión de reuniones
│   │   ├── metrics/       # Métricas n8n y estadísticas
│   │   ├── participants/  # Gestión de participantes
│   │   ├── reports/       # Exportación PDF
│   │   ├── services/      # Servicios de negocio
│   │   ├── summaries/     # Resúmenes IA
│   │   ├── tasks/         # Gestión de tareas
│   │   └── users/         # Gestión de usuarios
│   ├── tests/             # Pruebas unitarias
│   └── requirements.lock.txt
├── frontend/
│   ├── src/
│   │   ├── app/           # App Router
│   │   ├── components/    # Componentes UI
│   │   ├── context/       # Context API (Auth, Language)
│   │   └── lib/           # Utilidades, cliente API
│   └── package.json
├── querys para supabase/  # Scripts SQL
├── json n8n/              # Workflows n8n
└── docs/                  # Documentación (nueva)
```

---

## 2. Componentes y Responsabilidades

### 2.1. Backend

**Módulo de Autenticación (`auth/`):**
- Login con JWT
- Registro de usuarios
- Verificación de usuario actual
- Autorización basada en correo hardcodeado

**Módulo de Métricas (`metrics/`):**
- Registro de telemetría n8n
- Análisis estadístico inferencial
- Prueba t de Welch para latencias
- Chi-cuadrado/Fisher para resultados categóricos
- Endpoints: `/metrics/n8n`, `/metrics/n8n/stats`, `/metrics/n8n/statistics`

**Módulo de Reportes (`reports/`):**
- Exportación PDF de usuarios
- Exportación PDF de tareas
- Generación en memoria con ReportLab

**Cliente Supabase (`core/supabase_client.py`):**
- Cliente REST personalizado
- Métodos CRUD: select, insert, update, delete, upsert
- Storage: upload, signed URLs, delete
- Soporte para service_role_key

### 2.2. Frontend

**Autenticación (`context/AuthContext.tsx`):**
- Gestión de sesión con cookies
- Protección de rutas
- Interceptor axios para token JWT

**Cliente API (`lib/api.ts`):**
- Axios con baseURL configurable
- Interceptor para inyectar token
- Manejo de errores 401

**Sistema de Diseño:**
- Tailwind CSS 4 con tokens semánticos
- Tema claro/oscuro persistente
- Componentes reutilizables
- Estilo "command center" empresarial

**Vistas Principales:**
- Dashboard con KPIs y gráficos
- Gestión de reuniones y participantes
- Tablero Kanban de tareas
- Resúmenes IA con chat
- Métricas n8n con análisis estadístico

---

## 3. Flujo Actual

### 3.1. Autenticación
1. Usuario ingresa credenciales en `/login`
2. Backend valida contra tabla `usuarios`
3. Backend genera JWT con user_id
4. Frontend almacena token en cookie
5. Interceptor axios inyecta token en cada request
6. Backend valida token y extrae user_id
7. Admin check: comparación de correo con `ADMIN_EMAIL` hardcodeado

### 3.2. Creación de Reuniones
1. Usuario describe reunión en chat `/chat`
2. Frontend envía a webhook n8n
3. n8n procesa con IA (Groq/OpenAI)
4. n8n llama RPC Supabase para crear reunión y participantes
5. Backend recibe callback y actualiza estado

### 3.3. Resúmenes IA
1. Usuario sube PDF o usa grabación Zoom
2. Backend transmite a n8n
3. n8n procesa con IA
4. n8n almacena resultado en Supabase
5. Frontend muestra resumen estructurado

### 3.4. Métricas Estadísticas
1. n8n registra telemetría en `metricas_n8n`
2. Admin consulta `/metrics/n8n/statistics`
3. Backend ejecuta Welch t-test y Chi-cuadrado
4. Frontend visualiza resultados con Recharts

---

## 4. Tablas Existentes

### 4.1. Tablas Principales

**usuarios:**
- id (UUID, PK)
- nombre (TEXT)
- correo (VARCHAR, UNIQUE)
- password_hash (TEXT)
- nivel_suscripcion (VARCHAR: basico/pro/enterprise)
- estado_suscripcion (VARCHAR: activo/pendiente/cancelado)
- fecha_creacion (TIMESTAMPTZ)

**reuniones:**
- id (UUID, PK)
- creador_id (UUID, FK → usuarios)
- tema (TEXT)
- fecha_inicio (TIMESTAMPTZ)
- duracion_minutos (INTEGER)
- proveedor (VARCHAR: zoom)
- id_externo (VARCHAR, UNIQUE) - Zoom ID
- join_url (TEXT)
- start_url (TEXT)
- estado (VARCHAR: programada/completada/cancelada)
- tipo (VARCHAR: virtual/presencial/mixta)
- direccion (TEXT)
- fecha_creacion (TIMESTAMPTZ)

**participantes:**
- id (UUID, PK)
- reunion_id (UUID, FK → reuniones)
- usuario_id (UUID, FK → usuarios)
- correo (VARCHAR)
- rol (VARCHAR: organizador/participante/ponentente)
- estado_invitacion (VARCHAR: enviado/aceptado/rechazado)
- fecha_creacion (TIMESTAMPTZ)
- UNIQUE(reunion_id, correo)

**tareas:**
- id (UUID, PK)
- reunion_id (UUID, FK → reuniones)
- descripcion (TEXT)
- asignado_a_correo (VARCHAR)
- estado (VARCHAR: pendiente/en_progreso/completada)
- fecha_vencimiento (TIMESTAMPTZ)
- fecha_creacion (TIMESTAMPTZ)

**resumenes:**
- id (UUID, PK)
- reunion_id (UUID, FK → reuniones, UNIQUE)
- resumen (TEXT)
- fecha_creacion (TIMESTAMPTZ)

### 4.2. Tablas de Métricas

**metricas_n8n:**
- id (UUID, PK)
- endpoint (VARCHAR)
- tiempo_respuesta (FLOAT)
- estado (VARCHAR)
- fecha (TIMESTAMPTZ)
- codigo_estado (VARCHAR)
- reunion_id (UUID, FK → reuniones)
- tamano_respuesta (INTEGER)
- detalles (JSONB)
- outcome (VARCHAR: success/error/timeout)
- end_to_end_latency_seconds (FLOAT)
- started_at (TIMESTAMPTZ)
- completed_at (TIMESTAMPTZ)
- data_source (VARCHAR: production/demo/test/legacy)
- is_terminal (BOOLEAN)
- workflow_version (VARCHAR)
- attempt_number (INTEGER)
- correlation_id (VARCHAR)

---

## 5. Riesgos Identificados

### 5.1. Seguridad
- **CRÍTICO:** Autorización basada en correo hardcodeado (`ADMIN_EMAIL`)
- No hay sistema de roles en base de datos
- No hay auditoría de acciones sensibles
- Service role key expuesta en backend (necesario para storage)

### 5.2. Datos Científicos
- No hay tabla de versiones de prompts
- No hay registro de ejecuciones de IA con parámetros
- No hay evaluaciones de calidad de resúmenes
- No hay gold standard de tareas
- No hay mediciones de tiempo manual vs automatizado
- No hay evaluaciones SUS de usabilidad
- No hay acuerdo entre evaluadores

### 5.3. Trazabilidad
- No hay auditoría de cambios
- No hay versionado de resúmenes
- No hay historial de ediciones
- No hay registro de quién aprobó/rechazó resúmenes

### 5.4. Calidad de Datos
- No hay validación de JSON estructurado de resúmenes
- No hay detección de afirmaciones no respaldadas
- No hay registro de omisiones
- No hay comparación con gold standard

---

## 6. Deuda Técnica

### 6.1. Arquitectura
- Autorización hardcodeada debe migrarse a roles en BD
- Cliente Supabase personalizado es bueno pero requiere mantenimiento
- No hay ORM (ventaja: control total, desventaja: más código boilerplate)

### 6.2. Testing
- Pruebas unitarias limitadas (solo en módulo metrics)
- No hay pruebas de integración
- No hay pruebas E2E (Playwright configurado pero sin tests)

### 6.3. Documentación
- Buena documentación de migración
- Falta documentación de API endpoints
- Falta documentación de esquemas de base de datos

### 6.4. Frontend
- Buen sistema de componentes
- Falta validación de formularios robusta
- Manejo de errores básico pero mejorable

---

## 7. Problemas Funcionales

### 7.1. Críticos
- No se puede evaluar científicamente la calidad de resúmenes
- No se puede comparar versiones de prompts
- No se puede medir acuerdo entre evaluadores
- No hay gold standard para validar extracción de tareas

### 7.2. Moderados
- Sistema de roles inflexible
- No hay exportación de datos anonimizados para investigación
- No hay reproducción de análisis estadísticos

### 7.3. Menores
- UI de evaluación de resúmenes no existe
- No hay rúbrica de evaluación implementada
- No hay evaluación ciega de resúmenes

---

## 8. Problemas de Seguridad

### 8.1. Críticos
- Autorización por correo hardcodeado en `config.py` y `dependencies.py`
- No hay roles en base de datos
- No hay auditoría de acciones administrativas

### 8.2. Moderados
- Service role key necesaria para storage (aceptable pero debe documentarse)
- No hay validación de permisos a nivel de fila (RLS existe pero no se usa completamente)

### 8.3. Menores
- No hay límite de intentos de login
- No hay registro de IPs sospechosas

---

## 9. Oportunidades de Mejora

### 9.1. Para Evaluación Científica
- **ALTA PRIORIDAD:** Implementar tablas de evaluación
- **ALTA PRIORIDAD:** Sistema de roles en base de datos
- **ALTA PRIORIDAD:** Versionado de prompts
- **ALTA PRIORIDAD:** Registro de ejecuciones de IA
- **MEDIA:** Gold standard de tareas
- **MEDIA:** Evaluación SUS
- **MEDIA:** Acuerdo entre evaluadores

### 9.2. Para Seguridad
- **CRÍTICO:** Migrar a roles en base de datos
- **ALTA:** Auditoría de acciones
- **MEDIA:** Validación de permisos a nivel de fila
- **BAJA:** Rate limiting en login

### 9.3. Para Calidad de Código
- **MEDIA:** Expandir pruebas unitarias
- **MEDIA:** Agregar pruebas de integración
- **BAJA:** Configurar Playwright E2E

---

## 10. Dependencias Faltantes

### 10.1. Python
- Para estadísticas avanzadas: ya tiene NumPy, SciPy
- Para exportación Word: `python-docx` (opcional)
- Para exportación Excel: `openpyxl` o `xlsxwriter` (opcional)

### 10.2. Node.js
- Para formularios: ya tiene validación básica
- Para PDF en frontend: no necesario (backend ya genera PDF)
- Para Excel en frontend: `xlsx` (opcional)

### 10.3. Base de Datos
- No se requieren nuevas dependencias externas
- Todo se puede implementar con SQL estándar

---

## 11. Plan de Implementación por Fases

### Fase 0: Auditoría ✅ (COMPLETADO)
- Inspección técnica completa
- Documento de auditoría inicial
- Identificación de riesgos y deuda técnica

### Fase 1: Migraciones de Base de Datos
- Crear tabla de roles en `usuarios`
- Crear tabla `prompt_versions`
- Crear tabla `ai_executions`
- Crear tabla `summary_versions`
- Crear tabla `summary_evaluations`
- Crear tabla `reference_tasks`
- Crear tabla `task_evaluation_matches`
- Crear tabla `experiment_sessions`
- Crear tabla `time_measurements`
- Crear tabla `sus_responses`
- Crear tabla `performance_metrics`
- Crear tabla `audit_log`
- Crear índices necesarios
- Migrar usuarios existentes a roles

### Fase 2: Backend de Evaluación
- Implementar router de prompts
- Implementar router de ejecuciones IA
- Implementar router de evaluaciones
- Implementar router de experimentos
- Integrar con cliente Supabase existente
- Implementar validación de JSON estructurado

### Fase 3: Motor Estadístico Extendido
- Extender módulo statistics existente
- Implementar cálculo de acuerdo entre evaluadores (Kappa, ICC)
- Implementar análisis de gold standard (Precision, Recall, F1)
- Implementar análisis de tiempos (t-test pareado)
- Implementar análisis SUS
- Implementar correcciones por comparaciones múltiples (Bonferroni)

### Fase 4: Seguridad y Roles
- Migrar autorización hardcodeada a roles en BD
- Implementar middleware de roles
- Implementar auditoría de acciones
- Actualizar RLS policies
- Actualizar dependencias de autenticación

### Fase 5: Frontend de Evaluación
- Crear vista de gestión de prompts
- Crear vista de evaluación de resúmenes
- Implementar rúbrica interactiva
- Implementar evaluación ciega
- Crear vista de experimentos

### Fase 6: Frontend de Resultados
- Crear vista de análisis estadístico extendido
- Visualizar acuerdo entre evaluadores
- Visualizar métricas de gold standard
- Visualizar resultados SUS
- Implementar exportación de datos anonimizados

### Fase 7: Reportes Avanzados
- Implementar exportación Word
- Implementar exportación Excel
- Generar reportes de investigación
- Incluir metadatos de reproducibilidad

### Fase 8: Verificación y Pruebas
- Pruebas unitarias de nuevos módulos
- Pruebas de integración
- Pruebas E2E con Playwright
- Verificación de reproducibilidad de análisis
- Documentación final

---

## 12. Conclusiones

El proyecto Zoom2 tiene una **arquitectura sólida y bien organizada** con:

- Backend FastAPI modular y limpio
- Frontend Next.js moderno con App Router
- Sistema de métricas estadísticas ya implementado
- Cliente Supabase personalizado eficiente
- Buen sistema de diseño UI

**Sin embargo, para lograr el objetivo de evaluación científica, se requiere:**

1. **Infraestructura de datos experimental** (tablas nuevas)
2. **Sistema de roles robusto** (migración desde hardcode)
3. **Módulo de evaluación de calidad** (backend + frontend)
4. **Motor estadístico extendido** (acuerdo, gold standard, SUS)
5. **Auditoría y trazabilidad** (log de cambios)

La prioridad crítica es **Fase 1: Migraciones de Base de Datos**, ya que todas las demás fases dependen de la estructura de datos experimental.
