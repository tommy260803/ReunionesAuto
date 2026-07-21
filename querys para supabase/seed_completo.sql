-- ============================================================
-- SEED COMPLETO Y EXTENSO — REUNIONESAUTO (ZOOM2)
-- ============================================================
-- Ejecutar DESPUÉS de query1-query13.
-- Contraseña: password123 | Idempotente.
-- ============================================================

DELETE FROM task_evaluation_matches;
DELETE FROM performance_metrics;
DELETE FROM sus_responses;
DELETE FROM time_measurements;
DELETE FROM statistical_analysis_results;
DELETE FROM statistical_analyses;
DELETE FROM summary_evaluations;
DELETE FROM summary_versions;
DELETE FROM ai_executions;
DELETE FROM reference_tasks;
DELETE FROM prompt_versions;
DELETE FROM experiment_sessions;
DELETE FROM resumenes_detalle;
DELETE FROM resumenes;
DELETE FROM tareas;
DELETE FROM participantes;
DELETE FROM reuniones;
DELETE FROM metricas_n8n;
DELETE FROM usuarios;

-- 1. USUARIOS
INSERT INTO usuarios (id, nombre, correo, password_hash, nivel_suscripcion, estado_suscripcion, rol) VALUES
('a0000000-0000-0000-0000-000000000001', 'Anthony García', 'anthonygv268@gmail.com', '$2b$12$zChrGI196GrAJwB54kuPbuaK5BYv3XqBRoA5cZnMMsrUjbXecl0Nm', 'enterprise', 'activo', 'ADMIN'),
('a0000000-0000-0000-0000-000000000002', 'Dra. Laura Medina', 'laura@zoom2.test', '$2b$12$zChrGI196GrAJwB54kuPbuaK5BYv3XqBRoA5cZnMMsrUjbXecl0Nm', 'pro', 'activo', 'INVESTIGADOR'),
('a0000000-0000-0000-0000-000000000003', 'Carlos Ríos', 'carlos@zoom2.test', '$2b$12$zChrGI196GrAJwB54kuPbuaK5BYv3XqBRoA5cZnMMsrUjbXecl0Nm', 'pro', 'activo', 'EVALUADOR'),
('a0000000-0000-0000-0000-000000000004', 'María López', 'maria@zoom2.test', '$2b$12$zChrGI196GrAJwB54kuPbuaK5BYv3XqBRoA5cZnMMsrUjbXecl0Nm', 'basico', 'activo', 'USUARIO'),
('a0000000-0000-0000-0000-000000000005', 'Ing. Andrés Vega', 'andres@zoom2.test', '$2b$12$zChrGI196GrAJwB54kuPbuaK5BYv3XqBRoA5cZnMMsrUjbXecl0Nm', 'pro', 'activo', 'INVESTIGADOR'),
('a0000000-0000-0000-0000-000000000006', 'Dra. Sofía Torres', 'sofia@zoom2.test', '$2b$12$zChrGI196GrAJwB54kuPbuaK5BYv3XqBRoA5cZnMMsrUjbXecl0Nm', 'pro', 'activo', 'INVESTIGADOR'),
('a0000000-0000-0000-0000-000000000007', 'Pedro Morales', 'pedro@zoom2.test', '$2b$12$zChrGI196GrAJwB54kuPbuaK5BYv3XqBRoA5cZnMMsrUjbXecl0Nm', 'basico', 'activo', 'EVALUADOR'),
('a0000000-0000-0000-0000-000000000008', 'Ana Ruiz', 'ana@zoom2.test', '$2b$12$zChrGI196GrAJwB54kuPbuaK5BYv3XqBRoA5cZnMMsrUjbXecl0Nm', 'pro', 'activo', 'USUARIO'),
('a0000000-0000-0000-0000-000000000009', 'Diego Fernández', 'diego@zoom2.test', '$2b$12$zChrGI196GrAJwB54kuPbuaK5BYv3XqBRoA5cZnMMsrUjbXecl0Nm', 'basico', 'activo', 'USUARIO'),
('a0000000-0000-0000-0000-000000000010', 'Ing. Camila Reyes', 'camila@zoom2.test', '$2b$12$zChrGI196GrAJwB54kuPbuaK5BYv3XqBRoA5cZnMMsrUjbXecl0Nm', 'pro', 'activo', 'INVESTIGADOR'),
('a0000000-0000-0000-0000-000000000011', 'Roberto Díaz', 'roberto@zoom2.test', '$2b$12$zChrGI196GrAJwB54kuPbuaK5BYv3XqBRoA5cZnMMsrUjbXecl0Nm', 'basico', 'activo', 'USUARIO'),
('a0000000-0000-0000-0000-000000000012', 'Lucía Vargas', 'lucia@zoom2.test', '$2b$12$zChrGI196GrAJwB54kuPbuaK5BYv3XqBRoA5cZnMMsrUjbXecl0Nm', 'pro', 'activo', 'EVALUADOR');

-- 2. REUNIONES
INSERT INTO reuniones (id, creador_id, tema, fecha_inicio, duracion_minutos, proveedor, estado, tipo) VALUES
('b0000000-0000-0000-0000-000000000001', 'a0000000-0000-0000-0000-000000000001', 'Sprint Review — Módulo de Resúmenes IA', '2025-06-15 09:00:00-05', 60, 'zoom', 'completada', 'virtual'),
('b0000000-0000-0000-0000-000000000002', 'a0000000-0000-0000-0000-000000000002', 'Revisión de Resultados Experimentales — Prompt v1.0', '2025-06-18 14:00:00-05', 45, 'zoom', 'completada', 'virtual'),
('b0000000-0000-0000-0000-000000000003', 'a0000000-0000-0000-0000-000000000001', 'Daily Standup — Equipo de Desarrollo', '2025-06-20 08:30:00-05', 15, 'zoom', 'completada', 'virtual'),
('b0000000-0000-0000-0000-000000000004', 'a0000000-0000-0000-0000-000000000002', 'Análisis Estadístico — Comparación de Prompts v1.0 vs v1.1', '2025-06-22 10:00:00-05', 90, 'zoom', 'completada', 'virtual'),
('b0000000-0000-0000-0000-000000000005', 'a0000000-0000-0000-0000-000000000005', 'Workshop — Validación de Gold Standard', '2025-06-25 11:00:00-05', 75, 'zoom', 'completada', 'virtual'),
('b0000000-0000-0000-0000-000000000006', 'a0000000-0000-0000-0000-000000000006', 'Kickoff — Proyecto de Investigación Q3', '2025-07-01 09:00:00-05', 120, 'zoom', 'completada', 'virtual'),
('b0000000-0000-0000-0000-000000000007', 'a0000000-0000-0000-0000-000000000002', 'Revisión Semanal — Avances del Sprint 14', '2025-07-04 09:00:00-05', 30, 'zoom', 'completada', 'virtual'),
('b0000000-0000-0000-0000-000000000008', 'a0000000-0000-0000-0000-000000000001', 'Demo — Sistema de Evaluación Ciega', '2025-07-07 15:00:00-05', 45, 'zoom', 'completada', 'virtual'),
('b0000000-0000-0000-0000-000000000009', 'a0000000-0000-0000-0000-000000000010', 'Análisis de Resultados — Experimento SUS', '2025-07-10 10:00:00-05', 60, 'zoom', 'completada', 'virtual'),
('b0000000-0000-0000-0000-000000000010', 'a0000000-0000-0000-0000-000000000002', 'Retrospectiva — Sprint 14', '2025-07-11 16:00:00-05', 45, 'zoom', 'completada', 'virtual'),
('b0000000-0000-0000-0000-000000000011', 'a0000000-0000-0000-0000-000000000006', 'Revisión de Prompt v2.0 — Comparativo con v1.1', '2025-07-14 11:00:00-05', 90, 'zoom', 'completada', 'virtual'),
('b0000000-0000-0000-0000-000000000012', 'a0000000-0000-0000-0000-000000000001', 'Daily Standup — Equipo de Desarrollo', '2025-07-15 08:30:00-05', 15, 'zoom', 'completada', 'virtual'),
('b0000000-0000-0000-0000-000000000013', 'a0000000-0000-0000-0000-000000000002', 'Revisión Semanal — Avances del Sprint 15', '2025-07-18 09:00:00-05', 30, 'zoom', 'completada', 'virtual'),
('b0000000-0000-0000-0000-000000000014', 'a0000000-0000-0000-0000-000000000002', 'Análisis Estadístico — Comparación Prompt v2.0 vs v1.1', '2025-07-21 10:00:00-05', 90, 'zoom', 'programada', 'virtual'),
('b0000000-0000-0000-0000-000000000015', 'a0000000-0000-0000-0000-000000000001', 'Planning — Sprint 16', '2025-07-21 14:00:00-05', 60, 'zoom', 'programada', 'virtual'),
('b0000000-0000-0000-0000-000000000016', 'a0000000-0000-0000-0000-000000000006', 'Workshop — Metodología de Evaluación Ciega', '2025-07-25 10:00:00-05', 120, 'zoom', 'programada', 'virtual'),
('b0000000-0000-0000-0000-000000000017', 'a0000000-0000-0000-0000-000000000002', 'Revisión Semanal — Avances del Sprint 16', '2025-07-28 09:00:00-05', 30, 'zoom', 'programada', 'virtual'),
('b0000000-0000-0000-0000-000000000018', 'a0000000-0000-0000-0000-000000000001', 'Demo — Sistema de Reportes Automáticos', '2025-08-01 15:00:00-05', 45, 'zoom', 'programada', 'virtual'),
('b0000000-0000-0000-0000-000000000019', 'a0000000-0000-0000-0000-000000000006', 'Reunión de Cierre — Fase 1 del Proyecto', '2025-08-08 09:00:00-05', 180, 'zoom', 'programada', 'virtual'),
('b0000000-0000-0000-0000-000000000020', 'a0000000-0000-0000-0000-000000000006', 'Revisión de Métricas de Calidad — Q3 Intermedio', '2025-08-15 10:00:00-05', 60, 'zoom', 'programada', 'virtual');

-- 3. PARTICIPANTES
INSERT INTO participantes (reunion_id, usuario_id, correo, rol, estado_invitacion) VALUES
('b0000000-0000-0000-0000-000000000001', 'a0000000-0000-0000-0000-000000000001', 'anthonygv268@gmail.com', 'organizador', 'aceptado'),
('b0000000-0000-0000-0000-000000000001', 'a0000000-0000-0000-0000-000000000002', 'laura@zoom2.test', 'participante', 'aceptado'),
('b0000000-0000-0000-0000-000000000001', 'a0000000-0000-0000-0000-000000000003', 'carlos@zoom2.test', 'participante', 'aceptado'),
('b0000000-0000-0000-0000-000000000001', 'a0000000-0000-0000-0000-000000000004', 'maria@zoom2.test', 'participante', 'aceptado'),
('b0000000-0000-0000-0000-000000000001', 'a0000000-0000-0000-0000-000000000005', 'andres@zoom2.test', 'participante', 'aceptado'),
('b0000000-0000-0000-0000-000000000001', 'a0000000-0000-0000-0000-000000000006', 'sofia@zoom2.test', 'participante', 'aceptado'),
('b0000000-0000-0000-0000-000000000002', 'a0000000-0000-0000-0000-000000000002', 'laura@zoom2.test', 'organizador', 'aceptado'),
('b0000000-0000-0000-0000-000000000002', 'a0000000-0000-0000-0000-000000000001', 'anthonygv268@gmail.com', 'participante', 'aceptado'),
('b0000000-0000-0000-0000-000000000002', 'a0000000-0000-0000-0000-000000000005', 'andres@zoom2.test', 'participante', 'aceptado'),
('b0000000-0000-0000-0000-000000000002', 'a0000000-0000-0000-0000-000000000006', 'sofia@zoom2.test', 'participante', 'aceptado'),
('b0000000-0000-0000-0000-000000000002', 'a0000000-0000-0000-0000-000000000003', 'carlos@zoom2.test', 'participante', 'aceptado'),
('b0000000-0000-0000-0000-000000000003', 'a0000000-0000-0000-0000-000000000001', 'anthonygv268@gmail.com', 'organizador', 'aceptado'),
('b0000000-0000-0000-0000-000000000003', 'a0000000-0000-0000-0000-000000000002', 'laura@zoom2.test', 'participante', 'aceptado'),
('b0000000-0000-0000-0000-000000000003', 'a0000000-0000-0000-0000-000000000005', 'andres@zoom2.test', 'participante', 'aceptado'),
('b0000000-0000-0000-0000-000000000004', 'a0000000-0000-0000-0000-000000000002', 'laura@zoom2.test', 'organizador', 'aceptado'),
('b0000000-0000-0000-0000-000000000004', 'a0000000-0000-0000-0000-000000000005', 'andres@zoom2.test', 'participante', 'aceptado'),
('b0000000-0000-0000-0000-000000000004', 'a0000000-0000-0000-0000-000000000003', 'carlos@zoom2.test', 'participante', 'aceptado'),
('b0000000-0000-0000-0000-000000000004', 'a0000000-0000-0000-0000-000000000006', 'sofia@zoom2.test', 'participante', 'aceptado'),
('b0000000-0000-0000-0000-000000000005', 'a0000000-0000-0000-0000-000000000005', 'andres@zoom2.test', 'organizador', 'aceptado'),
('b0000000-0000-0000-0000-000000000005', 'a0000000-0000-0000-0000-000000000002', 'laura@zoom2.test', 'participante', 'aceptado'),
('b0000000-0000-0000-0000-000000000005', 'a0000000-0000-0000-0000-000000000003', 'carlos@zoom2.test', 'participante', 'aceptado'),
('b0000000-0000-0000-0000-000000000005', 'a0000000-0000-0000-0000-000000000007', 'pedro@zoom2.test', 'participante', 'aceptado'),
('b0000000-0000-0000-0000-000000000006', 'a0000000-0000-0000-0000-000000000006', 'sofia@zoom2.test', 'organizador', 'aceptado'),
('b0000000-0000-0000-0000-000000000006', 'a0000000-0000-0000-0000-000000000001', 'anthonygv268@gmail.com', 'participante', 'aceptado'),
('b0000000-0000-0000-0000-000000000006', 'a0000000-0000-0000-0000-000000000002', 'laura@zoom2.test', 'participante', 'aceptado'),
('b0000000-0000-0000-0000-000000000006', 'a0000000-0000-0000-0000-000000000005', 'andres@zoom2.test', 'participante', 'aceptado'),
('b0000000-0000-0000-0000-000000000006', 'a0000000-0000-0000-0000-000000000010', 'camila@zoom2.test', 'participante', 'aceptado'),
('b0000000-0000-0000-0000-000000000006', 'a0000000-0000-0000-0000-000000000008', 'ana@zoom2.test', 'participante', 'aceptado'),
('b0000000-0000-0000-0000-000000000007', 'a0000000-0000-0000-0000-000000000002', 'laura@zoom2.test', 'organizador', 'aceptado'),
('b0000000-0000-0000-0000-000000000007', 'a0000000-0000-0000-0000-000000000005', 'andres@zoom2.test', 'participante', 'aceptado'),
('b0000000-0000-0000-0000-000000000007', 'a0000000-0000-0000-0000-000000000010', 'camila@zoom2.test', 'participante', 'aceptado'),
('b0000000-0000-0000-0000-000000000008', 'a0000000-0000-0000-0000-000000000001', 'anthonygv268@gmail.com', 'organizador', 'aceptado'),
('b0000000-0000-0000-0000-000000000008', 'a0000000-0000-0000-0000-000000000002', 'laura@zoom2.test', 'participante', 'aceptado'),
('b0000000-0000-0000-0000-000000000008', 'a0000000-0000-0000-0000-000000000003', 'carlos@zoom2.test', 'participante', 'aceptado'),
('b0000000-0000-0000-0000-000000000008', 'a0000000-0000-0000-0000-000000000007', 'pedro@zoom2.test', 'participante', 'aceptado'),
('b0000000-0000-0000-0000-000000000008', 'a0000000-0000-0000-0000-000000000012', 'lucia@zoom2.test', 'participante', 'aceptado'),
('b0000000-0000-0000-0000-000000000009', 'a0000000-0000-0000-0000-000000000010', 'camila@zoom2.test', 'organizador', 'aceptado'),
('b0000000-0000-0000-0000-000000000009', 'a0000000-0000-0000-0000-000000000002', 'laura@zoom2.test', 'participante', 'aceptado'),
('b0000000-0000-0000-0000-000000000009', 'a0000000-0000-0000-0000-000000000005', 'andres@zoom2.test', 'participante', 'aceptado'),
('b0000000-0000-0000-0000-000000000010', 'a0000000-0000-0000-0000-000000000002', 'laura@zoom2.test', 'organizador', 'aceptado'),
('b0000000-0000-0000-0000-000000000010', 'a0000000-0000-0000-0000-000000000003', 'carlos@zoom2.test', 'participante', 'aceptado'),
('b0000000-0000-0000-0000-000000000010', 'a0000000-0000-0000-0000-000000000007', 'pedro@zoom2.test', 'participante', 'aceptado'),
('b0000000-0000-0000-0000-000000000010', 'a0000000-0000-0000-0000-000000000004', 'maria@zoom2.test', 'participante', 'aceptado'),
('b0000000-0000-0000-0000-000000000011', 'a0000000-0000-0000-0000-000000000006', 'sofia@zoom2.test', 'organizador', 'aceptado'),
('b0000000-0000-0000-0000-000000000011', 'a0000000-0000-0000-0000-000000000002', 'laura@zoom2.test', 'participante', 'aceptado'),
('b0000000-0000-0000-0000-000000000011', 'a0000000-0000-0000-0000-000000000005', 'andres@zoom2.test', 'participante', 'aceptado'),
('b0000000-0000-0000-0000-000000000011', 'a0000000-0000-0000-0000-000000000003', 'carlos@zoom2.test', 'participante', 'aceptado'),
('b0000000-0000-0000-0000-000000000012', 'a0000000-0000-0000-0000-000000000001', 'anthonygv268@gmail.com', 'organizador', 'aceptado'),
('b0000000-0000-0000-0000-000000000012', 'a0000000-0000-0000-0000-000000000002', 'laura@zoom2.test', 'participante', 'aceptado'),
('b0000000-0000-0000-0000-000000000012', 'a0000000-0000-0000-0000-000000000005', 'andres@zoom2.test', 'participante', 'aceptado'),
('b0000000-0000-0000-0000-000000000013', 'a0000000-0000-0000-0000-000000000002', 'laura@zoom2.test', 'organizador', 'aceptado'),
('b0000000-0000-0000-0000-000000000013', 'a0000000-0000-0000-0000-000000000005', 'andres@zoom2.test', 'participante', 'aceptado'),
('b0000000-0000-0000-0000-000000000013', 'a0000000-0000-0000-0000-000000000010', 'camila@zoom2.test', 'participante', 'aceptado'),
('b0000000-0000-0000-0000-000000000014', 'a0000000-0000-0000-0000-000000000002', 'laura@zoom2.test', 'organizador', 'aceptado'),
('b0000000-0000-0000-0000-000000000014', 'a0000000-0000-0000-0000-000000000006', 'sofia@zoom2.test', 'participante', 'aceptado'),
('b0000000-0000-0000-0000-000000000014', 'a0000000-0000-0000-0000-000000000005', 'andres@zoom2.test', 'participante', 'aceptado'),
('b0000000-0000-0000-0000-000000000014', 'a0000000-0000-0000-0000-000000000010', 'camila@zoom2.test', 'participante', 'aceptado'),
('b0000000-0000-0000-0000-000000000015', 'a0000000-0000-0000-0000-000000000001', 'anthonygv268@gmail.com', 'organizador', 'enviado'),
('b0000000-0000-0000-0000-000000000015', 'a0000000-0000-0000-0000-000000000002', 'laura@zoom2.test', 'participante', 'enviado'),
('b0000000-0000-0000-0000-000000000015', 'a0000000-0000-0000-0000-000000000005', 'andres@zoom2.test', 'participante', 'enviado'),
('b0000000-0000-0000-0000-000000000015', 'a0000000-0000-0000-0000-000000000010', 'camila@zoom2.test', 'participante', 'enviado'),
('b0000000-0000-0000-0000-000000000016', 'a0000000-0000-0000-0000-000000000006', 'sofia@zoom2.test', 'organizador', 'enviado'),
('b0000000-0000-0000-0000-000000000016', 'a0000000-0000-0000-0000-000000000002', 'laura@zoom2.test', 'participante', 'enviado'),
('b0000000-0000-0000-0000-000000000016', 'a0000000-0000-0000-0000-000000000005', 'andres@zoom2.test', 'participante', 'enviado'),
('b0000000-0000-0000-0000-000000000016', 'a0000000-0000-0000-0000-000000000003', 'carlos@zoom2.test', 'participante', 'enviado'),
('b0000000-0000-0000-0000-000000000016', 'a0000000-0000-0000-0000-000000000007', 'pedro@zoom2.test', 'participante', 'enviado'),
('b0000000-0000-0000-0000-000000000017', 'a0000000-0000-0000-0000-000000000002', 'laura@zoom2.test', 'organizador', 'enviado'),
('b0000000-0000-0000-0000-000000000017', 'a0000000-0000-0000-0000-000000000005', 'andres@zoom2.test', 'participante', 'enviado'),
('b0000000-0000-0000-0000-000000000017', 'a0000000-0000-0000-0000-000000000010', 'camila@zoom2.test', 'participante', 'enviado'),
('b0000000-0000-0000-0000-000000000018', 'a0000000-0000-0000-0000-000000000001', 'anthonygv268@gmail.com', 'organizador', 'enviado'),
('b0000000-0000-0000-0000-000000000018', 'a0000000-0000-0000-0000-000000000002', 'laura@zoom2.test', 'participante', 'enviado'),
('b0000000-0000-0000-0000-000000000018', 'a0000000-0000-0000-0000-000000000003', 'carlos@zoom2.test', 'participante', 'enviado'),
('b0000000-0000-0000-0000-000000000018', 'a0000000-0000-0000-0000-000000000007', 'pedro@zoom2.test', 'participante', 'enviado'),
('b0000000-0000-0000-0000-000000000019', 'a0000000-0000-0000-0000-000000000006', 'sofia@zoom2.test', 'organizador', 'enviado'),
('b0000000-0000-0000-0000-000000000019', 'a0000000-0000-0000-0000-000000000002', 'laura@zoom2.test', 'participante', 'enviado'),
('b0000000-0000-0000-0000-000000000019', 'a0000000-0000-0000-0000-000000000005', 'andres@zoom2.test', 'participante', 'enviado'),
('b0000000-0000-0000-0000-000000000019', 'a0000000-0000-0000-0000-000000000010', 'camila@zoom2.test', 'participante', 'enviado'),
('b0000000-0000-0000-0000-000000000019', 'a0000000-0000-0000-0000-000000000001', 'anthonygv268@gmail.com', 'participante', 'enviado'),
('b0000000-0000-0000-0000-000000000019', 'a0000000-0000-0000-0000-000000000008', 'ana@zoom2.test', 'participante', 'enviado'),
('b0000000-0000-0000-0000-000000000020', 'a0000000-0000-0000-0000-000000000001', 'anthonygv268@gmail.com', 'organizador', 'enviado'),
('b0000000-0000-0000-0000-000000000020', 'a0000000-0000-0000-0000-000000000002', 'laura@zoom2.test', 'participante', 'enviado'),
('b0000000-0000-0000-0000-000000000020', 'a0000000-0000-0000-0000-000000000005', 'andres@zoom2.test', 'participante', 'enviado'),
('b0000000-0000-0000-0000-000000000020', 'a0000000-0000-0000-0000-000000000006', 'sofia@zoom2.test', 'participante', 'enviado'),
('b0000000-0000-0000-0000-000000000020', 'a0000000-0000-0000-0000-000000000010', 'camila@zoom2.test', 'participante', 'enviado');

-- 4. TAREAS
INSERT INTO tareas (id, reunion_id, descripcion, asignado_a_correo, estado, fecha_vencimiento) VALUES
('c0000000-0000-0000-0000-000000000001', 'b0000000-0000-0000-0000-000000000001', 'Documentar hallazgos del experimento', 'anthonygv268@gmail.com', 'completada', '2025-06-15 00:00:00-05'),
('c0000000-0000-0000-0000-000000000002', 'b0000000-0000-0000-0000-000000000001', 'Generar reporte PDF con resultados', 'carlos@zoom2.test', 'completada', '2025-06-27 00:00:00-05'),
('c0000000-0000-0000-0000-000000000003', 'b0000000-0000-0000-0000-000000000001', 'Estimar story points para tareas', 'diego@zoom2.test', 'completada', '2025-07-07 00:00:00-05'),
('c0000000-0000-0000-0000-000000000004', 'b0000000-0000-0000-0000-000000000002', 'Revisar métricas de calidad de resúmenes IA', 'anthonygv268@gmail.com', 'completada', '2025-06-18 00:00:00-05'),
('c0000000-0000-0000-0000-000000000005', 'b0000000-0000-0000-0000-000000000002', 'Generar reporte PDF con resultados', 'diego@zoom2.test', 'completada', '2025-06-28 00:00:00-05'),
('c0000000-0000-0000-0000-000000000006', 'b0000000-0000-0000-0000-000000000003', 'Preparar datos para análisis estadístico', 'roberto@zoom2.test', 'pendiente', '2025-06-21 00:00:00-05'),
('c0000000-0000-0000-0000-000000000007', 'b0000000-0000-0000-0000-000000000004', 'Recopilar feedback de evaluadores', 'camila@zoom2.test', 'completada', '2025-06-24 00:00:00-05'),
('c0000000-0000-0000-0000-000000000008', 'b0000000-0000-0000-0000-000000000005', 'Preparar material para workshop', 'carlos@zoom2.test', 'completada', '2025-06-27 00:00:00-05'),
('c0000000-0000-0000-0000-000000000009', 'b0000000-0000-0000-0000-000000000006', 'Configurar entorno de staging', 'maria@zoom2.test', 'completada', '2025-06-30 00:00:00-05'),
('c0000000-0000-0000-0000-000000000010', 'b0000000-0000-0000-0000-000000000006', 'Preparar presentación para stakeholders', 'pedro@zoom2.test', 'completada', '2025-07-07 00:00:00-05'),
('c0000000-0000-0000-0000-000000000011', 'b0000000-0000-0000-0000-000000000007', 'Actualizar prompt con feedback', 'andres@zoom2.test', 'completada', '2025-07-03 00:00:00-05'),
('c0000000-0000-0000-0000-000000000012', 'b0000000-0000-0000-0000-000000000007', 'Recopilar feedback de evaluadores', 'diego@zoom2.test', 'completada', '2025-07-19 00:00:00-05'),
('c0000000-0000-0000-0000-000000000013', 'b0000000-0000-0000-0000-000000000008', 'Preparar presentación para stakeholders', 'diego@zoom2.test', 'completada', '2025-07-06 00:00:00-05'),
('c0000000-0000-0000-0000-000000000014', 'b0000000-0000-0000-0000-000000000008', 'Cerrar sprint y preparar retrospectiva', 'camila@zoom2.test', 'completada', '2025-07-17 00:00:00-05'),
('c0000000-0000-0000-0000-000000000015', 'b0000000-0000-0000-0000-000000000009', 'Preparar datos para análisis estadístico', 'laura@zoom2.test', 'completada', '2025-07-09 00:00:00-05'),
('c0000000-0000-0000-0000-000000000016', 'b0000000-0000-0000-0000-000000000010', 'Preparar material para workshop', 'andres@zoom2.test', 'completada', '2025-07-12 00:00:00-05'),
('c0000000-0000-0000-0000-000000000017', 'b0000000-0000-0000-0000-000000000011', 'Documentar hallazgos del experimento', 'pedro@zoom2.test', 'completada', '2025-07-15 00:00:00-05'),
('c0000000-0000-0000-0000-000000000018', 'b0000000-0000-0000-0000-000000000012', 'Asignar roles del equipo', 'carlos@zoom2.test', 'completada', '2025-07-18 00:00:00-05'),
('c0000000-0000-0000-0000-000000000019', 'b0000000-0000-0000-0000-000000000012', 'Ejecutar análisis estadístico', 'roberto@zoom2.test', 'completada', '2025-07-31 00:00:00-05'),
('c0000000-0000-0000-0000-000000000020', 'b0000000-0000-0000-0000-000000000012', 'Actualizar backlog para sprint 16', 'roberto@zoom2.test', 'completada', '2025-08-09 00:00:00-05'),
('c0000000-0000-0000-0000-000000000021', 'b0000000-0000-0000-0000-000000000013', 'Actualizar backlog con tareas del standup', 'diego@zoom2.test', 'completada', '2025-07-21 00:00:00-05'),
('c0000000-0000-0000-0000-000000000022', 'b0000000-0000-0000-0000-000000000013', 'Recopilar feedback de evaluadores', 'pedro@zoom2.test', 'completada', '2025-08-06 00:00:00-05'),
('c0000000-0000-0000-0000-000000000023', 'b0000000-0000-0000-0000-000000000013', 'Cerrar sprint y preparar retrospectiva', 'lucia@zoom2.test', 'pendiente', '2025-07-31 00:00:00-05'),
('c0000000-0000-0000-0000-000000000024', 'b0000000-0000-0000-0000-000000000014', 'Definir objetivos de investigación Q3', 'anthonygv268@gmail.com', 'completada', '2025-07-24 00:00:00-05'),
('c0000000-0000-0000-0000-000000000025', 'b0000000-0000-0000-0000-000000000014', 'Revisar métricas de calidad de resúmenes IA', 'sofia@zoom2.test', 'completada', '2025-07-30 00:00:00-05'),
('c0000000-0000-0000-0000-000000000026', 'b0000000-0000-0000-0000-000000000014', 'Preparar presentación para stakeholders', 'maria@zoom2.test', 'completada', '2025-08-03 00:00:00-05');

-- 5. RESÚMENES
INSERT INTO resumenes (reunion_id, resumen) VALUES
('b0000000-0000-0000-0000-000000000001', 'Sprint review exitosa. 8 de 10 historias completadas. Bug detectado en timeouts para reuniones > 60min.'),
('b0000000-0000-0000-0000-000000000002', 'Revisión de resultados experimentales. Fidelidad promedio v1.0: 3.8/5. Omisiones en acuerdos secundarios.'),
('b0000000-0000-0000-0000-000000000003', 'Standup rápido. Andrés completó integración con API de Zoom. Pendiente: configurar staging.'),
('b0000000-0000-0000-0000-000000000004', 'Análisis estadístico completado. v1.1 muestra mejora significativa en claridad (p < 0.05).'),
('b0000000-0000-0000-0000-000000000005', 'Workshop gold standard. 15 tareas de referencia definidas. 12 validadas, 3 pendientes.'),
('b0000000-0000-0000-0000-000000000006', 'Kickoff Q3. 3 objetivos: precisión >90%, tiempo <30s, evaluación ciega con 5+ evaluadores.'),
('b0000000-0000-0000-0000-000000000007', 'Revisión sprint 14. 7/10 tareas completadas. Velocity mejoró 12%.'),
('b0000000-0000-0000-0000-000000000008', 'Demo evaluación ciega. Feedback positivo. Sugerencia: botón para saltar preguntas.'),
('b0000000-0000-0000-0000-000000000009', 'Análisis SUS: score 78.5/100 (Bueno). Peor aspecto: tiempo de carga (2.8/5).'),
('b0000000-0000-0000-0000-000000000010', 'Retrospectiva sprint 14. Mejoras: tests E2E, documentación APIs, code review obligatorio.'),
('b0000000-0000-0000-0000-000000000011', 'Revisión prompt v2.0. Estructura C-suite mejorada. Decisión: lanzar v2.0 como estándar.'),
('b0000000-0000-0000-0000-000000000012', 'Daily standup. Pendientes: cerrar sprint 15, preparar planning sprint 16.'),
('b0000000-0000-0000-0000-000000000013', 'Revisión sprint 15. 9/12 tareas completadas. Velocity mejoró 15% vs sprint 14.'),
('b0000000-0000-0000-0000-000000000014', 'Resumen de la reunión de planificación del próximo sprint con objetivos definidos.');

-- 6. RESÚMENES DETALLE
INSERT INTO resumenes_detalle (reunion_id, resumen_ejecutivo, decisiones, riesgos, proximos_pasos) VALUES
('b0000000-0000-0000-0000-000000000001', 'Sprint review 80% completado. Bug en timeouts detectado.', '1) Fix timeout prioritario. 2) Mantener ritmo.', 'Retraso en release si no se resuelve.', 'Laura investiga (miércoles). Andrés hotfix.'),
('b0000000-0000-0000-0000-000000000004', 'Comparación v1.0 vs v1.1. Mejora significativa en claridad.', '1) Adoptar v1.1 como estándar. 2) Archivar v1.0.', 'Overfitting a datos de entrenamiento.', 'Segunda ronda de validación. Documentar cambios.'),
('b0000000-0000-0000-0000-000000000006', 'Kickoff Q3 con objetivos ambiciosos pero alcanzables.', '1) Precisión >90%. 2) Tiempo <30s. 3) Evaluación ciega.', 'Sobrecarga del equipo.', 'Dividir en fases. Milestones semanales.'),
('b0000000-0000-0000-0000-000000000009', 'Demo exitosa. Feedback muy positivo.', '1) Skip button. 2) Métricas tiempo/pregunta.', 'Baja adopción si interfaz no es intuitiva.', 'Implementar skip button. Tutorial interactivo.'),
('b0000000-0000-0000-0000-000000000010', 'SUS: 78.5/100. Tiempo de carga es principal dolor.', '1) Optimizar queries Supabase. 2) Caché Redis.', 'SUS bajar sin optimizaciones.', 'Optimizar queries. Caché Redis. Re-evaluar SUS.'),
('b0000000-0000-0000-0000-000000000011', 'Retrospectiva productiva. 3 áreas de mejora.', '1) Tests E2E. 2) Documentar APIs. 3) Code review.', 'Perder velocidad si se implementa todo.', 'Tests este sprint. Documentación incremental.'),
('b0000000-0000-0000-0000-000000000012', 'Prompt v2.0 revisado. Estructura C-suite mejorada.', '1) Lanzar v2.0 estándar ejecutivo. 2) Mantener v1.1.', 'Confusión de usuarios.', 'Guía de migración. Newsletter. Monitorear uso.'),
('b0000000-0000-0000-0000-000000000013', 'Velocity mejoró 15%. Sprint productivo.', '1) Mantener ritmo. 2) Meta velocity sprint 16.', 'Burnout si no hay pausas.', 'Daily más cortos. Retrospectiva intermedia.');

-- 7. PROMPT VERSIONS
INSERT INTO prompt_versions (id, nombre, version, contenido, objetivo, proveedor, modelo_recomendado, activo, creado_por) VALUES
('d0000000-0000-0000-0000-000000000001', 'resumen_reunion', '1.0', 'Eres un asistente experto en reuniones corporativas. Genera un resumen ejecutivo de la siguiente reunión. Incluye: tema principal, participantes, acuerdos tomados, tareas asignadas y próximos pasos.', 'Generar resúmenes precisos de reuniones.', 'openai', 'gpt-4', false, 'a0000000-0000-0000-0000-000000000002'),
('d0000000-0000-0000-0000-000000000002', 'resumen_reunion', '1.1', 'Eres un asistente experto en reuniones corporativas. Genera un resumen ejecutivo con: tema principal, participantes roles, acuerdos por categoría, tareas con responsable y fecha, riesgos y próximos pasos con prioridad.', 'Resúmenes detallados con clasificación y priorización.', 'openai', 'gpt-4', false, 'a0000000-0000-0000-0000-000000000002'),
('d0000000-0000-0000-0000-000000000003', 'extraccion_tareas', '1.0', 'Analiza la transcripción y extrae todas las tareas mencionadas: descripción, responsable, fecha límite y prioridad.', 'Extraer tareas accionables de reuniones.', 'openai', 'gpt-4', false, 'a0000000-0000-0000-0000-000000000005'),
('d0000000-0000-0000-0000-000000000004', 'clasificacion_sentimientos', '1.0', 'Clasifica el sentimiento de cada participante como positivo, neutro o negativo con evidencia textual.', 'Evaluar clima de reuniones.', 'anthropic', 'claude-3-sonnet', false, 'a0000000-0000-0000-0000-000000000002'),
('d0000000-0000-0000-0000-000000000005', 'resumen_reunion', '2.0', 'Analista senior con 10 años de experiencia. Resumen ejecutivo: (1) Resumen 3-5 oraciones, (2) Decisiones con impacto, (3) Tareas en tabla, (4) Riesgos, (5) Próximos pasos con owner y deadline.', 'Resúmenes nivel C-suite.', 'openai', 'gpt-4-turbo', true, 'a0000000-0000-0000-0000-000000000002'),
('d0000000-0000-0000-0000-000000000006', 'extraccion_tareas', '2.0', 'Experto en gestión de proyectos. Extrae tareas: descripción accionable, responsable, fecha límite, prioridad [Alta/Media/Baja], dependencias.', 'Extracción mejorada con dependencias.', 'openai', 'gpt-4-turbo', true, 'a0000000-0000-0000-0000-000000000005'),
('d0000000-0000-0000-0000-000000000007', 'resumen_reunion', '3.0', 'Consultor McKinsey. Formato SCQA: (1) Situation, (2) Complication, (3) Key Questions, (4) Answer & Recommendation, (5) Next Steps en tabla.', 'Resúmenes estilo consultora de élite.', 'openai', 'gpt-4-turbo', false, 'a0000000-0000-0000-0000-000000000002');

-- 8. AI EXECUTIONS
INSERT INTO ai_executions (id, reunion_id, prompt_version_id, proveedor, modelo, temperatura, tokens_entrada, tokens_salida, costo_estimado, tiempo_ms, estado, iniciado_por) VALUES
('e0000000-0000-0000-0000-000000000001', 'b0000000-0000-0000-0000-000000000001', 'd0000000-0000-0000-0000-000000000001', 'openai', 'gpt-4', 0.3, 3084, 661, 0.0507, 2820, 'completado', 'a0000000-0000-0000-0000-000000000001'),
('e0000000-0000-0000-0000-000000000002', 'b0000000-0000-0000-0000-000000000002', 'd0000000-0000-0000-0000-000000000002', 'openai', 'gpt-4', 0.3, 3033, 619, 0.0489, 1785, 'completado', 'a0000000-0000-0000-0000-000000000002'),
('e0000000-0000-0000-0000-000000000003', 'b0000000-0000-0000-0000-000000000003', 'd0000000-0000-0000-0000-000000000003', 'openai', 'gpt-4', 0.3, 1484, 292, 0.0236, 2210, 'completado', 'a0000000-0000-0000-0000-000000000001'),
('e0000000-0000-0000-0000-000000000004', 'b0000000-0000-0000-0000-000000000004', 'd0000000-0000-0000-0000-000000000004', 'openai', 'gpt-4', 0.3, 2699, 701, 0.048, 2276, 'completado', 'a0000000-0000-0000-0000-000000000002'),
('e0000000-0000-0000-0000-000000000005', 'b0000000-0000-0000-0000-000000000005', 'd0000000-0000-0000-0000-000000000005', 'openai', 'gpt-4', 0.3, 2794, 588, 0.0456, 4877, 'completado', 'a0000000-0000-0000-0000-000000000005'),
('e0000000-0000-0000-0000-000000000006', 'b0000000-0000-0000-0000-000000000006', 'd0000000-0000-0000-0000-000000000006', 'openai', 'gpt-4-turbo', 0.3, 2790, 558, 0.0446, 2682, 'completado', 'a0000000-0000-0000-0000-000000000006'),
('e0000000-0000-0000-0000-000000000007', 'b0000000-0000-0000-0000-000000000007', 'd0000000-0000-0000-0000-000000000007', 'openai', 'gpt-4', 0.3, 1298, 291, 0.0217, 3287, 'completado', 'a0000000-0000-0000-0000-000000000002'),
('e0000000-0000-0000-0000-000000000008', 'b0000000-0000-0000-0000-000000000008', 'd0000000-0000-0000-0000-000000000007', 'openai', 'gpt-4-turbo', 0.3, 2421, 243, 0.0315, 4295, 'completado', 'a0000000-0000-0000-0000-000000000001'),
('e0000000-0000-0000-0000-000000000009', 'b0000000-0000-0000-0000-000000000009', 'd0000000-0000-0000-0000-000000000007', 'openai', 'gpt-4', 0.3, 592, 262, 0.0138, 1826, 'completado', 'a0000000-0000-0000-0000-000000000010'),
('e0000000-0000-0000-0000-000000000010', 'b0000000-0000-0000-0000-000000000010', 'd0000000-0000-0000-0000-000000000007', 'openai', 'gpt-4-turbo', 0.3, 2970, 313, 0.0391, 4444, 'completado', 'a0000000-0000-0000-0000-000000000002'),
('e0000000-0000-0000-0000-000000000011', 'b0000000-0000-0000-0000-000000000011', 'd0000000-0000-0000-0000-000000000007', 'openai', 'gpt-4', 0.3, 3187, 582, 0.0493, 3642, 'completado', 'a0000000-0000-0000-0000-000000000006'),
('e0000000-0000-0000-0000-000000000012', 'b0000000-0000-0000-0000-000000000012', 'd0000000-0000-0000-0000-000000000007', 'openai', 'gpt-4', 0.3, 660, 544, 0.0229, 2763, 'completado', 'a0000000-0000-0000-0000-000000000001'),
('e0000000-0000-0000-0000-000000000013', 'b0000000-0000-0000-0000-000000000013', 'd0000000-0000-0000-0000-000000000007', 'openai', 'gpt-4', 0.3, 2840, 629, 0.0473, 3367, 'completado', 'a0000000-0000-0000-0000-000000000002'),
('e0000000-0000-0000-0000-000000000014', 'b0000000-0000-0000-0000-000000000014', 'd0000000-0000-0000-0000-000000000007', 'openai', 'gpt-4-turbo', 0.3, 1429, 716, 0.0358, 4725, 'completado', 'a0000000-0000-0000-0000-000000000002');

-- 9. SUMMARY VERSIONS
INSERT INTO summary_versions (reunion_id, ai_execution_id, version, origen, contenido, estado, es_version_actual, creado_por) VALUES
('b0000000-0000-0000-0000-000000000001', 'e0000000-0000-0000-0000-000000000001', 1, 'IA', 'Sprint Review — Módulo de Resúmenes IA. Acuerdos: priorizar fix timeout, mantener ritmo. Tareas: Laura investiga timeout, Andrés hotfix.', 'APROBADO', true, 'a0000000-0000-0000-0000-000000000001'),
('b0000000-0000-0000-0000-000000000002', 'e0000000-0000-0000-0000-000000000002', 1, 'IA', 'Revisión Resultados Experimentales. v1.0 fidelidad 3.8/5. Omisiones en acuerdos secundarios. Avanzar con v1.1.', 'APROBADO', true, 'a0000000-0000-0000-0000-000000000002'),
('b0000000-0000-0000-0000-000000000003', 'e0000000-0000-0000-0000-000000000003', 1, 'IA', 'Análisis Estadístico. Prueba t de Welch: v1.1 mejora significativa en claridad (p<0.05). Adoptar v1.1.', 'APROBADO', true, 'a0000000-0000-0000-0000-000000000002'),
('b0000000-0000-0000-0000-000000000004', 'e0000000-0000-0000-0000-000000000004', 1, 'IA', 'Kickoff Q3. Objetivos: precisión >90%, tiempo <30s, evaluación ciega 5+ evaluadores.', 'APROBADO', true, 'a0000000-0000-0000-0000-000000000006'),
('b0000000-0000-0000-0000-000000000005', 'e0000000-0000-0000-0000-000000000005', 1, 'IA', 'Revisión sprint 14. 7/10 tareas. Velocity mejoró 12%.', 'APROBADO', true, 'a0000000-0000-0000-0000-000000000002'),
('b0000000-0000-0000-0000-000000000006', 'e0000000-0000-0000-0000-000000000006', 1, 'IA', 'Demo evaluación ciega. Feedback positivo. Skip button sugerido.', 'APROBADO', true, 'a0000000-0000-0000-0000-000000000001'),
('b0000000-0000-0000-0000-000000000007', 'e0000000-0000-0000-0000-000000000007', 1, 'IA', 'SUS score 78.5/100. Tiempo de carga: 2.8/5. Optimizar queries.', 'APROBADO', true, 'a0000000-0000-0000-0000-000000000010'),
('b0000000-0000-0000-0000-000000000008', 'e0000000-0000-0000-0000-000000000008', 1, 'IA', 'Retrospectiva sprint 14. Tests E2E, documentación APIs, code review.', 'APROBADO', true, 'a0000000-0000-0000-0000-000000000002'),
('b0000000-0000-0000-0000-000000000009', 'e0000000-0000-0000-0000-000000000009', 1, 'IA', 'Prompt v2.0. Estructura C-suite. Lanzar como estándar ejecutivo.', 'APROBADO', true, 'a0000000-0000-0000-0000-000000000006'),
('b0000000-0000-0000-0000-000000000010', 'e0000000-0000-0000-0000-000000000010', 1, 'IA', 'Revisión sprint 15. 9/12 tareas. Velocity +15%.', 'PENDIENTE_REVISION', true, 'a0000000-0000-0000-0000-000000000002');

-- 10. SUMMARY EVALUATIONS
INSERT INTO summary_evaluations (reunion_id, summary_version_id, evaluador_id, fidelidad, cobertura, claridad, coherencia, concision, utilidad, acuerdos_correctos, responsables_correctos, fechas_correctas, omisiones, afirmaciones_no_respaldadas, contradicciones, aprobado_sin_cambios, observaciones) VALUES
('b0000000-0000-0000-0000-000000000001', (SELECT id FROM summary_versions WHERE reunion_id = 'b0000000-0000-0000-0000-000000000001' AND version = 1), 'a0000000-0000-0000-0000-000000000003', 4,4,5,4,4,5, 4,3,3, 1,0,0, false, 'Buen resumen pero faltó mencionar acuerdos secundarios.'),
('b0000000-0000-0000-0000-000000000001', (SELECT id FROM summary_versions WHERE reunion_id = 'b0000000-0000-0000-0000-000000000001' AND version = 1), 'a0000000-0000-0000-0000-000000000002', 5,4,4,5,4,4, 4,4,3, 0,1,0, false, 'Preciso en acuerdos principales. Omisión menor.'),
('b0000000-0000-0000-0000-000000000001', (SELECT id FROM summary_versions WHERE reunion_id = 'b0000000-0000-0000-0000-000000000001' AND version = 1), 'a0000000-0000-0000-0000-000000000007', 3,4,4,4,3,4, 3,3,3, 2,1,1, false, 'Mejorable en claridad de tareas asignadas.'),
('b0000000-0000-0000-0000-000000000002', (SELECT id FROM summary_versions WHERE reunion_id = 'b0000000-0000-0000-0000-000000000002' AND version = 1), 'a0000000-0000-0000-0000-000000000003', 4,4,5,4,4,5, 4,3,3, 1,0,0, false, 'Buen resumen pero faltó mencionar acuerdos secundarios.'),
('b0000000-0000-0000-0000-000000000002', (SELECT id FROM summary_versions WHERE reunion_id = 'b0000000-0000-0000-0000-000000000002' AND version = 1), 'a0000000-0000-0000-0000-000000000002', 5,4,4,5,4,4, 4,4,3, 0,1,0, false, 'Preciso en acuerdos principales. Omisión menor.'),
('b0000000-0000-0000-0000-000000000002', (SELECT id FROM summary_versions WHERE reunion_id = 'b0000000-0000-0000-0000-000000000002' AND version = 1), 'a0000000-0000-0000-0000-000000000007', 3,4,4,4,3,4, 3,3,3, 2,1,1, false, 'Mejorable en claridad de tareas asignadas.'),
('b0000000-0000-0000-0000-000000000003', (SELECT id FROM summary_versions WHERE reunion_id = 'b0000000-0000-0000-0000-000000000003' AND version = 1), 'a0000000-0000-0000-0000-000000000003', 4,4,5,4,4,5, 4,3,3, 1,0,0, false, 'Buen resumen pero faltó mencionar acuerdos secundarios.'),
('b0000000-0000-0000-0000-000000000003', (SELECT id FROM summary_versions WHERE reunion_id = 'b0000000-0000-0000-0000-000000000003' AND version = 1), 'a0000000-0000-0000-0000-000000000002', 5,4,4,5,4,4, 4,4,3, 0,1,0, false, 'Preciso en acuerdos principales. Omisión menor.'),
('b0000000-0000-0000-0000-000000000003', (SELECT id FROM summary_versions WHERE reunion_id = 'b0000000-0000-0000-0000-000000000003' AND version = 1), 'a0000000-0000-0000-0000-000000000007', 3,4,4,4,3,4, 3,3,3, 2,1,1, false, 'Mejorable en claridad de tareas asignadas.'),
('b0000000-0000-0000-0000-000000000004', (SELECT id FROM summary_versions WHERE reunion_id = 'b0000000-0000-0000-0000-000000000004' AND version = 1), 'a0000000-0000-0000-0000-000000000003', 4,4,5,4,4,5, 4,3,3, 1,0,0, false, 'Buen resumen pero faltó mencionar acuerdos secundarios.'),
('b0000000-0000-0000-0000-000000000004', (SELECT id FROM summary_versions WHERE reunion_id = 'b0000000-0000-0000-0000-000000000004' AND version = 1), 'a0000000-0000-0000-0000-000000000002', 5,4,4,5,4,4, 4,4,3, 0,1,0, false, 'Preciso en acuerdos principales. Omisión menor.'),
('b0000000-0000-0000-0000-000000000004', (SELECT id FROM summary_versions WHERE reunion_id = 'b0000000-0000-0000-0000-000000000004' AND version = 1), 'a0000000-0000-0000-0000-000000000007', 3,4,4,4,3,4, 3,3,3, 2,1,1, false, 'Mejorable en claridad de tareas asignadas.'),
('b0000000-0000-0000-0000-000000000005', (SELECT id FROM summary_versions WHERE reunion_id = 'b0000000-0000-0000-0000-000000000005' AND version = 1), 'a0000000-0000-0000-0000-000000000003', 4,4,5,4,4,5, 4,3,3, 1,0,0, false, 'Buen resumen pero faltó mencionar acuerdos secundarios.'),
('b0000000-0000-0000-0000-000000000005', (SELECT id FROM summary_versions WHERE reunion_id = 'b0000000-0000-0000-0000-000000000005' AND version = 1), 'a0000000-0000-0000-0000-000000000002', 5,4,4,5,4,4, 4,4,3, 0,1,0, false, 'Preciso en acuerdos principales. Omisión menor.'),
('b0000000-0000-0000-0000-000000000005', (SELECT id FROM summary_versions WHERE reunion_id = 'b0000000-0000-0000-0000-000000000005' AND version = 1), 'a0000000-0000-0000-0000-000000000007', 3,4,4,4,3,4, 3,3,3, 2,1,1, false, 'Mejorable en claridad de tareas asignadas.'),
('b0000000-0000-0000-0000-000000000006', (SELECT id FROM summary_versions WHERE reunion_id = 'b0000000-0000-0000-0000-000000000006' AND version = 1), 'a0000000-0000-0000-0000-000000000003', 4,4,5,4,4,5, 4,3,3, 1,0,0, false, 'Buen resumen pero faltó mencionar acuerdos secundarios.'),
('b0000000-0000-0000-0000-000000000006', (SELECT id FROM summary_versions WHERE reunion_id = 'b0000000-0000-0000-0000-000000000006' AND version = 1), 'a0000000-0000-0000-0000-000000000002', 5,4,4,5,4,4, 4,4,3, 0,1,0, false, 'Preciso en acuerdos principales. Omisión menor.'),
('b0000000-0000-0000-0000-000000000006', (SELECT id FROM summary_versions WHERE reunion_id = 'b0000000-0000-0000-0000-000000000006' AND version = 1), 'a0000000-0000-0000-0000-000000000007', 3,4,4,4,3,4, 3,3,3, 2,1,1, false, 'Mejorable en claridad de tareas asignadas.');

-- 11. REFERENCE TASKS (GOLD STANDARD)
INSERT INTO reference_tasks (id, reunion_id, descripcion, responsable_referencia, fecha_limite_referencia, creado_por, validado) VALUES
('f0000000-0000-0000-0000-000000000001', 'b0000000-0000-0000-0000-000000000001', 'Publicar resumen en Confluence', 'María López', '2025-06-17', 'a0000000-0000-0000-0000-000000000001', true),
('f0000000-0000-0000-0000-000000000002', 'b0000000-0000-0000-0000-000000000001', 'Revisar métricas calidad resúmenes IA', 'Carlos Ríos', '2025-06-18', 'a0000000-0000-0000-0000-000000000001', true),
('f0000000-0000-0000-0000-000000000003', 'b0000000-0000-0000-0000-000000000001', 'Preparar presentación resultados', 'Laura Medina', '2025-06-20', 'a0000000-0000-0000-0000-000000000001', true),
('f0000000-0000-0000-0000-000000000004', 'b0000000-0000-0000-0000-000000000001', 'Configurar entorno staging', 'Andrés Vega', '2025-06-22', 'a0000000-0000-0000-0000-000000000001', false),
('f0000000-0000-0000-0000-000000000005', 'b0000000-0000-0000-0000-000000000002', 'Documentar hallazgos experimento v1.0', 'Laura Medina', '2025-06-20', 'a0000000-0000-0000-0000-000000000001', true),
('f0000000-0000-0000-0000-000000000006', 'b0000000-0000-0000-0000-000000000002', 'Configurar experimentos v1.1', 'Andrés Vega', '2025-06-25', 'a0000000-0000-0000-0000-000000000001', true),
('f0000000-0000-0000-0000-000000000007', 'b0000000-0000-0000-0000-000000000005', 'Validar tareas gold standard', 'Carlos Ríos', '2025-06-26', 'a0000000-0000-0000-0000-000000000002', true),
('f0000000-0000-0000-0000-000000000008', 'b0000000-0000-0000-0000-000000000005', 'Definir criterios evaluación SUS', 'Laura Medina', '2025-06-26', 'a0000000-0000-0000-0000-000000000002', true),
('f0000000-0000-0000-0000-000000000009', 'b0000000-0000-0000-0000-000000000004', 'Ejecutar análisis estadístico fidelidad', 'Laura Medina', '2025-06-24', 'a0000000-0000-0000-0000-000000000002', true),
('f0000000-0000-0000-0000-000000000010', 'b0000000-0000-0000-0000-000000000004', 'Generar reporte PDF resultados', 'Andrés Vega', '2025-06-28', 'a0000000-0000-0000-0000-000000000002', false),
('f0000000-0000-0000-0000-000000000011', 'b0000000-0000-0000-0000-000000000006', 'Documentar metodología análisis prompts', 'Andrés Vega', '2025-07-05', 'a0000000-0000-0000-0000-000000000002', true),
('f0000000-0000-0000-0000-000000000012', 'b0000000-0000-0000-0000-000000000006', 'Definir objetivos investigación Q3', 'Sofía Torres', '2025-07-05', 'a0000000-0000-0000-0000-000000000002', true),
('f0000000-0000-0000-0000-000000000013', 'b0000000-0000-0000-0000-000000000009', 'Preparar demo evaluación ciega', 'Anthony García', '2025-07-07', 'a0000000-0000-0000-0000-000000000006', true),
('f0000000-0000-0000-0000-000000000014', 'b0000000-0000-0000-0000-000000000009', 'Recopilar feedback evaluadores', 'Carlos Ríos', '2025-07-08', 'a0000000-0000-0000-0000-000000000006', true),
('f0000000-0000-0000-0000-000000000015', 'b0000000-0000-0000-0000-000000000010', 'Analizar resultados SUS Cronbach alpha', 'Camila Reyes', '2025-07-12', 'a0000000-0000-0000-0000-000000000002', true),
('f0000000-0000-0000-0000-000000000016', 'b0000000-0000-0000-0000-000000000012', 'Documentar comparativa prompts v2.0', 'Sofía Torres', '2025-07-16', 'a0000000-0000-0000-0000-000000000002', true),
('f0000000-0000-0000-0000-000000000017', 'b0000000-0000-0000-0000-000000000012', 'Actualizar prompt v2.0 con feedback', 'Laura Medina', '2025-07-18', 'a0000000-0000-0000-0000-000000000002', false);

-- 12. EXPERIMENT SESSIONS
INSERT INTO experiment_sessions (id, nombre, descripcion, investigador_id, condicion, prompt_version_id, modelo, estado, fecha_inicio, fecha_fin) VALUES
('10000000-0000-0000-0000-000000000001', 'Experimento Prompt v1.0 — Fidelidad', 'Evaluar fidelidad con prompt v1.0', 'a0000000-0000-0000-0000-000000000002', 'manual', 'd0000000-0000-0000-0000-000000000001', 'gpt-4', 'COMPLETADO', '2025-06-15 10:00:00-05', '2025-06-22 16:00:00-05'),
('10000000-0000-0000-0000-000000000002', 'Experimento Prompt v1.1 — Fidelidad', 'Evaluar fidelidad con prompt v1.1 mejorado', 'a0000000-0000-0000-0000-000000000002', 'manual', 'd0000000-0000-0000-0000-000000000002', 'gpt-4', 'COMPLETADO', '2025-06-23 09:00:00-05', '2025-07-01 14:00:00-05'),
('10000000-0000-0000-0000-000000000003', 'Experimento Extracción de Tareas', 'Evaluar extracción automática de tareas', 'a0000000-0000-0000-0000-000000000005', 'zoom2_base', 'd0000000-0000-0000-0000-000000000003', 'gpt-4', 'COMPLETADO', '2025-06-20 11:00:00-05', '2025-06-25 14:30:00-05'),
('10000000-0000-0000-0000-000000000004', 'Experimento SUS — Usabilidad', 'Evaluar usabilidad con cuestionario SUS', 'a0000000-0000-0000-0000-000000000002', 'manual', NULL, NULL, 'COMPLETADO', '2025-07-05 09:00:00-05', '2025-07-10 16:00:00-05'),
('10000000-0000-0000-0000-000000000005', 'Experimento Prompt v2.0 — Comparativo', 'Comparar v2.0 (C-suite) vs v1.1', 'a0000000-0000-0000-0000-000000000002', 'zoom2_mejorado', 'd0000000-0000-0000-0000-000000000005', 'gpt-4-turbo', 'EN_CURSO', '2025-07-14 10:00:00-05', NULL),
('10000000-0000-0000-0000-000000000006', 'Experimento Sentimientos', 'Clasificar sentimientos en reuniones', 'a0000000-0000-0000-0000-000000000006', 'manual', 'd0000000-0000-0000-0000-000000000004', 'claude-3-sonnet', 'PLANIFICADO', '2025-07-25 10:00:00-05', NULL),
('10000000-0000-0000-0000-000000000007', 'Experimento Extracción v2.0', 'Evaluar extracción con dependencias', 'a0000000-0000-0000-0000-000000000005', 'zoom2_mejorado', 'd0000000-0000-0000-0000-000000000006', 'gpt-4-turbo', 'PLANIFICADO', '2025-08-01 09:00:00-05', NULL);

-- 13. STATISTICAL ANALYSES
INSERT INTO statistical_analyses (id, experiment_session_id, nombre, objetivo, variable_resultado, variable_grupo, diseno, prueba_solicitada, prueba_ejecutada, alpha, correccion_multiple, filtros, configuracion, estado, creado_por, fecha_ejecucion) VALUES
('20000000-0000-0000-0000-000000000001', '10000000-0000-0000-0000-000000000002', 'Comparación v1.0 vs v1.1 — Fidelidad', NULL, 'fidelidad', 'version_prompt', 'INDEPENDIENTE', 'welch_t_test', 'welch_t_test', 0.05, 'HOLM', '{"groups":{"v1.0":{"values":[3,4,3,4,3,4,3,4,5,4,3,4]},"v1.1":{"values":[4,5,4,4,5,4,5,4,5,4,4,5]}}}', '{}', 'COMPLETADO', 'a0000000-0000-0000-0000-000000000001', '2025-06-22 15:30:00-05'),
('20000000-0000-0000-0000-000000000002', '10000000-0000-0000-0000-000000000002', 'Comparación v1.0 vs v1.1 — Claridad', NULL, 'claridad', 'version_prompt', 'INDEPENDIENTE', 'mann_whitney_u', 'mann_whitney_u', 0.05, 'HOLM', '{"groups":{"v1.0":{"values":[3,4,3,3,4,3,4,3,3,4,3,3]},"v1.1":{"values":[4,5,5,4,5,4,4,5,4,4,5,4]}}}', '{}', 'COMPLETADO', 'a0000000-0000-0000-0000-000000000001', '2025-06-22 15:45:00-05'),
('20000000-0000-0000-0000-000000000003', '10000000-0000-0000-0000-000000000005', 'Extracción de Tareas — Precisión', NULL, 'precision', 'condicion', 'INDEPENDIENTE', 'welch_t_test', 'welch_t_test', 0.05, 'HOLM', '{"groups":{"manual":{"values":[0.85,0.90,0.88,0.92,0.87,0.91,0.89,0.93]},"zoom2":{"values":[0.78,0.82,0.80,0.85,0.79,0.83,0.81,0.84]}}}', '{}', 'COMPLETADO', 'a0000000-0000-0000-0000-000000000003', '2025-06-25 15:00:00-05'),
('20000000-0000-0000-0000-000000000004', '10000000-0000-0000-0000-000000000002', 'Consistencia Escala Likert — Cronbach', NULL, 'consistency', NULL, 'INDEPENDIENTE', 'cronbach_alpha', 'cronbach_alpha', 0.05, 'HOLM', '{"groups":{"eval":[[4,4,5,4,4,5],[5,4,4,5,4,4],[4,5,5,4,5,4],[3,4,4,3,4,3],[4,3,4,5,3,4]]}}', '{}', 'COMPLETADO', 'a0000000-0000-0000-0000-000000000002', '2025-07-10 11:00:00-05'),
('20000000-0000-0000-0000-000000000005', '10000000-0000-0000-0000-000000000006', 'Comparación v2.0 vs v1.1 — Ejecutividad', NULL, 'ejecutividad', 'version_prompt', 'INDEPENDIENTE', 'welch_t_test', 'welch_t_test', 0.05, 'HOLM', '{"groups":{"v1.1":{"values":[3.5,4.0,3.8,4.2,3.9]},"v2.0":{"values":[4.5,4.8,4.6,4.7,4.9]}}}', '{}', 'EJECUTANDO', 'a0000000-0000-0000-0000-000000000005', '2025-07-21 10:00:00-05'),
('20000000-0000-0000-0000-000000000006', '10000000-0000-0000-0000-000000000002', 'Comparación v1.0 vs v1.1 — Cobertura', NULL, 'cobertura', 'version_prompt', 'INDEPENDIENTE', 'welch_t_test', 'welch_t_test', 0.05, 'HOLM', '{"groups":{"v1.0":{"values":[3,3,4,3,4,3,3,4,3,3,4,3]},"v1.1":{"values":[4,4,5,4,4,5,4,4,5,4,4,4]}}}', '{}', 'COMPLETADO', 'a0000000-0000-0000-0000-000000000001', '2025-06-22 16:00:00-05'),
('20000000-0000-0000-0000-000000000007', '10000000-0000-0000-0000-000000000003', 'Comparación manual vs zoom2 — Tiempo', NULL, 'tiempo_total', 'condicion', 'INDEPENDIENTE', 'welch_t_test', 'welch_t_test', 0.05, 'HOLM', '{"groups":{"manual":{"values":[300,250,210,280,320,270,240,290]},"zoom2":{"values":[150,170,140,160,180,155,165,175]}}}', '{}', 'COMPLETADO', 'a0000000-0000-0000-0000-000000000005', '2025-06-25 16:00:00-05'),
('20000000-0000-0000-0000-000000000008', '10000000-0000-0000-0000-000000000004', 'Análisis SUS — Consistencia Interna', NULL, 'sus_score', NULL, 'INDEPENDIENTE', 'cronbach_alpha', 'cronbach_alpha', 0.05, 'HOLM', '{"groups":{"sus":[[4,2,5,2,4,2,4,2,5,2],[5,1,5,1,4,2,5,1,4,2],[4,3,4,3,3,3,4,3,4,3]]}}', '{}', 'PLANIFICADO', 'a0000000-0000-0000-0000-000000000002', NULL);

-- 14. STATISTICAL ANALYSIS RESULTS
INSERT INTO statistical_analysis_results (analysis_id, resultado, descriptivos, supuestos, efecto, intervalos, advertencias, interpretacion) VALUES
('20000000-0000-0000-0000-000000000001', '{"statistic": 2.34, "p_value": 0.028, "significant": true}', '{"group_a":{"mean":4.14,"std":0.67,"n":12}, "group_b":{"mean":4.54,"std":0.67,"n":12}}', '{}', '{"cohens_d": 0.6, "magnitude": "large"}', '{}', '[]', 'v1.1 produce fidelidad significativamente mayor que v1.0 (t=2.34, p=0.028).'),
('20000000-0000-0000-0000-000000000002', '{"statistic": 2.89, "p_value": 0.012, "significant": true}', '{"group_a":{"mean":3.95,"std":0.71,"n":12}, "group_b":{"mean":4.56,"std":0.49,"n":12}}', '{}', '{"cohens_d": 1.02, "magnitude": "large"}', '{}', '[]', 'v1.1 produce claridad significativamente mayor (U=2.89, p=0.012).'),
('20000000-0000-0000-0000-000000000003', '{"statistic": 3.12, "p_value": 0.008, "significant": true}', '{"group_a":{"mean":3.36,"std":0.4,"n":12}, "group_b":{"mean":4.31,"std":0.62,"n":12}}', '{}', '{"cohens_d": 1.86, "magnitude": "large"}', '{}', '[]', 'Método manual tiene precisión significativamente mayor que zoom2_base (t=3.12, p=0.008).'),
('20000000-0000-0000-0000-000000000004', '{"statistic": 4.21, "p_value": 0.003, "significant": true}', '{"group_a":{"mean":4.17,"std":0.7,"n":12}, "group_b":{"mean":4.93,"std":0.43,"n":12}}', '{}', '{"cohens_d": 1.35, "magnitude": "large"}', '{}', '[]', 'Escala de evaluación muestra consistencia interna excelente (α=0.91).'),
('20000000-0000-0000-0000-000000000006', '{"statistic": 1.95, "p_value": 0.042, "significant": true}', '{"group_a":{"mean":3.83,"std":0.74,"n":12}, "group_b":{"mean":4.59,"std":0.46,"n":12}}', '{}', '{"cohens_d": 1.27, "magnitude": "large"}', '{}', '[]', 'v1.1 produce cobertura significativamente mayor que v1.0 (t=1.95, p=0.042).'),
('20000000-0000-0000-0000-000000000007', '{"statistic": 5.67, "p_value": 0.001, "significant": true}', '{"group_a":{"mean":3.57,"std":0.46,"n":12}, "group_b":{"mean":4.73,"std":0.68,"n":12}}', '{}', '{"cohens_d": 2.04, "magnitude": "large"}', '{}', '[]', 'Método manual es significativamente más lento que zoom2_base (t=5.67, p=0.001).');

-- 15. SUS RESPONSES
INSERT INTO sus_responses (experiment_session_id, usuario_id, q1, q2, q3, q4, q5, q6, q7, q8, q9, q10, observaciones) VALUES
('10000000-0000-0000-0000-000000000004', 'a0000000-0000-0000-0000-000000000001', 4,2,5,2,4,2,4,2,5,2, 'Interfaz intuitiva. Tiempo de carga mejorable.'),
('10000000-0000-0000-0000-000000000004', 'a0000000-0000-0000-0000-000000000003', 5,1,5,1,4,2,5,1,4,2, 'Muy fácil. Evaluaciones ciegas son buen feature.'),
('10000000-0000-0000-0000-000000000004', 'a0000000-0000-0000-0000-000000000004', 4,3,4,3,3,3,4,3,4,3, 'Aceptable. Algunas funcionalidades no claras.'),
('10000000-0000-0000-0000-000000000004', 'a0000000-0000-0000-0000-000000000008', 5,1,4,1,5,1,5,1,5,1, 'Excelente usabilidad. Nada que mejorar.'),
('10000000-0000-0000-0000-000000000004', 'a0000000-0000-0000-0000-000000000009', 3,3,3,3,3,3,3,3,3,3, 'Neutral. No tengo opinión fuerte.'),
('10000000-0000-0000-0000-000000000004', 'a0000000-0000-0000-0000-000000000010', 4,2,4,2,4,2,4,2,4,2, 'Bueno pero puede mejorar en velocidad.'),
('10000000-0000-0000-0000-000000000004', 'a0000000-0000-0000-0000-000000000011', 5,1,5,2,4,2,5,1,4,2, 'Muy bueno para investigación.'),
('10000000-0000-0000-0000-000000000004', 'a0000000-0000-0000-0000-000000000012', 3,2,4,2,3,2,4,2,3,2, 'Aceptable. Falta documentación.'),
('10000000-0000-0000-0000-000000000004', 'a0000000-0000-0000-0000-000000000006', 5,1,5,1,5,1,5,1,5,1, 'Perfecto para uso diario.');

-- 16. TIME MEASUREMENTS
INSERT INTO time_measurements (experiment_session_id, reunion_id, participante_id, condicion, tiempo_elaboracion_segundos, tiempo_revision_segundos, tiempo_total_segundos, errores_detectados) VALUES
('10000000-0000-0000-0000-000000000001', 'b0000000-0000-0000-0000-000000000001', 'a0000000-0000-0000-0000-000000000003', 'manual', 180, 120, 300, 1),
('10000000-0000-0000-0000-000000000001', 'b0000000-0000-0000-0000-000000000002', 'a0000000-0000-0000-0000-000000000003', 'manual', 150, 100, 250, 0),
('10000000-0000-0000-0000-000000000002', 'b0000000-0000-0000-0000-000000000004', 'a0000000-0000-0000-0000-000000000003', 'manual', 120, 90, 210, 0),
('10000000-0000-0000-0000-000000000003', 'b0000000-0000-0000-0000-000000000003', 'a0000000-0000-0000-0000-000000000004', 'zoom2_base', 90, 60, 150, 2),
('10000000-0000-0000-0000-000000000003', 'b0000000-0000-0000-0000-000000000005', 'a0000000-0000-0000-0000-000000000004', 'zoom2_base', 100, 70, 170, 1),
('10000000-0000-0000-0000-000000000005', 'b0000000-0000-0000-0000-000000000012', 'a0000000-0000-0000-0000-000000000002', 'manual', 140, 100, 240, 0),
('10000000-0000-0000-0000-000000000005', 'b0000000-0000-0000-0000-000000000013', 'a0000000-0000-0000-0000-000000000005', 'manual', 110, 80, 190, 1),
('10000000-0000-0000-0000-000000000007', 'b0000000-0000-0000-0000-000000000009', 'a0000000-0000-0000-0000-000000000010', 'zoom2_mejorado', 80, 55, 135, 0);

-- 17. TASK EVALUATION MATCHES
INSERT INTO task_evaluation_matches (reunion_id, ai_execution_id, reference_task_id, detected_task_id, resultado, similitud, validado_por, observaciones) VALUES
('b0000000-0000-0000-0000-000000000001', 'e0000000-0000-0000-0000-000000000001', 'f0000000-0000-0000-0000-000000000001', 'c0000000-0000-0000-0000-000000000001', 'TP', 0.92, 'a0000000-0000-0000-0000-000000000003', 'Tarea detectada correctamente'),
('b0000000-0000-0000-0000-000000000001', 'e0000000-0000-0000-0000-000000000001', 'f0000000-0000-0000-0000-000000000002', 'c0000000-0000-0000-0000-000000000002', 'TP', 0.87, 'a0000000-0000-0000-0000-000000000003', 'Variación en redacción'),
('b0000000-0000-0000-0000-000000000001', 'e0000000-0000-0000-0000-000000000001', 'f0000000-0000-0000-0000-000000000003', NULL, 'FN', NULL, 'a0000000-0000-0000-0000-000000000003', 'Tarea no detectada'),
('b0000000-0000-0000-0000-000000000002', 'e0000000-0000-0000-0000-000000000002', 'f0000000-0000-0000-0000-000000000005', 'c0000000-0000-0000-0000-000000000004', 'TP', 0.95, 'a0000000-0000-0000-0000-000000000003', 'Coincidencia casi perfecta'),
('b0000000-0000-0000-0000-000000000002', 'e0000000-0000-0000-0000-000000000002', 'f0000000-0000-0000-0000-000000000006', 'c0000000-0000-0000-0000-000000000005', 'TP', 0.88, 'a0000000-0000-0000-0000-000000000003', 'Detectada con variación menor'),
('b0000000-0000-0000-0000-000000000005', 'e0000000-0000-0000-0000-000000000004', 'f0000000-0000-0000-0000-000000000012', 'c0000000-0000-0000-0000-000000000010', 'TP', 0.9, 'a0000000-0000-0000-0000-000000000003', 'Detectada correctamente'),
('b0000000-0000-0000-0000-000000000006', 'e0000000-0000-0000-0000-000000000005', 'f0000000-0000-0000-0000-000000000013', NULL, 'FN', NULL, 'a0000000-0000-0000-0000-000000000003', 'Tarea no detectada');

-- 18. PERFORMANCE METRICS
INSERT INTO performance_metrics (reunion_id, ai_execution_id, componente, operacion, duracion_ms, exitoso, codigo_estado) VALUES
('b0000000-0000-0000-0000-000000000001', 'e0000000-0000-0000-0000-000000000001', 'n8n', 'webhook_receive', 30, true, '200'),
('b0000000-0000-0000-0000-000000000001', 'e0000000-0000-0000-0000-000000000001', 'openai', 'chat_completion', 3653, true, '200'),
('b0000000-0000-0000-0000-000000000001', 'e0000000-0000-0000-0000-000000000001', 'supabase', 'insert', 132, true, '200'),
('b0000000-0000-0000-0000-000000000002', 'e0000000-0000-0000-0000-000000000002', 'n8n', 'webhook_receive', 61, true, '200'),
('b0000000-0000-0000-0000-000000000002', 'e0000000-0000-0000-0000-000000000002', 'openai', 'chat_completion', 1279, true, '200'),
('b0000000-0000-0000-0000-000000000002', 'e0000000-0000-0000-0000-000000000002', 'supabase', 'insert', 78, true, '200'),
('b0000000-0000-0000-0000-000000000003', 'e0000000-0000-0000-0000-000000000003', 'n8n', 'webhook_receive', 53, true, '200'),
('b0000000-0000-0000-0000-000000000003', 'e0000000-0000-0000-0000-000000000003', 'openai', 'chat_completion', 4799, true, '200'),
('b0000000-0000-0000-0000-000000000003', 'e0000000-0000-0000-0000-000000000003', 'supabase', 'insert', 128, true, '200'),
('b0000000-0000-0000-0000-000000000004', 'e0000000-0000-0000-0000-000000000004', 'n8n', 'webhook_receive', 45, true, '200'),
('b0000000-0000-0000-0000-000000000004', 'e0000000-0000-0000-0000-000000000004', 'openai', 'chat_completion', 1437, true, '200'),
('b0000000-0000-0000-0000-000000000004', 'e0000000-0000-0000-0000-000000000004', 'supabase', 'insert', 111, true, '200'),
('b0000000-0000-0000-0000-000000000005', 'e0000000-0000-0000-0000-000000000005', 'n8n', 'webhook_receive', 66, true, '200'),
('b0000000-0000-0000-0000-000000000005', 'e0000000-0000-0000-0000-000000000005', 'openai', 'chat_completion', 5078, true, '200'),
('b0000000-0000-0000-0000-000000000005', 'e0000000-0000-0000-0000-000000000005', 'supabase', 'insert', 70, true, '200'),
('b0000000-0000-0000-0000-000000000006', 'e0000000-0000-0000-0000-000000000006', 'n8n', 'webhook_receive', 35, true, '200'),
('b0000000-0000-0000-0000-000000000006', 'e0000000-0000-0000-0000-000000000006', 'openai', 'chat_completion', 4197, true, '200'),
('b0000000-0000-0000-0000-000000000006', 'e0000000-0000-0000-0000-000000000006', 'supabase', 'insert', 174, true, '200'),
('b0000000-0000-0000-0000-000000000007', 'e0000000-0000-0000-0000-000000000007', 'n8n', 'webhook_receive', 34, true, '200'),
('b0000000-0000-0000-0000-000000000007', 'e0000000-0000-0000-0000-000000000007', 'openai', 'chat_completion', 4315, true, '200'),
('b0000000-0000-0000-0000-000000000007', 'e0000000-0000-0000-0000-000000000007', 'supabase', 'insert', 186, true, '200'),
('b0000000-0000-0000-0000-000000000008', 'e0000000-0000-0000-0000-000000000008', 'n8n', 'webhook_receive', 79, true, '200'),
('b0000000-0000-0000-0000-000000000008', 'e0000000-0000-0000-0000-000000000008', 'openai', 'chat_completion', 1715, true, '200'),
('b0000000-0000-0000-0000-000000000008', 'e0000000-0000-0000-0000-000000000008', 'supabase', 'insert', 82, true, '200'),
('b0000000-0000-0000-0000-000000000009', 'e0000000-0000-0000-0000-000000000009', 'n8n', 'webhook_receive', 72, true, '200'),
('b0000000-0000-0000-0000-000000000009', 'e0000000-0000-0000-0000-000000000009', 'openai', 'chat_completion', 3146, true, '200'),
('b0000000-0000-0000-0000-000000000009', 'e0000000-0000-0000-0000-000000000009', 'supabase', 'insert', 190, true, '200'),
('b0000000-0000-0000-0000-000000000010', 'e0000000-0000-0000-0000-000000000010', 'n8n', 'webhook_receive', 40, true, '200'),
('b0000000-0000-0000-0000-000000000010', 'e0000000-0000-0000-0000-000000000010', 'openai', 'chat_completion', 2285, true, '200'),
('b0000000-0000-0000-0000-000000000010', 'e0000000-0000-0000-0000-000000000010', 'supabase', 'insert', 185, true, '200');

-- 19. METRICAS N8N
INSERT INTO metricas_n8n (endpoint, tiempo_respuesta, estado, fecha, codigo_estado, tamano_respuesta, outcome, is_terminal, data_source, started_at, completed_at, end_to_end_latency_seconds) VALUES
('/api/v1/research/analyses', 0.22, 'success', NOW() - INTERVAL '14 days', 200, 1933, 'success', true, 'production', NOW() - INTERVAL '14 days', NOW() - INTERVAL '14 days' + INTERVAL '0.22 seconds', 0.22),
('/experiments/sessions', 0.24, 'success', NOW() - INTERVAL '13 days', 200, 2408, 'success', true, 'production', NOW() - INTERVAL '13 days', NOW() - INTERVAL '13 days' + INTERVAL '0.24 seconds', 0.24),
('/evaluations/summaries', 0.2, 'success', NOW() - INTERVAL '12 days', 200, 3025, 'success', true, 'production', NOW() - INTERVAL '12 days', NOW() - INTERVAL '12 days' + INTERVAL '0.2 seconds', 0.2),
('/prompts', 0.07, 'success', NOW() - INTERVAL '11 days', 200, 1476, 'success', true, 'production', NOW() - INTERVAL '11 days', NOW() - INTERVAL '11 days' + INTERVAL '0.07 seconds', 0.07),
('/auth/login', 0.12, 'success', NOW() - INTERVAL '10 days', 200, 2951, 'success', true, 'production', NOW() - INTERVAL '10 days', NOW() - INTERVAL '10 days' + INTERVAL '0.12 seconds', 0.12),
('/auth/me', 0.17, 'success', NOW() - INTERVAL '9 days', 200, 1994, 'success', true, 'production', NOW() - INTERVAL '9 days', NOW() - INTERVAL '9 days' + INTERVAL '0.17 seconds', 0.17),
('/reports', 0.23, 'success', NOW() - INTERVAL '8 days', 200, 2049, 'success', true, 'production', NOW() - INTERVAL '8 days', NOW() - INTERVAL '8 days' + INTERVAL '0.23 seconds', 0.23);

-- ============================================================
-- FIN DEL SEED: 12 usuarios, 20 reuniones,
-- 26 tareas, 14 resúmenes, 7 prompts,
-- 14 ejecuciones IA, 10 summary versions, 17 gold standards,
-- 7 experiment sessions, 8 análisis estadísticos, 7 resultados,
-- 9 SUS responses, 8 time measurements.
-- ============================================================