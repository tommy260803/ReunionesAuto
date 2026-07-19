# ReunionesAuto (Zoom2)

Plataforma para crear reuniones de Zoom, gestionar participantes y tareas, generar resúmenes con IA mediante n8n y auditar estadísticamente el rendimiento de sus automatizaciones.

## Arquitectura Actual

```text
Next.js 16 / React 19 -> FastAPI -> Supabase PostgreSQL
                              -> n8n -> Zoom / IA
```

- `frontend/`: interfaz Next.js con TypeScript, Tailwind CSS y Recharts.
- `backend/`: API FastAPI, autenticación, lógica de negocio y cliente REST de Supabase.
- `querys para supabase/`: esquema, migraciones, restricciones y RLS.
- `json n8n/`: workflows importables de automatización.
- `app.py`: aplicación Streamlit antigua, conservada únicamente como referencia.

## Base De Datos

Ejecutar en el SQL Editor de Supabase, en este orden:

1. `query1.txt`
2. `query2.txt`
3. `query3.txt`
4. `query4.txt`
5. `insert_sample_tasks.sql`
6. `query5_metricas.txt`
7. `query6_reuniones_participantes.sql`
8. `query7_resumenes_modulo.sql`
9. `query8_metricas_inferenciales.sql`

`query8_metricas_inferenciales.sql` es obligatorio antes de iniciar la nueva telemetría. Conserva las métricas existentes como `legacy`, inicia una cohorte productiva limpia, añade identidad por ejecución, latencias separadas, resultados terminales, índices y RLS.

`seed_metricas_estadisticas.sql` es opcional y exclusivo para demostración. Sus filas usan `data_source='demo'` y nunca se incluyen en el análisis productivo.

## Variables De Entorno

Crear `.env` en la raíz. Usar `backend/.env.example` como referencia. Para métricas son obligatorias:

```env
SUPABASE_URL=https://proyecto.supabase.co
SUPABASE_ANON_KEY=...
SUPABASE_SERVICE_ROLE_KEY=...
N8N_WORKFLOW_VERSION=2026-07-v1
```

La clave de servicio solo debe existir en el backend.

## Backend

```powershell
python -m venv backend\.venv
backend\.venv\Scripts\python.exe -m pip install -r backend\requirements.lock.txt
backend\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000 --app-dir backend
```

Pruebas:

```powershell
backend\.venv\Scripts\python.exe -m unittest discover -s backend\tests -t backend -v
```

## Frontend

```powershell
npm ci --prefix frontend
npm run dev --prefix frontend
```

Verificación:

```powershell
npm run build --prefix frontend
npm run lint --prefix frontend
```

## Auditoría Estadística

El endpoint administrativo `GET /metrics/n8n/statistics` compara dos periodos UTC no superpuestos del mismo endpoint.

- Velocidad: prueba t de Welch bilateral sobre latencias end-to-end de ejecuciones productivas, exitosas y terminales.
- Resultados: Chi-cuadrado de Pearson sin corrección de Yates cuando todas las frecuencias esperadas son al menos 5.
- Muestras pequeñas: prueba exacta de Fisher bilateral.
- Reporte: tamaños muestrales, descriptivos, IC 95%, estadísticos, grados de libertad, p-value y tamaños del efecto.
- Interpretación: `p >= 0.05` se informa como ausencia de evidencia de diferencia, no como equivalencia.
- Reproducibilidad: cada periodo incluye hash SHA-256 y el panel descarga el resultado JSON.

La especificación completa está en `METODOLOGIA_ESTADISTICA.md`.

## Exportación Para Investigación

Desde `backend/`:

```powershell
.venv\Scripts\python.exe -m scripts.export_metrics_dataset `
  --endpoint borrador_reunion_chat `
  --start-a 2026-08-01 --end-a 2026-08-31 `
  --start-b 2026-09-01 --end-b 2026-09-30 `
  --output exports\metricas_articulo.csv
```

El comando genera el CSV y un manifiesto JSON con parámetros, fecha, cantidad de filas y hash SHA-256.

## Endpoints De Métricas

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/metrics/n8n` | Logs productivos terminales recientes |
| `GET` | `/metrics/n8n/stats` | KPIs operativos y endpoints disponibles |
| `GET` | `/metrics/n8n/statistics` | Welch y Chi-cuadrado/Fisher entre periodos |

Todos requieren una cuenta administradora.
