"""Router FastAPI para el módulo de análisis estadístico."""

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text

from app.analyses.execution import execute_analysis, select_statistical_test
from app.analyses.schemas import (
    AnalysisExecutionRequest,
    AnalysisRerunRequest,
    AnalysisResultResponse,
    DataQualityValidationRequest,
    DataQualityValidationResponse,
    StatisticalAnalysisCreate,
    StatisticalAnalysisResponse,
    StatisticalAnalysisUpdate,
)
from app.core.dependencies import get_current_investigator, get_current_user
from app.core.supabase_client import get_supabase

router = APIRouter(prefix="/api/v1/research/analyses", tags=["Análisis Estadístico"])


@router.post("/validate", response_model=DataQualityValidationResponse)
async def validate_data(
    request: DataQualityValidationRequest,
    user: dict = Depends(get_current_user),
) -> DataQualityValidationResponse:
    """
    Valida la calidad de los datos antes de ejecutar un análisis estadístico.
    
    Realiza verificaciones exhaustivas según Sección 17.1.2 de las especificaciones.
    """
    validation_result = validate_data_quality(
        data=request.data,
        test_type=request.test_type,
        design=request.design,
        min_observations=request.min_observations,
    )
    
    return DataQualityValidationResponse(**validation_result)


@router.post("/select-test")
async def select_test(
    variable_type: str,
    n_conditions: int,
    design: str,
    sample_size: int,
    is_normal: bool | None = None,
    equal_variances: bool | None = None,
    user: dict = Depends(get_current_user),
) -> dict[str, Any]:
    """
    Selector automático de prueba estadística según Sección 18.
    
    Analiza el tipo de variable, número de condiciones y diseño para sugerir
    la prueba estadística apropiada.
    """
    selection = select_statistical_test(
        variable_type=variable_type,
        n_conditions=n_conditions,
        design=design,
        sample_size=sample_size,
        is_normal=is_normal,
        equal_variances=equal_variances,
    )
    
    return selection


@router.post("", response_model=StatisticalAnalysisResponse, status_code=status.HTTP_201_CREATED)
async def create_analysis(
    analysis: StatisticalAnalysisCreate,
    user: dict = Depends(get_current_investigator),
) -> StatisticalAnalysisResponse:
    """Crea un nuevo análisis estadístico."""
    supabase = get_supabase()
    
    # Generar hash inicial de datos
    import hashlib
    import json
    
    data_to_hash = analysis.filtros.copy()
    data_to_hash.update(analysis.configuracion)
    datos_hash = hashlib.sha256(json.dumps(data_to_hash, sort_keys=True).encode()).hexdigest()
    
    # Insertar análisis en base de datos
    analysis_data = {
        "nombre": analysis.nombre,
        "objetivo": analysis.objetivo,
        "variable_resultado": analysis.variable_resultado,
        "variable_grupo": analysis.variable_grupo,
        "diseno": analysis.diseno,
        "prueba_solicitada": analysis.prueba_solicitada,
        "prueba_ejecutada": analysis.prueba_solicitada or "PENDIENTE",
        "alpha": analysis.alpha,
        "correccion_multiple": analysis.correccion_multiple,
        "filtros": analysis.filtros,
        "configuracion": analysis.configuracion,
        "estado": "PLANIFICADO",
        "datos_hash": datos_hash,
        "codigo_version": "1.0.0",
        "creado_por": user["id"],
    }
    
    result = supabase.table("statistical_analyses").insert(analysis_data).select().single()
    
    if result.data is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al crear el análisis estadístico."
        )
    
    return StatisticalAnalysisResponse(**result.data)


@router.get("", response_model=list[StatisticalAnalysisResponse])
async def list_analyses(
    experiment_session_id: UUID | None = None,
    estado: str | None = None,
    user: dict = Depends(get_current_investigator),
) -> list[StatisticalAnalysisResponse]:
    """Lista los análisis estadísticos del investigador."""
    supabase = get_supabase()
    
    query = supabase.table("statistical_analyses").select("*")
    
    # Filtrar por sesión experimental si se proporciona
    if experiment_session_id:
        query = query.eq("experiment_session_id", str(experiment_session_id))
    
    # Filtrar por estado si se proporciona
    if estado:
        query = query.eq("estado", estado)
    
    # Filtrar por investigador actual
    query = query.eq("creado_por", user["id"])
    
    # Ordenar por fecha de creación descendente
    query = query.order("fecha_creacion", desc=True)
    
    result = query.execute()
    
    return [StatisticalAnalysisResponse(**item) for item in result.data]


@router.get("/{analysis_id}", response_model=StatisticalAnalysisResponse)
async def get_analysis(
    analysis_id: UUID,
    user: dict = Depends(get_current_investigator),
) -> StatisticalAnalysisResponse:
    """Obtiene un análisis estadístico específico."""
    supabase = get_supabase()
    
    result = supabase.table("statistical_analyses").select("*").eq("id", str(analysis_id)).single()
    
    if result.data is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Análisis estadístico no encontrado."
        )
    
    # Verificar que el usuario sea el creador o admin
    if result.data["creado_por"] != user["id"] and user.get("rol") != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para ver este análisis."
        )
    
    return StatisticalAnalysisResponse(**result.data)


@router.patch("/{analysis_id}", response_model=StatisticalAnalysisResponse)
async def update_analysis(
    analysis_id: UUID,
    analysis_update: StatisticalAnalysisUpdate,
    user: dict = Depends(get_current_investigator),
) -> StatisticalAnalysisResponse:
    """Actualiza un análisis estadístico."""
    supabase = get_supabase()
    
    # Verificar que el análisis existe y pertenezca al usuario
    existing = supabase.table("statistical_analyses").select("*").eq("id", str(analysis_id)).single()
    
    if existing.data is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Análisis estadístico no encontrado."
        )
    
    if existing.data["creado_por"] != user["id"] and user.get("rol") != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para actualizar este análisis."
        )
    
    # Actualizar solo campos proporcionados
    update_data = analysis_update.model_dump(exclude_unset=True)
    
    result = supabase.table("statistical_analyses").update(update_data).eq("id", str(analysis_id)).select().single()
    
    return StatisticalAnalysisResponse(**result.data)


@router.post("/{analysis_id}/rerun", response_model=StatisticalAnalysisResponse)
async def rerun_analysis(
    analysis_id: UUID,
    request: AnalysisRerunRequest,
    user: dict = Depends(get_current_investigator),
) -> StatisticalAnalysisResponse:
    """Reejecuta un análisis estadístico existente."""
    supabase = get_supabase()
    
    # Verificar que el análisis existe
    existing = supabase.table("statistical_analyses").select("*").eq("id", str(analysis_id)).single()
    
    if existing.data is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Análisis estadístico no encontrado."
        )
    
    if existing.data["creado_por"] != user["id"] and user.get("rol") != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para reejecutar este análisis."
        )
    
    # Verificar si los datos han cambiado (si no se fuerza reejecución)
    if not request.force:
        # Aquí se podría verificar si los datos de origen han cambiado
        # Por ahora, siempre permitimos reejecución
        pass
    
    # Actualizar estado a EJECUTANDO
    supabase.table("statistical_analyses").update({"estado": "EJECUTANDO"}).eq("id", str(analysis_id)).execute()
    
    try:
        # Ejecutar análisis real
        execution_result = execute_analysis(
            data=existing.data["filtros"],
            test_type=existing.data["prueba_ejecutada"] or "welch_t_test",
            design=existing.data["diseno"].lower(),
            alpha=existing.data["alpha"],
            correction=existing.data["correccion_multiple"],
        )
        
        # Guardar resultados
        result_data = {
            "analysis_id": str(analysis_id),
            "resultado": execution_result["resultado"],
            "descriptivos": execution_result.get("descriptivos"),
            "supuestos": execution_result.get("supuestos"),
            "efecto": execution_result.get("efecto"),
            "intervalos": execution_result.get("intervalos"),
            "advertencias": execution_result.get("advertencias"),
            "interpretacion": execution_result.get("interpretacion"),
        }
        
        # Insertar o actualizar resultados
        existing_result = supabase.table("statistical_analysis_results").select("*").eq("analysis_id", str(analysis_id)).single()
        
        if existing_result.data:
            supabase.table("statistical_analysis_results").update(result_data).eq("analysis_id", str(analysis_id)).execute()
        else:
            supabase.table("statistical_analysis_results").insert(result_data).execute()
        
        # Actualizar estado a COMPLETADO
        final_status = "COMPLETADO" if execution_result["status"] == "ok" else "ERROR"
        result = supabase.table("statistical_analyses").update(
            {"estado": final_status, "fecha_ejecucion": "NOW()"}
        ).eq("id", str(analysis_id)).select().single()
        
    except Exception as e:
        # Actualizar estado a ERROR
        result = supabase.table("statistical_analyses").update(
            {"estado": "ERROR"}
        ).eq("id", str(analysis_id)).select().single()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al ejecutar el análisis: {str(e)}"
        )
    
    return StatisticalAnalysisResponse(**result.data)


@router.get("/{analysis_id}/results", response_model=AnalysisResultResponse)
async def get_analysis_results(
    analysis_id: UUID,
    user: dict = Depends(get_current_investigator),
) -> AnalysisResultResponse:
    """Obtiene los resultados de un análisis estadístico."""
    supabase = get_supabase()
    
    # Verificar que el análisis existe y pertenezca al usuario
    analysis = supabase.table("statistical_analyses").select("*").eq("id", str(analysis_id)).single()
    
    if analysis.data is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Análisis estadístico no encontrado."
        )
    
    if analysis.data["creado_por"] != user["id"] and user.get("rol") != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para ver los resultados de este análisis."
        )
    
    # Buscar resultados
    result = supabase.table("statistical_analysis_results").select("*").eq("analysis_id", str(analysis_id)).single()
    
    if result.data is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resultados no encontrados. El análisis puede no haber sido ejecutado aún."
        )
    
    return AnalysisResultResponse(**result.data)
