"""
Router de ejecuciones de IA.

Permite registrar y consultar ejecuciones de modelos de IA
con parámetros completos para análisis de rendimiento.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from datetime import datetime

from app.core.dependencies import get_current_user
from app.core.supabase_client import SupabaseClient, get_supabase
from app.ai_executions.schemas import (
    AIExecutionCreate,
    AIExecutionUpdate,
    AIExecutionResponse,
    AIExecutionListResponse,
)

router = APIRouter(prefix="/ai-executions", tags=["Ejecuciones IA"])


@router.post(
    "/",
    response_model=AIExecutionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar ejecución de IA"
)
async def create_execution(
    body: AIExecutionCreate,
    user: dict = Depends(get_current_user),
    sb: SupabaseClient = Depends(get_supabase),
) -> AIExecutionResponse:
    """
    Registra una nueva ejecución de modelo de IA.
    
    Este endpoint es llamado típicamente por workflows de n8n
    o por el backend al procesar resúmenes.
    """
    # Verificar que la reunión existe
    meeting = sb.select(
        "reuniones",
        {
            "id": f"eq.{body.reunion_id}",
            "limit": "1",
        },
    )
    
    if not meeting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reunión no encontrada.",
        )
    
    # Verificar prompt_version_id si se proporciona
    if body.prompt_version_id:
        prompt = sb.select(
            "prompt_versions",
            {
                "id": f"eq.{body.prompt_version_id}",
                "limit": "1",
            },
        )
        if not prompt:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Versión de prompt no encontrada.",
            )
    
    # Crear ejecución
    new_execution = {
        "reunion_id": body.reunion_id,
        "prompt_version_id": body.prompt_version_id,
        "proveedor": body.proveedor,
        "modelo": body.modelo,
        "temperatura": body.temperatura,
        "parametros": body.parametros,
        "workflow_version": body.workflow_version,
        "input_hash": body.input_hash,
        "respuesta_original": body.respuesta_original,
        "respuesta_procesada": body.respuesta_procesada,
        "tokens_entrada": body.tokens_entrada,
        "tokens_salida": body.tokens_salida,
        "costo_estimado": body.costo_estimado,
        "tiempo_ms": body.tiempo_ms,
        "reintentos": body.reintentos,
        "estado": body.estado,
        "tipo_error": body.tipo_error,
        "mensaje_error": body.mensaje_error,
        "iniciado_por": user["id"],
        "fecha_inicio": datetime.utcnow().isoformat(),
    }
    
    result = sb.insert("ai_executions", [new_execution])
    
    if not result or isinstance(result, dict) and "status" in result:
        # Si la inserción fue exitosa, consultar el creado
        created = sb.select(
            "ai_executions",
            {
                "reunion_id": f"eq.{body.reunion_id}",
                "proveedor": f"eq.{body.proveedor}",
                "modelo": f"eq.{body.modelo}",
                "order": "fecha_inicio.desc",
                "limit": "1",
            },
        )
        if created:
            row = created[0]
            return AIExecutionResponse(
                id=str(row["id"]),
                reunion_id=str(row["reunion_id"]),
                prompt_version_id=str(row["prompt_version_id"]) if row.get("prompt_version_id") else None,
                proveedor=row["proveedor"],
                modelo=row["modelo"],
                temperatura=row.get("temperatura"),
                parametros=row.get("parametros"),
                workflow_version=row.get("workflow_version"),
                input_hash=row.get("input_hash"),
                respuesta_original=row.get("respuesta_original"),
                respuesta_procesada=row.get("respuesta_procesada"),
                tokens_entrada=row.get("tokens_entrada"),
                tokens_salida=row.get("tokens_salida"),
                costo_estimado=row.get("costo_estimado"),
                tiempo_ms=row.get("tiempo_ms"),
                reintentos=row["reintentos"],
                estado=row["estado"],
                tipo_error=row.get("tipo_error"),
                mensaje_error=row.get("mensaje_error"),
                iniciado_por=str(row["iniciado_por"]) if row.get("iniciado_por") else None,
                fecha_inicio=row["fecha_inicio"],
                fecha_fin=row.get("fecha_fin"),
            )
    
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Error al registrar la ejecución.",
    )


@router.get(
    "/",
    response_model=List[AIExecutionListResponse],
    summary="Listar ejecuciones de IA"
)
async def list_executions(
    reunion_id: Optional[str] = Query(None, description="Filtrar por reunión"),
    prompt_version_id: Optional[str] = Query(None, description="Filtrar por versión de prompt"),
    modelo: Optional[str] = Query(None, description="Filtrar por modelo"),
    estado: Optional[str] = Query(None, description="Filtrar por estado"),
    limit: int = Query(50, ge=1, le=100, description="Límite de resultados"),
    offset: int = Query(0, ge=0, description="Desplazamiento"),
    user: dict = Depends(get_current_user),
    sb: SupabaseClient = Depends(get_supabase),
) -> List[AIExecutionListResponse]:
    """
    Lista ejecuciones de IA con filtros opcionales.
    """
    params = {
        "select": "id,reunion_id,prompt_version_id,proveedor,modelo,estado,fecha_inicio,fecha_fin,tiempo_ms",
        "order": "fecha_inicio.desc",
        "limit": str(limit),
        "offset": str(offset),
    }
    
    if reunion_id:
        params["reunion_id"] = f"eq.{reunion_id}"
    if prompt_version_id:
        params["prompt_version_id"] = f"eq.{prompt_version_id}"
    if modelo:
        params["modelo"] = f"eq.{modelo}"
    if estado:
        params["estado"] = f"eq.{estado}"
    
    rows = sb.select("ai_executions", params)
    
    return [
        AIExecutionListResponse(
            id=str(row["id"]),
            reunion_id=str(row["reunion_id"]),
            prompt_version_id=str(row["prompt_version_id"]) if row.get("prompt_version_id") else None,
            proveedor=row["proveedor"],
            modelo=row["modelo"],
            estado=row["estado"],
            fecha_inicio=row["fecha_inicio"],
            fecha_fin=row.get("fecha_fin"),
            tiempo_ms=row.get("tiempo_ms"),
        )
        for row in rows
    ]


@router.get(
    "/{execution_id}",
    response_model=AIExecutionResponse,
    summary="Obtener ejecución de IA por ID"
)
async def get_execution(
    execution_id: str,
    user: dict = Depends(get_current_user),
    sb: SupabaseClient = Depends(get_supabase),
) -> AIExecutionResponse:
    """
    Obtiene los detalles completos de una ejecución de IA.
    """
    rows = sb.select(
        "ai_executions",
        {
            "id": f"eq.{execution_id}",
            "limit": "1",
        },
    )
    
    if not rows:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ejecución no encontrada.",
        )
    
    row = rows[0]
    return AIExecutionResponse(
        id=str(row["id"]),
        reunion_id=str(row["reunion_id"]),
        prompt_version_id=str(row["prompt_version_id"]) if row.get("prompt_version_id") else None,
        proveedor=row["proveedor"],
        modelo=row["modelo"],
        temperatura=row.get("temperatura"),
        parametros=row.get("parametros"),
        workflow_version=row.get("workflow_version"),
        input_hash=row.get("input_hash"),
        respuesta_original=row.get("respuesta_original"),
        respuesta_procesada=row.get("respuesta_procesada"),
        tokens_entrada=row.get("tokens_entrada"),
        tokens_salida=row.get("tokens_salida"),
        costo_estimado=row.get("costo_estimado"),
        tiempo_ms=row.get("tiempo_ms"),
        reintentos=row["reintentos"],
        estado=row["estado"],
        tipo_error=row.get("tipo_error"),
        mensaje_error=row.get("mensaje_error"),
        iniciado_por=str(row["iniciado_por"]) if row.get("iniciado_por") else None,
        fecha_inicio=row["fecha_inicio"],
        fecha_fin=row.get("fecha_fin"),
    )


@router.patch(
    "/{execution_id}",
    response_model=AIExecutionResponse,
    summary="Actualizar ejecución de IA"
)
async def update_execution(
    execution_id: str,
    body: AIExecutionUpdate,
    user: dict = Depends(get_current_user),
    sb: SupabaseClient = Depends(get_supabase),
) -> AIExecutionResponse:
    """
    Actualiza una ejecución de IA existente.
    
    Se usa típicamente para registrar el resultado final de una ejecución
    que estaba en proceso.
    """
    # Verificar que existe
    existing = sb.select(
        "ai_executions",
        {
            "id": f"eq.{execution_id}",
            "limit": "1",
        },
    )
    
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ejecución no encontrada.",
        )
    
    # Construir datos de actualización
    update_data = {}
    if body.respuesta_original is not None:
        update_data["respuesta_original"] = body.respuesta_original
    if body.respuesta_procesada is not None:
        update_data["respuesta_procesada"] = body.respuesta_procesada
    if body.tokens_entrada is not None:
        update_data["tokens_entrada"] = body.tokens_entrada
    if body.tokens_salida is not None:
        update_data["tokens_salida"] = body.tokens_salida
    if body.costo_estimado is not None:
        update_data["costo_estimado"] = body.costo_estimado
    if body.tiempo_ms is not None:
        update_data["tiempo_ms"] = body.tiempo_ms
    if body.reintentos is not None:
        update_data["reintentos"] = body.reintentos
    if body.estado is not None:
        update_data["estado"] = body.estado
    if body.tipo_error is not None:
        update_data["tipo_error"] = body.tipo_error
    if body.mensaje_error is not None:
        update_data["mensaje_error"] = body.mensaje_error
    if body.fecha_fin is not None:
        update_data["fecha_fin"] = body.fecha_fin.isoformat()
    
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se proporcionaron datos para actualizar.",
        )
    
    # Actualizar
    sb.update(
        "ai_executions",
        update_data,
        {"id": f"eq.{execution_id}"},
    )
    
    # Retornar la ejecución actualizada
    return await get_execution(execution_id, user, sb)
