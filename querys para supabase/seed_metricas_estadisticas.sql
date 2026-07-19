-- Deterministic demonstration fixture. Run only after
-- query8_metricas_inferenciales.sql and preferably in a development project.
-- These rows use data_source='demo' and are excluded from production analysis.

BEGIN;

DELETE FROM metricas_n8n
WHERE data_source = 'demo' AND detalles = 'DEMO-STATISTICS-V1';

WITH generated AS (
  SELECT
    i,
    ('10000000-0000-4000-8000-' || lpad(i::text, 12, '0'))::uuid AS invocation_id,
    TIMESTAMPTZ '2026-06-01 00:00:00+00'
      + ((i - 1) % 30) * INTERVAL '1 day'
      + ((i - 1) % 8) * INTERVAL '1 hour' AS started_at,
    2.50 + ((i * 37) % 300)::double precision / 100.0 AS latency,
    (i % 5 = 0) AS failed
  FROM generate_series(1, 150) AS series(i)
)
INSERT INTO metricas_n8n (
  invocation_id, correlation_id, data_source, started_at, completed_at,
  transport_latency_seconds, end_to_end_latency_seconds, outcome, is_terminal,
  attempt_number, workflow_version, endpoint, tiempo_respuesta, estado, fecha,
  codigo_estado, detalles
)
SELECT
  invocation_id,
  'demo-statistics-v1-a-' || i,
  'demo',
  started_at,
  started_at + latency * INTERVAL '1 second',
  latency * 0.75,
  latency,
  CASE WHEN failed THEN 'error' ELSE 'success' END,
  TRUE,
  1,
  'demo-v1',
  'borrador_reunion_chat',
  latency,
  CASE WHEN failed THEN 'error' ELSE 'éxito' END,
  started_at,
  CASE WHEN failed THEN 500 ELSE 200 END,
  'DEMO-STATISTICS-V1'
FROM generated;

WITH generated AS (
  SELECT
    i,
    ('20000000-0000-4000-8000-' || lpad(i::text, 12, '0'))::uuid AS invocation_id,
    TIMESTAMPTZ '2026-07-01 00:00:00+00'
      + ((i - 1) % 18) * INTERVAL '1 day'
      + ((i - 1) % 8) * INTERVAL '1 hour' AS started_at,
    0.80 + ((i * 29) % 150)::double precision / 100.0 AS latency,
    (i % 20 = 0) AS failed
  FROM generate_series(1, 150) AS series(i)
)
INSERT INTO metricas_n8n (
  invocation_id, correlation_id, data_source, started_at, completed_at,
  transport_latency_seconds, end_to_end_latency_seconds, outcome, is_terminal,
  attempt_number, workflow_version, endpoint, tiempo_respuesta, estado, fecha,
  codigo_estado, detalles
)
SELECT
  invocation_id,
  'demo-statistics-v1-b-' || i,
  'demo',
  started_at,
  started_at + latency * INTERVAL '1 second',
  latency * 0.75,
  latency,
  CASE WHEN failed THEN 'error' ELSE 'success' END,
  TRUE,
  1,
  'demo-v1',
  'borrador_reunion_chat',
  latency,
  CASE WHEN failed THEN 'error' ELSE 'éxito' END,
  started_at,
  CASE WHEN failed THEN 500 ELSE 200 END,
  'DEMO-STATISTICS-V1'
FROM generated;

COMMIT;

-- Cleanup:
-- DELETE FROM metricas_n8n
-- WHERE data_source = 'demo' AND detalles = 'DEMO-STATISTICS-V1';
