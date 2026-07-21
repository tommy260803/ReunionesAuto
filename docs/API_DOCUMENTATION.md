# DOCUMENTACIÓN DE API - ZOOM2

**Versión:** 1.0  
**Fecha:** 2026-07-20  
**Base URL:** `http://localhost:8000`  
**Documentación Interactiva:** `http://localhost:8000/docs`

---

## TABLA DE CONTENIDOS

1. [Autenticación](#autenticación)
2. [Usuarios](#usuarios)
3. [Reuniones](#reuniones)
4. [Participantes](#participantes)
5. [Tareas](#tareas)
6. [Resúmenes](#resúmenes)
7. [Métricas](#métricas)
8. [Análisis Estadísticos](#análisis-estadísticos)
9. [Experimentos](#experimentos)
10. [Evaluaciones](#evaluaciones)
11. [Prompts](#prompts)
12. [Reportes](#reportes)
13. [Códigos de Estado HTTP](#códigos-de-estado-http)
14. [Errores Comunes](#errores-comunes)

---

## AUTENTICACIÓN

### Iniciar Sesión
**Endpoint:** `POST /api/v1/auth/login`

**Request Body:**
```json
{
  "correo": "usuario@ejemplo.com",
  "password": "password123"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "nombre": "Usuario",
    "correo": "usuario@ejemplo.com",
    "rol": "INVESTIGADOR"
  }
}
```

### Registro
**Endpoint:** `POST /api/v1/auth/register`

**Request Body:**
```json
{
  "nombre": "Nuevo Usuario",
  "correo": "nuevo@ejemplo.com",
  "password": "password123"
}
```

**Response (201 Created):**
```json
{
  "id": "uuid",
  "nombre": "Nuevo Usuario",
  "correo": "nuevo@ejemplo.com",
  "rol": "USUARIO"
}
```

### Obtener Usuario Actual
**Endpoint:** `GET /api/v1/auth/me`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response (200 OK):**
```json
{
  "id": "uuid",
  "nombre": "Usuario",
  "correo": "usuario@ejemplo.com",
  "rol": "INVESTIGADOR"
}
```

---

## USUARIOS

### Listar Usuarios
**Endpoint:** `GET /api/v1/users`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Query Parameters:**
- `limit` (optional): Número de resultados (default: 50)
- `offset` (optional): Offset para paginación (default: 0)

**Response (200 OK):**
```json
[
  {
    "id": "uuid",
    "nombre": "Usuario",
    "correo": "usuario@ejemplo.com",
    "rol": "INVESTIGADOR",
    "fecha_creacion": "2026-07-20T00:00:00Z"
  }
]
```

### Obtener Usuario por ID
**Endpoint:** `GET /api/v1/users/{id}`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response (200 OK):**
```json
{
  "id": "uuid",
  "nombre": "Usuario",
  "correo": "usuario@ejemplo.com",
  "rol": "INVESTIGADOR",
  "fecha_creacion": "2026-07-20T00:00:00Z"
}
```

---

## REUNIONES

### Listar Reuniones
**Endpoint:** `GET /api/v1/meetings`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Query Parameters:**
- `estado` (optional): Filtro por estado
- `fecha_inicio` (optional): Filtro por fecha de inicio
- `fecha_fin` (optional): Filtro por fecha de fin

**Response (200 OK):**
```json
[
  {
    "id": "uuid",
    "tema": "Reunión de Proyecto",
    "fecha_inicio": "2026-07-20T10:00:00Z",
    "fecha_fin": "2026-07-20T11:00:00Z",
    "estado": "PROGRAMADA",
    "zoom_meeting_id": "123456789"
  }
]
```

### Crear Reunión
**Endpoint:** `POST /api/v1/meetings`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Request Body:**
```json
{
  "tema": "Reunión de Proyecto",
  "fecha_inicio": "2026-07-20T10:00:00Z",
  "fecha_fin": "2026-07-20T11:00:00Z",
  "descripcion": "Discusión del proyecto"
}
```

**Response (201 Created):**
```json
{
  "id": "uuid",
  "tema": "Reunión de Proyecto",
  "fecha_inicio": "2026-07-20T10:00:00Z",
  "fecha_fin": "2026-07-20T11:00:00Z",
  "estado": "PROGRAMADA"
}
```

---

## PARTICIPANTES

### Listar Participantes de Reunión
**Endpoint:** `GET /api/v1/participants?meeting_id={meeting_id}`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response (200 OK):**
```json
[
  {
    "id": "uuid",
    "reunion_id": "uuid",
    "correo": "participante@ejemplo.com",
    "rol": "ORGANIZADOR"
  }
]
```

### Agregar Participante
**Endpoint:** `POST /api/v1/participants`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Request Body:**
```json
{
  "reunion_id": "uuid",
  "correo": "participante@ejemplo.com",
  "rol": "PARTICIPANTE"
}
```

**Response (201 Created):**
```json
{
  "id": "uuid",
  "reunion_id": "uuid",
  "correo": "participante@ejemplo.com",
  "rol": "PARTICIPANTE"
}
```

---

## TAREAS

### Listar Tareas
**Endpoint:** `GET /api/v1/tasks`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Query Parameters:**
- `estado` (optional): Filtro por estado
- `asignado_a` (optional): Filtro por asignado

**Response (200 OK):**
```json
[
  {
    "id": "uuid",
    "reunion_id": "uuid",
    "descripcion": "Completar reporte",
    "asignado_a_correo": "usuario@ejemplo.com",
    "estado": "PENDIENTE",
    "fecha_vencimiento": "2026-07-25T00:00:00Z"
  }
]
```

### Crear Tarea
**Endpoint:** `POST /api/v1/tasks`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Request Body:**
```json
{
  "reunion_id": "uuid",
  "descripcion": "Completar reporte",
  "asignado_a_correo": "usuario@ejemplo.com",
  "fecha_vencimiento": "2026-07-25T00:00:00Z"
}
```

**Response (201 Created):**
```json
{
  "id": "uuid",
  "reunion_id": "uuid",
  "descripcion": "Completar reporte",
  "asignado_a_correo": "usuario@ejemplo.com",
  "estado": "PENDIENTE"
}
```

---

## RESÚMENES

### Listar Resúmenes
**Endpoint:** `GET /api/v1/summaries`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Query Parameters:**
- `reunion_id` (optional): Filtro por reunión
- `prompt_version_id` (optional): Filtro por versión de prompt

**Response (200 OK):**
```json
[
  {
    "id": "uuid",
    "reunion_id": "uuid",
    "prompt_version_id": "uuid",
    "contenido": "Resumen de la reunión...",
    "fecha_creacion": "2026-07-20T00:00:00Z"
  }
]
```

### Obtener Resumen por ID
**Endpoint:** `GET /api/v1/summaries/{id}`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response (200 OK):**
```json
{
  "id": "uuid",
  "reunion_id": "uuid",
  "prompt_version_id": "uuid",
  "contenido": "Resumen de la reunión...",
  "fecha_creacion": "2026-07-20T00:00:00Z"
}
```

---

## MÉTRICAS

### Obtener Métricas de Reuniones
**Endpoint:** `GET /api/v1/metrics/meetings`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Query Parameters:**
- `fecha_inicio` (optional): Fecha de inicio del periodo
- `fecha_fin` (optional): Fecha de fin del periodo

**Response (200 OK):**
```json
{
  "total_reuniones": 100,
  "reuniones_completadas": 85,
  "reuniones_canceladas": 5,
  "promedio_duracion": 3600
}
```

### Obtener Métricas de Resúmenes
**Endpoint:** `GET /api/v1/metrics/summaries`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Query Parameters:**
- `fecha_inicio` (optional): Fecha de inicio del periodo
- `fecha_fin` (optional): Fecha de fin del periodo

**Response (200 OK):**
```json
{
  "total_resumenes": 95,
  "promedio_longitud": 500,
  "promedio_calidad": 8.5
}
```

---

## ANÁLISIS ESTADÍSTICOS

### Validar Calidad de Datos
**Endpoint:** `POST /api/v1/research/analyses/validate`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Request Body:**
```json
{
  "data": {
    "group_a": [1, 2, 3, 4, 5],
    "group_b": [2, 3, 4, 5, 6]
  },
  "test_type": "welch_t_test",
  "design": "independent",
  "min_observations": 5
}
```

**Response (200 OK):**
```json
{
  "valid": true,
  "warnings": [],
  "errors": []
}
```

### Crear Análisis
**Endpoint:** `POST /api/v1/research/analyses`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Request Body:**
```json
{
  "nombre": "Comparación de Prompts",
  "objetivo": "Comparar calidad entre v1.0 y v1.1",
  "variable_resultado": "calidad",
  "variable_grupo": "version_prompt",
  "diseno": "INDEPENDIENTE",
  "prueba_solicitada": "welch_t_test",
  "alpha": 0.05,
  "correccion_multiple": "HOLM"
}
```

**Response (201 Created):**
```json
{
  "id": "uuid",
  "nombre": "Comparación de Prompts",
  "estado": "PLANIFICADO",
  "fecha_creacion": "2026-07-20T00:00:00Z"
}
```

### Listar Análisis
**Endpoint:** `GET /api/v1/research/analyses`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Query Parameters:**
- `estado` (optional): Filtro por estado

**Response (200 OK):**
```json
[
  {
    "id": "uuid",
    "nombre": "Comparación de Prompts",
    "estado": "COMPLETADO",
    "fecha_creacion": "2026-07-20T00:00:00Z"
  }
]
```

### Obtener Análisis por ID
**Endpoint:** `GET /api/v1/research/analyses/{id}`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response (200 OK):**
```json
{
  "id": "uuid",
  "nombre": "Comparación de Prompts",
  "estado": "COMPLETADO",
  "variable_resultado": "calidad",
  "prueba_ejecutada": "welch_t_test"
}
```

### Reejecutar Análisis
**Endpoint:** `POST /api/v1/research/analyses/{id}/rerun`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Request Body:**
```json
{
  "force": false
}
```

**Response (200 OK):**
```json
{
  "id": "uuid",
  "estado": "EJECUTANDO",
  "fecha_ejecucion": "2026-07-20T00:00:00Z"
}
```

### Obtener Resultados de Análisis
**Endpoint:** `GET /api/v1/research/analyses/{id}/results`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response (200 OK):**
```json
{
  "resultado": {
    "statistic": 2.5,
    "p_value": 0.012
  },
  "descriptivos": {
    "group_a": {"mean": 3.5, "std": 1.2},
    "group_b": {"mean": 4.2, "std": 1.1}
  },
  "interpretacion": "Existe una diferencia significativa entre los grupos"
}
```

### Selector Automático de Prueba
**Endpoint:** `POST /api/v1/research/analyses/select-test`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Query Parameters:**
- `variable_type`: Tipo de variable (continuous, ordinal, binary)
- `n_conditions`: Número de condiciones
- `design`: Diseño (independent, paired, repeated_measures)
- `sample_size`: Tamaño de muestra
- `is_normal` (optional): Si los datos son normales
- `equal_variances` (optional): Si las varianzas son iguales

**Response (200 OK):**
```json
{
  "suggested_test": "welch_t_test",
  "alternative_tests": ["mann_whitney_u"],
  "justification": "Datos continuos independientes con 2 condiciones",
  "assumptions": ["Muestras independientes", "Normalidad"],
  "warnings": ["Se recomienda verificar normalidad"]
}
```

---

## EXPERIMENTOS

### Crear Sesión Experimental
**Endpoint:** `POST /api/v1/experiments`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Request Body:**
```json
{
  "nombre": "Evaluación de Prompts v1.0",
  "descripcion": "Evaluación comparativa de prompts",
  "estado": "PLANIFICADO"
}
```

**Response (201 Created):**
```json
{
  "id": "uuid",
  "nombre": "Evaluación de Prompts v1.0",
  "estado": "PLANIFICADO",
  "fecha_inicio": "2026-07-20T00:00:00Z"
}
```

### Listar Sesiones Experimentales
**Endpoint:** `GET /api/v1/experiments`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response (200 OK):**
```json
[
  {
    "id": "uuid",
    "nombre": "Evaluación de Prompts v1.0",
    "estado": "ACTIVO",
    "fecha_inicio": "2026-07-20T00:00:00Z"
  }
]
```

---

## EVALUACIONES

### Crear Evaluación Ciega
**Endpoint:** `POST /api/v1/evaluations/blind`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Request Body:**
```json
{
  "summary_id": "uuid",
  "quality_score": 8,
  "accuracy_score": 7,
  "completeness_score": 9,
  "clarity_score": 8,
  "comments": "Buen resumen en general"
  "evaluador_id": "uuid"
}
```

**Response (201 Created):**
```json
{
  "id": "uuid",
  "summary_id": "uuid",
  "puntaje_total": 32,
  "fecha_evaluacion": "2026-07-20T00:00:00Z"
}
```

---

## REPORTES

### Generar Reporte de Investigación
**Endpoint:** `POST /api/v1/reports/research/generate`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Request Body:**
```json
{
  "report_type": "ANALISIS",
  "format_type": "PDF",
  "data": {...},
  "title": "Reporte de Análisis"
}
```

**Response (200 OK):**
- Content-Type: `application/pdf`
- Content-Disposition: `attachment; filename="reporte.pdf"`

### Exportar Análisis
**Endpoint:** `GET /api/v1/reports/research/analyses/{analysis_id}/export`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Query Parameters:**
- `format_type`: Formato (PDF, WORD, EXCEL)

**Response (200 OK):**
- Content-Type: `application/pdf` (o formato seleccionado)
- Content-Disposition: `attachment; filename="analisis.pdf"`

---

## CÓDIGOS DE ESTADO HTTP

- `200 OK`: Solicitud exitosa
- `201 Created`: Recurso creado exitosamente
- `400 Bad Request`: Solicitud inválida
- `401 Unauthorized`: No autenticado
- `403 Forbidden`: No autorizado
- `404 Not Found`: Recurso no encontrado
- `500 Internal Server Error`: Error del servidor

---

## ERRORES COMUNES

### Error de Autenticación
```json
{
  "detail": "No autenticado"
}
```

**Solución:** Verifique que el token de acceso sea válido y esté incluido en el header Authorization.

### Error de Autorización
```json
{
  "detail": "Acceso restringido a administradores"
}
```

**Solución:** Verifique que tenga el rol adecuado para acceder al recurso.

### Error de Validación
```json
{
  "detail": [
    {
      "loc": ["body", "nombre"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

**Solución:** Verifique que todos los campos requeridos estén incluidos en la solicitud.

---

## APÉNDICE

### Ejemplo de Uso con cURL

**Iniciar Sesión:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"correo": "usuario@ejemplo.com", "password": "password123"}'
```

**Crear Análisis:**
```bash
curl -X POST http://localhost:8000/api/v1/research/analyses \
  -H "Authorization: Bearer {access_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Análisis de prueba",
    "variable_resultado": "calidad",
    "diseno": "INDEPENDIENTE"
  }'
```

**Exportar Análisis:**
```bash
curl -X GET "http://localhost:8000/api/v1/reports/research/analyses/{id}/export?format_type=PDF" \
  -H "Authorization: Bearer {access_token}" \
  -o reporte.pdf
```

---

**Fin de la Documentación de API**
