-- ============================================================
-- Módulo de Actas: tabla, índices y políticas RLS
-- Ejecutar después de query7_resumenes_modulo.sql
-- ============================================================

-- ---------- 1. Tabla de actas ----------
CREATE TABLE IF NOT EXISTS actas (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  reunion_id UUID NOT NULL REFERENCES reuniones(id) ON DELETE CASCADE,
  numero SERIAL,
  titulo TEXT NOT NULL DEFAULT 'Acta de Reunión',
  tipo_reunion VARCHAR(20) NOT NULL DEFAULT 'virtual',
  -- 'virtual' | 'presencial' | 'mixta'
  contenido TEXT,
  -- Markdown o HTML generado por IA
  formato_origen VARCHAR(20) NOT NULL DEFAULT 'pdf',
  -- 'pdf' | 'word' | 'transcripcion' | 'manual'
  archivo_origen_path TEXT,
  -- Ruta en Supabase Storage si se subió un archivo
  estado VARCHAR(20) NOT NULL DEFAULT 'borrador',
  -- 'borrador' | 'finalizada'
  fecha_reunion TIMESTAMPTZ,
  participantes TEXT,
  -- JSON o texto con lista de participantes
  orden_dia TEXT,
  decisiones TEXT,
  tareas_extraidas TEXT,
  proximos_pasos TEXT,
  observaciones TEXT,
  fecha_creacion TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  fecha_actualizacion TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_actas_reunion ON actas (reunion_id);
CREATE INDEX IF NOT EXISTS idx_actas_estado ON actas (estado);
CREATE INDEX IF NOT EXISTS idx_actas_tipo ON actas (tipo_reunion);
CREATE INDEX IF NOT EXISTS idx_actas_numero ON actas (numero);

-- ---------- 2. RLS ----------
ALTER TABLE actas ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS full_access_actas ON actas;
CREATE POLICY full_access_actas ON actas
  FOR ALL USING (true) WITH CHECK (true);

-- ---------- 3. Función para auto-generar número de acta ----------
CREATE OR REPLACE FUNCTION public.generar_numero_acta()
RETURNS TRIGGER AS $$
BEGIN
  IF NEW.numero IS NULL THEN
    NEW.numero := (
      SELECT COALESCE(MAX(numero), 0) + 1
      FROM public.actas
      WHERE tipo_reunion = NEW.tipo_reunion
    );
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_generar_numero_acta ON actas;
CREATE TRIGGER trg_generar_numero_acta
  BEFORE INSERT ON actas
  FOR EACH ROW
  EXECUTE FUNCTION public.generar_numero_acta();

NOTIFY pgrst, 'reload schema';
