-- ============================================================
-- LIMPIEZA COMPLETA DE LA BASE DE DATOS
-- Ejecutar cada línea por separado en el SQL Editor de Supabase
-- ============================================================

-- Tablas con dependencias FK (hijas primero)
DROP TABLE IF EXISTS audit_log CASCADE;
DROP TABLE IF EXISTS performance_metrics CASCADE;
DROP TABLE IF EXISTS sus_responses CASCADE;
DROP TABLE IF EXISTS time_measurements CASCADE;
DROP TABLE IF EXISTS task_evaluation_matches CASCADE;
DROP TABLE IF EXISTS statistical_analysis_results CASCADE;
DROP TABLE IF EXISTS statistical_analyses CASCADE;
DROP TABLE IF EXISTS experiment_sessions CASCADE;
DROP TABLE IF EXISTS summary_evaluations CASCADE;
DROP TABLE IF EXISTS summary_versions CASCADE;
DROP TABLE IF EXISTS ai_executions CASCADE;
DROP TABLE IF EXISTS reference_tasks CASCADE;
DROP TABLE IF EXISTS prompt_versions CASCADE;
DROP TABLE IF EXISTS actas CASCADE;
DROP TABLE IF EXISTS resumenes_detalle CASCADE;
DROP TABLE IF EXISTS trabajos_resumen CASCADE;
DROP TABLE IF EXISTS resumenes CASCADE;
DROP TABLE IF EXISTS tareas CASCADE;
DROP TABLE IF EXISTS participantes CASCADE;
DROP TABLE IF EXISTS reuniones CASCADE;
DROP TABLE IF EXISTS usuarios CASCADE;
DROP TABLE IF EXISTS metricas_n8n CASCADE;

-- Triggers y funciones
DROP TRIGGER IF EXISTS trg_calcular_sus ON sus_responses CASCADE;
DROP FUNCTION IF EXISTS calcular_puntaje_sus() CASCADE;
DROP TRIGGER IF EXISTS trigger_update_data_hash ON statistical_analyses CASCADE;
DROP FUNCTION IF EXISTS generate_data_hash() CASCADE;
DROP FUNCTION IF EXISTS crear_reunion_con_participantes(jsonb) CASCADE;

-- Tipos enum
DROP TYPE IF EXISTS user_role CASCADE;
