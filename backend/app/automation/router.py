"""
Router de automatización.

Envuelve las llamadas a los webhooks de n8n y registra las métricas.
"""

import requests
from fastapi import APIRouter, Depends, Header, HTTPException, status, UploadFile, File, Form

from app.automation.schemas import (
    CreateMeetingWebhookRequest,
    GenerateVirtualSummaryRequest,
    ChatRequest,
    SummaryCallbackPayload,
    ZoomRecordingRequest,
    SummaryJobStatus,
)
from app.services import summaries_service as summaries
from app.services.metrics_service import (
    finalize_async_invocation,
    finalize_invocation,
    start_invocation,
)
from app.core.dependencies import get_current_user, get_current_admin
from app.core.supabase_client import SupabaseClient, get_supabase
from app.core.config import settings

router = APIRouter(prefix="/automation", tags=["Automatización"])

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
    
    invocation = start_invocation(sb, "crear_reunion")
    resp = None
    transport_latency = None
    try:
        resp = requests.post(settings.N8N_CREATE_MEETING_WEBHOOK_URL, json=payload, timeout=90)
        transport_latency = invocation.elapsed()
        response_size = len(resp.content) if resp.content else 0

        if not 200 <= resp.status_code < 300:
            finalize_invocation(
                invocation,
                "error",
                status_code=resp.status_code,
                response_size=response_size,
                transport_latency_seconds=transport_latency,
                details=resp.text[:1000] or "n8n rechazó la solicitud.",
            )
            raise HTTPException(status_code=resp.status_code, detail=resp.text)

        if resp.text.strip():
            try:
                result = resp.json()
            except ValueError:
                detail = f"El webhook n8n devolvió contenido inválido: {resp.text[:200]}"
                finalize_invocation(
                    invocation,
                    "error",
                    status_code=resp.status_code,
                    response_size=response_size,
                    transport_latency_seconds=transport_latency,
                    details=detail,
                )
                raise HTTPException(status_code=500, detail=detail)
        else:
            result = {"message": "Webhook ejecutado con éxito"}

        finalize_invocation(
            invocation,
            "success",
            status_code=resp.status_code,
            response_size=response_size,
            transport_latency_seconds=transport_latency,
        )
        return result
    except requests.exceptions.Timeout as exc:
        finalize_invocation(invocation, "timeout", details=str(exc))
        raise HTTPException(status_code=504, detail="Timeout contactando a n8n")
    except HTTPException:
        raise
    except requests.exceptions.RequestException as exc:
        finalize_invocation(invocation, "error", details=str(exc))
        raise HTTPException(status_code=500, detail=str(exc))
    except Exception as e:
        finalize_invocation(
            invocation,
            "error",
            status_code=resp.status_code if resp is not None else None,
            response_size=len(resp.content) if resp is not None and resp.content else 0,
            transport_latency_seconds=transport_latency,
            details=str(e),
        )
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/summary/virtual", summary="Generar resumen virtual vía n8n webhook")
async def generate_virtual_summary(
    body: GenerateVirtualSummaryRequest,
    user: dict = Depends(get_current_user),
    sb: SupabaseClient = Depends(get_supabase)
):
    if not settings.N8N_RESUMEN_VIRTUAL_WEBHOOK_URL:
        raise HTTPException(status_code=500, detail="N8N_RESUMEN_VIRTUAL_WEBHOOK_URL no configurado")
    
    reunion_id = body.reunion_id
    invocation = start_invocation(sb, "resumen_virtual", reunion_id=reunion_id)
    resp = None
    transport_latency = None
    
    try:
        resp = requests.post(settings.N8N_RESUMEN_VIRTUAL_WEBHOOK_URL, json={"reunion_id": reunion_id}, timeout=120)
        transport_latency = invocation.elapsed()
        response_size = len(resp.content) if resp.content else 0

        if 200 <= resp.status_code < 300:
            try:
                data = resp.json()
            except ValueError:
                data = None
            if not isinstance(data, dict):
                detail = "El flujo de n8n no devolvió JSON válido."
                finalize_invocation(
                    invocation,
                    "error",
                    status_code=resp.status_code,
                    response_size=response_size,
                    transport_latency_seconds=transport_latency,
                    details=detail,
                )
                raise HTTPException(status_code=500, detail=detail)
            resumen_texto = data.get("resumen") or data.get("summary") or ""
            if resumen_texto:
                # Guardar el resumen en supabase
                sb.insert("resumenes", [{
                    "reunion_id": reunion_id,
                    "resumen": resumen_texto
                }])
                finalize_invocation(
                    invocation,
                    "success",
                    status_code=resp.status_code,
                    response_size=response_size,
                    transport_latency_seconds=transport_latency,
                )
                return {"message": "Resumen generado y guardado exitosamente.", "resumen": resumen_texto}
            else:
                detail = "El flujo de n8n no devolvió un resumen válido."
                finalize_invocation(
                    invocation,
                    "error",
                    status_code=resp.status_code,
                    response_size=response_size,
                    transport_latency_seconds=transport_latency,
                    details=detail,
                )
                raise HTTPException(status_code=500, detail=detail)
        else:
            finalize_invocation(
                invocation,
                "error",
                status_code=resp.status_code,
                response_size=response_size,
                transport_latency_seconds=transport_latency,
                details=resp.text[:1000] or "n8n rechazó la solicitud.",
            )
            raise HTTPException(status_code=resp.status_code, detail=resp.text)
    except requests.exceptions.Timeout as exc:
        finalize_invocation(invocation, "timeout", details=str(exc))
        raise HTTPException(status_code=504, detail="Timeout contactando a n8n")
    except HTTPException:
        raise
    except requests.exceptions.RequestException as exc:
        finalize_invocation(invocation, "error", details=str(exc))
        raise HTTPException(status_code=500, detail=str(exc))
    except Exception as e:
        finalize_invocation(
            invocation,
            "error",
            status_code=resp.status_code if resp is not None else None,
            response_size=len(resp.content) if resp is not None and resp.content else 0,
            transport_latency_seconds=transport_latency,
            details=str(e),
        )
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/summary/presencial", summary="Procesar acta en PDF/Word vía n8n webhook")
async def generate_presencial_summary(
    reunion_id: str = Form(...),
    file: UploadFile = File(...),
    user: dict = Depends(get_current_user),
    sb: SupabaseClient = Depends(get_supabase)
):
    """
    Envía un archivo PDF o Word a n8n para su procesamiento.
    El workflow responde después de guardar el resumen; el frontend puede
    consultar Supabase después de recibir esta confirmación.
    """
    if not settings.N8N_RESUMEN_PRESENCIAL_WEBHOOK_URL:
        raise HTTPException(status_code=500, detail="N8N_RESUMEN_PRESENCIAL_WEBHOOK_URL no configurado")
    
    # Soportar PDF y Word
    allowed_types = {"application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"}
    allowed_extensions = {".pdf", ".docx"}
    filename = file.filename or "document.pdf"
    ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    
    if file.content_type not in allowed_types and ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail="Solo se aceptan archivos PDF y Word (.docx)."
        )
    
    files = {"data": (file.filename, await file.read(), file.content_type)}
    data_form = {"reunion_id": reunion_id, "nombre_archivo": file.filename}
    invocation = start_invocation(sb, "resumen_presencial", reunion_id=reunion_id)
    resp = None
    transport_latency = None

    try:
        resp = requests.post(settings.N8N_RESUMEN_PRESENCIAL_WEBHOOK_URL, files=files, data=data_form, timeout=180)
        transport_latency = invocation.elapsed()
        response_size = len(resp.content) if resp.content else 0

        if 200 <= resp.status_code < 300:
            try:
                result = resp.json() if resp.text.strip() else {}
            except ValueError:
                result = None
            if not isinstance(result, dict) or result.get("success") is not True:
                detail = "El flujo presencial no confirmó que el resumen fuera guardado."
                finalize_invocation(
                    invocation,
                    "error",
                    status_code=resp.status_code,
                    response_size=response_size,
                    transport_latency_seconds=transport_latency,
                    details=detail,
                )
                raise HTTPException(status_code=502, detail=detail)
            finalize_invocation(
                invocation,
                "success",
                status_code=resp.status_code,
                response_size=response_size,
                transport_latency_seconds=transport_latency,
            )
            return {"message": "Resumen presencial procesado y guardado.", **result}
        else:
            finalize_invocation(
                invocation,
                "error",
                status_code=resp.status_code,
                response_size=response_size,
                transport_latency_seconds=transport_latency,
                details=resp.text[:1000] or "n8n rechazó la solicitud.",
            )
            raise HTTPException(status_code=resp.status_code, detail=resp.text)
    except requests.exceptions.Timeout as exc:
        finalize_invocation(invocation, "timeout", details=str(exc))
        raise HTTPException(status_code=504, detail="Timeout contactando a n8n")
    except HTTPException:
        raise
    except requests.exceptions.RequestException as exc:
        finalize_invocation(invocation, "error", details=str(exc))
        raise HTTPException(status_code=500, detail=str(exc))
    except Exception as e:
        finalize_invocation(
            invocation,
            "error",
            status_code=resp.status_code if resp is not None else None,
            response_size=len(resp.content) if resp is not None and resp.content else 0,
            transport_latency_seconds=transport_latency,
            details=str(e),
        )
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
        # A manual upload is an explicit replacement of the prior recording.
        summaries.update_job(sb, existing["id"], {
            "estado": "cancelado",
            "error_detalle": "Reemplazado por una nueva grabación manual.",
        })
        finalize_async_invocation(
            sb,
            existing["id"],
            "cancelled",
            details="Reemplazado por una nueva grabación manual.",
        )

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
    except requests.exceptions.Timeout:
        raise HTTPException(status_code=504, detail="Timeout contactando a n8n")
    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code if e.response is not None else 502
        raise HTTPException(status_code=status_code, detail=str(e))
    except HTTPException:
        raise
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
        summaries.update_job(sb, existing["id"], {
            "estado": "cancelado",
            "error_detalle": "Reemplazado por una nueva solicitud de Zoom.",
        })
        finalize_async_invocation(
            sb,
            existing["id"],
            "cancelled",
            details="Reemplazado por una nueva solicitud de Zoom.",
        )

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
    except requests.exceptions.Timeout:
        raise HTTPException(status_code=504, detail="Timeout contactando al servicio externo")
    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code if e.response is not None else 502
        raise HTTPException(status_code=status_code, detail=str(e))
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
    "/summary/job/{job_id}/cancel",
    summary="Cancelar un trabajo de resumen en curso",
)
async def cancel_summary_job(
    job_id: str,
    user: dict = Depends(get_current_user),
):
    """Cancela un trabajo atascado o iniciado por error para permitir reintentar."""
    sb = get_supabase(service_role=True)
    job = summaries.get_job(sb, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Trabajo no encontrado")
    if job.get("estado") == "finalizado":
        raise HTTPException(status_code=409, detail="No se puede cancelar un trabajo finalizado")

    summaries.update_job(sb, job_id, {
        "estado": "cancelado",
        "error_detalle": "Cancelado por el usuario.",
    })
    finalize_async_invocation(sb, job_id, "cancelled", details="Cancelado por el usuario.")
    return {"message": "Proceso cancelado. Ya puedes subir otra grabación."}


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
        finalize_async_invocation(sb, payload.job_id, "success")
        return {"message": "El trabajo ya fue finalizado"}
    if job.get("estado") == "cancelado":
        finalize_async_invocation(
            sb,
            payload.job_id,
            "cancelled",
            details="El trabajo fue cancelado antes de recibir el callback.",
        )
        return {"message": "El trabajo fue cancelado; se ignoró el callback tardío"}

    if payload.estado == "error":
        summaries.update_job(sb, job["id"], {
            "estado": "error",
            "error_detalle": payload.error_detalle or "Error desconocido",
        })
        finalize_async_invocation(
            sb,
            payload.job_id,
            "error",
            details=payload.error_detalle or "Error asíncrono informado por n8n.",
        )
        return {"message": "Estado de error registrado"}

    try:
        summaries.save_summary_and_tasks(sb, job, payload.model_dump(exclude_unset=True))
    except Exception as e:
        summaries.update_job(sb, job["id"], {
            "estado": "error",
            "error_detalle": str(e),
        })
        finalize_async_invocation(sb, payload.job_id, "error", details=str(e))
        raise HTTPException(status_code=500, detail=str(e))
    try:
        finalize_async_invocation(sb, payload.job_id, "success")
    except Exception as e:
        raise HTTPException(status_code=503, detail="El resumen se guardó, pero la telemetría no pudo finalizarse.") from e
    return {"message": "Resumen y tareas guardados"}


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
    
    invocation = start_invocation(sb, metric_endpoint)
    resp = None
    transport_latency = None
    try:
        resp = requests.post(webhook_url, json=payload, timeout=90)
        transport_latency = invocation.elapsed()
        response_size = len(resp.content) if resp.content else 0

        if 200 <= resp.status_code < 300:
            if not resp.text.strip():
                detail = "El webhook n8n devolvió una respuesta vacía. Verifica el workflow."
                finalize_invocation(
                    invocation,
                    "error",
                    status_code=resp.status_code,
                    response_size=response_size,
                    transport_latency_seconds=transport_latency,
                    details=detail,
                )
                raise HTTPException(status_code=500, detail=detail)
            
            try:
                data = resp.json()
            except ValueError:
                detail = f"El webhook n8n devolvió contenido inválido: {resp.text[:200]}"
                finalize_invocation(
                    invocation,
                    "error",
                    status_code=resp.status_code,
                    response_size=response_size,
                    transport_latency_seconds=transport_latency,
                    details=detail,
                )
                raise HTTPException(status_code=500, detail=detail)
            if not isinstance(data, dict):
                detail = "El webhook n8n debe devolver un objeto JSON."
                finalize_invocation(
                    invocation,
                    "error",
                    status_code=resp.status_code,
                    response_size=response_size,
                    transport_latency_seconds=transport_latency,
                    details=detail,
                )
                raise HTTPException(status_code=500, detail=detail)
            
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
            finalize_invocation(
                invocation,
                "success",
                status_code=resp.status_code,
                response_size=response_size,
                transport_latency_seconds=transport_latency,
            )
            return response
        else:
            finalize_invocation(
                invocation,
                "error",
                status_code=resp.status_code,
                response_size=response_size,
                transport_latency_seconds=transport_latency,
                details=resp.text[:1000] or "n8n rechazó la solicitud.",
            )
            raise HTTPException(status_code=resp.status_code, detail=resp.text)
    except requests.exceptions.Timeout as exc:
        finalize_invocation(invocation, "timeout", details=str(exc))
        raise HTTPException(status_code=504, detail="Timeout contactando a n8n")
    except HTTPException:
        raise
    except requests.exceptions.RequestException as exc:
        finalize_invocation(invocation, "error", details=str(exc))
        raise HTTPException(status_code=500, detail=str(exc))
    except Exception as e:
        finalize_invocation(
            invocation,
            "error",
            status_code=resp.status_code if resp is not None else None,
            response_size=len(resp.content) if resp is not None and resp.content else 0,
            transport_latency_seconds=transport_latency,
            details=str(e),
        )
        raise HTTPException(status_code=500, detail=str(e))
