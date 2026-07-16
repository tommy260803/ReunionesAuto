# Especificación Técnica: Módulo de Resúmenes Virtuales (Zoom + n8n)

Este documento detalla la arquitectura y el plan de implementación sugerido para el procesamiento automático de resúmenes de reuniones virtuales y mixtas grabadas en Zoom. La meta es crear un sistema robusto, asíncrono y resiliente a fallos.

---

## 1. Objetivo Arquitectónico
Implementar un sistema capaz de generar resúmenes mediante Inteligencia Artificial a partir de reuniones de Zoom, priorizando el uso de transcripciones nativas de Zoom (`.vtt`) para ahorrar costos de procesamiento y delegando la transcripción por audio (Whisper) solo como un método de respaldo (fallback).

El flujo ideal propuesto es:
`Zoom finaliza reunión` ➔ `Genera grabación y VTT` ➔ `Webhook dispara a Backend/n8n` ➔ `Procesa VTT limpio (o extrae Audio)` ➔ `IA Resume (por bloques si es muy larga)` ➔ `Guarda en Supabase`.

---

## 2. Fases de Implementación Recomendadas

Para no bloquear el desarrollo, se recomienda implementar las siguientes fases en orden secuencial:

### Fase 1: MVP Manual (El Respaldo de Audio)
*Sirve para tener un sistema funcional de inmediato y cubre los casos donde Zoom falla al generar el VTT.*
1. **Frontend (`/summaries`):** Agregar botón/zona para subir el archivo de audio de la reunión (permitir formatos comprimidos como `.m4a` o `.mp3`, evitar `.wav` por su gran peso).
2. **Backend (FastAPI):**
   - **NO** enviar el audio crudo directamente a n8n por HTTP (causa timeouts o Payload Too Large).
   - El endpoint `POST /automation/summary/recording` debe recibir el archivo, subirlo a un bucket de **Supabase Storage** y luego hacer un trigger a n8n enviándole la URL pública del archivo.
3. **n8n Workflow:** Descarga el audio desde la URL, lo manda a transcribir (ej. Groq / Whisper API), extrae el texto, genera el resumen con un LLM y lo inserta en la tabla `resumenes`.
4. **UI Updates:** Mantener la estrategia actual de *Polling* en el frontend para mostrar estados: *Subiendo ➔ Transcribiendo ➔ Generando Resumen ➔ Finalizado*.

### Fase 2: Extracción Nativa del Transcript (VTT de Zoom)
*Permite ahorrar miles de tokens y costos de API al aprovechar que Zoom ya transcribió la reunión gratis.*
1. **Verificación Previa:** Confirmar que la cuenta de Zoom (Account Settings > Recording) tiene activo "Audio Transcript" y "Cloud Recording".
2. **Endpoint FastAPI:** Crear `POST /automation/summary/zoom-recording` que reciba el `zoom_meeting_id`.
3. **Petición a Zoom API:** Hacer un `GET /v2/meetings/{zoom_meeting_id}/recordings`.
4. **Lógica de Extracción:**
   - Iterar sobre `recording_files`. Buscar el archivo donde `file_type === "TRANSCRIPT"` o `file_extension === "VTT"`.
   - Si **NO** existe: Detonar el proceso de la Fase 1 (descargar el `.m4a` del array).
   - Si **SÍ** existe: Descargar el archivo `.vtt`.
5. **Limpieza del VTT (Crucial):**
   - Los archivos `.vtt` contienen ruido (`WEBVTT`, timestamps como `00:01:23.000 --> 00:01:25.000`, IDs numéricos).
   - **Instrucción para el desarrollador:** Crear una función con Expresiones Regulares (Regex) en Python (backend) o JavaScript (n8n) para limpiar ese ruido y dejar solo un script puro (Ej: `Juan: Hola equipo`).
6. Enviar texto limpio al LLM para resumir.

### Fase 3: Automatización Asíncrona (Webhooks de Zoom)
*Para que el resumen aparezca por "arte de magia" sin que el usuario apriete ningún botón.*
1. Configurar una App en el Marketplace de Zoom con los Event Subscriptions: `recording.completed` y `recording.transcript_completed`.
2. Apuntar el Webhook hacia una ruta del Backend o hacia un webhook de n8n.
3. **Lógica de espera:** A veces el webhook de *grabación completada* llega minutos antes que el de *transcript completado*. Si llega el primero y no hay VTT, programar un reintento (delay loop de 3-5 minutos) antes de rendirse y procesar por audio (Fase 1).

### Fase 4: Chunks para Reuniones Largas (>45 minutos)
*Evitar el error de exceder el límite de tokens de la IA o que la IA "alucine" o pierda el hilo en reuniones de 1 o 2 horas.*
1. **Lógica de "Overlapping Chunks" (Bloques Solapados):**
   - No cortar el texto por minutos exactos, sino por longitud de caracteres (ej. 4,000 caracteres por bloque).
   - **Crucial:** Para que la IA no pierda contexto a mitad de una frase, el bloque 2 debe solaparse un poco con el final del bloque 1 (ej. si el Bloque 1 va de 0 a 4000, el Bloque 2 empieza en 3800 a 7800).
2. Mapear cada bloque pasándolo por un prompt de extracción (`Extrae puntos clave, tareas y decisiones de esta parte de la reunión`).
3. Agrupar todas las respuestas parciales y pasarlas por un prompt final (`Redacta un resumen corporativo unificado a partir de estos fragmentos`).

---

## 3. Modelo de Datos (Sugerencia)
Para hacer la auditoría escalable y saber por qué falló un proceso en reuniones asíncronas, se recomienda agregar al menos estas tablas (o adaptar la actual de resúmenes):

- `grabaciones_reuniones`: Guarda el estado del procesamiento (`reunion_id`, `zoom_meeting_id`, `estado_transcript: pendiente/vtt/audio`, `url_descarga_temporal`).
- `resumenes_bloques` (Opcional para Fase 4): Para guardar los resúmenes temporales de cada chunk antes del resumen final y evitar reprocesar todo si la API del LLM falla a la mitad de una reunión de 2 horas.
