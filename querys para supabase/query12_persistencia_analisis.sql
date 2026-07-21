-- ============================================
-- FASE 2: PERSISTENCIA DE ANÁLISIS ESTADÍSTICOS
-- ============================================
-- Este script crea las tablas necesarias para persistir
-- análisis estadísticos y garantizar reproducibilidad.
-- 
-- Basado en Sección 17.1.3 de especificaciones
-- ============================================

-- ============================================
-- 1. TABLA DE ANÁLISIS ESTADÍSTICOS
-- ============================================

CREATE TABLE IF NOT EXISTS statistical_analyses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    experiment_session_id UUID REFERENCES experiment_sessions(id) ON DELETE SET NULL,
    nombre VARCHAR(180) NOT NULL,
    objetivo TEXT,
    variable_resultado VARCHAR(120) NOT NULL,
    variable_grupo VARCHAR(120),
    diseno VARCHAR(40) NOT NULL,
    prueba_solicitada VARCHAR(80),
    prueba_ejecutada VARCHAR(80) NOT NULL,
    alpha NUMERIC(6,5) NOT NULL DEFAULT 0.05,
    correccion_multiple VARCHAR(40),
    filtros JSONB NOT NULL DEFAULT '{}'::jsonb,
    configuracion JSONB NOT NULL DEFAULT '{}'::jsonb,
    estado VARCHAR(30) NOT NULL,
    datos_hash VARCHAR(128),
    codigo_version VARCHAR(80),
    creado_por UUID NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    fecha_creacion TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    fecha_ejecucion TIMESTAMPTZ
);

-- Validar estado
ALTER TABLE statistical_analyses 
ADD CONSTRAINT check_estado_analisis 
CHECK (estado IN ('PLANIFICADO', 'VALIDADO', 'EJECUTANDO', 'COMPLETADO', 'ERROR', 'CANCELADO'));

-- Validar diseño
ALTER TABLE statistical_analyses 
ADD CONSTRAINT check_diseno_analisis 
CHECK (diseno IN ('INDEPENDIENTE', 'PAREADO', 'MEDIDAS_REPETIDAS'));

-- Validar corrección múltiple
ALTER TABLE statistical_analyses 
ADD CONSTRAINT check_correccion_analisis 
CHECK (correccion_multiple IN ('BONFERRONI', 'HOLM', 'NONE', NULL));

-- Índices para statistical_analyses
CREATE INDEX IF NOT EXISTS idx_statistical_analyses_session ON statistical_analyses(experiment_session_id);
CREATE INDEX IF NOT EXISTS idx_statistical_analyses_creado_por ON statistical_analyses(creado_por);
CREATE INDEX IF NOT EXISTS idx_statistical_analyses_estado ON statistical_analyses(estado);
CREATE INDEX IF NOT EXISTS idx_statistical_analyses_fecha_creacion ON statistical_analyses(fecha_creacion DESC);
CREATE INDEX IF NOT EXISTS idx_statistical_analyses_prueba ON statistical_analyses(prueba_ejecutada);

-- ============================================
-- 2. TABLA DE RESULTADOS DE ANÁLISIS
-- ============================================

CREATE TABLE IF NOT EXISTS statistical_analysis_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    analysis_id UUID NOT NULL REFERENCES statistical_analyses(id) ON DELETE CASCADE,
    resultado JSONB NOT NULL,
    descriptivos JSONB,
    supuestos JSONB,
    efecto JSONB,
    intervalos JSONB,
    advertencias JSONB,
    interpretacion TEXT,
    fecha_registro TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Índices para statistical_analysis_results
CREATE INDEX IF NOT EXISTS idx_statistical_results_analysis ON statistical_analysis_results(analysis_id);
CREATE INDEX IF NOT EXISTS idx_statistical_results_fecha ON statistical_analysis_results(fecha_registro DESC);

-- ============================================
-- 3. ROW LEVEL SECURITY (RLS)
-- ============================================

-- Habilitar RLS en tablas nuevas
ALTER TABLE statistical_analyses ENABLE ROW LEVEL SECURITY;
ALTER TABLE statistical_analysis_results ENABLE ROW LEVEL SECURITY;

-- Políticas para statistical_analyses
-- Los investigadores pueden crear y ver sus propios análisis
CREATE POLICY investigators_can_create_analyses ON statistical_analyses
FOR INSERT
WITH CHECK (
    EXISTS (
        SELECT 1 FROM usuarios 
        WHERE usuarios.id = creado_por 
        AND usuarios.rol IN ('INVESTIGADOR', 'ADMIN')
    )
);

CREATE POLICY investigators_can_view_own_analyses ON statistical_analyses
FOR SELECT
USING (
    creado_por = (SELECT id FROM usuarios WHERE correo = current_setting('app.current_email', true))
    OR EXISTS (
        SELECT 1 FROM usuarios 
        WHERE usuarios.id = creado_por 
        AND usuarios.rol = 'ADMIN'
    )
);

CREATE POLICY investigators_can_update_own_analyses ON statistical_analyses
FOR UPDATE
USING (
    creado_por = (SELECT id FROM usuarios WHERE correo = current_setting('app.current_email', true))
);

-- Los administradores pueden hacer todo
CREATE POLICY admins_full_access_analyses ON statistical_analyses
FOR ALL
USING (
    EXISTS (
        SELECT 1 FROM usuarios 
        WHERE usuarios.rol = 'ADMIN'
    )
);

-- Políticas para statistical_analysis_results
-- Los resultados se heredan del análisis padre
CREATE POLICY view_results_via_analysis ON statistical_analysis_results
FOR SELECT
USING (
    EXISTS (
        SELECT 1 FROM statistical_analyses sa
        WHERE sa.id = analysis_id
        AND (
            sa.creado_por = (SELECT id FROM usuarios WHERE correo = current_setting('app.current_email', true))
            OR EXISTS (
                SELECT 1 FROM usuarios 
                WHERE usuarios.id = sa.creado_por 
                AND usuarios.rol = 'ADMIN'
            )
        )
    )
);

CREATE POLICY insert_results_via_analysis ON statistical_analysis_results
FOR INSERT
WITH CHECK (
    EXISTS (
        SELECT 1 FROM statistical_analyses sa
        WHERE sa.id = analysis_id
        AND (
            sa.creado_por = (SELECT id FROM usuarios WHERE correo = current_setting('app.current_email', true))
            OR EXISTS (
                SELECT 1 FROM usuarios 
                WHERE usuarios.rol = 'ADMIN'
            )
        )
    )
);

-- ============================================
-- 4. FUNCIÓN PARA GENERAR HASH DE DATOS
-- ============================================

CREATE OR REPLACE FUNCTION generate_data_hash(data JSONB)
RETURNS VARCHAR(128) AS $$
BEGIN
    RETURN encode(digest(data::text, 'sha256'), 'hex');
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- 5. TRIGGER PARA ACTUALIZAR DATOS_HASH
-- ============================================

CREATE OR REPLACE FUNCTION update_analysis_data_hash()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.filtros IS DISTINCT FROM OLD.filtros OR NEW.configuracion IS DISTINCT FROM OLD.configuracion THEN
        NEW.datos_hash = generate_data_hash(NEW.filtros || NEW.configuracion);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_data_hash
BEFORE INSERT OR UPDATE ON statistical_analyses
FOR EACH ROW
EXECUTE FUNCTION update_analysis_data_hash();

-- ============================================
-- 6. VERIFICACIÓN
-- ============================================

-- Verificar tablas creadas
SELECT 
    table_name,
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns
WHERE table_name IN ('statistical_analyses', 'statistical_analysis_results')
ORDER BY table_name, ordinal_position;

-- Verificar índices creados
SELECT 
    indexname,
    tablename
FROM pg_indexes
WHERE tablename IN ('statistical_analyses', 'statistical_analysis_results')
ORDER BY tablename, indexname;
