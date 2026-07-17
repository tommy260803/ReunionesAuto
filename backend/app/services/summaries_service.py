"""
Servicios de negocio para el procesamiento de resúmenes.

Gestiona:
- Creación y actualización de trabajos de resumen.
- Subida de grabaciones a Supabase Storage.
- Descarga de transcripts de Zoom.
- Limpieza de VTT.
- Invocación de n8n para procesar audio.
- Callback de n8n para guardar resúmenes y tareas.
"""

from __future__ import annotations

import base64
import json
import time
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any
from urllib.parse import quote

import requests

from app.core.config import settings
from app.core.summaries_utils import clean_vtt
from app.core.supabase_client import SupabaseClient


# ------------------------------------------------------------------
# Constantes
# ------------------------------------------------------------------
ALLOWED_AUDIO_EXTENSIONS = {"m4a", "mp3", "mp4", "mpeg", "mpga", "wav", "webm", "ogg"}
ALLOWED_AUDIO_TYPES = {
    "audio/mp4",
    "audio/m4a",
    "audio/mpeg",
    "audio/mp3",
    "audio/mpga",
    "audio/wav",
    "audio/webm",
    "audio/ogg",
    "video/mp4",
    "video/webm",
    "video/ogg",
}
MAX_UPLOAD_SIZE = 200 * 1024 * 1024  # 200 MB


# ------------------------------------------------------------------
# Helpers internos
# ------------------------------------------------------------------

def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _bucket() -> str:
    return settings.SUPABASE_STORAGE_BUCKET


def _extract_ext(filename: str) -> str:
    parts = filename.rsplit(".", 1)
    return parts[-1].lower() if len(parts) > 1 else ""


def _get_n8n_webhook() -> str:
    if settings.N8N_PROCESS_RECORDING_WEBHOOK_URL:
        return settings.N8N_PROCESS_RECORDING_WEBHOOK_URL
    if settings.N8N_RESUMEN_VIRTUAL_WEBHOOK_URL:
        return settings.N8N_RESUMEN_VIRTUAL_WEBHOOK_URL
    raise RuntimeError("N8N_PROCESS_RECORDING_WEBHOOK_URL no está configurado")


def _get_callback_url() -> str:
    if settings.BACKEND_PUBLIC_URL:
        return f"{settings.BACKEND_PUBLIC_URL.rstrip('/')}/automation/summary/callback"
    return ""


# ------------------------------------------------------------------
# Zoom Server-to-Server OAuth
# ------------------------------------------------------------------

def _get_zoom_token() -> str:
    pair = f"{settings.ZOOM_CLIENT_ID}:{settings.ZOOM_CLIENT_SECRET}"
    basic = base64.b64encode(pair.encode()).decode()
    r = requests.post(
        "https://zoom.us/oauth/token",
        headers={"Authorization": f"Basic {basic}"},
        params={
            "grant_type": "account_credentials",
            "account_id": settings.ZOOM_ACCOUNT_ID,
        },
        timeout=30,
    )
    r.raise_for_status()
    return r.json()["access_token"]


def get_zoom_recordings(zoom_meeting_id: str) -> dict[str, Any]:
    """Obtiene el listado de grabaciones de Zoom para un meeting_id."""
    token = _get_zoom_token()
    # Zoom UUIDs can contain slash characters. Encoding twice is required by
    # Zoom for those IDs; numeric meeting IDs remain unchanged.
    encoded_meeting_id = quote(quote(str(zoom_meeting_id), safe=""), safe="")
    r = requests.get(
        f"https://api.zoom.us/v2/meetings/{encoded_meeting_id}/recordings",
        headers={"Authorization": f"Bearer {token}"},
        timeout=30,
    )
    if r.status_code == 404:
        try:
            zoom_detail = r.json().get("message", "")
        except ValueError:
            zoom_detail = ""
        raise LookupError(
            "Zoom no encontró esta reunión o su grabación. Verifica que la "
            "reunión haya finalizado, tenga Cloud Recording, pertenezca a la "
            "misma cuenta de la app Server-to-Server y que el id_externo sea "
            f"el ID/UUID correcto de Zoom. {zoom_detail}".strip()
        )
    r.raise_for_status()
    return r.json()


def download_url(url: str, headers: dict | None = None, timeout: int = 60) -> bytes:
    """Descarga un archivo binario desde una URL."""
    r = requests.get(url, headers=headers, stream=True, timeout=timeout)
    r.raise_for_status()
    return r.content


# ------------------------------------------------------------------
# Trabajos de resumen
# ------------------------------------------------------------------

def create_job(
    sb: SupabaseClient,
    reunion_id: str,
    fuente: str,
    zoom_meeting_id: str | None = None,
) -> dict[str, Any]:
    """Crea un nuevo trabajo de resumen en estado 'pendiente'."""
    job = {
        "id": str(uuid.uuid4()),
        "reunion_id": reunion_id,
        "estado": "pendiente",
        "fuente": fuente,
        "zoom_meeting_id": zoom_meeting_id,
        "expira_en": (datetime.now(timezone.utc) + timedelta(days=settings.RECORDING_MAX_AGE_DAYS)).isoformat(),
        "fecha_creacion": _now(),
        "fecha_actualizacion": _now(),
    }
    sb.insert("trabajos_resumen", [job])
    return job


def get_active_job_for_meeting(
    sb: SupabaseClient, reunion_id: str
) -> dict[str, Any] | None:
    """Devuelve el trabajo de resumen más reciente de una reunión."""
    rows = sb.select(
        "trabajos_resumen",
        {
            "select": "id,reunion_id,estado,fuente,archivo_path,archivo_url_publica,zoom_meeting_id,zoom_transcript_url,zoom_audio_url,resumen_texto,error_detalle,intentos,fecha_actualizacion,expira_en",
            "reunion_id": f"eq.{reunion_id}",
            "order": "fecha_creacion.desc",
            "limit": "1",
        },
    )
    return rows[0] if rows else None


def get_job(sb: SupabaseClient, job_id: str) -> dict[str, Any] | None:
    rows = sb.select(
        "trabajos_resumen",
        {
            "select": "id,reunion_id,estado,fuente,archivo_path,archivo_url_publica,zoom_meeting_id,zoom_transcript_url,zoom_audio_url,resumen_texto,error_detalle,intentos,fecha_actualizacion,expira_en",
            "id": f"eq.{job_id}",
        },
    )
    return rows[0] if rows else None


def update_job(
    sb: SupabaseClient,
    job_id: str,
    data: dict[str, Any],
) -> None:
    data["fecha_actualizacion"] = _now()
    sb.update("trabajos_resumen", data=data, params={"id": f"eq.{job_id}"})


# ------------------------------------------------------------------
# Subida manual de grabaciones
# ------------------------------------------------------------------

def upload_recording(
    sb: SupabaseClient,
    job_id: str,
    filename: str,
    content: bytes,
    content_type: str,
) -> str:
    """Sube la grabación a Storage y devuelve la ruta interna."""
    ext = _extract_ext(filename)
    if ext not in ALLOWED_AUDIO_EXTENSIONS:
        raise ValueError(f"Extensión no soportada: {ext}")
    if len(content) > MAX_UPLOAD_SIZE:
        raise ValueError("El archivo excede el límite de 200 MB")
    if content_type not in ALLOWED_AUDIO_TYPES:
        # Sino coincide exactamente, confiamos en la extensión si es de audio/video
        if not content_type.startswith("audio/") and not content_type.startswith("video/"):
            raise ValueError(f"Tipo de archivo no soportado: {content_type}")

    path = f"{job_id}/{uuid.uuid4()}.{ext}"
    sb.storage_upload(_bucket(), path, content, content_type, upsert=True)
    return path


# ------------------------------------------------------------------
# Zoom transcript / audio
# ------------------------------------------------------------------

def find_zoom_transcript_url(files: list[dict[str, Any]]) -> str | None:
    """Busca la URL de descarga del archivo VTT en los recording_files."""
    for f in files:
        ext = f.get("file_extension", "").lower()
        ftype = f.get("file_type", "").upper()
        if ext == "vtt" or ftype == "TRANSCRIPT":
            download = f.get("download_url") or f.get("play_url")
            if download:
                return download
    return None


def find_zoom_audio_url(files: list[dict[str, Any]]) -> str | None:
    """Busca la URL de descarga del archivo de audio (M4A preferido)."""
    preferred = []
    for f in files:
        ext = f.get("file_extension", "").lower()
        ftype = f.get("file_type", "").upper()
        if ftype in ("M4A", "MP3", "MP4", "AUDIO") or ext in ("m4a", "mp3", "mp4"):
            preferred.append((f.get("file_type", "").upper(), f.get("download_url") or f.get("play_url"), f))
    # Preferir M4A
    for p in preferred:
        if p[0] == "M4A" or p[2].get("file_extension", "").lower() == "m4a":
            return p[1]
    return preferred[0][1] if preferred else None


def download_zoom_vtt(
    sb: SupabaseClient,
    job_id: str,
    vtt_url: str,
    meeting_uuid: str,
    token: str,
) -> str:
    """Descarga el VTT, lo limpia y lo sube a Storage como texto."""
    content = download_url(vtt_url, headers={"Authorization": f"Bearer {token}"}, timeout=60)
    transcript = clean_vtt(content)
    path = f"{job_id}/transcript_{meeting_uuid}.txt"
    encoded = transcript.encode("utf-8")
    sb.storage_upload(_bucket(), path, encoded, "text/plain", upsert=True)
    return path


# ------------------------------------------------------------------
# Invocación a n8n
# ------------------------------------------------------------------

def send_to_n8n(
    sb: SupabaseClient,
    job_id: str,
    reunion_id: str,
    file_url: str,
    file_type: str,
) -> None:
    """Envía a n8n una URL firmada para procesar."""
    update_job(sb, job_id, {"estado": "transcribiendo" if file_type == "audio" else "generando"})
    payload = {
        "job_id": job_id,
        "reunion_id": reunion_id,
        "file_url": file_url,
        "file_type": file_type,
        "callback_url": _get_callback_url(),
        "callback_secret": settings.N8N_CALLBACK_SECRET,
    }
    requests.post(_get_n8n_webhook(), json=payload, timeout=30)


# ------------------------------------------------------------------
# Callback: guardar resultado
# ------------------------------------------------------------------

def save_summary_and_tasks(
    sb: SupabaseClient,
    job: dict[str, Any],
    payload: dict[str, Any],
) -> None:
    """Persiste el resumen estructurado y las tareas extraídas."""
    reunion_id = job["reunion_id"]
    resumen_texto = payload.get("resumen") or payload.get("resumen_ejecutivo") or ""
    resumen_texto = resumen_texto.strip()

    if not resumen_texto:
        raise ValueError("El payload no contiene un resumen válido")

    # PostgREST needs an explicit on_conflict target for a unique key other
    # than the primary key. Select/update avoids a 409 when the meeting
    # already has a summary generated by a previous workflow attempt.
    existing_summary = sb.select(
        "resumenes", {"select": "id", "reunion_id": f"eq.{reunion_id}"}
    )
    if existing_summary:
        sb.update(
            "resumenes", {"resumen": resumen_texto},
            {"reunion_id": f"eq.{reunion_id}"},
        )
    else:
        sb.insert("resumenes", [{"reunion_id": reunion_id, "resumen": resumen_texto}])

    detail = {
        "resumen_ejecutivo": payload.get("resumen_ejecutivo") or resumen_texto,
        "decisiones": payload.get("decisiones") or "",
        "riesgos": payload.get("riesgos") or "",
        "proximos_pasos": payload.get("proximos_pasos") or "",
    }
    existing_detail = sb.select(
        "resumenes_detalle", {"select": "id", "reunion_id": f"eq.{reunion_id}"}
    )
    if existing_detail:
        sb.update("resumenes_detalle", detail, {"reunion_id": f"eq.{reunion_id}"})
    else:
        sb.insert("resumenes_detalle", [{"reunion_id": reunion_id, **detail}])

    # Crear tareas
    for task in payload.get("tareas", []):
        if not task.get("descripcion"):
            continue
        sb.insert(
            "tareas",
            [{
                "reunion_id": reunion_id,
                "descripcion": task["descripcion"],
                "asignado_a_correo": task.get("responsable") or None,
                "estado": "pendiente",
                "fecha_vencimiento": task.get("fecha_vencimiento") or None,
            }],
        )

    # Actualizar trabajo
    update_job(
        sb,
        job["id"],
        {
            "estado": "finalizado",
            "resumen_texto": resumen_texto,
            "error_detalle": None,
        },
    )


# ------------------------------------------------------------------
# Limpieza de grabaciones expiradas
# ------------------------------------------------------------------

def cleanup_expired_recordings(sb: SupabaseClient) -> dict[str, Any]:
    """Elimina trabajos y archivos de Storage cuya expiración haya pasado."""
    rows = sb.select(
        "trabajos_resumen",
        {
            "select": "id,archivo_path",
            "expira_en": f"lt.{datetime.now(timezone.utc).isoformat()}",
        },
    )
    deleted = 0
    errors: list[str] = []
    for row in rows:
        try:
            if row.get("archivo_path"):
                sb.storage_delete(_bucket(), [row["archivo_path"]])
            sb.delete("trabajos_resumen", params={"id": f"eq.{row['id']}"})
            deleted += 1
        except Exception as e:
            errors.append(str(e))
    return {"deleted": deleted, "errors": errors}
