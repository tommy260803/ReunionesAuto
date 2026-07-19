# Documentación de Migración de Zoom2

Este documento resume todo el proceso de migración de la aplicación monolítica **Zoom2** (originalmente construida en Streamlit) hacia una arquitectura moderna, escalable y dividida en **Backend (FastAPI)** y **Frontend (Next.js)**.

---

## 1. Análisis de Arquitectura Inicial
La aplicación original (`app.py`) consistía en más de 3,000 líneas de código en Streamlit, mezclando interfaz de usuario, lógica de negocio, consultas HTTP (REST) directas a Supabase y generación de reportes PDF. 

**Objetivo de la migración:** Desacoplar la aplicación en dos capas independientes para mejorar el rendimiento, escalabilidad, mantenibilidad y brindar una experiencia de usuario (UI/UX) mucho más moderna.

---

## 2. Desarrollo del Backend (FastAPI)
Se construyó un servidor API RESTful completamente nuevo bajo el directorio `/backend`, encargado exclusivamente de manejar la lógica de negocio, autenticación y base de datos.

### Fases Completadas:
- **Estructura Base y Seguridad:** Implementación de JWT (JSON Web Tokens) y hashing de contraseñas (`passlib/bcrypt`).
- **Cliente Supabase Personalizado:** En lugar de usar un SDK pesado, se construyó un cliente REST genérico `SupabaseClient` (`core/supabase_client.py`) que replica el comportamiento original y centraliza todas las consultas HTTP (`GET`, `POST`, `PATCH`, `DELETE`).
- **Módulos CRUD (Routers):**
  - `auth`: Registro, Login y validación de usuarios.
  - `users`: Gestión de perfiles y permisos (Admin check).
  - `meetings`: Creación, listado y actualización de reuniones.
  - `participants`: Asignación y estados de invitación.
  - `tasks`: Creación y seguimiento de compromisos.
- **Automatización (n8n):** Integración nativa de webhooks de n8n para:
  - Generación de resúmenes virtuales.
  - Generación de resúmenes presenciales (multipart/form-data con carga de PDFs).
  - Chatbot conversacional para agendar reuniones automáticas.
- **Métricas:** Endpoints operativos e inferenciales (`/tasks/metrics`, `/metrics/n8n`, `/metrics/n8n/stats` y `/metrics/n8n/statistics`). La telemetría inferencial utiliza una fila por invocación, cohorte productiva y pruebas Welch/Chi-cuadrado/Fisher.
- **Reportes en PDF:** Migración exitosa de la lógica de pandas/reportlab a FastAPI (`/reports/`), generando streams en memoria (`BytesIO`) en lugar de archivos físicos.

---

## 3. Desarrollo del Frontend (Next.js)
Se construyó un cliente interactivo y estético bajo el directorio `/frontend`, utilizando las últimas tecnologías web.

### Stack Tecnológico:
- **Framework:** Next.js (App Router, Server/Client components).
- **Lenguaje:** TypeScript estricto.
- **Estilos:** Tailwind CSS v4 con tokens CSS semánticos, tema persistente y una estética de *command center* empresarial.
- **Componentes & Iconos:** Lucide-React y utilidades clsx/tailwind-merge.
- **Gráficos:** Recharts.

### Fases Completadas:
- **Autenticación (Context API):** Implementación de `AuthContext` y cliente genérico de `axios` con interceptores para inyectar y validar el token JWT desde las Cookies en cada petición.
- **Vistas Públicas:** Interfaces rediseñadas para `/login` y `/register`.
- **Layout Global:** Shell responsivo con sidebar navy colapsable, header operativo, navegación mobile-first y `Asistente IA` como primera herramienta operativa después de Dashboard.
- **Tema visual:** Toggle claro/oscuro persistido en `localStorage` bajo la clave `zoom2.theme`. El tema se aplica antes de la hidratación para reducir parpadeos, sin afectar `AuthContext`, `ChatContext` ni lógica de negocio.
- **Sistema de diseño:** Superficies, tablas, formularios, badges, alertas, skeletons, focus rings y animaciones se centralizan en `globals.css`. Mantiene contraste accesible, soporte de `prefers-reduced-motion` y tamaños funcionales de texto de al menos 14px.
- **Dashboard (`/dashboard`):** Panel de control resumiendo KPIs de tareas e integrando Recharts (Gráfico circular para Tareas y Gráfico de barras para métricas del tiempo de respuesta de n8n).
- **Gestión de Reuniones (`/meetings` y `/participants`):** Tablas dinámicas con insignias de estado. Los administradores pueden editar o eliminar reuniones, y modificar el correo y rol de participantes antes de guardar los cambios.
- **Tareas (`/tasks`):** Tablero Kanban, vista de grilla editable y panel de métricas con Recharts. Se normalizó el estado de progreso como `en_progreso` para coincidir con los datos de Supabase.
- **Exportación PDF:** Los administradores pueden descargar reportes de usuarios y tareas desde la interfaz. Los PDFs se generan en el backend con ReportLab y se transmiten en memoria.
- **Automatización (`/summaries` y `/chat`):** 
- Interfaz de arrastrar y soltar (Drag & Drop) para subir actas PDF de manera fluida.
- Generación de resúmenes IA a un clic.
- Chat guiado con borrador editable: el asistente interpreta solicitudes y cambios posteriores antes de crear la reunión.
- Tarjeta estructurada con tema, fecha, duración, tipo, dirección, enlace e invitados. La creación en Zoom y Supabase ocurre solo mediante la confirmación explícita.
- El historial y el borrador se conservan en `sessionStorage` por usuario durante la sesión del navegador, incluso al navegar entre módulos.
- La vista de resúmenes organiza las reuniones en tres columnas fijas: Virtuales, Presenciales y Mixtas.
- **Auditoría n8n (`/metrics`):** Panel exclusivo de administración con KPIs, línea de actividad de siete días, latencia por endpoint y tabla de logs detallados.
- **Command Center UI:** Dashboard, métricas y chat incorporan retícula técnica sutil, señales de telemetría, paneles de profundidad y estados operativos. Es un reskin de presentación: no modifica rutas, endpoints, Contexts de negocio ni handlers existentes.
- **Integridad de invitados:** La creación por chat transmite el ID y correo del creador a n8n. El workflow registra siempre al creador como `organizador` y utiliza una RPC de Supabase para insertar la reunión y todos los participantes en una sola transacción.
- **Recuperación manual:** El administrador puede agregar invitados desde `/participants` para reparar reuniones históricas que no tengan registros de participantes.

---

## 4. Instrucciones de Ejecución
La plataforma está lista para uso en producción o desarrollo continuo.

### Backend:
```bash
cd backend
..venv\Scripts\Activate
python -m uvicorn app.main:app --reload --port 8000
```

### Frontend:
```bash
cd frontend
npm run dev
# Se ejecuta en http://localhost:3000
```

---

## 5. Endpoints Incorporados en la Finalización

| Método | Ruta | Propósito | Acceso |
| :--- | :--- | :--- | :--- |
| `DELETE` | `/meetings/{meeting_id}` | Elimina una reunión. | Administrador |
| `GET` | `/reports/users/pdf` | Descarga el reporte de usuarios. | Administrador |
| `GET` | `/reports/tasks/pdf` | Descarga el reporte de tareas. | Administrador |
| `GET` | `/metrics/n8n` | Consulta el historial de métricas de n8n. | Administrador |
| `GET` | `/metrics/n8n/stats` | Consulta KPIs, agregados y últimos 50 logs de n8n. | Administrador |
| `GET` | `/metrics/n8n/statistics` | Compara dos periodos de un mismo flujo con Welch y Chi-cuadrado/Fisher. | Administrador |

Los endpoints existentes `PATCH /meetings/{meeting_id}`, `PATCH /participants/{participant_id}` y `PATCH /tasks/{task_id}` son los utilizados por las nuevas ediciones en pantalla.

---

## 6. Despliegue del Flujo de Invitados

Antes de usar el workflow de creación de reuniones actualizado:

1. Ejecutar `querys para supabase/query6_reuniones_participantes.sql` en el editor SQL de Supabase, después de `query5_metricas.txt`.
2. Reimportar `json n8n/AsistenteIA1.json` en n8n y configurar nuevamente sus credenciales si la instancia lo solicita.
3. Comprobar que la URL de Supabase configurada en n8n corresponde al mismo proyecto que utiliza el backend.
4. Crear una reunión mediante el chat. Debe aparecer el creador con rol `organizador` y los correos invitados con rol `participante` en `/participants`.

La RPC `crear_reunion_con_participantes` evita que una falla al insertar participantes deje una reunión persistida sin registros asociados. La respuesta del webhook se entrega tras la inserción transaccional y no depende del envío de correo electrónico.

---

## 7. Despliegue del Chat con Borradores

1. Importar `json n8n/BorradorReunionChat.json` y configurar la credencial o clave de Groq.
2. Reimportar `json n8n/AsistenteIA1.json`; este workflow ahora solo confirma borradores y crea la reunión.
3. Agregar `N8N_DRAFT_MEETING_WEBHOOK_URL=https://<instancia-n8n>/webhook/borrador-reunion-chat` al archivo `.env` de la raíz.
4. Reiniciar FastAPI para cargar la nueva variable de entorno.
5. En `/chat`, crear un borrador, modificarlo mediante mensajes sucesivos y usar **Confirmar reunión**. Solo entonces se crea la reunión, participantes e invitaciones.

`BorradorReunionChat` contiene el nodo Groq. No se debe conectar Groq dentro de `AsistenteIA1`: su flujo debe iniciar directamente como `Webhook → Code in JavaScript → ... → Create a meeting`.

El borrador conserva invitados cuando solo se cambia fecha, hora, duración, tipo, tema o dirección. Los correos se agregan, reemplazan o eliminan únicamente cuando la instrucción lo indica explícitamente. La interfaz conserva versiones del borrador en la sesión: **Restaurar anterior** deshace el último cambio y **Cancelar borrador** elimina el borrador completo.

La respuesta confirmada se normaliza en el nodo `Preparar respuesta confirmada` después de la RPC de Supabase. Este nodo admite respuestas directas, arrays u objetos envueltos de PostgREST. FastAPI usa el borrador como respaldo, por lo que la tarjeta final conserva tema, fecha/hora, duración, tipo, dirección e invitados aunque n8n omita un campo opcional.

---

## 8. Reskin Command Center

El reskin se limita a la capa de presentación de Next.js. No modifica rutas, endpoints, autenticación, persistencia de chat, borradores, confirmación de reuniones ni contratos de API.

- **Identidad:** Sidebar `#0F172A` en claro y `#020617` en oscuro; contenido de alta legibilidad con superficies claras y tokens semánticos para éxito, advertencia, interacción y error.
- **Shell:** Sidebar con rail activo animado, estado operativo, modo colapsado en escritorio y drawer accesible en móvil. El header incluye el estado de servicios y el toggle de tema.
- **Telemetría:** Dashboard y métricas usan tarjetas de telemetría, paneles analíticos, grids sutiles y tooltips tematizados para Recharts.
- **Chat:** Se presenta como consola operativa; conserva el historial, borradores, restauración, confirmación y cancelación existentes. Su altura descuenta el header correspondiente en móvil y escritorio para evitar scroll global u ocultar el primer mensaje.
- **Accesibilidad y movimiento:** Focus visible, contraste mejorado, feedback de carga existente con estilo unificado y reducción de animaciones al detectar `prefers-reduced-motion`.

Archivos principales de presentación modificados:

- `frontend/src/app/globals.css`
- `frontend/src/components/ui/ThemeToggle.tsx`
- `frontend/src/app/layout.tsx`
- `frontend/src/app/(dashboard)/layout.tsx`
- `frontend/src/app/(dashboard)/dashboard/page.tsx`
- `frontend/src/app/(dashboard)/metrics/page.tsx`
- `frontend/src/app/(dashboard)/chat/page.tsx`
- `frontend/src/app/login/page.tsx`
- `frontend/src/app/register/page.tsx`
- `frontend/src/app/page.tsx`

---

## 9. Verificación Realizada

- `python -m compileall app` en `/backend`: correcto.
- `npm run build` en `/frontend`: correcto.
- `git diff --check`: correcto.
- El JSON de `AsistenteIA1.json` fue validado con `JSON.parse`.
- El JSON de `BorradorReunionChat.json` fue validado con `JSON.parse`.
- La topología de confirmación de `AsistenteIA1` fue validada para ejecutar `Preparar respuesta confirmada` después de la RPC de Supabase.

Next.js detecta dos archivos `package-lock.json` en directorios distintos y muestra una advertencia sobre la raíz de Turbopack. La compilación no se ve afectada.

---

## 10. Despliegue De Métricas Inferenciales

1. Ejecutar `querys para supabase/query8_metricas_inferenciales.sql` después de `query7_resumenes_modulo.sql`.
2. Configurar `SUPABASE_SERVICE_ROLE_KEY`, `N8N_WORKFLOW_VERSION`, `N8N_CALLBACK_SECRET` y `BACKEND_PUBLIC_URL` en el backend.
3. Reiniciar FastAPI para iniciar la cohorte productiva limpia.
4. Reimportar workflows modificados si se cambia el contrato de callback de n8n.
5. Verificar una invocación síncrona y una asíncrona antes de recolectar datos del artículo.
6. No ejecutar el seed de demostración en la base usada para evidencia empírica.

Los registros anteriores a la migración quedan marcados como `legacy`. El panel inferencial solo analiza `production` por defecto y permite seleccionar `demo` con una advertencia explícita.

¡Todo el sistema ha sido migrado exitosamente con una mejora drástica en arquitectura y apariencia visual!
