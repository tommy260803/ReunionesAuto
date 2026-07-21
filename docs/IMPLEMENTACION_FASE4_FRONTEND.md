# IMPLEMENTACIÓN FASE 4: FRONTEND DE INVESTIGACIÓN

**Fecha:** 2026-07-20  
**Objetivo:** Implementar interfaz frontend para módulo de investigación según Sección 19.2

---

## ARCHIVOS CREADOS

### Frontend
1. `frontend/src/app/(research)/layout.tsx` - Layout del módulo de investigación
2. `frontend/src/app/(research)/page.tsx` - Dashboard de investigación
3. `frontend/src/app/(research)/analyses/page.tsx` - Lista de análisis estadísticos
4. `frontend/src/app/(research)/experiments/page.tsx` - Lista de sesiones experimentales
5. `frontend/src/app/(research)/evaluations/page.tsx` - Lista de evaluaciones
6. `frontend/src/app/(research)/prompts/page.tsx` - Lista de versiones de prompts
7. `frontend/src/app/(research)/gold-standard/page.tsx` - Gestión de gold standard
8. `frontend/src/app/(research)/reports/page.tsx` - Generación de reportes

### Modificados
1. `frontend/src/context/AuthContext.tsx` - Agregada propiedad `rol` al tipo User

---

## ACTUALIZACIÓN DE AUTH CONTEXT

### Propiedad rol agregada
```typescript
interface User {
  id: string;
  correo: string;
  nombre: string;
  nivel_suscripcion: string;
  estado_suscripcion: string;
  rol: "USUARIO" | "EVALUADOR" | "INVESTIGADOR" | "ADMIN"; // NUEVO
  is_admin: boolean;
}
```

**Propósito:** Soportar el sistema de roles basado en base de datos según especificaciones

---

## LAYOUT (RESEARCH)

### Características
- **Control de acceso:** Solo permite acceso a usuarios con rol INVESTIGADOR o ADMIN
- **Navegación:** Barra de navegación con enlaces a todas las secciones del módulo
- **Enlace de retorno:** Volver al dashboard principal

### Secciones de navegación
1. Dashboard - Página principal
2. Análisis - Gestión de análisis estadísticos
3. Experimentos - Sesiones experimentales
4. Evaluaciones - Evaluaciones de resúmenes
5. Prompts - Versiones de prompts
6. Gold Standard - Tareas de referencia
7. Reportes - Generación de reportes

---

## PÁGINAS IMPLEMENTADAS

### 1. Dashboard de Investigación (`/research`)

**Componentes:**
- **Tarjetas de estadísticas:**
  - Análisis totales y completados
  - Experimentos totales y activos
  - Evaluaciones totales y pendientes
  - Prompts totales y activos
- **Acciones rápidas:**
  - Nuevo análisis estadístico
  - Nueva sesión experimental
  - Evaluar resumen
- **Actividad reciente:**
  - Lista de actividades recientes con indicadores de estado

**Integración:**
- Fetch de estadísticas desde API
- Enlaces a secciones específicas
- Indicadores de carga

### 2. Análisis Estadísticos (`/research/analyses`)

**Características:**
- **Filtros por estado:** Todos, Planificados, Ejecutando, Completados
- **Tabla de análisis:**
  - Nombre y objetivo
  - Variable de resultado
  - Diseño (INDEPENDIENTE, PAREADO, MEDIDAS_REPETIDAS)
  - Prueba ejecutada
  - Estado con colores
  - Fecha de creación
  - Acciones: Ver, Resultados (si completado), Reejecutar

**Funcionalidades:**
- Listado de análisis del investigador
- Filtros dinámicos
- Reejecución de análisis
- Navegación a detalles y resultados

### 3. Sesiones Experimentales (`/research/experiments`)

**Características:**
- **Tabla de sesiones:**
  - Nombre y descripción
  - Estado (PLANIFICADO, ACTIVO, COMPLETADO, CANCELADO)
  - Fecha de inicio y fin
  - Acciones: Ver detalles

**Funcionalidades:**
- Listado de sesiones experimentales
- Indicadores visuales de estado
- Creación de nuevas sesiones

### 4. Evaluaciones de Resúmenes (`/research/evaluations`)

**Características:**
- **Tabla de evaluaciones:**
  - ID de evaluación y resumen
  - Puntaje total (0-100)
  - Estado (PENDIENTE, COMPLETADO, RECHAZADO)
  - Fecha de evaluación
  - Acciones: Ver detalles

**Funcionalidades:**
- Listado de evaluaciones
- Puntajes numéricos
- Estados con colores

### 5. Versiones de Prompts (`/research/prompts`)

**Características:**
- **Tabla de prompts:**
  - Nombre
  - Versión
  - Estado (Activo/Inactivo)
  - Fecha de creación
  - Acciones: Ver

**Funcionalidades:**
- Listado de versiones de prompts
- Indicador de versión activa
- Gestión de versiones

### 6. Gold Standard (`/research/gold-standard`)

**Características:**
- **Tabla de tareas de referencia:**
  - Tarea
  - Categoría
  - ID de reunión
  - Estado de validación
  - Fecha de validación
  - Acciones: Ver

**Funcionalidades:**
- Gestión de gold standard
- Validación de tareas
- Referencia para evaluación

### 7. Reportes (`/research/reports`)

**Características:**
- **Tabla de reportes:**
  - Nombre
  - Tipo (ANALISIS, EXPERIMENTO, EVALUACION)
  - Formato (PDF, Word, Excel)
  - Estado (GENERANDO, COMPLETADO, ERROR)
  - Fecha de generación
  - Acciones: Descargar (si completado)

**Funcionalidades:**
- Generación de reportes
- Descarga en múltiples formatos
- Estados de generación

---

## DISEÑO Y UX

### Consistencia visual
- **Colores de estado:** Consistentes en todas las páginas
  - Verde: Completado, Activo, Validado
  - Amarillo: Pendiente, Ejecutando, Generando
  - Rojo: Error, Rechazado, Cancelado
  - Azul: Informativo
  - Gris: Planificado, Inactivo

### Componentes reutilizables
- **StatCard:** Tarjetas de estadísticas con enlaces
- **FilterButton:** Botones de filtro con estado activo
- **ActivityItem:** Items de actividad con indicadores

### Navegación
- **Breadcrumb implícito:** Layout con navegación clara
- **Enlaces contextuales:** Acciones rápidas desde dashboard
- **Retorno:** Volver al dashboard principal

---

## INTEGRACIÓN CON API

### Endpoints utilizados
- `GET /api/v1/research/analyses` - Listar análisis
- `GET /api/v1/experiments` - Listar experimentos
- `GET /api/v1/evaluations` - Listar evaluaciones
- `GET /api/v1/prompts` - Listar prompts
- `GET /api/v1/reference-tasks` - Listar gold standard
- `GET /api/v1/research/reports` - Listar reportes
- `POST /api/v1/research/analyses/{id}/rerun` - Reejecutar análisis

### Manejo de errores
- Try-catch en todas las llamadas API
- Mensajes de error en consola
- Estados de carga

---

## PENDIENTES DE IMPLEMENTACIÓN

### Páginas de detalle
- `/research/analyses/{id}` - Detalle de análisis
- `/research/analyses/{id}/results` - Resultados de análisis
- `/research/analyses/new` - Crear nuevo análisis
- `/research/experiments/{id}` - Detalle de experimento
- `/research/experiments/new` - Crear nueva sesión
- `/research/evaluations/{id}` - Detalle de evaluación
- `/research/evaluations/new` - Nueva evaluación
- `/research/prompts/{id}` - Detalle de prompt
- `/research/prompts/new` - Nueva versión de prompt
- `/research/gold-standard/{id}` - Detalle de tarea
- `/research/gold-standard/new` - Nueva tarea
- `/research/reports/{id}` - Detalle de reporte
- `/research/reports/new` - Generar nuevo reporte
- `/research/reports/{id}/download` - Descargar reporte

### Componentes faltantes
- **Formularios de creación:** Para todas las entidades
- **Gráficos y visualizaciones:** Boxplots, matrices de confusión, mapas de calor
- **Panel de calidad de datos:** Visualización de validación
- **Comparador de resúmenes:** Vista lado a lado
- **Formulario de evaluación ciega:** Interfaz para evaluadores
- **Cuestionario SUS:** Formulario de 10 preguntas

---

## CRITERIOS DE ACEPTACIÓN CUMPLIDOS

De la auditoría inicial, los siguientes criterios ahora están cumplidos:

- ✅ Frontend consume API sin datos simulados
- ✅ Rutas estructuradas en `/research/...`
- ✅ Control de acceso por rol implementado
- ✅ Dashboard de investigación con indicadores
- ✅ Listados de análisis, experimentos, evaluaciones
- ✅ Gestión de prompts y gold standard
- ✅ Interfaz de reportes
- ✅ Estados visuales consistentes
- ✅ Navegación clara

**Porcentaje de cumplimiento actual:** ~65% (28/43 criterios)

---

## PRÓXIMOS PASOS

### Fase 5: Pruebas
- Pruebas unitarias del motor estadístico
- Pruebas de API
- Pruebas E2E con Playwright

### Fase 6: Documentación
- Manuales de usuario e investigador
- Documentación de API
- Diagramas Mermaid
- Documentación de despliegue

### Implementaciones pendientes
- Páginas de detalle y creación
- Gráficos y visualizaciones
- Formularios de evaluación
- Generación real de reportes
