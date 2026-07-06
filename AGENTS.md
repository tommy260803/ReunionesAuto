# AGENTS.md – ReunionesAuto (Zoom2)

## Stack
- **Frontend**: Single-file Streamlit app (`app.py`, ~2780 lines). No framework, no routing lib.
- **Backend**: Supabase PostgreSQL accessed via **raw `requests`** REST API (`sb_select`, `sb_insert` helpers at `app.py:68-80`). No Supabase SDK.
- **Automation**: n8n workflows (`json n8n/AsistenteIA1.json`) for Zoom API, AI summaries, PDF OCR.
- **Charts**: Altair (donuts, bars, lines) + Plotly Express (metrics page).

## Setup (order matters)
1. Import n8n JSON → add credentials
2. Run SQL scripts in Supabase SQL Editor **in this order**: `query1.txt` → `query2.txt` → `query3.txt` → `query4.txt` → `insert_sample_tasks.sql` → `query5_metricas.txt`
3. Create `.env` with `SUPABASE_URL`, `SUPABASE_ANON_KEY`, 3 n8n webhook URLs
4. `python -m venv .venv` → `.\.venv\Scripts\Activate` → `pip install -r requirements.txt`
5. If bcrypt fails on install: `pip uninstall bcrypt -y` → `pip install passlib[bcrypt]` → `pip install "bcrypt==4.0.1"`
6. `streamlit run app.py`

## Key conventions
- **Admin** is hardcoded at `app.py:108` to `juanaureliodelacruzgamarra@gmail.com`
- **Supabase REST**: all CRUD goes through `SUPABASE_URL/rest/v1/{table}` with `HEADERS` (apikey + Bearer token). Filters use Supabase query syntax (e.g. `"id": "eq.{value}"`, `"order": "fecha.desc"`).
- **Chat state reset**: uses `st.session_state["chat_reset_pending"]` flag + `st.rerun()` to clear widgets safely (pattern at `app.py:440-444`).
- **PDF presencial polling**: after submitting PDF to n8n, polls Supabase `resumenes` table every 3s for up to 120s (`app.py:1301-1332`).
- **Metric logging**: every n8n call logs to `metricas_n8n` table via `registrar_metrica_n8n()` (`app.py:33-66`).
- **Password hashing**: uses `passlib.hash.bcrypt` (not bcrypt directly).

## Directories
- `querys para supabase/` – SQL scripts for schema, data, RLS
- `json n8n/` – n8n workflow JSON (import into n8n instance)

## Commands
```powershell
.venv\Scripts\Activate
streamlit run app.py
```

## What's missing
- No test framework, no tests
- No lint/typecheck config
- `.env` is committed with live keys (keep in mind)
- No CI/CD config
