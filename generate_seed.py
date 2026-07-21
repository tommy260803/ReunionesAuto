"""Genera seed_completo.sql con datos coherentes y realistas."""
import uuid
import random
from datetime import datetime, timedelta

random.seed(42)

HASH = "$2b$12$zChrGI196GrAJwB54kuPbuaK5BYv3XqBRoA5cZnMMsrUjbXecl0Nm"

def uid(prefix, i):
    return f"{prefix}0000000-0000-0000-0000-{str(i).zfill(12)}"

def ts(dt):
    return dt.strftime("%Y-%m-%d %H:%M:%S-05")

users = [
    (uid("a",1), "Anthony García", "anthonygv268@gmail.com", "enterprise", "activo", "ADMIN"),
    (uid("a",2), "Dra. Laura Medina", "laura@zoom2.test", "pro", "activo", "INVESTIGADOR"),
    (uid("a",3), "Carlos Ríos", "carlos@zoom2.test", "pro", "activo", "EVALUADOR"),
    (uid("a",4), "María López", "maria@zoom2.test", "basico", "activo", "USUARIO"),
    (uid("a",5), "Ing. Andrés Vega", "andres@zoom2.test", "pro", "activo", "INVESTIGADOR"),
    (uid("a",6), "Dra. Sofía Torres", "sofia@zoom2.test", "pro", "activo", "INVESTIGADOR"),
    (uid("a",7), "Pedro Morales", "pedro@zoom2.test", "basico", "activo", "EVALUADOR"),
    (uid("a",8), "Ana Ruiz", "ana@zoom2.test", "pro", "activo", "USUARIO"),
    (uid("a",9), "Diego Fernández", "diego@zoom2.test", "basico", "activo", "USUARIO"),
    (uid("a",10), "Ing. Camila Reyes", "camila@zoom2.test", "pro", "activo", "INVESTIGADOR"),
    (uid("a",11), "Roberto Díaz", "roberto@zoom2.test", "basico", "activo", "USUARIO"),
    (uid("a",12), "Lucía Vargas", "lucia@zoom2.test", "pro", "activo", "EVALUADOR"),
]

meetings_data = [
    ("Sprint Review — Módulo de Resúmenes IA", "2025-06-15 09:00", 60, "completada"),
    ("Revisión de Resultados Experimentales — Prompt v1.0", "2025-06-18 14:00", 45, "completada"),
    ("Daily Standup — Equipo de Desarrollo", "2025-06-20 08:30", 15, "completada"),
    ("Análisis Estadístico — Comparación de Prompts v1.0 vs v1.1", "2025-06-22 10:00", 90, "completada"),
    ("Workshop — Validación de Gold Standard", "2025-06-25 11:00", 75, "completada"),
    ("Kickoff — Proyecto de Investigación Q3", "2025-07-01 09:00", 120, "completada"),
    ("Revisión Semanal — Avances del Sprint 14", "2025-07-04 09:00", 30, "completada"),
    ("Demo — Sistema de Evaluación Ciega", "2025-07-07 15:00", 45, "completada"),
    ("Análisis de Resultados — Experimento SUS", "2025-07-10 10:00", 60, "completada"),
    ("Retrospectiva — Sprint 14", "2025-07-11 16:00", 45, "completada"),
    ("Revisión de Prompt v2.0 — Comparativo con v1.1", "2025-07-14 11:00", 90, "completada"),
    ("Daily Standup — Equipo de Desarrollo", "2025-07-15 08:30", 15, "completada"),
    ("Revisión Semanal — Avances del Sprint 15", "2025-07-18 09:00", 30, "completada"),
    ("Análisis Estadístico — Comparación Prompt v2.0 vs v1.1", "2025-07-21 10:00", 90, "programada"),
    ("Planning — Sprint 16", "2025-07-21 14:00", 60, "programada"),
    ("Workshop — Metodología de Evaluación Ciega", "2025-07-25 10:00", 120, "programada"),
    ("Revisión Semanal — Avances del Sprint 16", "2025-07-28 09:00", 30, "programada"),
    ("Demo — Sistema de Reportes Automáticos", "2025-08-01 15:00", 45, "programada"),
    ("Reunión de Cierre — Fase 1 del Proyecto", "2025-08-08 09:00", 180, "programada"),
    ("Revisión de Métricas de Calidad — Q3 Intermedio", "2025-08-15 10:00", 60, "programada"),
]

creadores = [0,1,0,1,4,5,1,0,9,1,5,0,1,1,0,5,1,0,5,5]
participantes_map = {
    0: [0,1,2,3,4,5], 1: [1,0,4,5,2], 2: [0,1,4], 3: [1,4,2,5],
    4: [4,1,2,6], 5: [5,0,1,4,9,7], 6: [1,4,9], 7: [0,1,2,6,11],
    8: [9,1,4], 9: [1,2,6,3], 10: [5,1,4,2], 11: [0,1,4],
    12: [1,4,9], 13: [1,5,4,9], 14: [0,1,4,9], 15: [5,1,4,2,6],
    16: [1,4,9], 17: [0,1,2,6], 18: [5,1,4,9,0,7], 19: [0,1,4,5,9],
}
estados_inv = ["aceptado"]*12 + ["enviado"]*8

tareas_data = []
tarea_idx = 0
for mid in range(14):
    n = random.randint(1,3)
    for j in range(n):
        tarea_idx += 1
        desc = random.choice([
            "Publicar resumen del sprint en Confluence",
            "Revisar métricas de calidad de resúmenes IA",
            "Preparar presentación para stakeholders",
            "Documentar hallazgos del experimento",
            "Configurar entorno de staging",
            "Actualizar backlog con tareas del standup",
            "Ejecutar análisis estadístico",
            "Generar reporte PDF con resultados",
            "Validar tareas gold standard",
            "Definir criterios de evaluación SUS",
            "Definir objetivos de investigación Q3",
            "Asignar roles del equipo",
            "Cerrar sprint y actualizar métricas",
            "Preparar demo del sistema",
            "Recopilar feedback de evaluadores",
            "Analizar resultados SUS con Cronbach alpha",
            "Identificar mejoras para próximo sprint",
            "Crear action items del sprint",
            "Documentar comparativa de prompts",
            "Actualizar prompt con feedback",
            "Cerrar sprint y preparar retrospectiva",
            "Actualizar backlog para sprint 16",
            "Preparar datos para análisis estadístico",
            "Estimar story points para tareas",
            "Preparar material para workshop",
        ])
        email = random.choice(users)[2]
        estado = random.choice(["completada"]*7 + ["en_progreso", "pendiente"])
        dias = 2 + random.randint(0, 14)
        fecha = datetime(2025, 6, 15) + timedelta(days=mid*3 + j*dias)
        tareas_data.append((uid("c", tarea_idx), uid("b", mid+1), desc, email, estado, ts(fecha)))

resumenes_textos = [
    "Sprint review exitosa. 8 de 10 historias completadas. Bug detectado en timeouts para reuniones > 60min.",
    "Revisión de resultados experimentales. Fidelidad promedio v1.0: 3.8/5. Omisiones en acuerdos secundarios.",
    "Standup rápido. Andrés completó integración con API de Zoom. Pendiente: configurar staging.",
    "Análisis estadístico completado. v1.1 muestra mejora significativa en claridad (p < 0.05).",
    "Workshop gold standard. 15 tareas de referencia definidas. 12 validadas, 3 pendientes.",
    "Kickoff Q3. 3 objetivos: precisión >90%, tiempo <30s, evaluación ciega con 5+ evaluadores.",
    "Revisión sprint 14. 7/10 tareas completadas. Velocity mejoró 12%.",
    "Demo evaluación ciega. Feedback positivo. Sugerencia: botón para saltar preguntas.",
    "Análisis SUS: score 78.5/100 (Bueno). Peor aspecto: tiempo de carga (2.8/5).",
    "Retrospectiva sprint 14. Mejoras: tests E2E, documentación APIs, code review obligatorio.",
    "Revisión prompt v2.0. Estructura C-suite mejorada. Decisión: lanzar v2.0 como estándar.",
    "Daily standup. Pendientes: cerrar sprint 15, preparar planning sprint 16.",
    "Revisión sprint 15. 9/12 tareas completadas. Velocity mejoró 15% vs sprint 14.",
    "Resumen de la reunión de planificación del próximo sprint con objetivos definidos.",
]

resumenes_detalle_data = [
    (uid("b",1), "Sprint review 80% completado. Bug en timeouts detectado.", "1) Fix timeout prioritario. 2) Mantener ritmo.", "Retraso en release si no se resuelve.", "Laura investiga (miércoles). Andrés hotfix."),
    (uid("b",4), "Comparación v1.0 vs v1.1. Mejora significativa en claridad.", "1) Adoptar v1.1 como estándar. 2) Archivar v1.0.", "Overfitting a datos de entrenamiento.", "Segunda ronda de validación. Documentar cambios."),
    (uid("b",6), "Kickoff Q3 con objetivos ambiciosos pero alcanzables.", "1) Precisión >90%. 2) Tiempo <30s. 3) Evaluación ciega.", "Sobrecarga del equipo.", "Dividir en fases. Milestones semanales."),
    (uid("b",9), "Demo exitosa. Feedback muy positivo.", "1) Skip button. 2) Métricas tiempo/pregunta.", "Baja adopción si interfaz no es intuitiva.", "Implementar skip button. Tutorial interactivo."),
    (uid("b",10), "SUS: 78.5/100. Tiempo de carga es principal dolor.", "1) Optimizar queries Supabase. 2) Caché Redis.", "SUS bajar sin optimizaciones.", "Optimizar queries. Caché Redis. Re-evaluar SUS."),
    (uid("b",11), "Retrospectiva productiva. 3 áreas de mejora.", "1) Tests E2E. 2) Documentar APIs. 3) Code review.", "Perder velocidad si se implementa todo.", "Tests este sprint. Documentación incremental."),
    (uid("b",12), "Prompt v2.0 revisado. Estructura C-suite mejorada.", "1) Lanzar v2.0 estándar ejecutivo. 2) Mantener v1.1.", "Confusión de usuarios.", "Guía de migración. Newsletter. Monitorear uso."),
    (uid("b",13), "Velocity mejoró 15%. Sprint productivo.", "1) Mantener ritmo. 2) Meta velocity sprint 16.", "Burnout si no hay pausas.", "Daily más cortos. Retrospectiva intermedia."),
]

prompts_data = [
    (uid("d",1), "resumen_reunion", "1.0", "Eres un asistente experto en reuniones corporativas. Genera un resumen ejecutivo de la siguiente reunión. Incluye: tema principal, participantes, acuerdos tomados, tareas asignadas y próximos pasos.", "Generar resúmenes precisos de reuniones.", "openai", "gpt-4", False, 1),
    (uid("d",2), "resumen_reunion", "1.1", "Eres un asistente experto en reuniones corporativas. Genera un resumen ejecutivo con: tema principal, participantes roles, acuerdos por categoría, tareas con responsable y fecha, riesgos y próximos pasos con prioridad.", "Resúmenes detallados con clasificación y priorización.", "openai", "gpt-4", False, 1),
    (uid("d",3), "extraccion_tareas", "1.0", "Analiza la transcripción y extrae todas las tareas mencionadas: descripción, responsable, fecha límite y prioridad.", "Extraer tareas accionables de reuniones.", "openai", "gpt-4", False, 4),
    (uid("d",4), "clasificacion_sentimientos", "1.0", "Clasifica el sentimiento de cada participante como positivo, neutro o negativo con evidencia textual.", "Evaluar clima de reuniones.", "anthropic", "claude-3-sonnet", False, 1),
    (uid("d",5), "resumen_reunion", "2.0", "Analista senior con 10 años de experiencia. Resumen ejecutivo: (1) Resumen 3-5 oraciones, (2) Decisiones con impacto, (3) Tareas en tabla, (4) Riesgos, (5) Próximos pasos con owner y deadline.", "Resúmenes nivel C-suite.", "openai", "gpt-4-turbo", True, 1),
    (uid("d",6), "extraccion_tareas", "2.0", "Experto en gestión de proyectos. Extrae tareas: descripción accionable, responsable, fecha límite, prioridad [Alta/Media/Baja], dependencias.", "Extracción mejorada con dependencias.", "openai", "gpt-4-turbo", True, 4),
    (uid("d",7), "resumen_reunion", "3.0", "Consultor McKinsey. Formato SCQA: (1) Situation, (2) Complication, (3) Key Questions, (4) Answer & Recommendation, (5) Next Steps en tabla.", "Resúmenes estilo consultora de élite.", "openai", "gpt-4-turbo", False, 1),
]

# Build SQL
sql = []
sql.append("-- ============================================================")
sql.append("-- SEED COMPLETO Y EXTENSO — REUNIONESAUTO (ZOOM2)")
sql.append("-- ============================================================")
sql.append("-- Ejecutar DESPUÉS de query1-query13.")
sql.append("-- Contraseña: password123 | Idempotente.")
sql.append("-- ============================================================")
sql.append("")
sql.append("DELETE FROM task_evaluation_matches;")
sql.append("DELETE FROM performance_metrics;")
sql.append("DELETE FROM sus_responses;")
sql.append("DELETE FROM time_measurements;")
sql.append("DELETE FROM statistical_analysis_results;")
sql.append("DELETE FROM statistical_analyses;")
sql.append("DELETE FROM summary_evaluations;")
sql.append("DELETE FROM summary_versions;")
sql.append("DELETE FROM ai_executions;")
sql.append("DELETE FROM reference_tasks;")
sql.append("DELETE FROM prompt_versions;")
sql.append("DELETE FROM experiment_sessions;")
sql.append("DELETE FROM resumenes_detalle;")
sql.append("DELETE FROM resumenes;")
sql.append("DELETE FROM tareas;")
sql.append("DELETE FROM participantes;")
sql.append("DELETE FROM reuniones;")
sql.append("DELETE FROM metricas_n8n;")
sql.append("DELETE FROM usuarios;")
sql.append("")

# Users
sql.append("-- 1. USUARIOS")
sql.append("INSERT INTO usuarios (id, nombre, correo, password_hash, nivel_suscripcion, estado_suscripcion, rol) VALUES")
for i, (id_, name, email, nivel, estado, rol) in enumerate(users):
    comma = "," if i < len(users)-1 else ";"
    sql.append(f"('{id_}', '{name}', '{email}', '{HASH}', '{nivel}', '{estado}', '{rol}'){comma}")
sql.append("")

# Meetings
sql.append("-- 2. REUNIONES")
sql.append("INSERT INTO reuniones (id, creador_id, tema, fecha_inicio, duracion_minutos, proveedor, estado, tipo) VALUES")
for i, (tema, fecha, dur, estado) in enumerate(meetings_data):
    bid = uid("b", i+1)
    cid = uid("b", 0)  # placeholder, we fix below
    # Fix: use real creator IDs
    creator_idx = creadores[i]
    cid = users[creator_idx][0]
    comma = "," if i < len(meetings_data)-1 else ";"
    sql.append(f"('{bid}', '{cid}', '{tema}', '{fecha}:00-05', {dur}, 'zoom', '{estado}', 'virtual'){comma}")
sql.append("")

# Participants
sql.append("-- 3. PARTICIPANTES")
sql.append("INSERT INTO participantes (reunion_id, usuario_id, correo, rol, estado_invitacion) VALUES")
pvals = []
for mid in range(len(meetings_data)):
    bid = uid("b", mid+1)
    rol = "organizador"
    for uidx in participantes_map.get(mid, [0]):
        email = users[uidx][2]
        estado = "aceptado" if mid < 14 else "enviado"
        pvals.append(f"('{bid}', '{users[uidx][0]}', '{email}', '{rol}', '{estado}')")
        rol = "participante"
for i, v in enumerate(pvals):
    comma = "," if i < len(pvals)-1 else ";"
    sql.append(f"{v}{comma}")
sql.append("")

# Tasks
sql.append("-- 4. TAREAS")
sql.append("INSERT INTO tareas (id, reunion_id, descripcion, asignado_a_correo, estado, fecha_vencimiento) VALUES")
for i, (tid, rid, desc, email, estado, fecha) in enumerate(tareas_data):
    comma = "," if i < len(tareas_data)-1 else ";"
    desc = desc.replace("'", "''")
    sql.append(f"('{tid}', '{rid}', '{desc}', '{email}', '{estado}', '{fecha}'){comma}")
sql.append("")

# Resúmenes
sql.append("-- 5. RESÚMENES")
sql.append("INSERT INTO resumenes (reunion_id, resumen) VALUES")
for i in range(14):
    bid = uid("b", i+1)
    texto = resumenes_textos[i].replace("'", "''")
    comma = "," if i < 13 else ";"
    sql.append(f"('{bid}', '{texto}'){comma}")
sql.append("")

# Resúmenes detalle
sql.append("-- 6. RESÚMENES DETALLE")
sql.append("INSERT INTO resumenes_detalle (reunion_id, resumen_ejecutivo, decisiones, riesgos, proximos_pasos) VALUES")
for i, (rid, ejec, dec, riesgos, pasos) in enumerate(resumenes_detalle_data):
    ejec = ejec.replace("'","''")
    dec = dec.replace("'","''")
    riesgos = riesgos.replace("'","''")
    pasos = pasos.replace("'","''")
    comma = "," if i < len(resumenes_detalle_data)-1 else ";"
    sql.append(f"('{rid}', '{ejec}', '{dec}', '{riesgos}', '{pasos}'){comma}")
sql.append("")

# Prompt versions
sql.append("-- 7. PROMPT VERSIONS")
sql.append("INSERT INTO prompt_versions (id, nombre, version, contenido, objetivo, proveedor, modelo_recomendado, activo, creado_por) VALUES")
for i, (pid, nombre, ver, contenido, objetivo, prov, modelo, activo, autor) in enumerate(prompts_data):
    contenido = contenido.replace("'","''")
    objetivo = objetivo.replace("'","''")
    activo_str = "true" if activo else "false"
    comma = "," if i < len(prompts_data)-1 else ";"
    sql.append(f"('{pid}', '{nombre}', '{ver}', '{contenido}', '{objetivo}', '{prov}', '{modelo}', {activo_str}, '{users[autor][0]}'){comma}")
sql.append("")

# AI Executions (14 — one per completed meeting that has a prompt)
sql.append("-- 8. AI EXECUTIONS")
sql.append("INSERT INTO ai_executions (id, reunion_id, prompt_version_id, proveedor, modelo, temperatura, tokens_entrada, tokens_salida, costo_estimado, tiempo_ms, estado, iniciado_por) VALUES")
ai_execs = []
for i in range(14):
    eid = uid("e", i+1)
    bid = uid("b", i+1)
    pid = prompts_data[min(i, 6)][0]
    proveedor = "openai"
    modelo = "gpt-4-turbo" if i in [5,7,9,13] else "gpt-4"
    tokens_in = random.randint(400, 3200)
    tokens_out = random.randint(150, 900)
    costo = round(tokens_in * 0.00001 + tokens_out * 0.00003, 4)
    tiempo = random.randint(1200, 5200)
    autor_idx = creadores[i]
    ai_execs.append((eid, bid, pid, proveedor, modelo, 0.3, tokens_in, tokens_out, costo, tiempo, "completado", users[autor_idx][0]))
for i, (eid, bid, pid, prov, modelo, temp, tin, tout, cost, tiempo, estado, autor) in enumerate(ai_execs):
    comma = "," if i < len(ai_execs)-1 else ";"
    sql.append(f"('{eid}', '{bid}', '{pid}', '{prov}', '{modelo}', {temp}, {tin}, {tout}, {cost}, {tiempo}, '{estado}', '{autor}'){comma}")
sql.append("")

# Summary versions
sql.append("-- 9. SUMMARY VERSIONS")
sql.append("INSERT INTO summary_versions (reunion_id, ai_execution_id, version, origen, contenido, estado, es_version_actual, creado_por) VALUES")
sv_contents = [
    "Sprint Review — Módulo de Resúmenes IA. Acuerdos: priorizar fix timeout, mantener ritmo. Tareas: Laura investiga timeout, Andrés hotfix.",
    "Revisión Resultados Experimentales. v1.0 fidelidad 3.8/5. Omisiones en acuerdos secundarios. Avanzar con v1.1.",
    "Análisis Estadístico. Prueba t de Welch: v1.1 mejora significativa en claridad (p<0.05). Adoptar v1.1.",
    "Kickoff Q3. Objetivos: precisión >90%, tiempo <30s, evaluación ciega 5+ evaluadores.",
    "Revisión sprint 14. 7/10 tareas. Velocity mejoró 12%.",
    "Demo evaluación ciega. Feedback positivo. Skip button sugerido.",
    "SUS score 78.5/100. Tiempo de carga: 2.8/5. Optimizar queries.",
    "Retrospectiva sprint 14. Tests E2E, documentación APIs, code review.",
    "Prompt v2.0. Estructura C-suite. Lanzar como estándar ejecutivo.",
    "Revisión sprint 15. 9/12 tareas. Velocity +15%.",
]
sv_estados = ["APROBADO"]*9 + ["PENDIENTE_REVISION"]
sv_creadores = [0,1,1,5,1,0,9,1,5,1]
for i in range(10):
    bid = uid("b", i+1)
    eid = uid("e", i+1)
    contenido = sv_contents[i].replace("'","''")
    estado = sv_estados[i]
    autor = users[sv_creadores[i]][0]
    comma = "," if i < 9 else ";"
    sql.append(f"('{bid}', '{eid}', 1, 'IA', '{contenido}', '{estado}', true, '{autor}'){comma}")
sql.append("")

# Summary evaluations
sql.append("-- 10. SUMMARY EVALUATIONS")
sql.append("INSERT INTO summary_evaluations (reunion_id, summary_version_id, evaluador_id, fidelidad, cobertura, claridad, coherencia, concision, utilidad, acuerdos_correctos, responsables_correctos, fechas_correctas, omisiones, afirmaciones_no_respaldadas, contradicciones, aprobado_sin_cambios, observaciones) VALUES")
evals = []
for i in range(6):
    bid = uid("b", i+1)
    sv_id_sub = f"(SELECT id FROM summary_versions WHERE reunion_id = '{bid}' AND version = 1)"
    evals.append((bid, sv_id_sub, users[2][0], 4,4,5,4,4,5, 4,3,3, 1,0,0, False, "Buen resumen pero faltó mencionar acuerdos secundarios."))
    evals.append((bid, sv_id_sub, users[1][0], 5,4,4,5,4,4, 4,4,3, 0,1,0, False, "Preciso en acuerdos principales. Omisión menor."))
    evals.append((bid, sv_id_sub, users[6][0], 3,4,4,4,3,4, 3,3,3, 2,1,1, False, "Mejorable en claridad de tareas asignadas."))
for i, (bid, sv_id, eval_uid, f, co, cl, coh, ci, ut, ac, re, fe, om, af, co2, ap, obs) in enumerate(evals):
    obs = obs.replace("'","''")
    comma = "," if i < len(evals)-1 else ";"
    sql.append(f"('{bid}', {sv_id}, '{eval_uid}', {f},{co},{cl},{coh},{ci},{ut}, {ac},{re},{fe}, {om},{af},{co2}, {str(ap).lower()}, '{obs}'){comma}")
sql.append("")

# Reference tasks
sql.append("-- 11. REFERENCE TASKS (GOLD STANDARD)")
sql.append("INSERT INTO reference_tasks (id, reunion_id, descripcion, responsable_referencia, fecha_limite_referencia, creado_por, validado) VALUES")
rt_data = [
    (1, "Publicar resumen en Confluence", "María López", "2025-06-17", True),
    (1, "Revisar métricas calidad resúmenes IA", "Carlos Ríos", "2025-06-18", True),
    (1, "Preparar presentación resultados", "Laura Medina", "2025-06-20", True),
    (1, "Configurar entorno staging", "Andrés Vega", "2025-06-22", False),
    (2, "Documentar hallazgos experimento v1.0", "Laura Medina", "2025-06-20", True),
    (2, "Configurar experimentos v1.1", "Andrés Vega", "2025-06-25", True),
    (5, "Validar tareas gold standard", "Carlos Ríos", "2025-06-26", True),
    (5, "Definir criterios evaluación SUS", "Laura Medina", "2025-06-26", True),
    (4, "Ejecutar análisis estadístico fidelidad", "Laura Medina", "2025-06-24", True),
    (4, "Generar reporte PDF resultados", "Andrés Vega", "2025-06-28", False),
    (6, "Documentar metodología análisis prompts", "Andrés Vega", "2025-07-05", True),
    (6, "Definir objetivos investigación Q3", "Sofía Torres", "2025-07-05", True),
    (9, "Preparar demo evaluación ciega", "Anthony García", "2025-07-07", True),
    (9, "Recopilar feedback evaluadores", "Carlos Ríos", "2025-07-08", True),
    (10, "Analizar resultados SUS Cronbach alpha", "Camila Reyes", "2025-07-12", True),
    (12, "Documentar comparativa prompts v2.0", "Sofía Torres", "2025-07-16", True),
    (12, "Actualizar prompt v2.0 con feedback", "Laura Medina", "2025-07-18", False),
]
for i, (midx, desc, resp, fecha, val) in enumerate(rt_data):
    rid = uid("b", midx)
    cid = users[0 if midx < 4 else 1 if midx < 7 else 5 if midx < 10 else 1 if midx < 13 else 5][0]
    fid = uid("f", i+1)
    desc = desc.replace("'","''")
    comma = "," if i < len(rt_data)-1 else ";"
    sql.append(f"('{fid}', '{rid}', '{desc}', '{resp}', '{fecha}', '{cid}', {str(val).lower()}){comma}")
sql.append("")

# Experiment sessions
sql.append("-- 12. EXPERIMENT SESSIONS")
sql.append("INSERT INTO experiment_sessions (id, nombre, descripcion, investigador_id, condicion, prompt_version_id, modelo, estado, fecha_inicio, fecha_fin) VALUES")
exp_sessions = [
    ("Experimento Prompt v1.0 — Fidelidad", "Evaluar fidelidad con prompt v1.0", 1, "manual", 0, "gpt-4", "COMPLETADO", "2025-06-15 10:00", "2025-06-22 16:00"),
    ("Experimento Prompt v1.1 — Fidelidad", "Evaluar fidelidad con prompt v1.1 mejorado", 1, "manual", 1, "gpt-4", "COMPLETADO", "2025-06-23 09:00", "2025-07-01 14:00"),
    ("Experimento Extracción de Tareas", "Evaluar extracción automática de tareas", 4, "zoom2_base", 2, "gpt-4", "COMPLETADO", "2025-06-20 11:00", "2025-06-25 14:30"),
    ("Experimento SUS — Usabilidad", "Evaluar usabilidad con cuestionario SUS", 1, "manual", None, None, "COMPLETADO", "2025-07-05 09:00", "2025-07-10 16:00"),
    ("Experimento Prompt v2.0 — Comparativo", "Comparar v2.0 (C-suite) vs v1.1", 1, "zoom2_mejorado", 4, "gpt-4-turbo", "EN_CURSO", "2025-07-14 10:00", None),
    ("Experimento Sentimientos", "Clasificar sentimientos en reuniones", 5, "manual", 3, "claude-3-sonnet", "PLANIFICADO", "2025-07-25 10:00", None),
    ("Experimento Extracción v2.0", "Evaluar extracción con dependencias", 4, "zoom2_mejorado", 5, "gpt-4-turbo", "PLANIFICADO", "2025-08-01 09:00", None),
]
for i, (nombre, desc, autor_idx, cond, pidx, modelo, estado, fini, ffin) in enumerate(exp_sessions):
    eid = uid("1", i+1)
    pid = f"'{prompts_data[pidx][0]}'" if pidx is not None else "NULL"
    modelo_str = f"'{modelo}'" if modelo else "NULL"
    ffin_str = f"'{ffin}:00-05'" if ffin else "NULL"
    comma = "," if i < len(exp_sessions)-1 else ";"
    desc = desc.replace("'","''")
    sql.append(f"('{eid}', '{nombre}', '{desc}', '{users[autor_idx][0]}', '{cond}', {pid}, {modelo_str}, '{estado}', '{fini}:00-05', {ffin_str}){comma}")
sql.append("")

# Statistical analyses
sql.append("-- 13. STATISTICAL ANALYSES")
sql.append("INSERT INTO statistical_analyses (id, experiment_session_id, nombre, objetivo, variable_resultado, variable_grupo, diseno, prueba_solicitada, prueba_ejecutada, alpha, correccion_multiple, filtros, configuracion, estado, creado_por, fecha_ejecucion) VALUES")
analyses = [
    ("Comparación v1.0 vs v1.1 — Fidelidad", "fidelidad", "version_prompt", "welch_t_test", "COMPLETADO", 1, 0, "2025-06-22 15:30", '{"groups":{"v1.0":{"values":[3,4,3,4,3,4,3,4,5,4,3,4]},"v1.1":{"values":[4,5,4,4,5,4,5,4,5,4,4,5]}}}'),
    ("Comparación v1.0 vs v1.1 — Claridad", "claridad", "version_prompt", "mann_whitney_u", "COMPLETADO", 1, 0, "2025-06-22 15:45", '{"groups":{"v1.0":{"values":[3,4,3,3,4,3,4,3,3,4,3,3]},"v1.1":{"values":[4,5,5,4,5,4,4,5,4,4,5,4]}}}'),
    ("Extracción de Tareas — Precisión", "precision", "condicion", "welch_t_test", "COMPLETADO", 4, 2, "2025-06-25 15:00", '{"groups":{"manual":{"values":[0.85,0.90,0.88,0.92,0.87,0.91,0.89,0.93]},"zoom2":{"values":[0.78,0.82,0.80,0.85,0.79,0.83,0.81,0.84]}}}'),
    ("Consistencia Escala Likert — Cronbach", "consistency", None, "cronbach_alpha", "COMPLETADO", 1, 1, "2025-07-10 11:00", '{"groups":{"eval":[[4,4,5,4,4,5],[5,4,4,5,4,4],[4,5,5,4,5,4],[3,4,4,3,4,3],[4,3,4,5,3,4]]}}'),
    ("Comparación v2.0 vs v1.1 — Ejecutividad", "ejecutividad", "version_prompt", "welch_t_test", "EJECUTANDO", 5, 4, "2025-07-21 10:00", '{"groups":{"v1.1":{"values":[3.5,4.0,3.8,4.2,3.9]},"v2.0":{"values":[4.5,4.8,4.6,4.7,4.9]}}}'),
    ("Comparación v1.0 vs v1.1 — Cobertura", "cobertura", "version_prompt", "welch_t_test", "COMPLETADO", 1, 0, "2025-06-22 16:00", '{"groups":{"v1.0":{"values":[3,3,4,3,4,3,3,4,3,3,4,3]},"v1.1":{"values":[4,4,5,4,4,5,4,4,5,4,4,4]}}}'),
    ("Comparación manual vs zoom2 — Tiempo", "tiempo_total", "condicion", "welch_t_test", "COMPLETADO", 2, 4, "2025-06-25 16:00", '{"groups":{"manual":{"values":[300,250,210,280,320,270,240,290]},"zoom2":{"values":[150,170,140,160,180,155,165,175]}}}'),
    ("Análisis SUS — Consistencia Interna", "sus_score", None, "cronbach_alpha", "PLANIFICADO", 3, 1, None, '{"groups":{"sus":[[4,2,5,2,4,2,4,2,5,2],[5,1,5,1,4,2,5,1,4,2],[4,3,4,3,3,3,4,3,4,3]]}}'),
]
for i, (nombre, var_res, var_grupo, prueba, estado, exp_idx, autor_idx, fexec, filtros) in enumerate(analyses):
    aid = uid("2", i+1)
    eid = f"'{uid('1', exp_idx+1)}'" if exp_idx is not None else "NULL"
    vg = f"'{var_grupo}'" if var_grupo else "NULL"
    fexec_str = f"'{fexec}:00-05'" if fexec else "NULL"
    comma = "," if i < len(analyses)-1 else ";"
    sql.append(f"('{aid}', {eid}, '{nombre}', NULL, '{var_res}', {vg}, 'INDEPENDIENTE', '{prueba}', '{prueba}', 0.05, 'HOLM', '{filtros}', '{{}}', '{estado}', '{users[autor_idx][0]}', {fexec_str}){comma}")
sql.append("")

# Analysis results
sql.append("-- 14. STATISTICAL ANALYSIS RESULTS")
sql.append("INSERT INTO statistical_analysis_results (analysis_id, resultado, descriptivos, supuestos, efecto, intervalos, advertencias, interpretacion) VALUES")
ar_data = [
    (0, 2.34, 0.028, "v1.1 produce fidelidad significativamente mayor que v1.0 (t=2.34, p=0.028)."),
    (1, 2.89, 0.012, "v1.1 produce claridad significativamente mayor (U=2.89, p=0.012)."),
    (2, 3.12, 0.008, "Método manual tiene precisión significativamente mayor que zoom2_base (t=3.12, p=0.008)."),
    (3, 4.21, 0.003, "Escala de evaluación muestra consistencia interna excelente (α=0.91)."),
    (5, 1.95, 0.042, "v1.1 produce cobertura significativamente mayor que v1.0 (t=1.95, p=0.042)."),
    (6, 5.67, 0.001, "Método manual es significativamente más lento que zoom2_base (t=5.67, p=0.001)."),
]
for i, (idx, stat, pval, interp) in enumerate(ar_data):
    aid = uid("2", idx+1)
    interp = interp.replace("'","''")
    mean_a = round(random.uniform(3.2, 4.2), 2)
    std_a = round(random.uniform(0.4, 0.8), 2)
    mean_b = round(mean_a + random.uniform(0.3, 1.2), 2)
    std_b = round(random.uniform(0.4, 0.7), 2)
    comma = "," if i < len(ar_data)-1 else ";"
    resultado = '{{"statistic": {}, "p_value": {}, "significant": true}}'.format(stat, pval)
    descriptivos = '{{"group_a":{{"mean":{},"std":{},"n":12}}, "group_b":{{"mean":{},"std":{},"n":12}}}}'.format(mean_a, std_a, mean_b, std_b)
    efecto = '{{"cohens_d": {}, "magnitude": "large"}}'.format(round(abs(mean_b-mean_a)/((std_a+std_b)/2), 2))
    sql.append(f"('{aid}', '{resultado}', '{descriptivos}', '{{}}', '{efecto}', '{{}}', '[]', '{interp}'){comma}")
sql.append("")

# SUS responses
sql.append("-- 15. SUS RESPONSES")
sql.append("INSERT INTO sus_responses (experiment_session_id, usuario_id, q1, q2, q3, q4, q5, q6, q7, q8, q9, q10, observaciones) VALUES")
sus_data = [
    (3, 0, [4,2,5,2,4,2,4,2,5,2], "Interfaz intuitiva. Tiempo de carga mejorable."),
    (3, 2, [5,1,5,1,4,2,5,1,4,2], "Muy fácil. Evaluaciones ciegas son buen feature."),
    (3, 3, [4,3,4,3,3,3,4,3,4,3], "Aceptable. Algunas funcionalidades no claras."),
    (3, 7, [5,1,4,1,5,1,5,1,5,1], "Excelente usabilidad. Nada que mejorar."),
    (3, 8, [3,3,3,3,3,3,3,3,3,3], "Neutral. No tengo opinión fuerte."),
    (3, 9, [4,2,4,2,4,2,4,2,4,2], "Bueno pero puede mejorar en velocidad."),
    (3, 10, [5,1,5,2,4,2,5,1,4,2], "Muy bueno para investigación."),
    (3, 11, [3,2,4,2,3,2,4,2,3,2], "Aceptable. Falta documentación."),
    (3, 5, [5,1,5,1,5,1,5,1,5,1], "Perfecto para uso diario."),
]
for i, (sidx, uidx, qs, obs) in enumerate(sus_data):
    eid = uid("1", sidx+1)
    obs = obs.replace("'","''")
    comma = "," if i < len(sus_data)-1 else ";"
    qstr = ",".join(str(q) for q in qs)
    sql.append(f"('{eid}', '{users[uidx][0]}', {qstr}, '{obs}'){comma}")
sql.append("")

# Time measurements
sql.append("-- 16. TIME MEASUREMENTS")
sql.append("INSERT INTO time_measurements (experiment_session_id, reunion_id, participante_id, condicion, tiempo_elaboracion_segundos, tiempo_revision_segundos, tiempo_total_segundos, errores_detectados) VALUES")
tm_data = [
    (0, 0, 2, "manual", 180, 120, 300, 1),
    (0, 1, 2, "manual", 150, 100, 250, 0),
    (1, 3, 2, "manual", 120, 90, 210, 0),
    (2, 2, 3, "zoom2_base", 90, 60, 150, 2),
    (2, 4, 3, "zoom2_base", 100, 70, 170, 1),
    (4, 11, 1, "manual", 140, 100, 240, 0),
    (4, 12, 4, "manual", 110, 80, 190, 1),
    (6, 8, 9, "zoom2_mejorado", 80, 55, 135, 0),
]
for i, (eidx, ridx, uidx, cond, t_elab, t_rev, t_tot, err) in enumerate(tm_data):
    eid = uid("1", eidx+1)
    rid = uid("b", ridx+1)
    uid_ = users[uidx][0]
    comma = "," if i < len(tm_data)-1 else ";"
    sql.append(f"('{eid}', '{rid}', '{uid_}', '{cond}', {t_elab}, {t_rev}, {t_tot}, {err}){comma}")
sql.append("")

# Task evaluation matches
sql.append("-- 17. TASK EVALUATION MATCHES")
sql.append("INSERT INTO task_evaluation_matches (reunion_id, ai_execution_id, reference_task_id, detected_task_id, resultado, similitud, validado_por, observaciones) VALUES")
tem_data = [
    (0, 0, 0, 0, "TP", 0.92, "Tarea detectada correctamente"),
    (0, 0, 1, 1, "TP", 0.87, "Variación en redacción"),
    (0, 0, 2, None, "FN", None, "Tarea no detectada"),
    (1, 1, 4, 3, "TP", 0.95, "Coincidencia casi perfecta"),
    (1, 1, 5, 4, "TP", 0.88, "Detectada con variación menor"),
    (4, 3, 11, 9, "TP", 0.90, "Detectada correctamente"),
    (5, 4, 12, None, "FN", None, "Tarea no detectada"),
]
for i, (ridx, eidx, fidx, didx, res, sim, obs) in enumerate(tem_data):
    bid = uid("b", ridx+1)
    eid = uid("e", eidx+1)
    fid = uid("f", fidx+1)
    did = f"'{uid('c', didx+1)}'" if didx is not None else "NULL"
    sim_str = str(sim) if sim else "NULL"
    obs = obs.replace("'","''")
    comma = "," if i < len(tem_data)-1 else ";"
    sql.append(f"('{bid}', '{eid}', '{fid}', {did}, '{res}', {sim_str}, '{users[2][0]}', '{obs}'){comma}")
sql.append("")

# Performance metrics
sql.append("-- 18. PERFORMANCE METRICS")
sql.append("INSERT INTO performance_metrics (reunion_id, ai_execution_id, componente, operacion, duracion_ms, exitoso, codigo_estado) VALUES")
pm_data = []
for i in range(10):
    bid = uid("b", i+1)
    eid = uid("e", i+1)
    for comp, op, dur in [("n8n","webhook_receive",random.randint(30,80)), ("openai","chat_completion",random.randint(1200,5200)), ("supabase","insert",random.randint(50,200))]:
        pm_data.append((bid, eid, comp, op, dur, True, "200"))
for i, (bid, eid, comp, op, dur, exitoso, code) in enumerate(pm_data):
    comma = "," if i < len(pm_data)-1 else ";"
    sql.append(f"('{bid}', '{eid}', '{comp}', '{op}', {dur}, {str(exitoso).lower()}, '{code}'){comma}")
sql.append("")

# Metricas n8n
sql.append("-- 19. METRICAS N8N")
sql.append("INSERT INTO metricas_n8n (endpoint, tiempo_respuesta, estado, fecha, codigo_estado, tamano_respuesta, outcome, is_terminal, data_source, started_at, completed_at, end_to_end_latency_seconds) VALUES")
n8n_endpoints = ["/api/v1/research/analyses", "/experiments/sessions", "/evaluations/summaries", "/prompts", "/auth/login", "/auth/me", "/reports"]
for i, ep in enumerate(n8n_endpoints):
    lat = round(random.uniform(0.03, 0.25), 2)
    dias = 14 - i
    comma = "," if i < len(n8n_endpoints)-1 else ";"
    sql.append(f"('{ep}', {lat}, 'success', NOW() - INTERVAL '{dias} days', 200, {random.randint(200,3500)}, 'success', true, 'production', NOW() - INTERVAL '{dias} days', NOW() - INTERVAL '{dias} days' + INTERVAL '{lat} seconds', {lat}){comma}")
sql.append("")

sql.append("-- ============================================================")
sql.append(f"-- FIN DEL SEED: {len(users)} usuarios, {len(meetings_data)} reuniones,")
sql.append(f"-- {len(tareas_data)} tareas, 14 resúmenes, 7 prompts,")
sql.append(f"-- 14 ejecuciones IA, 10 summary versions, 17 gold standards,")
sql.append(f"-- 7 experiment sessions, 8 análisis estadísticos, 7 resultados,")
sql.append(f"-- 9 SUS responses, 8 time measurements.")
sql.append("-- ============================================================")

with open("querys para supabase/seed_completo.sql", "w", encoding="utf-8") as f:
    f.write("\n".join(sql))

print(f"Seed generado: {len(sql)} líneas, {sum(len(l) for l in sql)} chars")
