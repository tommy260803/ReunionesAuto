# MANUAL DE USUARIO - ZOOM2

**Versión:** 1.0  
**Fecha:** 2026-07-20  
**Sistema:** ReunionesAuto - Sistema de Gestión de Reuniones y Análisis Estadístico

---

## TABLA DE CONTENIDOS

1. [Introducción](#introducción)
2. [Requisitos del Sistema](#requisitos-del-sistema)
3. [Acceso al Sistema](#acceso-al-sistema)
4. [Dashboard Principal](#dashboard-principal)
5. [Módulo de Investigación](#módulo-de-investigación)
6. [Análisis Estadísticos](#análisis-estadísticos)
7. [Sesiones Experimentales](#sesiones-experimentales)
8. [Evaluaciones](#evaluaciones)
9. [Prompts](#prompts)
10. [Gold Standard](#gold-standard)
11. [Reportes](#reportes)
12. [Evaluación Ciega](#evaluación-ciega)
13. [Cuestionario SUS](#cuestionario-sus)
14. [Solución de Problemas](#solución-de-problemas)

---

## INTRODUCCIÓN

ReunionesAuto es un sistema integral para la gestión automática de reuniones Zoom, análisis estadístico de datos y evaluación científica de resúmenes generados por IA. Este manual proporciona instrucciones detalladas para utilizar todas las funcionalidades del sistema.

### Características Principales
- Gestión de reuniones y participantes
- Generación automática de resúmenes
- Análisis estadísticos avanzados
- Evaluación ciega de resúmenes
- Gestión de sesiones experimentales
- Generación de reportes en múltiples formatos
- Visualizaciones interactivas

---

## REQUISITOS DEL SISTEMA

### Navegadores Soportados
- Google Chrome (última versión)
- Mozilla Firefox (última versión)
- Safari (última versión)
- Microsoft Edge (última versión)

### Requisitos de Conexión
- Conexión a internet estable
- Acceso a Supabase (base de datos)
- Acceso a n8n (automatización)

---

## ACCESO AL SISTEMA

### Inicio de Sesión

1. Navegue a `http://localhost:3000` (o la URL de producción)
2. Haga clic en "Iniciar Sesión"
3. Ingrese su correo electrónico
4. Ingrese su contraseña
5. Haga clic en "Ingresar"

### Credenciales de Prueba

**Administrador:**
- Email: juanaureliodelacruzgamarra@gmail.com
- Password: password123

### Recuperación de Contraseña
Si olvidó su contraseña:
1. Haga clic en "¿Olvidaste tu contraseña?"
2. Ingrese su correo electrónico
3. Siga las instrucciones enviadas a su correo

---

## DASHBOARD PRINCIPAL

El dashboard principal proporciona una vista general de todas las actividades del sistema.

### Secciones del Dashboard
- **Reuniones Recientes:** Lista de las últimas reuniones programadas
- **Tareas Pendientes:** Tareas asignadas al usuario
- **Estadísticas:** Resumen de reuniones, resúmenes y participantes
- **Acciones Rápidas:** Botones para acciones comunes

### Navegación
Use el menú lateral para navegar entre las diferentes secciones:
- Reuniones
- Participantes
- Tareas
- Resúmenes
- Métricas
- Investigación (requiere rol INVESTIGADOR o ADMIN)

---

## MÓDULO DE INVESTIGACIÓN

El módulo de investigación está diseñado para investigadores y administradores que realizan análisis estadísticos y evaluaciones científicas.

### Acceso al Módulo
1. Haga clic en "Investigación" en el menú lateral
2. Solo usuarios con rol INVESTIGADOR o ADMIN pueden acceder

### Dashboard de Investigación
El dashboard de investigación muestra:
- **Análisis Estadísticos:** Número total de análisis creados
- **Experimentos:** Número de sesiones experimentales
- **Evaluaciones:** Número de evaluaciones realizadas
- **Prompts:** Número de versiones de prompts
- **Gold Standard:** Número de tareas de referencia
- **Reportes:** Número de reportes generados

---

## ANÁLISIS ESTADÍSTICOS

### Crear un Nuevo Análisis

1. Navegue a `/research/analyses/new`
2. Complete el formulario:
   - **Nombre:** Nombre descriptivo del análisis
   - **Objetivo:** Descripción del objetivo del análisis
   - **Variable de Resultado:** Variable a analizar (ej: calidad_resumen)
   - **Variable de Agrupación:** Variable para agrupar datos (ej: version_prompt)
   - **Diseño:** Tipo de diseño (INDEPENDIENTE, PAREADO, MEDIDAS_REPETIDAS)
   - **Prueba Estadística:** Seleccione una prueba específica o deje vacío para selector automático
   - **Nivel de Significancia (α):** Valor alfa (default: 0.05)
   - **Corrección Múltiple:** Método de corrección (HOLM, BONFERRONI, NONE)
3. Haga clic en "Crear Análisis"

### Ver Resultados de Análisis

1. Navegue a `/research/analyses`
2. Haga clic en el análisis deseado
3. La página de detalle muestra:
   - Información del análisis
   - Resultados estadísticos
   - Visualizaciones (BoxPlot, Matriz de Confusión)
   - Interpretación del resultado

### Reejecutar un Análisis

1. Navegue a la página de detalle del análisis
2. Haga clic en "Reejecutar"
3. El análisis se ejecutará nuevamente con los mismos parámetros

### Selector Automático de Prueba Estadística

Si no selecciona una prueba específica, el sistema automáticamente seleccionará la prueba estadística apropiada basándose en:
- Tipo de variable (continua, ordinal, binaria)
- Número de condiciones/grupos
- Diseño del estudio (independiente, pareado, medidas repetidas)
- Tamaño de muestra
- Normalidad y varianzas (si se conocen)

---

## SESIONES EXPERIMENTALES

### Crear una Nueva Sesión Experimental

1. Navegue a `/research/experiments/new`
2. Complete el formulario:
   - **Nombre:** Nombre de la sesión experimental
   - **Descripción:** Descripción del experimento
   - **Estado:** Estado inicial (PLANIFICADO, ACTIVO)
3. Haga clic en "Crear Sesión"

### Gestionar una Sesión Experimental

1. Navegue a `/research/experiments`
2. Haga clic en la sesión deseada
3. Acciones disponibles:
   - **Iniciar Sesión:** Cambia el estado a ACTIVO
   - **Finalizar Sesión:** Cambia el estado a COMPLETADO
   - **Ver Análisis Asociados:** Muestra análisis relacionados
   - **Ver Evaluaciones:** Muestra evaluaciones relacionadas

### Cuestionario SUS

Para evaluar la usabilidad del sistema:
1. Navegue a `/research/experiments/[id]/sus`
2. Responda las 10 preguntas usando la escala 1-5
3. Haga clic en "Enviar Cuestionario"
4. El sistema calculará automáticamente la puntuación SUS (0-100)

**Interpretación de Puntuación SUS:**
- 85-100: Excelente
- 70-84: Bueno
- 50-69: Aceptable
- 35-49: Pobre
- 0-34: Muy pobre

---

## EVALUACIONES

### Ver Evaluaciones

1. Navegue a `/research/evaluations`
2. La tabla muestra todas las evaluaciones con:
   - ID de la evaluación
   - ID del resumen evaluado
   - Puntuación total
   - Estado
   - Fecha de evaluación

### Evaluación Ciega

Para realizar una evaluación ciega de un resumen:
1. Navegue a `/research/evaluations/blind`
2. Ingrese el ID del resumen a evaluar
3. Haga clic en "Cargar"
4. Evalúe el resumen usando los criterios (1-10):
   - Calidad General
   - Precisión
   - Completitud
   - Claridad
5. Agregue comentarios adicionales
6. Haga clic en "Guardar Evaluación"

**Instrucciones de Evaluación Ciega:**
- Evalúe basándose únicamente en calidad y contenido
- No intente identificar qué prompt generó el resumen
- Use la escala 1-10 (1 = muy pobre, 10 = excelente)
- Sea objetivo y consistente

---

## PROMPTS

### Ver Versiones de Prompts

1. Navegue a `/research/prompts`
2. La tabla muestra todas las versiones de prompts con:
   - ID de la versión
   - Nombre
   - Versión
   - Estado (ACTIVO, INACTIVO)
   - Fecha de creación

### Crear Nueva Versión de Prompt

1. Haga clic en "Crear Nueva Versión"
2. Complete el formulario con:
   - Nombre del prompt
   - Contenido del prompt
   - Versión
   - Estado
3. Haga clic en "Guardar"

---

## GOLD STANDARD

### Ver Tareas de Referencia

1. Navegue a `/research/gold-standard`
2. La tabla muestra todas las tareas de referencia con:
   - ID de la tarea
   - Descripción
   - Estado de validación
   - Fecha de creación

### Crear Nueva Tarea de Referencia

1. Haga clic en "Crear Nueva Tarea"
2. Complete el formulario con:
   - Descripción de la tarea
   - Respuesta de referencia
   - Criterios de evaluación
3. Haga clic en "Guardar"

---

## REPORTES

### Ver Reportes Generados

1. Navegue a `/research/reports`
2. La tabla muestra todos los reportes con:
   - ID del reporte
   - Tipo
   - Formato
   - Estado
   - Fecha de generación

### Exportar Análisis

1. Navegue a la página de detalle del análisis
2. Seleccione el formato deseado (PDF, Word, Excel)
3. Haga clic en "Exportar"
4. El archivo se descargará automáticamente

### Exportar Sesión Experimental

1. Navegue a la página de detalle de la sesión
2. Seleccione el formato deseado (PDF, Word, Excel)
3. Haga clic en "Exportar"
4. El archivo se descargará automáticamente

---

## SOLUCIÓN DE PROBLEMAS

### Problemas Comunes

**No puedo acceder al módulo de investigación**
- Verifique que tiene rol INVESTIGADOR o ADMIN
- Contacte al administrador si necesita acceso

**El análisis no se ejecuta**
- Verifique que los datos son válidos
- Revise los mensajes de error en la página de detalle
- Intente reejecutar el análisis

**No puedo ver los gráficos**
- Verifique que los resultados están disponibles
- Asegúrese de que hay datos descriptivos en los resultados
- Recargue la página

**El reporte no se descarga**
- Verifique que las dependencias de reportes están instaladas
- Contacte al administrador si el problema persiste

### Contacto de Soporte

Para problemas técnicos:
- Email: soporte@reunionesauto.com
- Horario: Lunes a Viernes, 9:00 - 18:00

---

## APÉNDICE

### Glosario

- **ANOVA:** Análisis de Varianza
- **BoxPlot:** Diagrama de caja para visualizar distribución de datos
- **Matriz de Confusión:** Tabla que muestra el desempeño de un modelo de clasificación
- **SUS:** System Usability Scale - Cuestionario de usabilidad estándar
- **RLS:** Row Level Security - Seguridad a nivel de fila en base de datos
- **E2E:** End-to-End - Pruebas de extremo a extremo

### Referencias

- Documentación de FastAPI: https://fastapi.tiangolo.com/
- Documentación de Next.js: https://nextjs.org/docs
- Documentación de Supabase: https://supabase.com/docs

---

**Fin del Manual de Usuario**
