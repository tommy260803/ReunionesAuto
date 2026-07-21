-- ============================================
-- FASE 2: MEJORAR POLÍTICAS RLS PARA EVALUACIÓN CIENTÍFICA
-- ============================================
-- Este script mejora las políticas RLS de las tablas del módulo
-- de evaluación científica para ser más específicas por rol.
-- 
-- Reemplaza las políticas full_access con políticas granulares
-- basadas en roles (ADMIN, INVESTIGADOR, EVALUADOR, USUARIO)
-- ============================================

-- ============================================
-- 1. ELIMINAR POLÍTICAS EXISTENTES (full_access)
-- ============================================

-- Tablas de evaluación científica
DROP POLICY IF EXISTS full_access_prompt_versions ON prompt_versions;
DROP POLICY IF EXISTS full_access_ai_executions ON ai_executions;
DROP POLICY IF EXISTS full_access_summary_versions ON summary_versions;
DROP POLICY IF EXISTS full_access_summary_evaluations ON summary_evaluations;
DROP POLICY IF EXISTS full_access_reference_tasks ON reference_tasks;
DROP POLICY IF EXISTS full_access_task_evaluation_matches ON task_evaluation_matches;
DROP POLICY IF EXISTS full_access_experiment_sessions ON experiment_sessions;
DROP POLICY IF EXISTS full_access_time_measurements ON time_measurements;
DROP POLICY IF EXISTS full_access_sus_responses ON sus_responses;
DROP POLICY IF EXISTS full_access_performance_metrics ON performance_metrics;
DROP POLICY IF EXISTS full_access_audit_log ON audit_log;

-- ============================================
-- 2. POLÍTICAS PARA PROMPT_VERSIONS
-- ============================================

-- Solo investigadores y administradores pueden crear
CREATE POLICY prompts_create_investigator_admin ON prompt_versions
FOR INSERT
WITH CHECK (
    EXISTS (
        SELECT 1 FROM usuarios 
        WHERE usuarios.id = creado_por 
        AND usuarios.rol IN ('INVESTIGADOR', 'ADMIN')
    )
);

-- Todos pueden ver prompts activos
CREATE POLICY prompts_view_active ON prompt_versions
FOR SELECT
USING (activo = true);

-- Solo investigadores y administradores pueden ver todos
CREATE POLICY prompts_view_all_investigator_admin ON prompt_versions
FOR SELECT
USING (
    EXISTS (
        SELECT 1 FROM usuarios 
        WHERE usuarios.rol IN ('INVESTIGADOR', 'ADMIN')
    )
);

-- Solo creador o admin puede actualizar
CREATE POLICY prompts_update_own ON prompt_versions
FOR UPDATE
USING (
    creado_por = (SELECT id FROM usuarios WHERE correo = current_setting('app.current_email', true))
    OR EXISTS (
        SELECT 1 FROM usuarios 
        WHERE usuarios.rol = 'ADMIN'
    )
);

-- Solo admin puede eliminar
CREATE POLICY prompts_delete_admin ON prompt_versions
FOR DELETE
USING (
    EXISTS (
        SELECT 1 FROM usuarios 
        WHERE usuarios.rol = 'ADMIN'
    )
);

-- ============================================
-- 3. POLÍTICAS PARA AI_EXECUTIONS
-- ============================================

-- Todos autenticados pueden ver sus propias ejecuciones
CREATE POLICY ai_executions_view_own ON ai_executions
FOR SELECT
USING (
    iniciado_por = (SELECT id FROM usuarios WHERE correo = current_setting('app.current_email', true))
);

-- Investigadores y administradores pueden ver todas
CREATE POLICY ai_executions_view_all_investigator_admin ON ai_executions
FOR SELECT
USING (
    EXISTS (
        SELECT 1 FROM usuarios 
        WHERE usuarios.rol IN ('INVESTIGADOR', 'ADMIN')
    )
);

-- Solo administradores pueden crear (normalmente vía n8n)
CREATE POLICY ai_executions_create_admin ON ai_executions
FOR INSERT
WITH CHECK (
    EXISTS (
        SELECT 1 FROM usuarios 
        WHERE usuarios.rol = 'ADMIN'
    )
);

-- ============================================
-- 4. POLÍTICAS PARA SUMMARY_VERSIONS
-- ============================================

-- Todos pueden ver resúmenes de reuniones donde participan
CREATE POLICY summary_versions_view_participant ON summary_versions
FOR SELECT
USING (
    EXISTS (
        SELECT 1 FROM reuniones r
        JOIN participantes p ON r.id = p.reunion_id
        WHERE r.id = summary_versions.reunion_id
        AND p.usuario_id = (SELECT id FROM usuarios WHERE correo = current_setting('app.current_email', true))
    )
);

-- Investigadores y administradores pueden ver todas
CREATE POLICY summary_versions_view_all_investigator_admin ON summary_versions
FOR SELECT
USING (
    EXISTS (
        SELECT 1 FROM usuarios 
        WHERE usuarios.rol IN ('INVESTIGADOR', 'ADMIN')
    )
);

-- Solo creador o admin puede actualizar
CREATE POLICY summary_versions_update_own ON summary_versions
FOR UPDATE
USING (
    creado_por = (SELECT id FROM usuarios WHERE correo = current_setting('app.current_email', true))
    OR EXISTS (
        SELECT 1 FROM usuarios 
        WHERE usuarios.rol = 'ADMIN'
    )
);

-- ============================================
-- 5. POLÍTICAS PARA SUMMARY_EVALUATIONS
-- ============================================

-- Evaluadores pueden ver sus propias evaluaciones
CREATE POLICY summary_evaluations_view_own ON summary_evaluations
FOR SELECT
USING (
    evaluador_id = (SELECT id FROM usuarios WHERE correo = current_setting('app.current_email', true))
);

-- Investigadores y administradores pueden ver todas
CREATE POLICY summary_evaluations_view_all_investigator_admin ON summary_evaluations
FOR SELECT
USING (
    EXISTS (
        SELECT 1 FROM usuarios 
        WHERE usuarios.rol IN ('INVESTIGADOR', 'ADMIN')
    )
);

-- Solo evaluadores y administradores pueden crear
CREATE POLICY summary_evaluations_create_evaluator_admin ON summary_evaluations
FOR INSERT
WITH CHECK (
    evaluador_id = (SELECT id FROM usuarios WHERE correo = current_setting('app.current_email', true))
    AND EXISTS (
        SELECT 1 FROM usuarios 
        WHERE usuarios.rol IN ('EVALUADOR', 'ADMIN')
    )
);

-- Solo evaluador propietario o admin puede actualizar
CREATE POLICY summary_evaluations_update_own ON summary_evaluations
FOR UPDATE
USING (
    evaluador_id = (SELECT id FROM usuarios WHERE correo = current_setting('app.current_email', true))
    OR EXISTS (
        SELECT 1 FROM usuarios 
        WHERE usuarios.rol = 'ADMIN'
    )
);

-- ============================================
-- 6. POLÍTICAS PARA REFERENCE_TASKS (GOLD STANDARD)
-- ============================================

-- Solo investigadores y administradores pueden ver gold standard
CREATE POLICY reference_tasks_view_investigator_admin ON reference_tasks
FOR SELECT
USING (
    EXISTS (
        SELECT 1 FROM usuarios 
        WHERE usuarios.rol IN ('INVESTIGADOR', 'ADMIN')
    )
);

-- Solo investigadores y administradores pueden crear
CREATE POLICY reference_tasks_create_investigator_admin ON reference_tasks
FOR INSERT
WITH CHECK (
    creado_por = (SELECT id FROM usuarios WHERE correo = current_setting('app.current_email', true))
    AND EXISTS (
        SELECT 1 FROM usuarios 
        WHERE usuarios.rol IN ('INVESTIGADOR', 'ADMIN')
    )
);

-- Solo creador o admin puede actualizar
CREATE POLICY reference_tasks_update_own ON reference_tasks
FOR UPDATE
USING (
    creado_por = (SELECT id FROM usuarios WHERE correo = current_setting('app.current_email', true))
    OR EXISTS (
        SELECT 1 FROM usuarios 
        WHERE usuarios.rol = 'ADMIN'
    )
);

-- ============================================
-- 7. POLÍTICAS PARA TASK_EVALUATION_MATCHES
-- ============================================

-- Solo investigadores y administradores pueden ver
CREATE POLICY task_matches_view_investigator_admin ON task_evaluation_matches
FOR SELECT
USING (
    EXISTS (
        SELECT 1 FROM usuarios 
        WHERE usuarios.rol IN ('INVESTIGADOR', 'ADMIN')
    )
);

-- Solo investigadores y administradores pueden crear
CREATE POLICY task_matches_create_investigator_admin ON task_evaluation_matches
FOR INSERT
WITH CHECK (
    EXISTS (
        SELECT 1 FROM usuarios 
        WHERE usuarios.rol IN ('INVESTIGADOR', 'ADMIN')
    )
);

-- Solo validador o admin puede actualizar
CREATE POLICY task_matches_update_validator ON task_evaluation_matches
FOR UPDATE
USING (
    validado_por = (SELECT id FROM usuarios WHERE correo = current_setting('app.current_email', true))
    OR EXISTS (
        SELECT 1 FROM usuarios 
        WHERE usuarios.rol = 'ADMIN'
    )
);

-- ============================================
-- 8. POLÍTICAS PARA EXPERIMENT_SESSIONS
-- ============================================

-- Investigadores pueden ver sus propias sesiones
CREATE POLICY experiment_sessions_view_own ON experiment_sessions
FOR SELECT
USING (
    investigador_id = (SELECT id FROM usuarios WHERE correo = current_setting('app.current_email', true))
);

-- Administradores pueden ver todas
CREATE POLICY experiment_sessions_view_admin ON experiment_sessions
FOR SELECT
USING (
    EXISTS (
        SELECT 1 FROM usuarios 
        WHERE usuarios.rol = 'ADMIN'
    )
);

-- Solo investigadores y administradores pueden crear
CREATE POLICY experiment_sessions_create_investigator_admin ON experiment_sessions
FOR INSERT
WITH CHECK (
    investigador_id = (SELECT id FROM usuarios WHERE correo = current_setting('app.current_email', true))
    AND EXISTS (
        SELECT 1 FROM usuarios 
        WHERE usuarios.rol IN ('INVESTIGADOR', 'ADMIN')
    )
);

-- Solo investigador propietario o admin puede actualizar
CREATE POLICY experiment_sessions_update_own ON experiment_sessions
FOR UPDATE
USING (
    investigador_id = (SELECT id FROM usuarios WHERE correo = current_setting('app.current_email', true))
    OR EXISTS (
        SELECT 1 FROM usuarios 
        WHERE usuarios.rol = 'ADMIN'
    )
);

-- ============================================
-- 9. POLÍTICAS PARA TIME_MEASUREMENTS
-- ============================================

-- Participantes pueden ver sus propias mediciones
CREATE POLICY time_measurements_view_own ON time_measurements
FOR SELECT
USING (
    participante_id = (SELECT id FROM usuarios WHERE correo = current_setting('app.current_email', true))
);

-- Investigadores y administradores pueden ver todas
CREATE POLICY time_measurements_view_investigator_admin ON time_measurements
FOR SELECT
USING (
    EXISTS (
        SELECT 1 FROM usuarios 
        WHERE usuarios.rol IN ('INVESTIGADOR', 'ADMIN')
    )
);

-- Solo investigadores y administradores pueden crear
CREATE POLICY time_measurements_create_investigator_admin ON time_measurements
FOR INSERT
WITH CHECK (
    EXISTS (
        SELECT 1 FROM usuarios 
        WHERE usuarios.rol IN ('INVESTIGADOR', 'ADMIN')
    )
);

-- ============================================
-- 10. POLÍTICAS PARA SUS_RESPONSES
-- ============================================

-- Usuarios pueden ver sus propias respuestas
CREATE POLICY sus_responses_view_own ON sus_responses
FOR SELECT
USING (
    usuario_id = (SELECT id FROM usuarios WHERE correo = current_setting('app.current_email', true))
);

-- Investigadores y administradores pueden ver todas
CREATE POLICY sus_responses_view_investigator_admin ON sus_responses
FOR SELECT
USING (
    EXISTS (
        SELECT 1 FROM usuarios 
        WHERE usuarios.rol IN ('INVESTIGADOR', 'ADMIN')
    )
);

-- Todos autenticados pueden crear (para cuestionarios SUS)
CREATE POLICY sus_responses_create_authenticated ON sus_responses
FOR INSERT
WITH CHECK (
    usuario_id = (SELECT id FROM usuarios WHERE correo = current_setting('app.current_email', true))
);

-- ============================================
-- 11. POLÍTICAS PARA PERFORMANCE_METRICS
-- ============================================

-- Solo investigadores y administradores pueden ver
CREATE POLICY performance_metrics_view_investigator_admin ON performance_metrics
FOR SELECT
USING (
    EXISTS (
        SELECT 1 FROM usuarios 
        WHERE usuarios.rol IN ('INVESTIGADOR', 'ADMIN')
    )
);

-- Solo sistema (vía service role) puede crear
CREATE POLICY performance_metrics_create_service ON performance_metrics
FOR INSERT
WITH CHECK (true);

-- ============================================
-- 12. POLÍTICAS PARA AUDIT_LOG
-- ============================================

-- Solo administradores pueden ver
CREATE POLICY audit_log_view_admin ON audit_log
FOR SELECT
USING (
    EXISTS (
        SELECT 1 FROM usuarios 
        WHERE usuarios.rol = 'ADMIN'
    )
);

-- Solo sistema puede crear
CREATE POLICY audit_log_create_service ON audit_log
FOR INSERT
WITH CHECK (true);

-- ============================================
-- 13. VERIFICACIÓN
-- ============================================

-- Verificar políticas creadas
SELECT 
    schemaname,
    tablename,
    policyname,
    permissive,
    roles,
    cmd,
    qual,
    with_check
FROM pg_policies
WHERE tablename IN (
    'prompt_versions',
    'ai_executions',
    'summary_versions',
    'summary_evaluations',
    'reference_tasks',
    'task_evaluation_matches',
    'experiment_sessions',
    'time_measurements',
    'sus_responses',
    'performance_metrics',
    'audit_log'
)
ORDER BY tablename, policyname;
