"""
Router de automatización.

Envuelve las llamadas a los webhooks de n8n y registra las métricas.
"""

import time
import requests
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from datetime import datetime

from app.automation.schemas import CreateMeetingWebhookRequest, GenerateVirtualSummaryRequest, ChatRequest
from app.core.dependencies import get_current_user
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
