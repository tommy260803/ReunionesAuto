# Implementación Fase 1: Migraciones de Base de Datos

**Estado:** COMPLETADO  
**Fecha:** 2026-07-20  
**Script:** `querys para supabase/query9_evaluacion_cientifica.sql`

---

## Objetivo

Crear la infraestructura de datos necesaria para el módulo de evaluación científica y estadística del sistema Zoom2.

---

## Cambios Realizados

### 1. Sistema de Roles en Usuarios

**Cambio:** Agregar columna `rol` a tabla `usuarios`

```sql
ALTER TABLE usuarios 
ADD COLUMN IF NOT EXISTS rol VARCHAR(20) NOT NULL DEFAULT 'USUARIO';
```

**Tipo de datos:** VARCHAR(20) con valores permitidos:
- `ADMIN` - Administrador del sistema
- `INVESTIGADOR` - Puede crear experimentos y gestionar prompts
- `EVALUADOR` - Puede evaluar resúmenes
- `USUARIO` - Usuario estándar

**Migración de datos existentes:**
- El correo hardcodeado `juanaureliodelacruzgamarra@gmail.com` se convierte en `ADMIN`
- Los demás usuarios permanecen como `USUARIO`

**Impacto:** Prepara el sistema para eliminar la autorización hardcodeada en Fase 6.

---

### 2. Tabla `prompt_versions`

**Propósito:** Almacenar versiones de prompts de IA con control de cambios.

**Columnas principales:**
- `id` (UUID, PK)
- `nombre` (VARCHAR) - Nombre del prompt (ej: "resumen_reunion")
- `version` (VARCHAR) - Versión semántica (ej: "1.0", "1.1", "2.0")
- `contenido` (TEXT) - Contenido completo del prompt
- `objetivo` (TEXT) - Descripción del propósito
- `proveedor` (VARCHAR) - Proveedor de IA (openai, groq, etc.)
- `modelo_recomendado` (VARCHAR) - Modelo recomendado
- `activo` (BOOLEAN) - Si está activo para uso
- `creado_por` (UUID, FK → usuarios)
- `fecha_creacion` (TIMESTAMPTZ)

**Restricciones:**
- `UNIQUE(nombre, version)` - No puede haber duplicados de nombre+versión

**Índices:**
- `idx_prompt_versions_nombre` - Búsqueda por nombre
- `idx_prompt_versions_activo` - Filtrar prompts activos
- `idx_prompt_versions_creado_por` - Auditoría por creador

**Uso:** Permite comparar versiones de prompts y asociar cada ejecución de IA con la versión exacta utilizada.

---

### 3. Tabla `ai_executions`

**Propósito:** Registrar cada llamada a modelos de IA con parámetros completos.

**Columnas principales:**
- `id` (UUID, PK)
- `reunion_id` (UUID, FK → reuniones)
- `prompt_version_id` (UUID, FK → prompt_versions)
- `proveedor` (VARCHAR) - openai, groq, etc.
- `modelo` (VARCHAR) - gpt-4, llama-3, etc.
- `temperatura` (NUMERIC) - Parámetro de temperatura
- `parametros` (JSONB) - Parámetros adicionales
- `workflow_version` (VARCHAR) - Versión del workflow n8n
- `input_hash` (VARCHAR) - Hash para detectar duplicados
- `respuesta_original` (TEXT) - Respuesta cruda del modelo
- `respuesta_procesada` (JSONB) - Respuesta estructurada
- `tokens_entrada` (INTEGER) - Tokens de entrada
- `tokens_salida` (INTEGER) - Tokens de salida
- `costo_estimado` (NUMERIC) - Costo en USD
- `tiempo_ms` (INTEGER) - Tiempo de ejecución
- `reintentos` (INTEGER) - Número de reintentos
- `estado` (VARCHAR) - Estado de la ejecución
- `tipo_error` (VARCHAR) - Tipo de error si falló
- `mensaje_error` (TEXT) - Mensaje de error detallado
- `iniciado_por` (UUID, FK → usuarios)
- `fecha_inicio` (TIMESTAMPTZ)
- `fecha_fin` (TIMESTAMPTZ)

**Índices:**
- `idx_ai_executions_reunion` - Búsqueda por reunión
- `idx_ai_executions_prompt_version` - Análisis por versión de prompt
- `idx_ai_executions_estado` - Filtrar por estado
- `idx_ai_executions_fecha_inicio` - Análisis temporal
- `idx_ai_executions_modelo` - Comparación por modelo

**Uso:** Permite análisis de rendimiento, costos, comparación de modelos y reproducibilidad de ejecuciones.

---

### 4. Tabla `summary_versions`

**Propósito:** Versionado de resúmenes con control de cambios y estados.

**Columnas principales:**
- `id` (UUID, PK)
- `reunion_id` (UUID, FK → reuniones)
- `ai_execution_id` (UUID, FK → ai_executions)
- `version` (INTEGER) - Número de versión
- `origen` (VARCHAR) - IA, HUMANO, REGENERACION, IMPORTACION
- `contenido` (TEXT) - Resumen en texto plano
- `contenido_estructurado` (JSONB) - Resumen estructurado
- `estado` (VARCHAR) - GENERADO, PENDIENTE_REVISION, EN_REVISION, APROBADO, RECHAZADO, PUBLICADO, ARCHIVADO
- `es_version_actual` (BOOLEAN) - Si es la versión activa
- `creado_por` (UUID, FK → usuarios)
- `fecha_creacion` (TIMESTAMPTZ)

**Restricciones:**
- `check_origen` - Valores permitidos para origen
- `check_estado_resumen` - Valores permitidos para estado
- `UNIQUE(reunion_id, version)` - Una versión por número por reunión

**Índices:**
- `idx_summary_versions_reunion` - Historial por reunión
- `idx_summary_versions_ai_execution` - Trazabilidad a ejecución IA
- `idx_summary_versions_estado` - Filtrar por estado
- `idx_summary_versions_actual` - Obtener versión actual

**Uso:** Permite flujo de aprobación, comparación de versiones y auditoría de cambios.

---

### 5. Tabla `summary_evaluations`

**Propósito:** Evaluaciones de calidad de resúmenes por múltiples evaluadores.

**Columnas principales:**
- `id` (UUID, PK)
- `reunion_id` (UUID, FK → reuniones)
- `summary_version_id` (UUID, FK → summary_versions)
- `evaluador_id` (UUID, FK → usuarios)
- `fidelidad` (SMALLINT 1-5) - Fidelidad al contenido original
- `cobertura` (SMALLINT 1-5) - Cobertura de temas importantes
- `claridad` (SMALLINT 1-5) - Claridad del resumen
- `coherencia` (SMALLINT 1-5) - Coherencia interna
- `concision` (SMALLINT 1-5) - Concisión apropiada
- `utilidad` (SMALLINT 1-5) - Utilidad práctica
- `acuerdos_correctos` (SMALLINT 1-5) - Identificación correcta de acuerdos
- `responsables_correctos` (SMALLINT 1-5) - Identificación correcta de responsables
- `fechas_correctas` (SMALLINT 1-5) - Identificación correcta de fechas
- `omisiones` (INTEGER) - Conteo de omisiones
- `afirmaciones_no_respaldadas` (INTEGER) - Afirmaciones sin evidencia
- `contradicciones` (INTEGER) - Contradicciones detectadas
- `aprobado_sin_cambios` (BOOLEAN) - Si se aprobó sin editar
- `observaciones` (TEXT) - Comentarios del evaluador
- `fecha_evaluacion` (TIMESTAMPTZ)

**Restricciones:**
- CHECKs para escalas 1-5
- `UNIQUE(summary_version_id, evaluador_id)` - Un evaluador por versión

**Índices:**
- `idx_summary_evaluations_reunion` - Evaluaciones por reunión
- `idx_summary_evaluations_summary_version` - Por versión de resumen
- `idx_summary_evaluations_evaluador` - Por evaluador
- `idx_summary_evaluations_fecha` - Análisis temporal

**Uso:** Permite cálculo de acuerdo entre evaluadores, análisis de calidad y rúbrica estructurada.

---

### 6. Tabla `reference_tasks`

**Propósito:** Gold standard de tareas para validación de extracción.

**Columnas principales:**
- `id` (UUID, PK)
- `reunion_id` (UUID, FK → reuniones)
- `descripcion` (TEXT) - Descripción de la tarea
- `responsable_referencia` (TEXT) - Responsable correcto
- `fecha_limite_referencia` (DATE) - Fecha límite correcta
- `creado_por` (UUID, FK → usuarios)
- `validado` (BOOLEAN) - Si está validado como gold standard
- `fecha_creacion` (TIMESTAMPTZ)

**Índices:**
- `idx_reference_tasks_reunion` - Tareas por reunión
- `idx_reference_tasks_creado_por` - Por creador
- `idx_reference_tasks_validado` - Filtrar gold standard

**Uso:** Permite calcular precision, recall y F1 de extracción de tareas por IA.

---

### 7. Tabla `task_evaluation_matches`

**Propósito:** Coincidencias entre tareas detectadas y gold standard.

**Columnas principales:**
- `id` (UUID, PK)
- `reunion_id` (UUID, FK → reuniones)
- `ai_execution_id` (UUID, FK → ai_executions)
- `reference_task_id` (UUID, FK → reference_tasks)
- `detected_task_id` (UUID, FK → tareas)
- `resultado` (VARCHAR) - TP, FP, FN, TN
- `similitud` (NUMERIC) - Puntuación de similitud
- `validado_por` (UUID, FK → usuarios)
- `observaciones` (TEXT)
- `fecha_registro` (TIMESTAMPTZ)

**Restricciones:**
- `check_resultado` - Valores permitidos: TP, FP, FN, TN

**Índices:**
- `idx_task_matches_reunion` - Por reunión
- `idx_task_matches_ai_execution` - Por ejecución IA
- `idx_task_matches_reference` - Por tarea de referencia
- `idx_task_matches_detected` - Por tarea detectada
- `idx_task_matches_resultado` - Por tipo de resultado

**Uso:** Permite cálculo de métricas de extracción: precision, recall, F1.

---

### 8. Tabla `experiment_sessions`

**Propósito:** Sesiones experimentales para comparar condiciones.

**Columnas principales:**
- `id` (UUID, PK)
- `nombre` (VARCHAR) - Nombre del experimento
- `descripcion` (TEXT) - Descripción detallada
- `investigador_id` (UUID, FK → usuarios)
- `condicion` (VARCHAR) - manual, zoom2_base, zoom2_mejorado, etc.
- `prompt_version_id` (UUID, FK → prompt_versions)
- `modelo` (VARCHAR) - Modelo utilizado
- `fecha_inicio` (TIMESTAMPTZ)
- `fecha_fin` (TIMESTAMPTZ)
- `configuracion` (JSONB) - Configuración adicional
- `estado` (VARCHAR) - PLANIFICADO, EN_CURSO, COMPLETADO, CANCELADO

**Restricciones:**
- `check_estado_experiment` - Estados permitidos

**Índices:**
- `idx_experiment_sessions_investigador` - Por investigador
- `idx_experiment_sessions_condicion` - Por condición experimental
- `idx_experiment_sessions_estado` - Por estado
- `idx_experiment_sessions_fecha_inicio` - Análisis temporal

**Uso:** Permite diseño experimental controlado y comparación de condiciones.

---

### 9. Tabla `time_measurements`

**Propósito:** Mediciones de tiempo para comparar manual vs automatizado.

**Columnas principales:**
- `id` (UUID, PK)
- `experiment_session_id` (UUID, FK → experiment_sessions)
- `reunion_id` (UUID, FK → reuniones)
- `participante_id` (UUID, FK → usuarios)
- `condicion` (VARCHAR) - Condición experimental
- `tiempo_elaboracion_segundos` (INTEGER) - Tiempo de elaboración
- `tiempo_revision_segundos` (INTEGER) - Tiempo de revisión
- `tiempo_total_segundos` (INTEGER) - Tiempo total
- `errores_detectados` (INTEGER) - Errores detectados
- `fecha_registro` (TIMESTAMPTZ)

**Índices:**
- `idx_time_measurements_session` - Por sesión experimental
- `idx_time_measurements_reunion` - Por reunión
- `idx_time_measurements_participante` - Por participante
- `idx_time_measurements_condicion` - Por condición

**Uso:** Permite análisis estadístico de reducción de tiempo (t-test pareado).

---

### 10. Tabla `sus_responses`

**Propósito:** Respuestas del cuestionario SUS de usabilidad.

**Columnas principales:**
- `id` (UUID, PK)
- `experiment_session_id` (UUID, FK → experiment_sessions)
- `usuario_id` (UUID, FK → usuarios)
- `q1` a `q10` (SMALLINT 1-5) - Respuestas a 10 preguntas
- `puntaje_sus` (NUMERIC) - Puntaje calculado (0-100)
- `observaciones` (TEXT)
- `fecha_registro` (TIMESTAMPTZ)

**Funciones:**
- `calcular_puntaje_sus()` - Calcula puntaje SUS automáticamente
- Trigger `trg_calcular_sus` - Calcula puntaje al insertar/actualizar

**Índices:**
- `idx_sus_responses_session` - Por sesión experimental
- `idx_sus_responses_usuario` - Por usuario
- `idx_sus_responses_fecha` - Análisis temporal

**Uso:** Permite evaluación de usabilidad con metodología SUS estandarizada.

---

### 11. Tabla `performance_metrics`

**Propósito:** Métricas de rendimiento detalladas por componente.

**Columnas principales:**
- `id` (UUID, PK)
- `reunion_id` (UUID, FK → reuniones)
- `ai_execution_id` (UUID, FK → ai_executions)
- `componente` (VARCHAR) - Componente del sistema
- `operacion` (VARCHAR) - Operación específica
- `duracion_ms` (INTEGER) - Duración en milisegundos
- `exitoso` (BOOLEAN) - Si fue exitoso
- `codigo_estado` (VARCHAR) - Código HTTP o de error
- `mensaje_error` (TEXT)
- `metadata` (JSONB) - Metadatos adicionales
- `fecha_registro` (TIMESTAMPTZ)

**Índices:**
- `idx_performance_metrics_reunion` - Por reunión
- `idx_performance_metrics_ai_execution` - Por ejecución IA
- `idx_performance_metrics_componente` - Por componente
- `idx_performance_metrics_fecha` - Análisis temporal

**Uso:** Permite análisis de rendimiento y cuellos de botella.

---

### 12. Tabla `audit_log`

**Propósito:** Auditoría de acciones sensibles en el sistema.

**Columnas principales:**
- `id` (UUID, PK)
- `usuario_id` (UUID, FK → usuarios)
- `accion` (VARCHAR) - Acción realizada
- `entidad` (VARCHAR) - Tipo de entidad afectada
- `entidad_id` (UUID) - ID de la entidad
- `datos_anteriores` (JSONB) - Estado anterior
- `datos_nuevos` (JSONB) - Estado nuevo
- `ip_hash` (VARCHAR) - Hash de IP para trazabilidad
- `fecha` (TIMESTAMPTZ)

**Índices:**
- `idx_audit_log_usuario` - Por usuario
- `idx_audit_log_accion` - Por tipo de acción
- `idx_audit_log_entidad` - Por tipo de entidad
- `idx_audit_log_fecha` - Análisis temporal

**Uso:** Permite auditoría de seguridad, trazabilidad y reproducibilidad.

---

## Row Level Security (RLS)

Se habilitó RLS en todas las tablas nuevas con políticas de acceso completo para autenticados. Estas políticas se refinarán en Fase 6 cuando se implemente el sistema de roles completo.

**Políticas actuales (temporales):**
- `full_access_*` - Acceso completo para usuarios autenticados

**Próximos pasos (Fase 6):**
- Implementar políticas basadas en roles
- Restringir acceso a datos experimentales
- Implementar aislamiento por investigador

---

## Datos Iniciales de Prueba

Se insertó un prompt de ejemplo en `prompt_versions`:

```sql
INSERT INTO prompt_versions (nombre, version, contenido, objetivo, proveedor, modelo_recomendado, activo)
VALUES (
    'resumen_reunion',
    '1.0',
    'Genera un resumen estructurado de la reunión incluyendo: título, resumen ejecutivo, temas principales, decisiones, acuerdos con responsables y fechas, riesgos identificados y preguntas pendientes.',
    'Generar resúmenes de reuniones con estructura JSON',
    'openai',
    'gpt-4',
    true
);
```

---

## Verificación

El script incluye una consulta de verificación que muestra el conteo de registros en cada tabla nueva.

---

## Próximos Pasos

**Fase 2: Backend de Evaluación**
- Implementar router de prompts
- Implementar router de ejecuciones IA
- Implementar router de evaluaciones
- Implementar router de experimentos
- Integrar con cliente Supabase existente

---

## Notas de Implementación

1. **Compatibilidad:** Todas las tablas usan UUID como PK para consistencia con el esquema existente.
2. **Referencias:** Las FKs tienen `ON DELETE CASCADE` o `SET NULL` según corresponda.
3. **Índices:** Se crearon índices estratégicos para las consultas más comunes.
4. **Validaciones:** Se implementaron CHECK constraints para garantizar integridad de datos.
5. **RLS:** Políticas básicas temporales, se refinarán con roles en Fase 6.
6. **Funciones:** Se implementó función y trigger para cálculo automático de puntaje SUS.

---

## Estado

✅ **COMPLETADO** - Script SQL generado y listo para ejecución en Supabase.
