# IMPLEMENTACIÓN FASE 3: BACKEND API DE ANÁLISIS ESTADÍSTICO

**Fecha:** 2026-07-20  
**Objetivo:** Implementar endpoints de API para análisis estadístico según Sección 19.1

---

## ARCHIVOS CREADOS

### Backend
1. `backend/app/analyses/__init__.py` - Módulo de análisis estadístico
2. `backend/app/analyses/schemas.py` - Schemas Pydantic para análisis
3. `backend/app/analyses/router.py` - Router FastAPI para análisis

### Modificados
1. `backend/app/main.py` - Integración del router de análisis

---

## SCHEMAS PYDANTIC

### StatisticalAnalysisCreate
- **Propósito:** Crear nuevo análisis estadístico
- **Campos:**
  - `nombre`: Nombre del análisis (1-180 caracteres)
  - `objetivo`: Objetivo del análisis (opcional)
  - `variable_resultado`: Variable de resultado (obligatorio)
  - `variable_grupo`: Variable de agrupación (opcional)
  - `diseno`: INDEPENDIENTE, PAREADO, MEDIDAS_REPETIDAS
  - `prueba_solicitada`: Prueba solicitada (opcional)
  - `alpha`: Nivel de significancia (0.001-0.999, default 0.05)
  - `correccion_multiple`: BONFERRONI, HOLM, NONE
  - `filtros`: JSONB con filtros aplicados
  - `configuracion`: JSONB con configuración adicional

### StatisticalAnalysisUpdate
- **Propósito:** Actualizar análisis existente
- **Campos:** Todos opcionales, solo actualiza los proporcionados

### StatisticalAnalysisResponse
- **Propósito:** Respuesta de análisis
- **Campos:** Todos los campos de la tabla `statistical_analyses`

### DataQualityValidationRequest
- **Propósito:** Solicitud de validación de calidad de datos
- **Campos:**
  - `data`: Datos a validar
  - `test_type`: Tipo de prueba estadística
  - `design`: independent, paired, repeated_measures
  - `min_observations`: Mínimo de observaciones (default 5)

### DataQualityValidationResponse
- **Propósito:** Respuesta de validación
- **Campos:**
  - `status`: ok, warnings, invalid_data, insufficient_data
  - `can_proceed`: Indicador de si puede proceder
  - `warnings`: Lista de advertencias
  - `errors`: Lista de errores críticos
  - `quality_report`: Reporte detallado de calidad

### AnalysisResultResponse
- **Propósito:** Respuesta de resultados de análisis
- **Campos:** Todos los campos de la tabla `statistical_analysis_results`

---

## ENDPOINTS IMPLEMENTADOS

### POST /api/v1/research/analyses/validate
- **Propósito:** Validar calidad de datos antes de análisis
- **Auth:** Requiere autenticación
- **Request:** `DataQualityValidationRequest`
- **Response:** `DataQualityValidationResponse`
- **Lógica:**
  - Llama a `validate_data_quality()` del motor estadístico
  - Realiza verificaciones según Sección 17.1.2
  - Retorna reporte con advertencias y errores

### POST /api/v1/research/analyses
- **Propósito:** Crear nuevo análisis estadístico
- **Auth:** Requiere rol INVESTIGADOR o ADMIN
- **Request:** `StatisticalAnalysisCreate`
- **Response:** `StatisticalAnalysisResponse` (201)
- **Lógica:**
  - Genera hash SHA256 de filtros+configuración
  - Inserta en tabla `statistical_analyses`
  - Estado inicial: PLANIFICADO

### GET /api/v1/research/analyses
- **Propósito:** Listar análisis del investigador
- **Auth:** Requiere rol INVESTIGADOR o ADMIN
- **Query params:**
  - `experiment_session_id`: Filtrar por sesión (opcional)
  - `estado`: Filtrar por estado (opcional)
- **Response:** Lista de `StatisticalAnalysisResponse`
- **Lógica:**
  - Filtra por investigador actual
  - Aplica filtros opcionales
  - Ordena por fecha descendente

### GET /api/v1/research/analyses/{id}
- **Propósito:** Obtener análisis específico
- **Auth:** Requiere rol INVESTIGADOR o ADMIN
- **Response:** `StatisticalAnalysisResponse`
- **Lógica:**
  - Verifica que el análisis exista
  - Verifica que el usuario sea creador o admin

### PATCH /api/v1/research/analyses/{id}
- **Propósito:** Actualizar análisis existente
- **Auth:** Requiere rol INVESTIGADOR o ADMIN
- **Request:** `StatisticalAnalysisUpdate`
- **Response:** `StatisticalAnalysisResponse`
- **Lógica:**
  - Verifica permisos
  - Actualiza solo campos proporcionados
  - Hash se actualiza automáticamente via trigger

### POST /api/v1/research/analyses/{id}/rerun
- **Propósito:** Reejecutar análisis existente
- **Auth:** Requiere rol INVESTIGADOR o ADMIN
- **Request:** `AnalysisRerunRequest`
- **Response:** `StatisticalAnalysisResponse`
- **Lógica:**
  - Verifica permisos
  - Actualiza estado a EJECUTANDO
  - Ejecuta análisis (TODO: implementar lógica real)
  - Actualiza estado a COMPLETADO
  - Registra fecha_ejecucion

### GET /api/v1/research/analyses/{id}/results
- **Propósito:** Obtener resultados de análisis
- **Auth:** Requiere rol INVESTIGADOR o ADMIN
- **Response:** `AnalysisResultResponse`
- **Lógica:**
  - Verifica permisos
  - Busca resultados en `statistical_analysis_results`
  - Retorna 404 si no hay resultados

---

## INTEGRACIÓN CON MAIN.PY

### Importaciones agregadas
```python
from app.analyses.router import router as analyses_router
```

### Router incluido
```python
app.include_router(analyses_router)
```

---

## CONTROL DE ACCESO

### Dependencias utilizadas
- `get_current_user`: Verifica autenticación básica
- `get_current_investigator`: Verifica rol INVESTIGADOR o ADMIN

### Permisos por endpoint
- **validate:** Todos autenticados
- **create, update, rerun:** INVESTIGADOR o ADMIN
- **list, get, results:** INVESTIGADOR (solo propios) o ADMIN (todos)

---

## PENDIENTES DE IMPLEMENTACIÓN

### Lógica de ejecución real
El endpoint `rerun` actualmente simula la ejecución. Se necesita implementar:

1. **Selector automático de prueba** (Sección 18)
   - Analizar tipo de variable
   - Analizar número de condiciones
   - Analizar diseño (pareado/independiente)
   - Sugerir prueba apropiada

2. **Ejecución de pruebas estadísticas**
   - Mapear `prueba_ejecutada` a función del motor estadístico
   - Ejecutar prueba con parámetros de configuración
   - Aplicar corrección múltiple si corresponde

3. **Persistencia de resultados**
   - Guardar resultado en `statistical_analysis_results`
   - Incluir descriptivos, supuestos, efectos, intervalos
   - Generar interpretación controlada (Sección 19)

4. **Manejo de errores**
   - Capturar errores de ejecución
   - Actualizar estado a ERROR
   - Guardar mensaje de error

### Endpoints faltantes
Según Sección 19.1, aún faltan:

**Reportes y exportaciones:**
- `POST /api/v1/research/reports` - Generar reporte
- `GET /api/v1/research/reports/{id}` - Obtener reporte
- `GET /api/v1/research/exports/data` - Exportar datos anonimizados

---

## DEPENDENCIAS

No se requieren nuevas dependencias. Se utilizan:
- `pydantic` - Validación de schemas
- `fastapi` - Framework API
- Supabase client - Persistencia

---

## CRITERIOS DE ACEPTACIÓN CUMPLIDOS

De la auditoría inicial, los siguientes criterios ahora están cumplidos:

- ✅ OpenAPI documenta endpoints de investigación
- ✅ Control de acceso por rol implementado
- ✅ Validación Pydantic en todos los endpoints
- ✅ Respuestas tipadas
- ✅ Códigos HTTP correctos
- ✅ Errores con mensajes utilizables

**Porcentaje de cumplimiento actual:** ~50% (22/43 criterios)

---

## PRÓXIMOS PASOS

### Fase 4: Frontend
- Reestructurar rutas a `/research/...`
- Implementar dashboard de investigación
- Implementar vista de análisis estadísticos
- Implementar gráficos y visualizaciones

### Fase 5: Pruebas
- Pruebas unitarias del motor estadístico
- Pruebas de API
- Pruebas E2E

### Fase 6: Documentación
- Manuales de usuario e investigador
- Documentación de API
- Diagramas Mermaid
