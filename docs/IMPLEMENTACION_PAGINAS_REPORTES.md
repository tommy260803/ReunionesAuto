# IMPLEMENTACIÓN PÁGINAS Y GENERACIÓN DE REPORTES

**Fecha:** 2026-07-20  
**Objetivo:** Documentar la implementación de páginas de detalle/creación y generación de reportes

---

## ARCHIVOS CREADOS

### Frontend (4 archivos)
1. `frontend/src/app/(research)/analyses/new/page.tsx` - Creación de análisis
2. `frontend/src/app/(research)/analyses/[id]/page.tsx` - Detalle de análisis
3. `frontend/src/app/(research)/experiments/new/page.tsx` - Creación de sesión experimental
4. `frontend/src/app/(research)/experiments/[id]/page.tsx` - Detalle de sesión experimental

### Backend (2 archivos)
1. `backend/app/reports/generator.py` - Generador de reportes
2. `backend/app/reports/router.py` - Router de reportes (modificado)

---

## PÁGINAS IMPLEMENTADAS

### 1. Creación de Análisis Estadístico
**Ruta:** `/research/analyses/new`

**Campos del formulario:**
- Nombre del análisis (obligatorio)
- Objetivo (opcional)
- Variable de resultado (obligatorio)
- Variable de agrupación (opcional)
- Diseño del análisis (INDEPENDIENTE, PAREADO, MEDIDAS_REPETIDAS)
- Prueba estadística solicitada (opcional, usa selector automático si no se especifica)
- Nivel de significancia (α)
- Corrección múltiple (HOLM, BONFERRONI, NONE)

**Funcionalidades:**
- Validación de campos obligatorios
- Creación vía API POST `/research/analyses`
- Redirección a página de detalle después de crear
- Botón de cancelar para volver atrás

### 2. Detalle de Análisis Estadístico
**Ruta:** `/research/analyses/[id]`

**Información mostrada:**
- Nombre y objetivo del análisis
- Estado con indicador visual
- Variable de resultado y agrupación
- Diseño y pruebas solicitada/ejecutada
- Nivel de significancia y corrección múltiple
- Fechas de creación y ejecución

**Resultados (si disponibles):**
- Interpretación del resultado
- Advertencias
- Resultado principal (JSON)
- Estadísticos descriptivos (JSON)
- Tamaño del efecto (JSON)
- Intervalos de confianza (JSON)

**Funcionalidades:**
- Botón de reejecutar análisis
- Visualización de estado (PLANIFICADO, EJECUTANDO, COMPLETADO, ERROR)
- Mensajes informativos según estado
- Navegación de retorno

### 3. Creación de Sesión Experimental
**Ruta:** `/research/experiments/new`

**Campos del formulario:**
- Nombre de la sesión (obligatorio)
- Descripción (opcional)
- Estado inicial (PLANIFICADO, ACTIVO)

**Funcionalidades:**
- Validación de campos obligatorios
- Creación vía API POST `/experiments`
- Redirección a página de detalle después de crear
- Botón de cancelar para volver atrás

### 4. Detalle de Sesión Experimental
**Ruta:** `/research/experiments/[id]`

**Información mostrada:**
- Nombre y descripción
- Estado con indicador visual
- Fechas de inicio y fin
- ID de la sesión

**Acciones disponibles:**
- Iniciar sesión (si está PLANIFICADO)
- Finalizar sesión (si está ACTIVO)
- Ver análisis asociados
- Ver evaluaciones

**Funcionalidades:**
- Mensajes informativos según estado
- Botones deshabilitados según estado
- Navegación de retorno

---

## GENERACIÓN DE REPORTES

### Módulo Generator
**Archivo:** `backend/app/reports/generator.py`

**Funciones implementadas:**
- `generate_report()` - Función principal de generación
- `generate_pdf_report()` - Generación en PDF
- `generate_word_report()` - Generación en Word
- `generate_excel_report()` - Generación en Excel
- `check_format_availability()` - Verifica disponibilidad de formato
- `get_missing_dependency()` - Retorna dependencia faltante

**Dependencias opcionales:**
- `reportlab` - Para PDF
- `python-docx` - Para Word
- `pandas` y `openpyxl` - Para Excel

**Graceful degradation:**
- Si una dependencia no está instalada, retorna error informativo
- No falla el sistema si una dependencia falta

### Endpoints de Reportes
**Archivo:** `backend/app/reports/router.py`

**Endpoints nuevos:**

#### POST `/reports/research/generate`
- **Propósito:** Generar reporte de investigación
- **Parámetros:** report_type, format_type, data, title
- **Formatos soportados:** PDF, WORD, EXCEL
- **Control de acceso:** INVESTIGADOR o ADMIN
- **Funcionalidad:** Genera reporte y retorna archivo para descarga

#### GET `/reports/research/analyses/{analysis_id}/export`
- **Propósito:** Exportar análisis estadístico
- **Parámetros:** analysis_id, format_type (default PDF)
- **Control de acceso:** INVESTIGADOR (solo propios) o ADMIN
- **Funcionalidad:** Obtiene análisis y resultados, genera reporte

#### GET `/reports/research/experiments/{experiment_id}/export`
- **Propósito:** Exportar sesión experimental
- **Parámetros:** experiment_id, format_type (default PDF)
- **Control de acceso:** INVESTIGADOR (solo propios) o ADMIN
- **Funcionalidad:** Obtiene sesión experimental, genera reporte

---

## INTEGRACIÓN

### Router de reportes
El router de reportes ya estaba integrado en `main.py`, no se requirió modificación adicional.

### Dependencias
Las dependencias para generación de reportes son opcionales:
- `reportlab` - Instalar con: `pip install reportlab`
- `python-docx` - Instalar con: `pip install python-docx`
- `pandas openpyxl` - Instalar con: `pip install pandas openpyxl`

---

## CRITERIOS DE ACEPTACIÓN CUMPLIDOS

De la auditoría inicial, los siguientes criterios ahora están cumplidos:

- ✅ Páginas de detalle y creación en frontend
- ✅ Generación de reportes en múltiples formatos
- ✅ Exportación de análisis y experimentos
- ✅ Control de acceso por rol en reportes
- ✅ Manejo de dependencias opcionales

**Porcentaje de cumplimiento actual:** ~85% (37/43 criterios)

---

## PRÓXIMOS PASOS

### Pendientes de media prioridad
1. Implementar gráficos y visualizaciones (boxplots, matrices de confusión)
2. Implementar formularios de evaluación ciega
3. Implementar cuestionario SUS (10 preguntas)

### Pendientes de baja prioridad
4. Completar documentación de API
5. Completar manuales de usuario
6. Crear diagramas Mermaid

---

## CONCLUSIÓN

Se han implementado las páginas de detalle y creación para análisis estadísticos y sesiones experimentales, así como la generación de reportes en PDF, Word y Excel. El sistema ahora permite:

- Crear análisis estadísticos desde la UI
- Ver resultados detallados de análisis
- Crear sesiones experimentales
- Gestionar sesiones experimentales
- Exportar análisis y experimentos en múltiples formatos
- Reejecutar análisis desde la UI

**Estado:** ✅ Páginas y generación de reportes implementadas exitosamente  
**Porcentaje de cumplimiento actual:** ~85% (37/43 criterios)
