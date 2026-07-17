-- ============================================================
-- Módulo de Resúmenes Virtuales: trabajos, grabaciones y estructura
-- Ejecutar después de los scripts base query1..query4
-- ============================================================

-- ---------- 1. Bucket privado para grabaciones de audio/vídeo/VTT ----------
-- Se crea como PRIVATE mediante la API de Supabase Storage; no se puede
-- crear completamente desde SQL. Este script habilita las tablas y
-- políticas. El bucket debe crearse con idéntico nombre en el Dashboard
-- de Supabase > Storage > New bucket: `grabaciones-reuniones` (private).

-- ---------- 2. Tabla de trabajos de resumen ----------
CREATE TABLE IF NOT EXISTS trabajos_resumen (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  reunion_id UUID NOT NULL REFERENCES reuniones(id) ON DELETE CASCADE,
  estado VARCHAR(30) NOT NULL DEFAULT 'pendiente',
  -- posibles estados: pendiente, subiendo, obteniendo_transcript, transcribiendo,
  --                   generando, finalizado, error, cancelado
  fuente VARCHAR(20) NOT NULL DEFAULT 'desconocida',
  -- posibles fuentes: zoom_vtt, zoom_audio, manual, desconocida
  archivo_path TEXT,
  archivo_url_publica TEXT,
  zoom_meeting_id VARCHAR(255),
  zoom_transcript_url TEXT,
  zoom_audio_url TEXT,
  resumen_texto TEXT,
  error_detalle TEXT,
  expira_en TIMESTAMPTZ NOT NULL DEFAULT (NOW() + INTERVAL '7 days'),
  intentos INTEGER NOT NULL DEFAULT 0,
  fecha_creacion TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  fecha_actualizacion TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_trabajos_resumen_reunion ON trabajos_resumen (reunion_id);
CREATE INDEX IF NOT EXISTS idx_trabajos_resumen_estado ON trabajos_resumen (estado);
CREATE INDEX IF NOT EXISTS idx_trabajos_resumen_expira ON trabajos_resumen (expira_en);

-- ---------- 3. Tabla de resúmenes estructurados ----------
CREATE TABLE IF NOT EXISTS resumenes_detalle (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  reunion_id UUID NOT NULL UNIQUE REFERENCES reuniones(id) ON DELETE CASCADE,
  resumen_ejecutivo TEXT,
  decisiones TEXT,
  riesgos TEXT,
  proximos_pasos TEXT,
  fecha_creacion TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  fecha_actualizacion TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ---------- 4. Políticas RLS mínimas para desarrollo ----------
-- El backend usará SUPABASE_SERVICE_ROLE_KEY, pero habilitamos RLS para
-- permitir test con anon key si fuera necesario. En producción, ajusta.

ALTER TABLE trabajos_resumen ENABLE ROW LEVEL SECURITY;
ALTER TABLE resumenes_detalle ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS full_access_trabajos_resumen ON trabajos_resumen;
CREATE POLICY full_access_trabajos_resumen ON trabajos_resumen
  FOR ALL USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS full_access_resumenes_detalle ON resumenes_detalle;
CREATE POLICY full_access_resumenes_detalle ON resumenes_detalle
  FOR ALL USING (true) WITH CHECK (true);
