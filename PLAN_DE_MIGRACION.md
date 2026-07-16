# Plan de Finalización de la Migración (Zoom2)

He revisado a fondo todas las rutas y el código actual de la aplicación Next.js + FastAPI y lo he comparado con la especificación original basada en Streamlit. A continuación se detalla el estado actual de cada módulo y los desarrollos pendientes que se deben implementar para lograr el **100% de paridad**.

## Estado Actual vs Especificación

| Módulo | Especificación | Estado Actual | Pendiente |
| :--- | :--- | :--- | :--- |
| **Chat** | Crear reuniones vía chat NLP con n8n y Zoom | ✅ **Completado**. Funciona y registra métricas. | - |
| **Usuarios** | CRUD (Básico/Pro/Enterprise) y exportación PDF | ⚠️ **Parcial**. Panel CRUD implementado. | Falta botón/lógica para **exportar a PDF**. |
| **Reuniones** | Lista y editor (reprogramar, cambiar tipo, borrar) | ⚠️ **Parcial**. Lista implementada en solo-lectura. | Falta modal de **edición y borrado**. |
| **Participantes**| Consulta y edición de correos invitados y roles | ⚠️ **Parcial**. Consulta implementada. | Falta **edición** de roles y correos. |
| **Resúmenes** | Vista en tres columnas (Virtual/Presencial/Mixta) y flujos n8n | ⚠️ **Desviación UX**. Se implementaron los flujos n8n (Polling y Chat), pero se usó **una sola lista con filtros** en lugar de 3 columnas fijas. | **Validar UX**: Mantener filtro desplegable o volver a las 3 columnas. |
| **Tareas** | Kanban, Métricas (Altair), Edición en Grilla y PDF | ⚠️ **Parcial**. Kanban básico y creación de tareas listos. | Faltan **Gráficos (Recharts)**, **Grilla interactiva**, y **Exportación PDF**. |
| **Métricas** | Panel de Plotly para auditar desempeño de n8n | ❌ **Faltante**. Solo hay KPIs básicos en el Dashboard. | Crear ruta `/metrics` con **gráficos interactivos y logs detallados**. |

---

## Proposed Changes (Plan de Acción para la IA)

A continuación, la ruta de implementación sugerida para completar el desarrollo. Se usarán bibliotecas modernas de React como `recharts` (para reemplazar Altair/Plotly de Python) y `jspdf` / `html2canvas` para las exportaciones en PDF.

### 1. Módulo de Reuniones y Participantes
- **[MODIFY]** `frontend/src/app/(dashboard)/meetings/page.tsx`:
  - Añadir menú de acciones por fila.
  - Integrar un Modal de Edición (permite cambiar `tema`, `fecha_inicio`, `duracion_minutos`, `tipo`, `estado`).
  - Lógica de borrado integrando el backend (`DELETE /meetings/:id`).
- **[MODIFY]** `frontend/src/app/(dashboard)/participants/page.tsx`:
  - Hacer la tabla editable (cambiar el `rol` usando un dropdown y editar el `correo`).
  - Añadir un botón flotante "Guardar Cambios" que envíe la actualización masiva (`PATCH /participants`).

### 2. Módulo de Usuarios (Exportación)
- **[MODIFY]** `frontend/src/app/(dashboard)/users/page.tsx`:
  - Integrar librería `jspdf` y `jspdf-autotable`.
  - Crear el botón "Exportar PDF" en el header de la página que descargue la grilla de usuarios manteniendo el formato corporativo.

### 3. Módulo de Tareas (Gráficos, Grilla y Exportación)
- **[MODIFY]** `frontend/src/app/(dashboard)/tasks/page.tsx`:
  - Reorganizar la página usando **Tabs** (Pestañas): "Tablero Kanban", "Vista Grilla" y "Métricas".
  - **Vista Grilla**: Una tabla de datos densa donde se puede editar directamente `asignado_a_correo` y `fecha_vencimiento`.
  - **Métricas**: Integrar `recharts` para mostrar: (1) Gráfico circular de tareas por estado, (2) Gráfico de barras de carga laboral por usuario.
  - **Exportación**: Añadir un botón "Descargar Reporte" que exporte la vista de grilla de las tareas en PDF.

### 4. Nuevo Módulo de Métricas n8n
- **[NEW]** `backend/app/automation/metrics.py`:
  - Crear endpoint `GET /automation/metrics/stats` que agrupe las métricas de la tabla `metricas_n8n` de Supabase (tiempos promedio, conteo por día/endpoint, tasas de error).
  - Enlazar este router en `backend/app/main.py`.
- **[NEW]** `frontend/src/app/(dashboard)/metrics/page.tsx`:
  - Construir un panel dedicado a auditar n8n.
  - Añadir KPI Cards: Tasa de éxito global, Tiempo promedio de respuesta, Total de peticiones procesadas.
  - Añadir gráficos (`recharts`): Línea de tiempo de peticiones (últimos 7 días) y gráfico de barras de latencia por endpoint.
  - Añadir una tabla inferior con los *Logs detallados* (últimos 50 eventos registrados de n8n).

---

> **Nota para el desarrollador AI:**  
> Asegúrate de preservar los diseños modernos con Tailwind CSS y evitar el uso de librerías de UI complejas si se pueden lograr componentes propios y livianos. Todos los endpoints deben seguir la estructura actual que depende de `api.ts` usando Axios.
