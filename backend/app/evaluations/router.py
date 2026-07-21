"""
Router de evaluaciones de resúmenes y gold standard.

Permite evaluar calidad de resúmenes, gestionar gold standard de tareas
y registrar coincidencias para análisis de extracción.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional

from app.core.dependencies import get_current_user, get_current_evaluator, get_current_investigator
from app.core.supabase_client import SupabaseClient, get_supabase
from app.evaluations.schemas import (
    SummaryEvaluationCreate,
    SummaryEvaluationUpdate,
    SummaryEvaluationResponse,
    SummaryEvaluationListResponse,
    ReferenceTaskCreate,
    ReferenceTaskUpdate,
    ReferenceTaskResponse,
    TaskMatchCreate,
    TaskMatchResponse,
)

router = APIRouter(prefix="/evaluations", tags=["Evaluaciones"])


# ==============================================================================
# EVALUACIONES DE RESÚMENES
# ==============================================================================

@router.post(
    "/summaries",
    response_model=SummaryEvaluationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear evaluación de resumen"
)
async def create_evaluation(
    body: SummaryEvaluationCreate,
    user: dict = Depends(get_current_evaluator),
    sb: SupabaseClient = Depends(get_supabase),
) -> SummaryEvaluationResponse:
    """
    Crea una nueva evaluación de resumen.
    
    Requiere rol de EVALUADOR, INVESTIGADOR o ADMIN.
    """
    if not user.get("is_evaluator"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo evaluadores, investigadores y administradores pueden evaluar resúmenes.",
        )
    
    # Verificar que la versión de resumen existe
    summary = sb.select(
        "summary_versions",
        {
            "id": f"eq.{body.summary_version_id}",
            "limit": "1",
        },
    )
    
    if not summary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Versión de resumen no encontrada.",
        )
    
    # Verificar que el evaluador existe
    evaluator = sb.select(
        "usuarios",
        {
            "id": f"eq.{body.evaluador_id}",
            "limit": "1",
        },
    )
    
    if not evaluator:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evaluador no encontrado.",
        )
    
    # Verificar que no exista evaluación previa del mismo evaluador para esta versión
    existing = sb.select(
        "summary_evaluations",
        {
            "summary_version_id": f"eq.{body.summary_version_id}",
            "evaluador_id": f"eq.{body.evaluador_id}",
            "limit": "1",
        },
    )
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Este evaluador ya evaluó esta versión de resumen.",
        )
    
    # Crear evaluación
    new_evaluation = {
        "reunion_id": body.reunion_id,
        "summary_version_id": body.summary_version_id,
        "evaluador_id": body.evaluador_id,
        "fidelidad": body.fidelidad,
        "cobertura": body.cobertura,
        "claridad": body.claridad,
        "coherencia": body.coherencia,
        "concision": body.concision,
        "utilidad": body.utilidad,
        "acuerdos_correctos": body.acuerdos_correctos,
        "responsables_correctos": body.responsables_correctos,
        "fechas_correctas": body.fechas_correctas,
        "omisiones": body.omisiones,
        "afirmaciones_no_respaldadas": body.afirmaciones_no_respaldadas,
        "contradicciones": body.contradicciones,
        "aprobado_sin_cambios": body.aprobado_sin_cambios,
        "observaciones": body.observaciones,
    }
    
    result = sb.insert("summary_evaluations", [new_evaluation])
    
    if not result or isinstance(result, dict) and "status" in result:
        # Si la inserción fue exitosa, consultar la creada
        created = sb.select(
            "summary_evaluations",
            {
                "summary_version_id": f"eq.{body.summary_version_id}",
                "evaluador_id": f"eq.{body.evaluador_id}",
                "limit": "1",
            },
        )
        if created:
            row = created[0]
            return SummaryEvaluationResponse(
                id=str(row["id"]),
                reunion_id=str(row["reunion_id"]),
                summary_version_id=str(row["summary_version_id"]),
                evaluador_id=str(row["evaluador_id"]),
                fidelidad=row.get("fidelidad"),
                cobertura=row.get("cobertura"),
                claridad=row.get("claridad"),
                coherencia=row.get("coherencia"),
                concision=row.get("concision"),
                utilidad=row.get("utilidad"),
                acuerdos_correctos=row.get("acuerdos_correctos"),
                responsables_correctos=row.get("responsables_correctos"),
                fechas_correctas=row.get("fechas_correctas"),
                omisiones=row["omisiones"],
                afirmaciones_no_respaldadas=row["afirmaciones_no_respaldadas"],
                contradicciones=row["contradicciones"],
                aprobado_sin_cambios=row.get("aprobado_sin_cambios"),
                observaciones=row.get("observaciones"),
                fecha_evaluacion=row["fecha_evaluacion"],
            )
    
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Error al crear la evaluación.",
    )


@router.get(
    "/summaries",
    response_model=List[SummaryEvaluationListResponse],
    summary="Listar evaluaciones de resúmenes"
)
async def list_evaluations(
    reunion_id: Optional[str] = Query(None, description="Filtrar por reunión"),
    summary_version_id: Optional[str] = Query(None, description="Filtrar por versión de resumen"),
    evaluador_id: Optional[str] = Query(None, description="Filtrar por evaluador"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    user: dict = Depends(get_current_user),
    sb: SupabaseClient = Depends(get_supabase),
) -> List[SummaryEvaluationListResponse]:
    """
    Lista evaluaciones de resúmenes con filtros opcionales.
    """
    params = {
        "select": "id,reunion_id,summary_version_id,evaluador_id,fidelidad,cobertura,claridad,coherencia,concision,utilidad,acuerdos_correctos,responsables_correctos,fechas_correctas,omisiones,afirmaciones_no_respaldadas,contradicciones,aprobado_sin_cambios,fecha_evaluacion",
        "order": "fecha_evaluacion.desc",
        "limit": str(limit),
        "offset": str(offset),
    }
    
    if reunion_id:
        params["reunion_id"] = f"eq.{reunion_id}"
    if summary_version_id:
        params["summary_version_id"] = f"eq.{summary_version_id}"
    if evaluador_id:
        params["evaluador_id"] = f"eq.{evaluador_id}"
    
    rows = sb.select("summary_evaluations", params)
    
    return [
        SummaryEvaluationListResponse(
            id=str(row["id"]),
            reunion_id=str(row["reunion_id"]),
            summary_version_id=str(row["summary_version_id"]),
            evaluador_id=str(row["evaluador_id"]),
            fidelidad=row.get("fidelidad"),
            cobertura=row.get("cobertura"),
            claridad=row.get("claridad"),
            coherencia=row.get("coherencia"),
            concision=row.get("concision"),
            utilidad=row.get("utilidad"),
            acuerdos_correctos=row.get("acuerdos_correctos"),
            responsables_correctos=row.get("responsables_correctos"),
            fechas_correctas=row.get("fechas_correctas"),
            omisiones=row["omisiones"],
            afirmaciones_no_respaldadas=row["afirmaciones_no_respaldadas"],
            contradicciones=row["contradicciones"],
            aprobado_sin_cambios=row.get("aprobado_sin_cambios"),
            fecha_evaluacion=row["fecha_evaluacion"],
        )
        for row in rows
    ]


@router.get(
    "/summaries/{evaluation_id}",
    response_model=SummaryEvaluationResponse,
    summary="Obtener evaluación de resumen por ID"
)
async def get_evaluation(
    evaluation_id: str,
    user: dict = Depends(get_current_user),
    sb: SupabaseClient = Depends(get_supabase),
) -> SummaryEvaluationResponse:
    """
    Obtiene los detalles de una evaluación específica.
    """
    rows = sb.select(
        "summary_evaluations",
        {
            "id": f"eq.{evaluation_id}",
            "limit": "1",
        },
    )
    
    if not rows:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evaluación no encontrada.",
        )
    
    row = rows[0]
    return SummaryEvaluationResponse(
        id=str(row["id"]),
        reunion_id=str(row["reunion_id"]),
        summary_version_id=str(row["summary_version_id"]),
        evaluador_id=str(row["evaluador_id"]),
        fidelidad=row.get("fidelidad"),
        cobertura=row.get("cobertura"),
        claridad=row.get("claridad"),
        coherencia=row.get("coherencia"),
        concision=row.get("concision"),
        utilidad=row.get("utilidad"),
        acuerdos_correctos=row.get("acuerdos_correctos"),
        responsables_correctos=row.get("responsables_correctos"),
        fechas_correctas=row.get("fechas_correctas"),
        omisiones=row["omisiones"],
        afirmaciones_no_respaldadas=row["afirmaciones_no_respaldadas"],
        contradicciones=row["contradicciones"],
        aprobado_sin_cambios=row.get("aprobado_sin_cambios"),
        observaciones=row.get("observaciones"),
        fecha_evaluacion=row["fecha_evaluacion"],
    )


@router.patch(
    "/summaries/{evaluation_id}",
    response_model=SummaryEvaluationResponse,
    summary="Actualizar evaluación de resumen"
)
async def update_evaluation(
    evaluation_id: str,
    body: SummaryEvaluationUpdate,
    user: dict = Depends(get_current_user),
    sb: SupabaseClient = Depends(get_supabase),
) -> SummaryEvaluationResponse:
    """
    Actualiza una evaluación existente.
    
    Solo el evaluador original o un administrador puede actualizar.
    """
    # Verificar que existe
    existing = sb.select(
        "summary_evaluations",
        {
            "id": f"eq.{evaluation_id}",
            "limit": "1",
        },
    )
    
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evaluación no encontrada.",
        )
    
    row = existing[0]
    
    # Verificar permisos
    if not user.get("is_admin") and str(row["evaluador_id"]) != user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo el evaluador original o un administrador puede actualizar la evaluación.",
        )
    
    # Construir datos de actualización
    update_data = {}
    if body.fidelidad is not None:
        update_data["fidelidad"] = body.fidelidad
    if body.cobertura is not None:
        update_data["cobertura"] = body.cobertura
    if body.claridad is not None:
        update_data["claridad"] = body.claridad
    if body.coherencia is not None:
        update_data["coherencia"] = body.coherencia
    if body.concision is not None:
        update_data["concision"] = body.concision
    if body.utilidad is not None:
        update_data["utilidad"] = body.utilidad
    if body.acuerdos_correctos is not None:
        update_data["acuerdos_correctos"] = body.acuerdos_correctos
    if body.responsables_correctos is not None:
        update_data["responsables_correctos"] = body.responsables_correctos
    if body.fechas_correctas is not None:
        update_data["fechas_correctas"] = body.fechas_correctas
    if body.omisiones is not None:
        update_data["omisiones"] = body.omisiones
    if body.afirmaciones_no_respaldadas is not None:
        update_data["afirmaciones_no_respaldadas"] = body.afirmaciones_no_respaldadas
    if body.contradicciones is not None:
        update_data["contradicciones"] = body.contradicciones
    if body.aprobado_sin_cambios is not None:
        update_data["aprobado_sin_cambios"] = body.aprobado_sin_cambios
    if body.observaciones is not None:
        update_data["observaciones"] = body.observaciones
    
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se proporcionaron datos para actualizar.",
        )
    
    # Actualizar
    sb.update(
        "summary_evaluations",
        update_data,
        {"id": f"eq.{evaluation_id}"},
    )
    
    # Retornar la evaluación actualizada
    return await get_evaluation(evaluation_id, user, sb)


# ==============================================================================
# GOLD STANDARD DE TAREAS
# ==============================================================================

@router.post(
    "/reference-tasks",
    response_model=ReferenceTaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear tarea de referencia (gold standard)"
)
async def create_reference_task(
    body: ReferenceTaskCreate,
    user: dict = Depends(get_current_investigator),
    sb: SupabaseClient = Depends(get_supabase),
) -> ReferenceTaskResponse:
    """
    Crea una tarea de referencia para validación de extracción.
    
    Requiere rol de INVESTIGADOR o ADMIN.
    """
    if not user.get("is_investigator"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo investigadores y administradores pueden crear tareas de referencia.",
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
    
    # Crear tarea de referencia
    new_task = {
        "reunion_id": body.reunion_id,
        "descripcion": body.descripcion,
        "responsable_referencia": body.responsable_referencia,
        "fecha_limite_referencia": body.fecha_limite_referencia,
        "validado": body.validado,
        "creado_por": user["id"],
    }
    
    result = sb.insert("reference_tasks", [new_task])
    
    if not result or isinstance(result, dict) and "status" in result:
        # Si la inserción fue exitosa, consultar la creada
        created = sb.select(
            "reference_tasks",
            {
                "reunion_id": f"eq.{body.reunion_id}",
                "descripcion": f"eq.{body.descripcion}",
                "order": "fecha_creacion.desc",
                "limit": "1",
            },
        )
        if created:
            row = created[0]
            return ReferenceTaskResponse(
                id=str(row["id"]),
                reunion_id=str(row["reunion_id"]),
                descripcion=row["descripcion"],
                responsable_referencia=row.get("responsable_referencia"),
                fecha_limite_referencia=row.get("fecha_limite_referencia"),
                validado=row["validado"],
                creado_por=str(row["creado_por"]),
                fecha_creacion=row["fecha_creacion"],
            )
    
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Error al crear la tarea de referencia.",
    )


@router.get(
    "/reference-tasks",
    response_model=List[ReferenceTaskResponse],
    summary="Listar tareas de referencia"
)
async def list_reference_tasks(
    reunion_id: Optional[str] = Query(None, description="Filtrar por reunión"),
    validado: Optional[bool] = Query(None, description="Filtrar por validación"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    user: dict = Depends(get_current_user),
    sb: SupabaseClient = Depends(get_supabase),
) -> List[ReferenceTaskResponse]:
    """
    Lista tareas de referencia con filtros opcionales.
    """
    params = {
        "select": "id,reunion_id,descripcion,responsable_referencia,fecha_limite_referencia,validado,creado_por,fecha_creacion",
        "order": "fecha_creacion.desc",
        "limit": str(limit),
        "offset": str(offset),
    }
    
    if reunion_id:
        params["reunion_id"] = f"eq.{reunion_id}"
    if validado is not None:
        params["validado"] = f"eq.{validado}"
    
    rows = sb.select("reference_tasks", params)
    
    return [
        ReferenceTaskResponse(
            id=str(row["id"]),
            reunion_id=str(row["reunion_id"]),
            descripcion=row["descripcion"],
            responsable_referencia=row.get("responsable_referencia"),
            fecha_limite_referencia=row.get("fecha_limite_referencia"),
            validado=row["validado"],
            creado_por=str(row["creado_por"]),
            fecha_creacion=row["fecha_creacion"],
        )
        for row in rows
    ]


@router.patch(
    "/reference-tasks/{task_id}",
    response_model=ReferenceTaskResponse,
    summary="Actualizar tarea de referencia"
)
async def update_reference_task(
    task_id: str,
    body: ReferenceTaskUpdate,
    user: dict = Depends(get_current_investigator),
    sb: SupabaseClient = Depends(get_supabase),
) -> ReferenceTaskResponse:
    """
    Actualiza una tarea de referencia existente.
    
    Requiere rol de INVESTIGADOR o ADMIN.
    """
    if not user.get("is_investigator"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo investigadores y administradores pueden actualizar tareas de referencia.",
        )
    
    # Verificar que existe
    existing = sb.select(
        "reference_tasks",
        {
            "id": f"eq.{task_id}",
            "limit": "1",
        },
    )
    
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarea de referencia no encontrada.",
        )
    
    # Construir datos de actualización
    update_data = {}
    if body.descripcion is not None:
        update_data["descripcion"] = body.descripcion
    if body.responsable_referencia is not None:
        update_data["responsable_referencia"] = body.responsable_referencia
    if body.fecha_limite_referencia is not None:
        update_data["fecha_limite_referencia"] = body.fecha_limite_referencia
    if body.validado is not None:
        update_data["validado"] = body.validado
    
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se proporcionaron datos para actualizar.",
        )
    
    # Actualizar
    sb.update(
        "reference_tasks",
        update_data,
        {"id": f"eq.{task_id}"},
    )
    
    # Retornar la tarea actualizada
    rows = sb.select(
        "reference_tasks",
        {
            "id": f"eq.{task_id}",
            "limit": "1",
        },
    )
    
    if rows:
        row = rows[0]
        return ReferenceTaskResponse(
            id=str(row["id"]),
            reunion_id=str(row["reunion_id"]),
            descripcion=row["descripcion"],
            responsable_referencia=row.get("responsable_referencia"),
            fecha_limite_referencia=row.get("fecha_limite_referencia"),
            validado=row["validado"],
            creado_por=str(row["creado_por"]),
            fecha_creacion=row["fecha_creacion"],
        )
    
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Error al actualizar la tarea de referencia.",
    )


# ==============================================================================
# COINCIDENCIAS DE TAREAS
# ==============================================================================

@router.post(
    "/task-matches",
    response_model=TaskMatchResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar coincidencia de tarea"
)
async def create_task_match(
    body: TaskMatchCreate,
    user: dict = Depends(get_current_investigator),
    sb: SupabaseClient = Depends(get_supabase),
) -> TaskMatchResponse:
    """
    Registra una coincidencia entre tarea detectada y gold standard.
    
    Requiere rol de INVESTIGADOR o ADMIN.
    """
    if not user.get("is_investigator"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo investigadores y administradores pueden registrar coincidencias.",
        )
    
    # Verificar que la tarea de referencia existe
    ref_task = sb.select(
        "reference_tasks",
        {
            "id": f"eq.{body.reference_task_id}",
            "limit": "1",
        },
    )
    
    if not ref_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarea de referencia no encontrada.",
        )
    
    # Crear coincidencia
    new_match = {
        "reunion_id": body.reunion_id,
        "ai_execution_id": body.ai_execution_id,
        "reference_task_id": body.reference_task_id,
        "detected_task_id": body.detected_task_id,
        "resultado": body.resultado,
        "similitud": body.similitud,
        "validado_por": body.validado_por,
        "observaciones": body.observaciones,
    }
    
    result = sb.insert("task_evaluation_matches", [new_match])
    
    if not result or isinstance(result, dict) and "status" in result:
        # Si la inserción fue exitosa, consultar la creada
        created = sb.select(
            "task_evaluation_matches",
            {
                "reference_task_id": f"eq.{body.reference_task_id}",
                "resultado": f"eq.{body.resultado}",
                "order": "fecha_registro.desc",
                "limit": "1",
            },
        )
        if created:
            row = created[0]
            return TaskMatchResponse(
                id=str(row["id"]),
                reunion_id=str(row["reunion_id"]),
                ai_execution_id=str(row["ai_execution_id"]) if row.get("ai_execution_id") else None,
                reference_task_id=str(row["reference_task_id"]),
                detected_task_id=str(row["detected_task_id"]) if row.get("detected_task_id") else None,
                resultado=row["resultado"],
                similitud=row.get("similitud"),
                observaciones=row.get("observaciones"),
                validado_por=str(row["validado_por"]) if row.get("validado_por") else None,
                fecha_registro=row["fecha_registro"],
            )
    
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Error al registrar la coincidencia.",
    )


@router.get(
    "/task-matches",
    response_model=List[TaskMatchResponse],
    summary="Listar coincidencias de tareas"
)
async def list_task_matches(
    reunion_id: Optional[str] = Query(None, description="Filtrar por reunión"),
    reference_task_id: Optional[str] = Query(None, description="Filtrar por tarea de referencia"),
    resultado: Optional[str] = Query(None, description="Filtrar por resultado (TP, FP, FN, TN)"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    user: dict = Depends(get_current_user),
    sb: SupabaseClient = Depends(get_supabase),
) -> List[TaskMatchResponse]:
    """
    Lista coincidencias de tareas con filtros opcionales.
    """
    params = {
        "select": "id,reunion_id,ai_execution_id,reference_task_id,detected_task_id,resultado,similitud,validado_por,observaciones,fecha_registro",
        "order": "fecha_registro.desc",
        "limit": str(limit),
        "offset": str(offset),
    }
    
    if reunion_id:
        params["reunion_id"] = f"eq.{reunion_id}"
    if reference_task_id:
        params["reference_task_id"] = f"eq.{reference_task_id}"
    if resultado:
        params["resultado"] = f"eq.{resultado}"
    
    rows = sb.select("task_evaluation_matches", params)
    
    return [
        TaskMatchResponse(
            id=str(row["id"]),
            reunion_id=str(row["reunion_id"]),
            ai_execution_id=str(row["ai_execution_id"]) if row.get("ai_execution_id") else None,
            reference_task_id=str(row["reference_task_id"]),
            detected_task_id=str(row["detected_task_id"]) if row.get("detected_task_id") else None,
            resultado=row["resultado"],
            similitud=row.get("similitud"),
            observaciones=row.get("observaciones"),
            validado_por=str(row["validado_por"]) if row.get("validado_por") else None,
            fecha_registro=row["fecha_registro"],
        )
        for row in rows
    ]
