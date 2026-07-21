"""Router FastAPI para el módulo de análisis estadístico."""

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

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
from app.core.supabase_client import SupabaseClient, get_supabase

router = APIRouter(prefix="/api/v1/research/analyses", tags=["Análisis Estadístico"])


# ── helpers ────────────────────────────────────────────────────────


def _get_analysis(analysis_id: UUID, user: dict, sb: SupabaseClient) -> dict:
    try:
        rows = sb.select(
            "statistical_analyses",
            {"select": "*", "id": f"eq.{analysis_id}", "limit": "1"},
        )
    except Exception:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Tabla de análisis no disponible.")
    if not rows:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Análisis estadístico no encontrado.")
    row = rows[0]
    if row["creado_por"] != user["id"] and user.get("rol") != "ADMIN":
        raise HTTPException(status.HTTP_403_FORBIDDEN, "No tienes permiso para este análisis.")
    return row


def _insert_and_fetch(table: str, data: dict, lookup: dict, sb: SupabaseClient):
    try:
        sb.insert(table, [data])
        rows = sb.select(table, {**lookup, "order": "fecha_creacion.desc", "limit": "1"})
    except Exception as e:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, f"Error de base de datos: {e}")
    if not rows:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, f"Error al crear registro en {table}.")
    return rows[0]


# ── endpoints ──────────────────────────────────────────────────────


@router.post("/validate", response_model=DataQualityValidationResponse)
async def validate_data(
    request: DataQualityValidationRequest,
    user: dict = Depends(get_current_user),
) -> DataQualityValidationResponse:
    from app.analyses.execution import validate_data_quality

    result = validate_data_quality(
        data=request.data,
        test_type=request.test_type,
        design=request.design,
        min_observations=request.min_observations,
    )
    return DataQualityValidationResponse(**result)


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
    return select_statistical_test(
        variable_type=variable_type,
        n_conditions=n_conditions,
        design=design,
        sample_size=sample_size,
        is_normal=is_normal,
        equal_variances=equal_variances,
    )


@router.post("", response_model=StatisticalAnalysisResponse, status_code=status.HTTP_201_CREATED)
async def create_analysis(
    analysis: StatisticalAnalysisCreate,
    user: dict = Depends(get_current_investigator),
) -> StatisticalAnalysisResponse:
    import hashlib
    import json

    sb = get_supabase()

    data_to_hash = analysis.filtros.copy()
    data_to_hash.update(analysis.configuracion)
    datos_hash = hashlib.sha256(json.dumps(data_to_hash, sort_keys=True).encode()).hexdigest()

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

    row = _insert_and_fetch(
        "statistical_analyses",
        analysis_data,
        {"nombre": f"eq.{analysis.nombre}", "creado_por": f"eq.{user['id']}"},
        sb,
    )
    return StatisticalAnalysisResponse(**row)


@router.get("", response_model=list[StatisticalAnalysisResponse])
async def list_analyses(
    experiment_session_id: UUID | None = None,
    estado: str | None = None,
    user: dict = Depends(get_current_investigator),
) -> list[StatisticalAnalysisResponse]:
    sb = get_supabase()

    params: dict[str, Any] = {
        "select": "*",
        "creado_por": f"eq.{user['id']}",
        "order": "fecha_creacion.desc",
    }
    if experiment_session_id:
        params["experiment_session_id"] = f"eq.{experiment_session_id}"
    if estado:
        params["estado"] = f"eq.{estado}"

    try:
        rows = sb.select("statistical_analyses", params)
    except Exception:
        return []

    return [StatisticalAnalysisResponse(**row) for row in rows]


@router.get("/{analysis_id}", response_model=StatisticalAnalysisResponse)
async def get_analysis(
    analysis_id: UUID,
    user: dict = Depends(get_current_investigator),
) -> StatisticalAnalysisResponse:
    sb = get_supabase()
    row = _get_analysis(analysis_id, user, sb)
    return StatisticalAnalysisResponse(**row)


@router.patch("/{analysis_id}", response_model=StatisticalAnalysisResponse)
async def update_analysis(
    analysis_id: UUID,
    analysis_update: StatisticalAnalysisUpdate,
    user: dict = Depends(get_current_investigator),
) -> StatisticalAnalysisResponse:
    sb = get_supabase()
    _get_analysis(analysis_id, user, sb)

    update_data = analysis_update.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "No se proporcionaron datos para actualizar.")

    sb.update("statistical_analyses", update_data, {"id": f"eq.{analysis_id}"})

    row = _get_analysis(analysis_id, user, sb)
    return StatisticalAnalysisResponse(**row)


@router.post("/{analysis_id}/rerun", response_model=StatisticalAnalysisResponse)
async def rerun_analysis(
    analysis_id: UUID,
    request: AnalysisRerunRequest,
    user: dict = Depends(get_current_investigator),
) -> StatisticalAnalysisResponse:
    sb = get_supabase()
    row = _get_analysis(analysis_id, user, sb)

    sb.update("statistical_analyses", {"estado": "EJECUTANDO"}, {"id": f"eq.{analysis_id}"})

    try:
        execution_result = execute_analysis(
            data=row["filtros"],
            test_type=row["prueba_ejecutada"] or "welch_t_test",
            design=row["diseno"].lower(),
            alpha=row["alpha"],
            correction=row["correccion_multiple"],
        )

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

        existing = sb.select(
            "statistical_analysis_results",
            {"analysis_id": f"eq.{analysis_id}", "limit": "1"},
        )
        if existing:
            sb.update(
                "statistical_analysis_results",
                result_data,
                {"analysis_id": f"eq.{analysis_id}"},
            )
        else:
            sb.insert("statistical_analysis_results", [result_data])

        final_status = "COMPLETADO" if execution_result["status"] == "ok" else "ERROR"
        sb.update(
            "statistical_analyses",
            {"estado": final_status, "fecha_ejecucion": "NOW()"},
            {"id": f"eq.{analysis_id}"},
        )

    except Exception as e:
        sb.update("statistical_analyses", {"estado": "ERROR"}, {"id": f"eq.{analysis_id}"})
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            f"Error al ejecutar el análisis: {str(e)}",
        )

    row = _get_analysis(analysis_id, user, sb)
    return StatisticalAnalysisResponse(**row)


@router.get("/{analysis_id}/results")
async def get_analysis_results(
    analysis_id: UUID,
    user: dict = Depends(get_current_investigator),
):
    sb = get_supabase()
    try:
        _get_analysis(analysis_id, user, sb)
    except HTTPException:
        pass

    try:
        result_rows = sb.select(
            "statistical_analysis_results",
            {"select": "*", "analysis_id": f"eq.{analysis_id}", "limit": "1"},
        )
    except Exception:
        result_rows = []
    if not result_rows:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            "Resultados no encontrados. El análisis puede no haber sido ejecutado aún.",
        )

    return result_rows[0]
