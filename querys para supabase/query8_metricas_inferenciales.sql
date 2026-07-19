-- Metric telemetry required by the inferential statistics module.
-- Run after query5_metricas.txt. Existing rows are retained as legacy data
-- and are intentionally excluded from publication analyses.

BEGIN;

ALTER TABLE metricas_n8n
  ADD COLUMN IF NOT EXISTS invocation_id UUID,
  ADD COLUMN IF NOT EXISTS correlation_id TEXT,
  ADD COLUMN IF NOT EXISTS data_source TEXT,
  ADD COLUMN IF NOT EXISTS started_at TIMESTAMPTZ,
  ADD COLUMN IF NOT EXISTS completed_at TIMESTAMPTZ,
  ADD COLUMN IF NOT EXISTS transport_latency_seconds DOUBLE PRECISION,
  ADD COLUMN IF NOT EXISTS end_to_end_latency_seconds DOUBLE PRECISION,
  ADD COLUMN IF NOT EXISTS outcome TEXT,
  ADD COLUMN IF NOT EXISTS is_terminal BOOLEAN,
  ADD COLUMN IF NOT EXISTS attempt_number INTEGER,
  ADD COLUMN IF NOT EXISTS workflow_version TEXT,
  ADD COLUMN IF NOT EXISTS error_type TEXT,
  ADD COLUMN IF NOT EXISTS metadata JSONB NOT NULL DEFAULT '{}'::jsonb;

-- The historical telemetry did not guarantee one row per invocation. Keep it
-- available for operational inspection, but never mix it with the clean cohort.
UPDATE metricas_n8n
SET
  data_source = COALESCE(data_source, 'legacy'),
  started_at = COALESCE(started_at, fecha),
  outcome = COALESCE(
    outcome,
    CASE lower(estado)
      WHEN 'éxito' THEN 'success'
      WHEN 'exito' THEN 'success'
      WHEN 'exitoso' THEN 'success'
      WHEN 'timeout' THEN 'timeout'
      WHEN 'cancelado' THEN 'cancelled'
      WHEN 'en_proceso' THEN 'pending'
      ELSE 'error'
    END
  ),
  is_terminal = COALESCE(is_terminal, lower(estado) <> 'en_proceso'),
  completed_at = COALESCE(
    completed_at,
    CASE WHEN lower(estado) <> 'en_proceso' THEN fecha ELSE NULL END
  ),
  attempt_number = COALESCE(attempt_number, 1);

ALTER TABLE metricas_n8n
  ALTER COLUMN data_source SET DEFAULT 'production',
  ALTER COLUMN data_source SET NOT NULL,
  ALTER COLUMN outcome SET DEFAULT 'pending',
  ALTER COLUMN outcome SET NOT NULL,
  ALTER COLUMN is_terminal SET DEFAULT FALSE,
  ALTER COLUMN is_terminal SET NOT NULL,
  ALTER COLUMN attempt_number SET DEFAULT 1,
  ALTER COLUMN attempt_number SET NOT NULL;

DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'metricas_n8n_data_source_check') THEN
    ALTER TABLE metricas_n8n ADD CONSTRAINT metricas_n8n_data_source_check
      CHECK (data_source IN ('production', 'demo', 'test', 'legacy'));
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'metricas_n8n_outcome_check') THEN
    ALTER TABLE metricas_n8n ADD CONSTRAINT metricas_n8n_outcome_check
      CHECK (outcome IN ('pending', 'success', 'error', 'timeout', 'cancelled'));
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'metricas_n8n_terminal_check') THEN
    ALTER TABLE metricas_n8n ADD CONSTRAINT metricas_n8n_terminal_check
      CHECK (
        (is_terminal = FALSE AND outcome = 'pending') OR
        (is_terminal = TRUE AND outcome IN ('success', 'error', 'timeout', 'cancelled'))
      );
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'metricas_n8n_attempt_check') THEN
    ALTER TABLE metricas_n8n ADD CONSTRAINT metricas_n8n_attempt_check
      CHECK (attempt_number >= 1);
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'metricas_n8n_completion_check') THEN
    ALTER TABLE metricas_n8n ADD CONSTRAINT metricas_n8n_completion_check
      CHECK (is_terminal = FALSE OR completed_at IS NOT NULL);
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'metricas_n8n_transport_latency_check') THEN
    ALTER TABLE metricas_n8n ADD CONSTRAINT metricas_n8n_transport_latency_check
      CHECK (
        transport_latency_seconds IS NULL OR
        (transport_latency_seconds >= 0 AND transport_latency_seconds < 'Infinity'::double precision)
      );
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'metricas_n8n_end_to_end_latency_check') THEN
    ALTER TABLE metricas_n8n ADD CONSTRAINT metricas_n8n_end_to_end_latency_check
      CHECK (
        end_to_end_latency_seconds IS NULL OR
        (end_to_end_latency_seconds >= 0 AND end_to_end_latency_seconds < 'Infinity'::double precision)
      );
  END IF;
END $$;

CREATE UNIQUE INDEX IF NOT EXISTS metricas_n8n_invocation_id_uidx
  ON metricas_n8n (invocation_id)
  WHERE invocation_id IS NOT NULL;

CREATE UNIQUE INDEX IF NOT EXISTS metricas_n8n_pending_correlation_uidx
  ON metricas_n8n (correlation_id)
  WHERE correlation_id IS NOT NULL AND is_terminal = FALSE;

CREATE INDEX IF NOT EXISTS metricas_n8n_analysis_idx
  ON metricas_n8n (data_source, endpoint, started_at, id)
  WHERE is_terminal = TRUE;

CREATE INDEX IF NOT EXISTS metricas_n8n_outcome_idx
  ON metricas_n8n (data_source, endpoint, outcome, started_at);

ALTER TABLE metricas_n8n ENABLE ROW LEVEL SECURITY;
REVOKE ALL ON TABLE metricas_n8n FROM anon, authenticated;
GRANT ALL ON TABLE metricas_n8n TO service_role;

COMMIT;
