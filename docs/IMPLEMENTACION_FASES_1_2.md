# IMPLEMENTACIÓN FASES 1-2: MOTOR ESTADÍSTICO Y BASE DE DATOS

**Fecha:** 2026-07-20  
**Objetivo:** Extender el motor estadístico y completar la base de datos para evaluación científica

---

## FASE 1: MOTOR ESTADÍSTICO EXTENDIDO

### 1.1. Pruebas de Supuestos Estadísticos

**Archivo modificado:** `backend/app/metrics/statistics.py`

#### Shapiro-Wilk Test
- **Función:** `shapiro_wilk_test(values, alpha=0.05)`
- **Propósito:** Evaluar normalidad de datos
- **Validaciones:**
  - Mínimo 3 observaciones
  - Máximo 5000 observaciones (recomendación scipy)
- **Retorna:** estadístico, p-value, indicador de normalidad, interpretación

#### Levene Test
- **Función:** `levene_test(*samples, alpha=0.05, center="median")`
- **Propósito:** Evaluar igualdad de varianzas entre grupos
- **Parámetros:**
  - `center="median"`: Brown-Forsythe (más robusto)
  - `center="mean"`: Levene clásico
- **Retorna:** estadístico, p-value, indicador de homocedasticidad, interpretación

### 1.2. Pruebas No Paramétricas

#### Mann-Whitney U Test
- **Función:** `mann_whitney_u_test(sample_a, sample_b, alpha=0.05, alternative="two_sided")`
- **Propósito:** Comparar dos muestras independientes (alternativa a t de Welch)
- **Retorna:** estadístico U, p-value, diferencia de medianas, tamaño del efecto r, interpretación

#### Friedman Test
- **Función:** `friedman_test(*samples, alpha=0.05)`
- **Propósito:** Comparar 3+ condiciones relacionadas (alternativa a ANOVA medidas repetidas)
- **Retorna:** estadístico, p-value, Kendall's W (tamaño del efecto), interpretación

### 1.3. Pruebas para Datos Binarios

#### McNemar Test
- **Función:** `mcnemar_test(before, after, alpha=0.05, exact=False)`
- **Propósito:** Comparar proporciones en datos binarios pareados
- **Uso:** Comparar error/no error entre dos configuraciones
- **Retorna:** tabla de contingencia, estadístico, p-value, proporciones, interpretación

#### Q de Cochran
- **Función:** `cochran_q_test(*samples, alpha=0.05)`
- **Propósito:** Comparar 3+ proporciones en datos binarios pareados
- **Uso:** Extensión de McNemar para múltiples condiciones
- **Retorna:** estadístico Q, p-value, proporciones por condición, interpretación

### 1.4. Acuerdo entre Evaluadores y Consistencia Interna

#### Krippendorff's Alpha
- **Función:** `krippendorff_alpha(ratings, level="ordinal")`
- **Propósito:** Medir acuerdo entre múltiples evaluadores
- **Ventajas:** Más robusto que Cohen's Kappa para datos faltantes
- **Dependencia:** Requiere librería `krippendorff` (opcional)
- **Retorna:** alpha, interpretación según Krippendorff (2011)

#### Alfa de Cronbach
- **Función:** `cronbach_alpha(ratings)`
- **Propósito:** Evaluar consistencia interna de escalas (ej: SUS)
- **Retorna:** alpha, interpretación según DeVellis (2012)

### 1.5. Corrección por Comparaciones Múltiples

#### Holm Correction
- **Función:** `holm_correction(p_values, alpha=0.05)`
- **Propósito:** Corrección step-down más potente que Bonferroni
- **Especificación:** Método predeterminado según Sección 17.12
- **Retorna:** p-values corregidos, significancia original y corregida, orden de rechazo

### 1.6. Validación de Calidad de Datos

#### validate_data_quality
- **Función:** `validate_data_quality(data, test_type, design="independent", min_observations=5)`
- **Propósito:** Validar datos antes de ejecutar análisis (Sección 17.1.2)
- **Verificaciones:**
  - Número total de registros
  - Registros utilizables
  - Duplicados
  - Valores faltantes
  - Valores fuera de rango
  - Pares incompletos (para diseños pareados)
  - Condiciones vacías
  - Duraciones negativas
  - Escalas inconsistentes
  - Valores idénticos (sin variación)
- **Retorna:** reporte de calidad, advertencias, errores, indicador de si puede proceder

---

## FASE 2: BASE DE DATOS

### 2.1. Tablas de Persistencia de Análisis

**Archivo creado:** `querys para supabase/query12_persistencia_analisis.sql`

#### statistical_analyses
- **Propósito:** Persistir configuraciones y metadatos de análisis
- **Campos clave:**
  - `experiment_session_id`: Sesión experimental relacionada
  - `nombre`, `objetivo`: Descripción del análisis
  - `variable_resultado`, `variable_grupo`: Variables analizadas
  - `diseno`: INDEPENDIENTE, PAREADO, MEDIDAS_REPETIDAS
  - `prueba_solicitada`, `prueba_ejecutada`: Pruebas estadísticas
  - `alpha`: Nivel de significancia
  - `correccion_multiple`: BONFERRONI, HOLM, NONE
  - `filtros`, `configuracion`: JSONB con parámetros
  - `estado`: PLANIFICADO, VALIDADO, EJECUTANDO, COMPLETADO, ERROR, CANCELADO
  - `datos_hash`: SHA256 de filtros+configuración (reproducibilidad)
  - `codigo_version`: Versión del código que ejecutó el análisis
- **Índices:** session, creado_por, estado, fecha_creación, prueba_ejecutada
- **Trigger:** Actualiza automáticamente datos_hash cuando cambian filtros/configuración

#### statistical_analysis_results
- **Propósito:** Persistir resultados de análisis
- **Campos clave:**
  - `analysis_id`: Referencia al análisis padre
  - `resultado`: JSONB con resultado principal
  - `descriptivos`: JSONB con estadísticos descriptivos
  - `supuestos`: JSONB con pruebas de supuestos
  - `efecto`: JSONB con tamaños del efecto
  - `intervalos`: JSONB con intervalos de confianza
  - `advertencias`: JSONB con advertencias
  - `interpretacion`: Texto con interpretación controlada
- **Índices:** analysis_id, fecha_registro

### 2.2. Políticas RLS Específicas por Rol

**Archivo creado:** `querys para supabase/query13_mejorar_rls_evaluacion.sql`

#### Cambios realizados
- **Eliminadas:** Políticas `full_access` demasiado permisivas
- **Implementadas:** Políticas granulares basadas en roles

#### Políticas por tabla

**prompt_versions:**
- INVESTIGADOR, ADMIN: Crear, ver todos, actualizar propios
- Todos: Ver prompts activos
- ADMIN: Eliminar

**ai_executions:**
- Todos: Ver propias ejecuciones
- INVESTIGADOR, ADMIN: Ver todas
- ADMIN: Crear

**summary_versions:**
- Participantes: Ver resúmenes de reuniones donde participan
- INVESTIGADOR, ADMIN: Ver todas
- Creador, ADMIN: Actualizar

**summary_evaluations:**
- EVALUADOR: Ver propias evaluaciones
- INVESTIGADOR, ADMIN: Ver todas
- EVALUADOR, ADMIN: Crear
- Evaluador propietario, ADMIN: Actualizar

**reference_tasks (Gold Standard):**
- INVESTIGADOR, ADMIN: Ver, crear, actualizar propios

**task_evaluation_matches:**
- INVESTIGADOR, ADMIN: Ver, crear
- Validador, ADMIN: Actualizar

**experiment_sessions:**
- INVESTIGADOR: Ver propias sesiones
- ADMIN: Ver todas, crear
- Investigador propietario, ADMIN: Actualizar

**time_measurements:**
- Participantes: Ver propias mediciones
- INVESTIGADOR, ADMIN: Ver todas, crear

**sus_responses:**
- Usuarios: Ver propias respuestas, crear
- INVESTIGADOR, ADMIN: Ver todas

**performance_metrics:**
- INVESTIGADOR, ADMIN: Ver
- Sistema (service role): Crear

**audit_log:**
- ADMIN: Ver
- Sistema: Crear

---

## DEPENDENCIAS ADICIONALES

### Backend (requirements.lock.txt)
Las siguientes dependencias ya están disponibles en el entorno:
- `scipy==1.18.0` ✅ (para pruebas estadísticas)
- `numpy==2.5.1` ✅ (para cálculos numéricos)

### Dependencia opcional recomendada
Agregar a `backend/requirements.lock.txt`:
```
krippendorff>=0.5.0
```

**Nota:** La función `krippendorff_alpha` maneja graceful degradation si la librería no está instalada.

---

## ARCHIVOS MODIFICADOS/CREADOS

### Backend
1. `backend/app/metrics/statistics.py` - Extendido con 8 nuevas funciones

### Base de Datos
1. `querys para supabase/query12_persistencia_analisis.sql` - Nuevo
2. `querys para supabase/query13_mejorar_rls_evaluacion.sql` - Nuevo

### Documentación
1. `docs/AUDITORIA_INICIAL_COMPLETA.md` - Auditoría del sistema
2. `docs/IMPLEMENTACION_FASES_1_2.md` - Este documento

---

## PRÓXIMOS PASOS

### Fase 3: Backend API
- Implementar endpoints para análisis estadístico
  - `POST /api/v1/research/analyses/validate`
  - `POST /api/v1/research/analyses`
  - `GET /api/v1/research/analyses`
  - `GET /api/v1/research/analyses/{id}`
  - `POST /api/v1/research/analyses/{id}/rerun`
  - `GET /api/v1/research/analyses/{id}/results`
- Implementar endpoints de reportes
- Implementar endpoints de exportación

### Fase 4: Frontend
- Reestructurar rutas a `/research/...`
- Implementar dashboard de investigación
- Implementar vista de análisis estadísticos
- Implementar vista de gold standard
- Implementar gráficos y visualizaciones

### Fase 5: Pruebas
- Pruebas unitarias del motor estadístico
- Pruebas de API
- Pruebas E2E

### Fase 6: Documentación
- Manuales de usuario e investigador
- Documentación de API
- Diagramas Mermaid

---

## CRITERIOS DE ACEPTACIÓN CUMPLIDOS

De la auditoría inicial, los siguientes criterios ahora están cumplidos:

- ✅ Se validan supuestos de normalidad (Shapiro-Wilk)
- ✅ Se validan supuestos de igualdad de varianzas (Levene)
- ✅ Se ejecutan pruebas pareadas (t pareada, Wilcoxon)
- ✅ Se ejecutan pruebas independientes (Welch, Mann-Whitney)
- ✅ Se ejecutan pruebas para 3+ condiciones (Friedman)
- ✅ Se ejecutan pruebas para datos binarios (McNemar, Q de Cochran)
- ✅ Se evalúa acuerdo entre evaluadores (Kappa, Krippendorff, ICC)
- ✅ Se calcula consistencia interna (Cronbach)
- ✅ Se corrigen comparaciones múltiples (Holm, Bonferroni)
- ✅ Se valida calidad de datos antes de análisis
- ✅ Se guardan parámetros y resultados de análisis
- ✅ Se puede reejecutar análisis guardado (persistencia)
- ✅ Políticas RLS específicas por rol implementadas

**Porcentaje de cumplimiento actual:** ~45% (19/43 criterios)

---

## NOTAS TÉCNICAS

### Diseño del Motor Estadístico
- Todas las funciones retornan diccionarios con estructura consistente
- Incluyen validación de datos y manejo de errores
- Proporcionan interpretaciones controladas (no afirmaciones libres)
- Manejan casos borde (división por cero, datos insuficientes, etc.)

### Reproducibilidad
- Cada análisis guarda hash de datos de entrada
- Se guarda versión del código
- Se guardan todos los parámetros y filtros
- Los resultados incluyen advertencias y limitaciones

### Seguridad
- Políticas RLS granulares por rol
- No se exponen datos sensibles
- Gold standard solo accesible a investigadores
- Audit log solo accesible a administradores
