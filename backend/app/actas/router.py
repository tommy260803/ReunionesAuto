"""
Router de actas.

Permite crear, consultar, actualizar, eliminar y descargar actas
de reuniones generadas a partir de documentos subidos (PDF/Word).
"""

from __future__ import annotations

import uuid
from typing import List, Optional

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Query,
    UploadFile,
    status,
)
from fastapi.responses import Response

from app.actas.schemas import (
    ActaListResponse,
    ActaResponse,
    ActaUpdateRequest,
)
from app.core.dependencies import get_current_user
from app.core.supabase_client import SupabaseClient, get_supabase
from app.services import acta_generator
from app.services.document_parser import detect_format, extract_text

router = APIRouter(prefix="/actas", tags=["Actas"])

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}
MAX_ACTA_FILE_SIZE = 20 * 1024 * 1024  # 20 MB


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

def _now() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat()


def _get_meeting(sb: SupabaseClient, meeting_id: str) -> dict:
    rows = sb.select(
        "reuniones",
        {
            "select": "id,tema,fecha_inicio,tipo,duracion_minutos,estado",
            "id": f"eq.{meeting_id}",
        },
    )
    if not rows:
        raise HTTPException(status_code=404, detail="Reunión no encontrada")
    return rows[0]


def _get_acta(sb: SupabaseClient, acta_id: str) -> dict:
    rows = sb.select(
        "actas",
        {
            "select": (
                "id,reunion_id,numero,titulo,tipo_reunion,contenido,"
                "formato_origen,estado,fecha_reunion,participantes,"
                "orden_dia,decisiones,tareas_extraidas,proximos_pasos,"
                "observaciones,fecha_creacion,fecha_actualizacion"
            ),
            "id": f"eq.{acta_id}",
        },
    )
    if not rows:
        raise HTTPException(status_code=404, detail="Acta no encontrada")
    return rows[0]


def _validate_file(filename: str, content: bytes) -> None:
    ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Formato no soportado: {ext}. Se aceptan PDF, Word (.docx) y texto plano.",
        )
    if len(content) > MAX_ACTA_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail="El archivo excede el límite de 20 MB.",
        )


# ------------------------------------------------------------------
# CRUD
# ------------------------------------------------------------------

@router.get("", response_model=List[ActaListResponse], summary="Listar actas")
async def list_actas(
    reunion_id: Optional[str] = Query(None, description="Filtrar por reunión"),
    tipo_reunion: Optional[str] = Query(None, description="Filtrar por tipo"),
    estado: Optional[str] = Query(None, description="Filtrar por estado"),
    user: dict = Depends(get_current_user),
    sb: SupabaseClient = Depends(get_supabase),
):
    params = {
        "select": (
            "id,reunion_id,numero,titulo,tipo_reunion,formato_origen,"
            "estado,fecha_reunion,fecha_creacion"
        ),
        "order": "fecha_creacion.desc",
    }
    if reunion_id:
        params["reunion_id"] = f"eq.{reunion_id}"
    if tipo_reunion:
        params["tipo_reunion"] = f"eq.{tipo_reunion}"
    if estado:
        params["estado"] = f"eq.{estado}"

    rows = sb.select("actas", params)
    return [ActaListResponse(**row) for row in rows]


@router.get("/{acta_id}", response_model=ActaResponse, summary="Detalle de acta")
async def get_acta(
    acta_id: str,
    user: dict = Depends(get_current_user),
    sb: SupabaseClient = Depends(get_supabase),
):
    row = _get_acta(sb, acta_id)
    return ActaResponse(**row)


@router.get(
    "/meeting/{reunion_id}",
    response_model=Optional[ActaResponse],
    summary="Obtener acta de una reunión",
)
async def get_acta_by_meeting(
    reunion_id: str,
    user: dict = Depends(get_current_user),
    sb: SupabaseClient = Depends(get_supabase),
):
    rows = sb.select(
        "actas",
        {
            "select": (
                "id,reunion_id,numero,titulo,tipo_reunion,contenido,"
                "formato_origen,estado,fecha_reunion,participantes,"
                "orden_dia,decisiones,tareas_extraidas,proximos_pasos,"
                "observaciones,fecha_creacion,fecha_actualizacion"
            ),
            "reunion_id": f"eq.{reunion_id}",
            "order": "fecha_creacion.desc",
            "limit": "1",
        },
    )
    if not rows:
        raise HTTPException(status_code=404, detail="No hay acta para esta reunión")
    return ActaResponse(**rows[0])


@router.patch("/{acta_id}", response_model=ActaResponse, summary="Actualizar acta")
async def update_acta(
    acta_id: str,
    body: ActaUpdateRequest,
    user: dict = Depends(get_current_user),
    sb: SupabaseClient = Depends(get_supabase),
):
    _get_acta(sb, acta_id)
    update_data = body.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="No hay datos para actualizar")
    update_data["fecha_actualizacion"] = _now()
    sb.update("actas", data=update_data, params={"id": f"eq.{acta_id}"})
    row = _get_acta(sb, acta_id)
    return ActaResponse(**row)


@router.delete("/{acta_id}", summary="Eliminar acta")
async def delete_acta(
    acta_id: str,
    user: dict = Depends(get_current_user),
    sb: SupabaseClient = Depends(get_supabase),
):
    _get_acta(sb, acta_id)
    sb.delete("actas", params={"id": f"eq.{acta_id}"})
    return {"message": "Acta eliminada"}


# ------------------------------------------------------------------
# Generación de acta desde documento subido
# ------------------------------------------------------------------

@router.post(
    "/generate",
    response_model=ActaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generar acta desde documento (PDF/Word)",
)
async def generate_acta_from_document(
    reunion_id: str = Form(...),
    titulo: str = Form("Acta de Reunión"),
    participantes: Optional[str] = Form(None),
    orden_dia: Optional[str] = Form(None),
    observaciones: Optional[str] = Form(None),
    file: UploadFile = File(...),
    user: dict = Depends(get_current_user),
    sb: SupabaseClient = Depends(get_supabase),
):
    """
    Sube un PDF o Word, extrae el texto, genera un acta con IA
    y la guarda en la base de datos.
    """
    meeting = _get_meeting(sb, reunion_id)
    content = await file.read()
    _validate_file(file.filename or "document.pdf", content)

    formato_origen = detect_format(file.filename or "document.pdf")
    texto_extraido = extract_text(file.filename or "document.pdf", content)

    if not texto_extraido.strip():
        raise HTTPException(
            status_code=400,
            detail="No se pudo extraer texto del archivo. "
            "Verifica que el documento no esté vacío o protegido.",
        )

    tipo_reunion = meeting.get("tipo") or "virtual"

    try:
        resultado = acta_generator.generate_acta(
            texto_documento=texto_extraido,
            titulo=titulo,
            tipo_reunion=tipo_reunion,
            participantes=participantes,
            orden_dia=orden_dia,
            observaciones=observaciones,
        )
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al generar el acta con IA: {str(e)}",
        )

    acta_id = str(uuid.uuid4())
    acta_record = {
        "id": acta_id,
        "reunion_id": reunion_id,
        "titulo": titulo,
        "tipo_reunion": tipo_reunion,
        "contenido": resultado["contenido"],
        "formato_origen": formato_origen,
        "estado": "borrador",
        "fecha_reunion": meeting.get("fecha_inicio"),
        "participantes": participantes,
        "orden_dia": orden_dia,
        "decisiones": resultado.get("decisiones"),
        "tareas_extraidas": resultado.get("tareas_extraidas"),
        "proximos_pasos": resultado.get("proximos_pasos"),
        "observaciones": observaciones,
        "fecha_creacion": _now(),
        "fecha_actualizacion": _now(),
    }
    sb.insert("actas", [acta_record])

    row = _get_acta(sb, acta_id)
    return ActaResponse(**row)


# ------------------------------------------------------------------
# Generación de acta desde texto (sin archivo)
# ------------------------------------------------------------------

@router.post(
    "/generate-from-text",
    response_model=ActaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generar acta desde texto pegado",
)
async def generate_acta_from_text(
    reunion_id: str = Form(...),
    titulo: str = Form("Acta de Reunión"),
    texto: str = Form(...),
    participantes: Optional[str] = Form(None),
    orden_dia: Optional[str] = Form(None),
    observaciones: Optional[str] = Form(None),
    user: dict = Depends(get_current_user),
    sb: SupabaseClient = Depends(get_supabase),
):
    """
    Genera un acta a partir de texto pegado directamente.
    Útil para transcripciones copiadas o notas de reunión.
    """
    meeting = _get_meeting(sb, reunion_id)
    tipo_reunion = meeting.get("tipo") or "virtual"

    try:
        resultado = acta_generator.generate_acta(
            texto_documento=texto,
            titulo=titulo or "Acta de Reunión",
            tipo_reunion=tipo_reunion,
            participantes=participantes,
            orden_dia=orden_dia,
            observaciones=observaciones,
        )
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al generar el acta con IA: {str(e)}",
        )

    acta_id = str(uuid.uuid4())
    acta_record = {
        "id": acta_id,
        "reunion_id": reunion_id,
        "titulo": titulo or "Acta de Reunión",
        "tipo_reunion": tipo_reunion,
        "contenido": resultado["contenido"],
        "formato_origen": "manual",
        "estado": "borrador",
        "fecha_reunion": meeting.get("fecha_inicio"),
        "participantes": participantes,
        "orden_dia": orden_dia,
        "decisiones": resultado.get("decisiones"),
        "tareas_extraidas": resultado.get("tareas_extraidas"),
        "proximos_pasos": resultado.get("proximos_pasos"),
        "observaciones": observaciones,
        "fecha_creacion": _now(),
        "fecha_actualizacion": _now(),
    }
    sb.insert("actas", [acta_record])

    row = _get_acta(sb, acta_id)
    return ActaResponse(**row)


# ------------------------------------------------------------------
# Finalizar acta
# ------------------------------------------------------------------

@router.post(
    "/{acta_id}/finalize",
    response_model=ActaResponse,
    summary="Finalizar acta (borrador → finalizada)",
)
async def finalize_acta(
    acta_id: str,
    user: dict = Depends(get_current_user),
    sb: SupabaseClient = Depends(get_supabase),
):
    _get_acta(sb, acta_id)
    sb.update(
        "actas",
        data={"estado": "finalizada", "fecha_actualizacion": _now()},
        params={"id": f"eq.{acta_id}"},
    )
    row = _get_acta(sb, acta_id)
    return ActaResponse(**row)
