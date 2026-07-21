-- ============================================
-- FASE 1: Migraciones para Evaluación Científica
-- ============================================
-- Este script crea las tablas necesarias para el módulo
-- de evaluación científica y estadística del sistema Zoom2.
-- 
-- Orden de ejecución:
-- 1. Agregar columna de roles a usuarios
-- 2. Crear tablas de prompts y ejecuciones IA
-- 3. Crear tablas de versiones de resúmenes
-- 4. Crear tablas de evaluaciones
-- 5. Crear tablas de experimentos
-- 6. Crear tablas de auditoría
-- ============================================

-- ============================================
-- 1. AGREGAR ROLES A TABLA USUARIOS
-- ============================================

-- Agregar columna de rol
ALTER TABLE usuarios 
ADD COLUMN IF NOT EXISTS rol VARCHAR(20) NOT NULL DEFAULT 'USUARIO';

-- Crear enum para roles (si no existe)
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'user_role') THEN
        CREATE TYPE user_role AS ENUM ('ADMIN', 'INVESTIGADOR', 'EVALUADOR', 'USUARIO');
    END IF;
END $$;

-- Actualizar datos existentes: el admin hardcodeado se convierte en ADMIN
UPDATE usuarios 
SET rol = 'ADMIN' 
WHERE correo = 'anthonygv268@gmail.com';

-- Los demás usuarios se quedan como USUARIO por defecto

-- ============================================
-- 2. TABLA DE VERSIONES DE PROMPTS
-- ============================================

CREATE TABLE IF NOT EXISTS prompt_versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nombre VARCHAR(120) NOT NULL,
    version VARCHAR(30) NOT NULL,
    contenido TEXT NOT NULL,
    objetivo TEXT,
    proveedor VARCHAR(80),
    modelo_recomendado VARCHAR(120),
    activo BOOLEAN NOT NULL DEFAULT true,
    creado_por UUID REFERENCES usuarios(id) ON DELETE SET NULL,
    fecha_creacion TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(nombre, version)
);

-- Índices para prompt_versions
CREATE INDEX IF NOT EXISTS idx_prompt_versions_nombre ON prompt_versions(nombre);
CREATE INDEX IF NOT EXISTS idx_prompt_versions_activo ON prompt_versions(activo);
CREATE INDEX IF NOT EXISTS idx_prompt_versions_creado_por ON prompt_versions(creado_por);

-- ============================================
-- 3. TABLA DE EJECUCIONES DE IA
-- ============================================

CREATE TABLE IF NOT EXISTS ai_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    reunion_id UUID NOT NULL REFERENCES reuniones(id) ON DELETE CASCADE,
    prompt_version_id UUID REFERENCES prompt_versions(id) ON DELETE SET NULL,
    proveedor VARCHAR(80) NOT NULL,
    modelo VARCHAR(120) NOT NULL,
    temperatura NUMERIC,
    parametros JSONB,
    workflow_version VARCHAR(50),
    input_hash VARCHAR(128),
    respuesta_original TEXT,
    respuesta_procesada JSONB,
    tokens_entrada INTEGER,
    tokens_salida INTEGER,
    costo_estimado NUMERIC(14,6),
    tiempo_ms INTEGER,
    reintentos INTEGER NOT NULL DEFAULT 0,
    estado VARCHAR(30) NOT NULL,
    tipo_error VARCHAR(120),
    mensaje_error TEXT,
    iniciado_por UUID REFERENCES usuarios(id) ON DELETE SET NULL,
    fecha_inicio TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    fecha_fin TIMESTAMPTZ
);

-- Índices para ai_executions
CREATE INDEX IF NOT EXISTS idx_ai_executions_reunion ON ai_executions(reunion_id);
CREATE INDEX IF NOT EXISTS idx_ai_executions_prompt_version ON ai_executions(prompt_version_id);
CREATE INDEX IF NOT EXISTS idx_ai_executions_estado ON ai_executions(estado);
CREATE INDEX IF NOT EXISTS idx_ai_executions_fecha_inicio ON ai_executions(fecha_inicio DESC);
CREATE INDEX IF NOT EXISTS idx_ai_executions_modelo ON ai_executions(modelo);

-- ============================================
-- 4. TABLA DE VERSIONES DE RESÚMENES
-- ============================================

CREATE TABLE IF NOT EXISTS summary_versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    reunion_id UUID NOT NULL REFERENCES reuniones(id) ON DELETE CASCADE,
    ai_execution_id UUID REFERENCES ai_executions(id) ON DELETE SET NULL,
    version INTEGER NOT NULL,
    origen VARCHAR(30) NOT NULL,
    contenido TEXT,
    contenido_estructurado JSONB,
    estado VARCHAR(30) NOT NULL DEFAULT 'GENERADO',
    es_version_actual BOOLEAN NOT NULL DEFAULT true,
    creado_por UUID REFERENCES usuarios(id) ON DELETE SET NULL,
    fecha_creacion TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(reunion_id, version)
);

-- Validar origen
ALTER TABLE summary_versions 
ADD CONSTRAINT check_origen 
CHECK (origen IN ('IA', 'HUMANO', 'REGENERACION', 'IMPORTACION'));

-- Validar estado
ALTER TABLE summary_versions 
ADD CONSTRAINT check_estado_resumen 
CHECK (estado IN ('GENERADO', 'PENDIENTE_REVISION', 'EN_REVISION', 'APROBADO', 'RECHAZADO', 'PUBLICADO', 'ARCHIVADO'));

-- Índices para summary_versions
CREATE INDEX IF NOT EXISTS idx_summary_versions_reunion ON summary_versions(reunion_id);
CREATE INDEX IF NOT EXISTS idx_summary_versions_ai_execution ON summary_versions(ai_execution_id);
CREATE INDEX IF NOT EXISTS idx_summary_versions_estado ON summary_versions(estado);
CREATE INDEX IF NOT EXISTS idx_summary_versions_actual ON summary_versions(es_version_actual);

-- ============================================
-- 5. TABLA DE EVALUACIONES DE RESÚMENES
-- ============================================

CREATE TABLE IF NOT EXISTS summary_evaluations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    reunion_id UUID NOT NULL REFERENCES reuniones(id) ON DELETE CASCADE,
    summary_version_id UUID NOT NULL REFERENCES summary_versions(id) ON DELETE CASCADE,
    evaluador_id UUID NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    fidelidad SMALLINT CHECK (fidelidad BETWEEN 1 AND 5),
    cobertura SMALLINT CHECK (cobertura BETWEEN 1 AND 5),
    claridad SMALLINT CHECK (claridad BETWEEN 1 AND 5),
    coherencia SMALLINT CHECK (coherencia BETWEEN 1 AND 5),
    concision SMALLINT CHECK (concision BETWEEN 1 AND 5),
    utilidad SMALLINT CHECK (utilidad BETWEEN 1 AND 5),
    acuerdos_correctos SMALLINT CHECK (acuerdos_correctos BETWEEN 1 AND 5),
    responsables_correctos SMALLINT CHECK (responsables_correctos BETWEEN 1 AND 5),
    fechas_correctas SMALLINT CHECK (fechas_correctas BETWEEN 1 AND 5),
    omisiones INTEGER NOT NULL DEFAULT 0,
    afirmaciones_no_respaldadas INTEGER NOT NULL DEFAULT 0,
    contradicciones INTEGER NOT NULL DEFAULT 0,
    aprobado_sin_cambios BOOLEAN,
    observaciones TEXT,
    fecha_evaluacion TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(summary_version_id, evaluador_id)
);

-- Índices para summary_evaluations
CREATE INDEX IF NOT EXISTS idx_summary_evaluations_reunion ON summary_evaluations(reunion_id);
CREATE INDEX IF NOT EXISTS idx_summary_evaluations_summary_version ON summary_evaluations(summary_version_id);
CREATE INDEX IF NOT EXISTS idx_summary_evaluations_evaluador ON summary_evaluations(evaluador_id);
CREATE INDEX IF NOT EXISTS idx_summary_evaluations_fecha ON summary_evaluations(fecha_evaluacion DESC);

-- ============================================
-- 6. TABLA DE GOLD STANDARD DE TAREAS
-- ============================================

CREATE TABLE IF NOT EXISTS reference_tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    reunion_id UUID NOT NULL REFERENCES reuniones(id) ON DELETE CASCADE,
    descripcion TEXT NOT NULL,
    responsable_referencia TEXT,
    fecha_limite_referencia DATE,
    creado_por UUID NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    validado BOOLEAN NOT NULL DEFAULT false,
    fecha_creacion TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Índices para reference_tasks
CREATE INDEX IF NOT EXISTS idx_reference_tasks_reunion ON reference_tasks(reunion_id);
CREATE INDEX IF NOT EXISTS idx_reference_tasks_creado_por ON reference_tasks(creado_por);
CREATE INDEX IF NOT EXISTS idx_reference_tasks_validado ON reference_tasks(validado);

-- ============================================
-- 7. TABLA DE COINCIDENCIAS DE TAREAS
-- ============================================

CREATE TABLE IF NOT EXISTS task_evaluation_matches (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    reunion_id UUID NOT NULL REFERENCES reuniones(id) ON DELETE CASCADE,
    ai_execution_id UUID REFERENCES ai_executions(id) ON DELETE SET NULL,
    reference_task_id UUID NOT NULL REFERENCES reference_tasks(id) ON DELETE CASCADE,
    detected_task_id UUID REFERENCES tareas(id) ON DELETE SET NULL,
    resultado VARCHAR(10) NOT NULL,
    similitud NUMERIC,
    validado_por UUID REFERENCES usuarios(id) ON DELETE SET NULL,
    observaciones TEXT,
    fecha_registro TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Validar resultado
ALTER TABLE task_evaluation_matches 
ADD CONSTRAINT check_resultado 
CHECK (resultado IN ('TP', 'FP', 'FN', 'TN'));

-- Índices para task_evaluation_matches
CREATE INDEX IF NOT EXISTS idx_task_matches_reunion ON task_evaluation_matches(reunion_id);
CREATE INDEX IF NOT EXISTS idx_task_matches_ai_execution ON task_evaluation_matches(ai_execution_id);
CREATE INDEX IF NOT EXISTS idx_task_matches_reference ON task_evaluation_matches(reference_task_id);
CREATE INDEX IF NOT EXISTS idx_task_matches_detected ON task_evaluation_matches(detected_task_id);
CREATE INDEX IF NOT EXISTS idx_task_matches_resultado ON task_evaluation_matches(resultado);

-- ============================================
-- 8. TABLA DE SESIONES EXPERIMENTALES
-- ============================================

CREATE TABLE IF NOT EXISTS experiment_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nombre VARCHAR(160) NOT NULL,
    descripcion TEXT,
    investigador_id UUID NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    condicion VARCHAR(80) NOT NULL,
    prompt_version_id UUID REFERENCES prompt_versions(id) ON DELETE SET NULL,
    modelo VARCHAR(120),
    fecha_inicio TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    fecha_fin TIMESTAMPTZ,
    configuracion JSONB,
    estado VARCHAR(30) NOT NULL DEFAULT 'PLANIFICADO'
);

-- Validar estado
ALTER TABLE experiment_sessions 
ADD CONSTRAINT check_estado_experiment 
CHECK (estado IN ('PLANIFICADO', 'EN_CURSO', 'COMPLETADO', 'CANCELADO'));

-- Índices para experiment_sessions
CREATE INDEX IF NOT EXISTS idx_experiment_sessions_investigador ON experiment_sessions(investigador_id);
CREATE INDEX IF NOT EXISTS idx_experiment_sessions_condicion ON experiment_sessions(condicion);
CREATE INDEX IF NOT EXISTS idx_experiment_sessions_estado ON experiment_sessions(estado);
CREATE INDEX IF NOT EXISTS idx_experiment_sessions_fecha_inicio ON experiment_sessions(fecha_inicio DESC);

-- ============================================
-- 9. TABLA DE MEDICIONES DE TIEMPO
-- ============================================

CREATE TABLE IF NOT EXISTS time_measurements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    experiment_session_id UUID REFERENCES experiment_sessions(id) ON DELETE SET NULL,
    reunion_id UUID NOT NULL REFERENCES reuniones(id) ON DELETE CASCADE,
    participante_id UUID REFERENCES usuarios(id) ON DELETE SET NULL,
    condicion VARCHAR(80) NOT NULL,
    tiempo_elaboracion_segundos INTEGER,
    tiempo_revision_segundos INTEGER,
    tiempo_total_segundos INTEGER,
    errores_detectados INTEGER,
    fecha_registro TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Índices para time_measurements
CREATE INDEX IF NOT EXISTS idx_time_measurements_session ON time_measurements(experiment_session_id);
CREATE INDEX IF NOT EXISTS idx_time_measurements_reunion ON time_measurements(reunion_id);
CREATE INDEX IF NOT EXISTS idx_time_measurements_participante ON time_measurements(participante_id);
CREATE INDEX IF NOT EXISTS idx_time_measurements_condicion ON time_measurements(condicion);

-- ============================================
-- 10. TABLA DE EVALUACIÓN SUS
-- ============================================

CREATE TABLE IF NOT EXISTS sus_responses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    experiment_session_id UUID REFERENCES experiment_sessions(id) ON DELETE SET NULL,
    usuario_id UUID NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    q1 SMALLINT NOT NULL CHECK (q1 BETWEEN 1 AND 5),
    q2 SMALLINT NOT NULL CHECK (q2 BETWEEN 1 AND 5),
    q3 SMALLINT NOT NULL CHECK (q3 BETWEEN 1 AND 5),
    q4 SMALLINT NOT NULL CHECK (q4 BETWEEN 1 AND 5),
    q5 SMALLINT NOT NULL CHECK (q5 BETWEEN 1 AND 5),
    q6 SMALLINT NOT NULL CHECK (q6 BETWEEN 1 AND 5),
    q7 SMALLINT NOT NULL CHECK (q7 BETWEEN 1 AND 5),
    q8 SMALLINT NOT NULL CHECK (q8 BETWEEN 1 AND 5),
    q9 SMALLINT NOT NULL CHECK (q9 BETWEEN 1 AND 5),
    q10 SMALLINT NOT NULL CHECK (q10 BETWEEN 1 AND 5),
    puntaje_sus NUMERIC(5,2),
    observaciones TEXT,
    fecha_registro TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Índices para sus_responses
CREATE INDEX IF NOT EXISTS idx_sus_responses_session ON sus_responses(experiment_session_id);
CREATE INDEX IF NOT EXISTS idx_sus_responses_usuario ON sus_responses(usuario_id);
CREATE INDEX IF NOT EXISTS idx_sus_responses_fecha ON sus_responses(fecha_registro DESC);

-- ============================================
-- 11. TABLA DE MÉTRICAS DE RENDIMIENTO
-- ============================================

CREATE TABLE IF NOT EXISTS performance_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    reunion_id UUID REFERENCES reuniones(id) ON DELETE SET NULL,
    ai_execution_id UUID REFERENCES ai_executions(id) ON DELETE SET NULL,
    componente VARCHAR(80) NOT NULL,
    operacion VARCHAR(120) NOT NULL,
    duracion_ms INTEGER,
    exitoso BOOLEAN NOT NULL,
    codigo_estado VARCHAR(40),
    mensaje_error TEXT,
    metadata JSONB,
    fecha_registro TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Índices para performance_metrics
CREATE INDEX IF NOT EXISTS idx_performance_metrics_reunion ON performance_metrics(reunion_id);
CREATE INDEX IF NOT EXISTS idx_performance_metrics_ai_execution ON performance_metrics(ai_execution_id);
CREATE INDEX IF NOT EXISTS idx_performance_metrics_componente ON performance_metrics(componente);
CREATE INDEX IF NOT EXISTS idx_performance_metrics_fecha ON performance_metrics(fecha_registro DESC);

-- ============================================
-- 12. TABLA DE AUDITORÍA
-- ============================================

CREATE TABLE IF NOT EXISTS audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    usuario_id UUID REFERENCES usuarios(id) ON DELETE SET NULL,
    accion VARCHAR(120) NOT NULL,
    entidad VARCHAR(120),
    entidad_id UUID,
    datos_anteriores JSONB,
    datos_nuevos JSONB,
    ip_hash VARCHAR(128),
    fecha TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Índices para audit_log
CREATE INDEX IF NOT EXISTS idx_audit_log_usuario ON audit_log(usuario_id);
CREATE INDEX IF NOT EXISTS idx_audit_log_accion ON audit_log(accion);
CREATE INDEX IF NOT EXISTS idx_audit_log_entidad ON audit_log(entidad);
CREATE INDEX IF NOT EXISTS idx_audit_log_fecha ON audit_log(fecha DESC);

-- ============================================
-- 13. ROW LEVEL SECURITY (RLS)
-- ============================================

-- Habilitar RLS en tablas nuevas
ALTER TABLE prompt_versions ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_executions ENABLE ROW LEVEL SECURITY;
ALTER TABLE summary_versions ENABLE ROW LEVEL SECURITY;
ALTER TABLE summary_evaluations ENABLE ROW LEVEL SECURITY;
ALTER TABLE reference_tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE task_evaluation_matches ENABLE ROW LEVEL SECURITY;
ALTER TABLE experiment_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE time_measurements ENABLE ROW LEVEL SECURITY;
ALTER TABLE sus_responses ENABLE ROW LEVEL SECURITY;
ALTER TABLE performance_metrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_log ENABLE ROW LEVEL SECURITY;

-- Políticas básicas (se pueden refinar según requisitos)
-- Por ahora, acceso completo para autenticados (se ajustará con roles)

CREATE POLICY full_access_prompt_versions ON prompt_versions
FOR ALL USING (true);

CREATE POLICY full_access_ai_executions ON ai_executions
FOR ALL USING (true);

CREATE POLICY full_access_summary_versions ON summary_versions
FOR ALL USING (true);

CREATE POLICY full_access_summary_evaluations ON summary_evaluations
FOR ALL USING (true);

CREATE POLICY full_access_reference_tasks ON reference_tasks
FOR ALL USING (true);

CREATE POLICY full_access_task_evaluation_matches ON task_evaluation_matches
FOR ALL USING (true);

CREATE POLICY full_access_experiment_sessions ON experiment_sessions
FOR ALL USING (true);

CREATE POLICY full_access_time_measurements ON time_measurements
FOR ALL USING (true);

CREATE POLICY full_access_sus_responses ON sus_responses
FOR ALL USING (true);

CREATE POLICY full_access_performance_metrics ON performance_metrics
FOR ALL USING (true);

CREATE POLICY full_access_audit_log ON audit_log
FOR ALL USING (true);

-- ============================================
-- 14. FUNCIÓN PARA CALCULAR PUNTAJE SUS
-- ============================================

CREATE OR REPLACE FUNCTION calcular_puntaje_sus(
    q1 SMALLINT, q2 SMALLINT, q3 SMALLINT, q4 SMALLINT,
    q5 SMALLINT, q6 SMALLINT, q7 SMALLINT, q8 SMALLINT,
    q9 SMALLINT, q10 SMALLINT
) RETURNS NUMERIC AS $$
BEGIN
    RETURN (
        (q1 - 1) + (5 - q2) + (q3 - 1) + (5 - q4) +
        (q5 - 1) + (5 - q6) + (q7 - 1) + (5 - q8) +
        (q9 - 1) + (5 - q10)
    ) * 2.5;
END;
$$ LANGUAGE plpgsql;

-- Trigger para calcular puntaje SUS automáticamente
CREATE OR REPLACE FUNCTION trigger_calcular_sus()
RETURNS TRIGGER AS $$
BEGIN
    NEW.puntaje_sus = calcular_puntaje_sus(
        NEW.q1, NEW.q2, NEW.q3, NEW.q4,
        NEW.q5, NEW.q6, NEW.q7, NEW.q8,
        NEW.q9, NEW.q10
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_calcular_sus
BEFORE INSERT OR UPDATE ON sus_responses
FOR EACH ROW
EXECUTE FUNCTION trigger_calcular_sus();

-- ============================================
-- 15. DATOS INICIALES DE PRUEBA
-- ============================================

-- Insertar un prompt de ejemplo
INSERT INTO prompt_versions (nombre, version, contenido, objetivo, proveedor, modelo_recomendado, activo)
VALUES (
    'resumen_reunion',
    '1.0',
    'Genera un resumen estructurado de la reunión incluyendo: título, resumen ejecutivo, temas principales, decisiones, acuerdos con responsables y fechas, riesgos identificados y preguntas pendientes.',
    'Generar resúmenes de reuniones con estructura JSON',
    'openai',
    'gpt-4',
    true
) ON CONFLICT (nombre, version) DO NOTHING;

-- ============================================
-- FIN DE MIGRACIÓN
-- ============================================

-- Verificación
SELECT 
    'prompt_versions' as tabla, COUNT(*) as registros FROM prompt_versions
UNION ALL
SELECT 'ai_executions', COUNT(*) FROM ai_executions
UNION ALL
SELECT 'summary_versions', COUNT(*) FROM summary_versions
UNION ALL
SELECT 'summary_evaluations', COUNT(*) FROM summary_evaluations
UNION ALL
SELECT 'reference_tasks', COUNT(*) FROM reference_tasks
UNION ALL
SELECT 'task_evaluation_matches', COUNT(*) FROM task_evaluation_matches
UNION ALL
SELECT 'experiment_sessions', COUNT(*) FROM experiment_sessions
UNION ALL
SELECT 'time_measurements', COUNT(*) FROM time_measurements
UNION ALL
SELECT 'sus_responses', COUNT(*) FROM sus_responses
UNION ALL
SELECT 'performance_metrics', COUNT(*) FROM performance_metrics
UNION ALL
SELECT 'audit_log', COUNT(*) FROM audit_log;
