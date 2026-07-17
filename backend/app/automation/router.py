"""
Router de automatización.

Envuelve las llamadas a los webhooks de n8n y registra las métricas.
"""

import time
import requests
from fastapi import APIRouter, Depends, Header, HTTPException, status, UploadFile, File, Form
from datetime import datetime

from app.automation.schemas import (
    CreateMeetingWebhookRequest,
    GenerateVirtualSummaryRequest,
    ChatRequest,
    SummaryCallbackPayload,
    ZoomRecordingRequest,
    SummaryJobStatus,
)
from app.services import summaries_service as summaries
from app.core.dependencies import get_current_user, get_current_admin
from app.core.supabase_client import SupabaseClient, get_supabase
from app.core.config import settings

router = APIRouter(prefix="/automation", tags=["Automatización"])

def registrar_metrica(sb: SupabaseClient, endpoint: str, tiempo_respuesta: float, estado: str, codigo_estado: int = None, reunion_id: str = None, tamano_respuesta: int = None, detalles: str = None):
    try:
        metrica = {
            'endpoint': endpoint,
            'tiempo_respuesta': tiempo_respuesta,
            'estado': estado,
            'fecha': datetime.now().isoformat(),
            'codigo_estado': codigo_estado,
            'reunion_id': reunion_id,
            'tamano_respuesta': tamano_respuesta,
            'detalles': detalles
        }
        sb.insert("metricas_n8n", [metrica])
    except Exception as e:
        print(f"Error registrando métrica: {e}")

@router.post("/meeting", summary="Crear reunión vía n8n webhook")
async def create_meeting_webhook(
    body: CreateMeetingWebhookRequest,
    user: dict = Depends(get_current_user),
    sb: SupabaseClient = Depends(get_supabase)
):
    if not settings.N8N_CREATE_MEETING_WEBHOOK_URL:
        raise HTTPException(status_code=500, detail="N8N_CREATE_MEETING_WEBHOOK_URL no configurado")
    
    payload = {
        "creador_id": str(user["id"]),
        "creador_correo": user["correo"],
        "borrador": {
            "tema": body.tema,
            "fecha_inicio": f"{body.fecha}T{body.hora}:00-05:00",
            "duracion_minutos": body.duracion_minutos,
            "tipo": "virtual",
            "direccion": None,
            "correos": body.participantes,
        },
    }
    
    inicio = time.time()
    try:
        resp = requests.post(settings.N8N_CREATE_MEETING_WEBHOOK_URL, json=payload, timeout=90)
        tiempo_respuesta = time.time() - inicio
        
        registrar_metrica(
            sb=sb,
            endpoint="crear_reunion",
            tiempo_respuesta=tiempo_respuesta,
            estado="éxito" if resp.status_code == 200 else "error",
            codigo_estado=resp.status_code,
            tamano_respuesta=len(resp.content) if resp.content else 0
        )
        
        if resp.status_code == 200:
            return resp.json() if resp.text else {"message": "Webhook ejecutado con éxito"}
        else:
            raise HTTPException(status_code=resp.status_code, detail=resp.text)
    except requests.exceptions.Timeout:
        registrar_metrica(sb, "crear_reunion", time.time() - inicio, "timeout")
        raise HTTPException(status_code=504, detail="Timeout contactando a n8n")
    except Exception as e:
        registrar_metrica(sb, "crear_reunion", time.time() - inicio, "error", detalles=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/summary/virtual", summary="Generar resumen virtual vía n8n webhook")
async def generate_virtual_summary(
    body: GenerateVirtualSummaryRequest,
    user: dict = Depends(get_current_user),
    sb: SupabaseClient = Depends(get_supabase)
):
    if not settings.N8N_RESUMEN_VIRTUAL_WEBHOOK_URL:
        raise HTTPException(status_code=500, detail="N8N_RESUMEN_VIRTUAL_WEBHOOK_URL no configurado")
    
    inicio = time.time()
    reunion_id = body.reunion_id
    
    try:
        resp = requests.post(settings.N8N_RESUMEN_VIRTUAL_WEBHOOK_URL, json={"reunion_id": reunion_id}, timeout=120)
        tiempo_respuesta = time.time() - inicio
        
        registrar_metrica(
            sb=sb,
            endpoint="resumen_virtual",
            tiempo_respuesta=tiempo_respuesta,
            estado="éxito" if resp.status_code == 200 else "error",
            codigo_estado=resp.status_code,
            reunion_id=reunion_id,
            tamano_respuesta=len(resp.content) if resp.content else 0
        )
        
        if resp.status_code == 200:
            data = resp.json()
            resumen_texto = data.get("resumen") or data.get("summary") or ""
            if resumen_texto:
                # Guardar el resumen en supabase
                sb.insert("resumenes", [{
                    "reunion_id": reunion_id,
                    "resumen": resumen_texto
                }])
                return {"message": "Resumen generado y guardado exitosamente.", "resumen": resumen_texto}
            else:
                raise HTTPException(status_code=500, detail="El flujo de n8n no devolvió un resumen válido.")
        else:
            raise HTTPException(status_code=resp.status_code, detail=resp.text)
    except requests.exceptions.Timeout:
        registrar_metrica(sb, "resumen_virtual", time.time() - inicio, "timeout", reunion_id=reunion_id)
        raise HTTPException(status_code=504, detail="Timeout contactando a n8n")
    except Exception as e:
        registrar_metrica(sb, "resumen_virtual", time.time() - inicio, "error", reunion_id=reunion_id, detalles=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/summary/presencial", summary="Procesar acta en PDF vía n8n webhook")
async def generate_presencial_summary(
    reunion_id: str = Form(...),
    file: UploadFile = File(...),
    user: dict = Depends(get_current_user),
    sb: SupabaseClient = Depends(get_supabase)
):
    """
    Envía un archivo PDF a n8n para su procesamiento OCR.
    La respuesta no incluye el resumen (es asíncrono). El frontend debe hacer polling.
    """
    if not settings.N8N_RESUMEN_PRESENCIAL_WEBHOOK_URL:
        raise HTTPException(status_code=500, detail="N8N_RESUMEN_PRESENCIAL_WEBHOOK_URL no configurado")
    
    inicio = time.time()
    
    try:
        files = {"data": (file.filename, await file.read(), file.content_type)}
        data_form = {"reunion_id": reunion_id, "nombre_archivo": file.filename}
        
        resp = requests.post(settings.N8N_RESUMEN_PRESENCIAL_WEBHOOK_URL, files=files, data=data_form, timeout=180)
        tiempo_respuesta = time.time() - inicio
        
        registrar_metrica(
            sb=sb,
            endpoint="resumen_presencial",
            tiempo_respuesta=tiempo_respuesta,
            estado="en_proceso" if resp.status_code == 200 else "error",
            codigo_estado=resp.status_code,
            reunion_id=reunion_id,
            tamano_respuesta=len(resp.content) if resp.content else 0
        )
        
        if resp.status_code == 200:
            return {"message": "Procesamiento iniciado. El resumen se guardará asíncronamente."}
        else:
            raise HTTPException(status_code=resp.status_code, detail=resp.text)
    except requests.exceptions.Timeout:
        registrar_metrica(sb, "resumen_presencial", time.time() - inicio, "timeout", reunion_id=reunion_id)
        raise HTTPException(status_code=504, detail="Timeout contactando a n8n")
    except Exception as e:
        registrar_metrica(sb, "resumen_presencial", time.time() - inicio, "error", reunion_id=reunion_id, detalles=str(e))
        raise HTTPException(status_code=500, detail=str(e))

# ------------------------------------------------------------------
# NUEVO: Módulo de resúmenes virtuales (audio manual + Zoom VTT)
# ------------------------------------------------------------------

@router.post(
    "/summary/recording",
    summary="Subir grabación manual y generar resumen (audio/vídeo)",
    status_code=status.HTTP_202_ACCEPTED,
)
async def create_summary_from_recording(
    reunion_id: str = Form(...),
    file: UploadFile = File(...),
    user: dict = Depends(get_current_user),
):
    """
    Recibe un archivo de audio/vídeo, lo sube a Supabase Storage y
    encola el procesamiento vía n8n. El frontend debe consultar el
    estado del trabajo mediante polling.
    """
    if not settings.N8N_RESUMEN_VIRTUAL_WEBHOOK_URL and not settings.N8N_PROCESS_RECORDING_WEBHOOK_URL:
        raise HTTPException(status_code=500, detail="Webhook de resumen no configurado")
    if not settings.SUPABASE_SERVICE_ROLE_KEY:
        raise HTTPException(status_code=500, detail="SUPABASE_SERVICE_ROLE_KEY no configurada")

    sb = get_supabase(service_role=True)

    # Evitar trabajos concurrentes en la misma reunión
    existing = summaries.get_active_job_for_meeting(sb, reunion_id)
    if existing and existing.get("estado") not in ("finalizado", "error", "cancelado"):
        return SummaryJobStatus(**existing)

    try:
        content = await file.read()
        job = summaries.create_job(sb, reunion_id, fuente="manual")
        path = summaries.upload_recording(sb, job["id"], file.filename or "audio.m4a", content, file.content_type or "audio/mpeg")
        url = sb.storage_create_signed_url(settings.SUPABASE_STORAGE_BUCKET, path, expires_in=3600 * 24)
        summaries.update_job(sb, job["id"], {
            "estado": "transcribiendo",
            "archivo_path": path,
            "archivo_url_publica": url,
        })
        summaries.send_to_n8n(sb, job["id"], reunion_id, url, "audio")
        return SummaryJobStatus(**job)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/summary/zoom-recording",
    summary="Obtener resumen desde grabación de Zoom (VTT o audio)",
    status_code=status.HTTP_202_ACCEPTED,
)
async def create_summary_from_zoom(
    body: ZoomRecordingRequest,
    user: dict = Depends(get_current_user),
):
    """
    Intenta obtener el transcript VTT nativo de Zoom. Si no existe,
    descarga el audio y lo envía a n8n para transcripción.
    """
    if not settings.ZOOM_ACCOUNT_ID or not settings.ZOOM_CLIENT_ID or not settings.ZOOM_CLIENT_SECRET:
        raise HTTPException(status_code=500, detail="Credenciales Zoom no configuradas")
    if not settings.SUPABASE_SERVICE_ROLE_KEY:
        raise HTTPException(status_code=500, detail="SUPABASE_SERVICE_ROLE_KEY no configurada")
    if not settings.N8N_RESUMEN_VIRTUAL_WEBHOOK_URL and not settings.N8N_PROCESS_RECORDING_WEBHOOK_URL:
        raise HTTPException(status_code=500, detail="Webhook de resumen no configurado")

    sb = get_supabase(service_role=True)

    existing = summaries.get_active_job_for_meeting(sb, body.reunion_id)
    if existing and existing.get("estado") not in ("finalizado", "error", "cancelado"):
        return SummaryJobStatus(**existing)

    try:
        # 1. Recuperar la reunión para obtener el id_externo (zoom meeting id)
        meeting_rows = sb.select(
            "reuniones",
            {"select": "id_externo", "id": f"eq.{body.reunion_id}"}
        )
        if not meeting_rows or not meeting_rows[0].get("id_externo"):
            raise HTTPException(status_code=400, detail="La reunión no tiene un id_externo de Zoom")
        zoom_meeting_id = meeting_rows[0]["id_externo"]

        # 2. Obtener grabaciones de Zoom
        recordings = summaries.get_zoom_recordings(zoom_meeting_id)
        files = recordings.get("recording_files", [])
        if not files:
            raise HTTPException(status_code=404, detail="No hay grabaciones disponibles para esta reunión")

        job = summaries.create_job(sb, body.reunion_id, fuente="zoom_vtt", zoom_meeting_id=zoom_meeting_id)
        token = summaries._get_zoom_token()
        vtt_url = summaries.find_zoom_transcript_url(files)

        if vtt_url:
            meeting_uuid = recordings.get("uuid", zoom_meeting_id)
            path = summaries.download_zoom_vtt(sb, job["id"], vtt_url, meeting_uuid, token)
            url = sb.storage_create_signed_url(settings.SUPABASE_STORAGE_BUCKET, path, expires_in=3600 * 24)
            summaries.update_job(sb, job["id"], {
                "estado": "generando",
                "archivo_path": path,
                "archivo_url_publica": url,
                "zoom_transcript_url": vtt_url,
            })
            summaries.send_to_n8n(sb, job["id"], body.reunion_id, url, "text")
            return SummaryJobStatus(**job)

        # 3. Fallback: audio
        audio_url = summaries.find_zoom_audio_url(files)
        if not audio_url:
            raise HTTPException(status_code=404, detail="No se encontró transcript ni audio de Zoom")

        audio_content = summaries.download_url(audio_url, headers={"Authorization": f"Bearer {token}"}, timeout=120)
        path = summaries.upload_recording(sb, job["id"], f"zoom_audio_{zoom_meeting_id}.m4a", audio_content, "audio/mp4")
        url = sb.storage_create_signed_url(settings.SUPABASE_STORAGE_BUCKET, path, expires_in=3600 * 24)
        summaries.update_job(sb, job["id"], {
            "estado": "transcribiendo",
            "archivo_path": path,
            "archivo_url_publica": url,
            "zoom_audio_url": audio_url,
        })
        summaries.send_to_n8n(sb, job["id"], body.reunion_id, url, "audio")
        return SummaryJobStatus(**job)

    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/summary/job/{reunion_id}",
    response_model=SummaryJobStatus,
    summary="Consultar estado del trabajo de resumen",
)
async def get_summary_job_status(
    reunion_id: str,
    user: dict = Depends(get_current_user),
):
    """Devuelve el estado del trabajo de resumen activo de una reunión."""
    sb = get_supabase(service_role=False)
    job = summaries.get_active_job_for_meeting(sb, reunion_id)
    if not job:
        raise HTTPException(status_code=404, detail="No hay trabajo de resumen para esta reunión")
    return SummaryJobStatus(**job)


@router.post(
    "/summary/callback",
    summary="Callback de n8n para entregar resumen y tareas",
    status_code=status.HTTP_200_OK,
)
async def summary_callback(
    payload: SummaryCallbackPayload,
    x_callback_secret: str = Header("", alias="X-Callback-Secret"),
):
    """Recibe el resultado del procesamiento de n8n y guarda resumen/tareas."""
    if not settings.N8N_CALLBACK_SECRET:
        raise HTTPException(status_code=500, detail="N8N_CALLBACK_SECRET no configurado")
    if x_callback_secret != settings.N8N_CALLBACK_SECRET:
        raise HTTPException(status_code=401, detail="Callback secret inválido")

    sb = get_supabase(service_role=True)
    job = summaries.get_job(sb, payload.job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Trabajo no encontrado")

    if job.get("estado") == "finalizado":
        return {"message": "El trabajo ya fue finalizado"}

    if payload.estado == "error":
        summaries.update_job(sb, job["id"], {
            "estado": "error",
            "error_detalle": payload.error_detalle or "Error desconocido",
        })
        return {"message": "Estado de error registrado"}

    try:
        summaries.save_summary_and_tasks(sb, job, payload.model_dump(exclude_unset=True))
        return {"message": "Resumen y tareas guardados"}
    except Exception as e:
        summaries.update_job(sb, job["id"], {
            "estado": "error",
            "error_detalle": str(e),
        })
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/summary/cleanup",
    summary="Eliminar grabaciones y trabajos de resumen expirados",
)
async def cleanup_summary_recordings(
    admin: dict = Depends(get_current_admin),
):
    """Elimina archivos de Storage y trabajos cuya expiración haya pasado."""
    sb = get_supabase(service_role=True)
    return summaries.cleanup_expired_recordings(sb)


@router.post("/chat", summary="Chatbot para crear reuniones vía n8n")
async def chat_webhook(
    body: ChatRequest,
    user: dict = Depends(get_current_user),
    sb: SupabaseClient = Depends(get_supabase)
):
    if body.accion == "cancelar":
        return {"estado": "cancelado", "respuesta": "Borrador descartado."}

    if body.accion == "confirmar":
        if not body.borrador:
            raise HTTPException(status_code=400, detail="No hay un borrador para confirmar.")
        webhook_url = settings.N8N_CREATE_MEETING_WEBHOOK_URL
        metric_endpoint = "confirmar_reunion_chat"
        payload = {
            "creador_id": str(user["id"]),
            "creador_correo": user["correo"],
            "borrador": body.borrador.model_dump(),
        }
    else:
        if not body.mensaje.strip():
            raise HTTPException(status_code=400, detail="Escribe una solicitud para generar el borrador.")
        webhook_url = settings.N8N_DRAFT_MEETING_WEBHOOK_URL
        metric_endpoint = "borrador_reunion_chat"
        payload = {
            "creador_id": str(user["id"]),
            "creador_correo": user["correo"],
            "mensaje": body.mensaje,
            "borrador": body.borrador.model_dump() if body.borrador else None,
        }

    if not webhook_url:
        raise HTTPException(
            status_code=500,
            detail="Webhook n8n no configurado para esta acción.",
        )
    
    inicio = time.time()
    try:
        resp = requests.post(webhook_url, json=payload, timeout=90)
        tiempo_respuesta = time.time() - inicio
        
        registrar_metrica(
            sb=sb,
            endpoint=metric_endpoint,
            tiempo_respuesta=tiempo_respuesta,
            estado="éxito" if resp.status_code == 200 else "error",
            codigo_estado=resp.status_code,
            tamano_respuesta=len(resp.content) if resp.content else 0
        )
        
        if resp.status_code == 200:
            if not resp.text.strip():
                raise HTTPException(status_code=500, detail="El webhook n8n devolvió una respuesta vacía. Verifica el workflow.")
            
            try:
                data = resp.json()
            except Exception:
                raise HTTPException(status_code=500, detail=f"El webhook n8n devolvió contenido inválido: {resp.text[:200]}")
            
            state = data.get("estado") or ("confirmada" if body.accion == "confirmar" else "borrador")
            meeting = data.get("meeting") or {}
            recipients = data.get("destinatarios") or []

            if state == "confirmada" and body.borrador:
                draft = body.borrador.model_dump()
                # A confirmation must retain the proposal fields even if an
                # automation response omits an optional value.
                meeting = {
                    **draft,
                    **{key: value for key, value in meeting.items() if value not in (None, "")},
                }
                if not recipients:
                    recipients = [
                        {"correo": user["correo"], "rol": "organizador"},
                        *[{"correo": correo, "rol": "participante"} for correo in draft["correos"]],
                    ]

            response = {
                "estado": state,
                "respuesta": data.get("respuesta") or (
                    "Reunión creada correctamente." if state == "confirmada" else "Revisa el borrador antes de confirmarlo."
                ),
                "meeting": meeting,
                "destinatarios": recipients,
            }
            return response
        else:
            raise HTTPException(status_code=resp.status_code, detail=resp.text)
    except HTTPException:
        raise
    except Exception as e:
        registrar_metrica(sb, metric_endpoint, time.time() - inicio, "error", detalles=str(e))
        raise HTTPException(status_code=500, detail=str(e))
