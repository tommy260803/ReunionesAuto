"""
Router de sesiones experimentales y mediciones.

Permite crear experimentos, registrar mediciones de tiempo
y respuestas del cuestionario SUS.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from datetime import datetime

from app.core.dependencies import get_current_user, get_current_investigator
from app.core.supabase_client import SupabaseClient, get_supabase
from app.experiments.schemas import (
    ExperimentSessionCreate,
    ExperimentSessionUpdate,
    ExperimentSessionResponse,
    ExperimentSessionListResponse,
    TimeMeasurementCreate,
    TimeMeasurementResponse,
    SusResponseCreate,
    SusResponseResponse,
)

router = APIRouter(prefix="/experiments", tags=["Experimentos"])


# ==============================================================================
# SESIONES EXPERIMENTALES
# ==============================================================================

@router.post(
    "/sessions",
    response_model=ExperimentSessionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear sesión experimental"
)
async def create_experiment_session(
    body: ExperimentSessionCreate,
    user: dict = Depends(get_current_investigator),
    sb: SupabaseClient = Depends(get_supabase),
) -> ExperimentSessionResponse:
    """
    Crea una nueva sesión experimental.
    
    Requiere rol de INVESTIGADOR o ADMIN.
    """
    if not user.get("is_investigator"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo investigadores y administradores pueden crear experimentos.",
        )
    
    # Verificar que el investigador existe
    investigator = sb.select(
        "usuarios",
        {
            "id": f"eq.{body.investigador_id}",
            "limit": "1",
        },
    )
    
    if not investigator:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Investigador no encontrado.",
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
    
    # Crear sesión experimental
    new_session = {
        "nombre": body.nombre,
        "descripcion": body.descripcion,
        "investigador_id": body.investigador_id,
        "condicion": body.condicion,
        "prompt_version_id": body.prompt_version_id,
        "modelo": body.modelo,
        "configuracion": body.configuracion,
        "estado": body.estado,
    }
    
    result = sb.insert("experiment_sessions", [new_session])
    
    if not result or isinstance(result, dict) and "status" in result:
        # Si la inserción fue exitosa, consultar la creada
        created = sb.select(
            "experiment_sessions",
            {
                "nombre": f"eq.{body.nombre}",
                "investigador_id": f"eq.{body.investigador_id}",
                "order": "fecha_inicio.desc",
                "limit": "1",
            },
        )
        if created:
            row = created[0]
            return ExperimentSessionResponse(
                id=str(row["id"]),
                nombre=row["nombre"],
                descripcion=row.get("descripcion"),
                investigador_id=str(row["investigador_id"]),
                condicion=row["condicion"],
                prompt_version_id=str(row["prompt_version_id"]) if row.get("prompt_version_id") else None,
                modelo=row.get("modelo"),
                configuracion=row.get("configuracion"),
                estado=row["estado"],
                fecha_inicio=row["fecha_inicio"],
                fecha_fin=row.get("fecha_fin"),
            )
    
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Error al crear la sesión experimental.",
    )


@router.get(
    "/sessions",
    response_model=List[ExperimentSessionListResponse],
    summary="Listar sesiones experimentales"
)
async def list_experiment_sessions(
    investigador_id: Optional[str] = Query(None, description="Filtrar por investigador"),
    condicion: Optional[str] = Query(None, description="Filtrar por condición"),
    estado: Optional[str] = Query(None, description="Filtrar por estado"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    user: dict = Depends(get_current_user),
    sb: SupabaseClient = Depends(get_supabase),
) -> List[ExperimentSessionListResponse]:
    """
    Lista sesiones experimentales con filtros opcionales.
    """
    params = {
        "select": "id,nombre,descripcion,investigador_id,condicion,prompt_version_id,modelo,estado,fecha_inicio,fecha_fin",
        "order": "fecha_inicio.desc",
        "limit": str(limit),
        "offset": str(offset),
    }
    
    if investigador_id:
        params["investigador_id"] = f"eq.{investigador_id}"
    if condicion:
        params["condicion"] = f"eq.{condicion}"
    if estado:
        params["estado"] = f"eq.{estado}"
    
    rows = sb.select("experiment_sessions", params)
    
    return [
        ExperimentSessionListResponse(
            id=str(row["id"]),
            nombre=row["nombre"],
            descripcion=row.get("descripcion"),
            investigador_id=str(row["investigador_id"]),
            condicion=row["condicion"],
            prompt_version_id=str(row["prompt_version_id"]) if row.get("prompt_version_id") else None,
            modelo=row.get("modelo"),
            estado=row["estado"],
            fecha_inicio=row["fecha_inicio"],
            fecha_fin=row.get("fecha_fin"),
        )
        for row in rows
    ]


@router.get(
    "/sessions/{session_id}",
    response_model=ExperimentSessionResponse,
    summary="Obtener sesión experimental por ID"
)
async def get_experiment_session(
    session_id: str,
    user: dict = Depends(get_current_user),
    sb: SupabaseClient = Depends(get_supabase),
) -> ExperimentSessionResponse:
    """
    Obtiene los detalles de una sesión experimental específica.
    """
    rows = sb.select(
        "experiment_sessions",
        {
            "id": f"eq.{session_id}",
            "limit": "1",
        },
    )
    
    if not rows:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sesión experimental no encontrada.",
        )
    
    row = rows[0]
    return ExperimentSessionResponse(
        id=str(row["id"]),
        nombre=row["nombre"],
        descripcion=row.get("descripcion"),
        investigador_id=str(row["investigador_id"]),
        condicion=row["condicion"],
        prompt_version_id=str(row["prompt_version_id"]) if row.get("prompt_version_id") else None,
        modelo=row.get("modelo"),
        configuracion=row.get("configuracion"),
        estado=row["estado"],
        fecha_inicio=row["fecha_inicio"],
        fecha_fin=row.get("fecha_fin"),
    )


@router.patch(
    "/sessions/{session_id}",
    response_model=ExperimentSessionResponse,
    summary="Actualizar sesión experimental"
)
async def update_experiment_session(
    session_id: str,
    body: ExperimentSessionUpdate,
    user: dict = Depends(get_current_investigator),
    sb: SupabaseClient = Depends(get_supabase),
) -> ExperimentSessionResponse:
    """
    Actualiza una sesión experimental existente.
    
    Requiere rol de INVESTIGADOR o ADMIN.
    """
    if not user.get("is_investigator"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo investigadores y administradores pueden actualizar experimentos.",
        )
    
    # Verificar que existe
    existing = sb.select(
        "experiment_sessions",
        {
            "id": f"eq.{session_id}",
            "limit": "1",
        },
    )
    
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sesión experimental no encontrada.",
        )
    
    # Construir datos de actualización
    update_data = {}
    if body.nombre is not None:
        update_data["nombre"] = body.nombre
    if body.descripcion is not None:
        update_data["descripcion"] = body.descripcion
    if body.condicion is not None:
        update_data["condicion"] = body.condicion
    if body.prompt_version_id is not None:
        update_data["prompt_version_id"] = body.prompt_version_id
    if body.modelo is not None:
        update_data["modelo"] = body.modelo
    if body.configuracion is not None:
        update_data["configuracion"] = body.configuracion
    if body.estado is not None:
        update_data["estado"] = body.estado
    if body.fecha_fin is not None:
        update_data["fecha_fin"] = body.fecha_fin.isoformat()
    
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se proporcionaron datos para actualizar.",
        )
    
    # Actualizar
    sb.update(
        "experiment_sessions",
        update_data,
        {"id": f"eq.{session_id}"},
    )
    
    # Retornar la sesión actualizada
    return await get_experiment_session(session_id, user, sb)


# ==============================================================================
# MEDICIONES DE TIEMPO
# ==============================================================================

@router.post(
    "/time-measurements",
    response_model=TimeMeasurementResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar medición de tiempo"
)
async def create_time_measurement(
    body: TimeMeasurementCreate,
    user: dict = Depends(get_current_investigator),
    sb: SupabaseClient = Depends(get_supabase),
) -> TimeMeasurementResponse:
    """
    Registra una medición de tiempo para análisis comparativo.
    
    Requiere rol de INVESTIGADOR o ADMIN.
    """
    if not user.get("is_investigator"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo investigadores y administradores pueden registrar mediciones.",
        )
    
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
    
    # Verificar experiment_session_id si se proporciona
    if body.experiment_session_id:
        session = sb.select(
            "experiment_sessions",
            {
                "id": f"eq.{body.experiment_session_id}",
                "limit": "1",
            },
        )
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sesión experimental no encontrada.",
            )
    
    # Crear medición
    new_measurement = {
        "experiment_session_id": body.experiment_session_id,
        "reunion_id": body.reunion_id,
        "participante_id": body.participante_id,
        "condicion": body.condicion,
        "tiempo_elaboracion_segundos": body.tiempo_elaboracion_segundos,
        "tiempo_revision_segundos": body.tiempo_revision_segundos,
        "tiempo_total_segundos": body.tiempo_total_segundos,
        "errores_detectados": body.errores_detectados,
    }
    
    result = sb.insert("time_measurements", [new_measurement])
    
    if not result or isinstance(result, dict) and "status" in result:
        # Si la inserción fue exitosa, consultar la creada
        created = sb.select(
            "time_measurements",
            {
                "reunion_id": f"eq.{body.reunion_id}",
                "condicion": f"eq.{body.condicion}",
                "order": "fecha_registro.desc",
                "limit": "1",
            },
        )
        if created:
            row = created[0]
            return TimeMeasurementResponse(
                id=str(row["id"]),
                experiment_session_id=str(row["experiment_session_id"]) if row.get("experiment_session_id") else None,
                reunion_id=str(row["reunion_id"]),
                participante_id=str(row["participante_id"]) if row.get("participante_id") else None,
                condicion=row["condicion"],
                tiempo_elaboracion_segundos=row.get("tiempo_elaboracion_segundos"),
                tiempo_revision_segundos=row.get("tiempo_revision_segundos"),
                tiempo_total_segundos=row.get("tiempo_total_segundos"),
                errores_detectados=row["errores_detectados"],
                fecha_registro=row["fecha_registro"],
            )
    
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Error al registrar la medición de tiempo.",
    )


@router.get(
    "/time-measurements",
    response_model=List[TimeMeasurementResponse],
    summary="Listar mediciones de tiempo"
)
async def list_time_measurements(
    experiment_session_id: Optional[str] = Query(None, description="Filtrar por sesión experimental"),
    reunion_id: Optional[str] = Query(None, description="Filtrar por reunión"),
    condicion: Optional[str] = Query(None, description="Filtrar por condición"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    user: dict = Depends(get_current_user),
    sb: SupabaseClient = Depends(get_supabase),
) -> List[TimeMeasurementResponse]:
    """
    Lista mediciones de tiempo con filtros opcionales.
    """
    params = {
        "select": "id,experiment_session_id,reunion_id,participante_id,condicion,tiempo_elaboracion_segundos,tiempo_revision_segundos,tiempo_total_segundos,errores_detectados,fecha_registro",
        "order": "fecha_registro.desc",
        "limit": str(limit),
        "offset": str(offset),
    }
    
    if experiment_session_id:
        params["experiment_session_id"] = f"eq.{experiment_session_id}"
    if reunion_id:
        params["reunion_id"] = f"eq.{reunion_id}"
    if condicion:
        params["condicion"] = f"eq.{condicion}"
    
    rows = sb.select("time_measurements", params)
    
    return [
        TimeMeasurementResponse(
            id=str(row["id"]),
            experiment_session_id=str(row["experiment_session_id"]) if row.get("experiment_session_id") else None,
            reunion_id=str(row["reunion_id"]),
            participante_id=str(row["participante_id"]) if row.get("participante_id") else None,
            condicion=row["condicion"],
            tiempo_elaboracion_segundos=row.get("tiempo_elaboracion_segundos"),
            tiempo_revision_segundos=row.get("tiempo_revision_segundos"),
            tiempo_total_segundos=row.get("tiempo_total_segundos"),
            errores_detectados=row["errores_detectados"],
            fecha_registro=row["fecha_registro"],
        )
        for row in rows
    ]


# ==============================================================================
# RESPUESTAS SUS
# ==============================================================================

@router.post(
    "/sus-responses",
    response_model=SusResponseResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar respuesta SUS"
)
async def create_sus_response(
    body: SusResponseCreate,
    user: dict = Depends(get_current_investigator),
    sb: SupabaseClient = Depends(get_supabase),
) -> SusResponseResponse:
    """
    Registra una respuesta del cuestionario SUS de usabilidad.
    
    El puntaje SUS se calcula automáticamente mediante trigger.
    """
    # Verificar que el usuario existe
    usuario = sb.select(
        "usuarios",
        {
            "id": f"eq.{body.usuario_id}",
            "limit": "1",
        },
    )
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado.",
        )
    
    # Verificar experiment_session_id si se proporciona
    if body.experiment_session_id:
        session = sb.select(
            "experiment_sessions",
            {
                "id": f"eq.{body.experiment_session_id}",
                "limit": "1",
            },
        )
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sesión experimental no encontrada.",
            )
    
    # Crear respuesta SUS
    new_response = {
        "experiment_session_id": body.experiment_session_id,
        "usuario_id": body.usuario_id,
        "q1": body.q1,
        "q2": body.q2,
        "q3": body.q3,
        "q4": body.q4,
        "q5": body.q5,
        "q6": body.q6,
        "q7": body.q7,
        "q8": body.q8,
        "q9": body.q9,
        "q10": body.q10,
        "observaciones": body.observaciones,
    }
    
    result = sb.insert("sus_responses", [new_response])
    
    if not result or isinstance(result, dict) and "status" in result:
        # Si la inserción fue exitosa, consultar la creada
        created = sb.select(
            "sus_responses",
            {
                "usuario_id": f"eq.{body.usuario_id}",
                "order": "fecha_registro.desc",
                "limit": "1",
            },
        )
        if created:
            row = created[0]
            return SusResponseResponse(
                id=str(row["id"]),
                experiment_session_id=str(row["experiment_session_id"]) if row.get("experiment_session_id") else None,
                usuario_id=str(row["usuario_id"]),
                q1=row["q1"],
                q2=row["q2"],
                q3=row["q3"],
                q4=row["q4"],
                q5=row["q5"],
                q6=row["q6"],
                q7=row["q7"],
                q8=row["q8"],
                q9=row["q9"],
                q10=row["q10"],
                observaciones=row.get("observaciones"),
                puntaje_sus=row.get("puntaje_sus"),
                fecha_registro=row["fecha_registro"],
            )
    
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Error al registrar la respuesta SUS.",
    )


@router.get(
    "/sus-responses",
    response_model=List[SusResponseResponse],
    summary="Listar respuestas SUS"
)
async def list_sus_responses(
    experiment_session_id: Optional[str] = Query(None, description="Filtrar por sesión experimental"),
    usuario_id: Optional[str] = Query(None, description="Filtrar por usuario"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    user: dict = Depends(get_current_user),
    sb: SupabaseClient = Depends(get_supabase),
) -> List[SusResponseResponse]:
    """
    Lista respuestas SUS con filtros opcionales.
    """
    params = {
        "select": "id,experiment_session_id,usuario_id,q1,q2,q3,q4,q5,q6,q7,q8,q9,q10,puntaje_sus,observaciones,fecha_registro",
        "order": "fecha_registro.desc",
        "limit": str(limit),
        "offset": str(offset),
    }
    
    if experiment_session_id:
        params["experiment_session_id"] = f"eq.{experiment_session_id}"
    if usuario_id:
        params["usuario_id"] = f"eq.{usuario_id}"
    
    rows = sb.select("sus_responses", params)
    
    return [
        SusResponseResponse(
            id=str(row["id"]),
            experiment_session_id=str(row["experiment_session_id"]) if row.get("experiment_session_id") else None,
            usuario_id=str(row["usuario_id"]),
            q1=row["q1"],
            q2=row["q2"],
            q3=row["q3"],
            q4=row["q4"],
            q5=row["q5"],
            q6=row["q6"],
            q7=row["q7"],
            q8=row["q8"],
            q9=row["q9"],
            q10=row["q10"],
            observaciones=row.get("observaciones"),
            puntaje_sus=row.get("puntaje_sus"),
            fecha_registro=row["fecha_registro"],
        )
        for row in rows
    ]
