# AGENTS.md - ReunionesAuto (Zoom2)

## Current Stack
- Frontend: Next.js 16 App Router, React 19, TypeScript, Tailwind CSS 4 and Recharts in `frontend/`.
- Backend: FastAPI in `backend/app/` with a raw `requests` Supabase REST client.
- Database: Supabase PostgreSQL. Versioned SQL scripts live in `querys para supabase/`.
- Automation: n8n workflows in `json n8n/` for Zoom, meeting creation and AI summaries.
- Legacy: `app.py` is the former Streamlit implementation and is not the active application.

## Setup
1. Run SQL scripts in order: `query1.txt`, `query2.txt`, `query3.txt`, `query4.txt`, `insert_sample_tasks.sql`, `query5_metricas.txt`, `query6_reuniones_participantes.sql`, `query7_resumenes_modulo.sql`, `query8_metricas_inferenciales.sql`.
2. Import the required workflows from `json n8n/` and configure their credentials.
3. Configure root `.env`, including `SUPABASE_SERVICE_ROLE_KEY`, n8n webhook URLs, `N8N_CALLBACK_SECRET` and `N8N_WORKFLOW_VERSION`.
4. Install backend dependencies from `backend/requirements.lock.txt` for a reproducible environment.
5. Install frontend dependencies with `npm ci` in `frontend/`.

## Commands
```powershell
# Backend
backend\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000 --app-dir backend
backend\.venv\Scripts\python.exe -m unittest discover -s backend\tests -t backend -v

# Frontend
npm run dev --prefix frontend
npm run build --prefix frontend
```

## Statistical Metrics
- `metricas_n8n` uses one row per invocation and is written with the Supabase service role.
- Production analysis excludes `legacy`, `demo` and `test` rows.
- Latency analysis uses successful terminal end-to-end durations from one selected endpoint.
- The primary latency test is two-sided Welch's t-test.
- Outcomes use uncorrected Pearson chi-square when every expected cell is at least 5, otherwise two-sided Fisher exact.
- A non-significant result is not described as stability or equivalence.
- Do not use `seed_metricas_estadisticas.sql` as empirical article evidence.

## Key Conventions
- Internal telemetry outcomes are `pending`, `success`, `error`, `timeout` and `cancelled`.
- Store timestamps in UTC and analyze inclusive calendar dates as half-open UTC intervals.
- One asynchronous job is correlated through `correlation_id` and finalized by its callback.
- Admin access is checked by the backend dependency in `backend/app/core/dependencies.py`.
- Never expose `SUPABASE_SERVICE_ROLE_KEY` to the frontend.
