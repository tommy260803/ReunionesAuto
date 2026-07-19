"""
Router de métricas.

Permite consultar el historial de ejecuciones y tiempos de respuesta de n8n.
"""

from collections import defaultdict
from datetime import date, datetime, time, timedelta, timezone
import hashlib
import json
import math
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.dependencies import get_current_admin
from app.core.config import settings
from app.core.supabase_client import SupabaseClient, get_supabase
from app.metrics.schemas import (
    ChiSquareResult,
    N8nMetricResponse,
    N8nMetricsStatsResponse,
    PeriodSampleMetadata,
    StatisticalAnalysisMetadata,
    StatisticalResponse,
    TTestResult,
)
from app.metrics.statistics import contingency_analysis, welch_t_test

router = APIRouter(prefix="/metrics", tags=["Métricas"])
_ALLOWED_DATA_SOURCES = frozenset({"production", "demo", "test"})


def get_metrics_supabase() -> SupabaseClient:
    """Use the service role for the RLS-protected telemetry table when available."""
    return get_supabase(service_role=bool(settings.SUPABASE_SERVICE_ROLE_KEY))


def serialize_metric(row: dict) -> N8nMetricResponse:
    return N8nMetricResponse(
        id=str(row["id"]),
        endpoint=row["endpoint"],
        tiempo_respuesta=float(row.get("tiempo_respuesta", 0.0)),
        estado=row.get("estado", ""),
        fecha=row.get("fecha", ""),
        codigo_estado=row.get("codigo_estado"),
        reunion_id=str(row["reunion_id"]) if row.get("reunion_id") else None,
        tamano_respuesta=row.get("tamano_respuesta"),
        detalles=row.get("detalles"),
    )

@router.get("/n8n", response_model=List[N8nMetricResponse], summary="Obtener métricas de n8n")
async def get_n8n_metrics(
    admin: dict = Depends(get_current_admin),
    sb: SupabaseClient = Depends(get_metrics_supabase)
):
    """
    Retorna el historial de métricas registradas para n8n.
    Solo accesible para administradores.
    """
    rows = sb.select(
        "metricas_n8n", 
        {
            "select": "id,endpoint,tiempo_respuesta,estado,fecha,codigo_estado,reunion_id,tamano_respuesta,detalles",
            "order": "fecha.desc",
            "data_source": "eq.production",
            "is_terminal": "eq.true",
            "limit": "100"
        }
    )
    
    return [serialize_metric(row) for row in rows]


@router.get("/n8n/stats", response_model=N8nMetricsStatsResponse, summary="Obtener estadísticas de n8n")
async def get_n8n_metrics_stats(
    admin: dict = Depends(get_current_admin),
    sb: SupabaseClient = Depends(get_metrics_supabase),
):
    rows = sb.select(
        "metricas_n8n",
        {
            "select": "id,endpoint,tiempo_respuesta,estado,fecha,codigo_estado,reunion_id,tamano_respuesta,detalles,outcome,end_to_end_latency_seconds",
            "order": "fecha.desc",
            "data_source": "eq.production",
            "is_terminal": "eq.true",
            "outcome": "in.(success,error,timeout)",
            "limit": "500",
        },
    )
    endpoint_values: dict[str, list[float]] = defaultdict(list)
    day_counts: dict[str, int] = defaultdict(int)
    successful = 0
    for row in rows:
        if row.get("outcome") == "success":
            successful += 1
            latency = row.get("end_to_end_latency_seconds")
            try:
                latency_value = float(latency)
            except (TypeError, ValueError, OverflowError):
                latency_value = 0.0
            if math.isfinite(latency_value) and latency_value > 0:
                endpoint_values[row.get("endpoint", "Sin endpoint")].append(latency_value)
        try:
            day_counts[datetime.fromisoformat(row.get("fecha", "").replace("Z", "+00:00")).date().isoformat()] += 1
        except (TypeError, ValueError):
            continue

    today = datetime.now().date()
    days = [(today - timedelta(days=offset)).isoformat() for offset in range(6, -1, -1)]
    total = len(rows)
    successful_latencies = [value for values in endpoint_values.values() for value in values]
    average = sum(successful_latencies) / len(successful_latencies) if successful_latencies else 0.0
    return N8nMetricsStatsResponse(
        total_peticiones=total,
        exitosas=successful,
        fallidas=total - successful,
        tasa_exito=round(successful / total * 100, 1) if total else 0.0,
        tiempo_promedio=round(average, 2),
        por_dia=[{"fecha": day, "cantidad": day_counts[day]} for day in days],
        por_endpoint=[
            {"endpoint": endpoint, "tiempo_promedio": round(sum(values) / len(values), 2), "cantidad": len(values)}
            for endpoint, values in sorted(endpoint_values.items())
        ],
        logs=[serialize_metric(row) for row in rows[:50]],
    )


@router.get("/n8n/endpoints", response_model=List[str], summary="Listar endpoints con telemetría")
async def get_n8n_metric_endpoints(
    data_source: str = Query("production", min_length=1),
    admin: dict = Depends(get_current_admin),
    sb: SupabaseClient = Depends(get_metrics_supabase),
):
    data_source = data_source.strip()
    if data_source not in _ALLOWED_DATA_SOURCES:
        raise HTTPException(status_code=400, detail="data_source no es válido.")
    snapshot_at = datetime.now(timezone.utc)
    endpoints: set[str] = set()
    offset = 0
    while True:
        page = sb.select(
            "metricas_n8n",
            {
                "select": "id,endpoint,started_at",
                "data_source": f"eq.{data_source}",
                "is_terminal": "eq.true",
                "outcome": "in.(success,error,timeout)",
                "completed_at": f"lte.{_utc_iso(snapshot_at)}",
                "order": "started_at.asc,id.asc",
                "limit": str(_PAGE_SIZE),
                "offset": str(offset),
            },
        )
        if not page:
            break
        endpoints.update(
            str(row.get("endpoint") or "").strip()
            for row in page
            if str(row.get("endpoint") or "").strip()
        )
        offset += len(page)
    return sorted(endpoints)


@router.get("/n8n/statistics", response_model=StatisticalResponse, summary="Análisis estadístico inferencial")
async def get_n8n_statistics(
    start_a: date,
    end_a: date,
    start_b: date,
    end_b: date,
    endpoint_filter: str = Query(..., min_length=1),
    data_source: str = Query("production", min_length=1),
    admin: dict = Depends(get_current_admin),
    sb: SupabaseClient = Depends(get_metrics_supabase),
):
    """Compare two non-overlapping UTC calendar-date periods."""
    endpoint_filter = endpoint_filter.strip()
    data_source = data_source.strip()
    if not endpoint_filter:
        raise HTTPException(status_code=400, detail="endpoint_filter no puede estar vacío.")
    if not data_source:
        raise HTTPException(status_code=400, detail="data_source no puede estar vacío.")
    if data_source not in _ALLOWED_DATA_SOURCES:
        raise HTTPException(status_code=400, detail="data_source no es válido.")
    if start_a > end_a or start_b > end_b:
        raise HTTPException(status_code=400, detail="El inicio de un periodo no puede ser posterior a su fin.")

    try:
        start_a_utc = datetime.combine(start_a, time.min, tzinfo=timezone.utc)
        end_a_utc = datetime.combine(end_a + timedelta(days=1), time.min, tzinfo=timezone.utc)
        start_b_utc = datetime.combine(start_b, time.min, tzinfo=timezone.utc)
        end_b_utc = datetime.combine(end_b + timedelta(days=1), time.min, tzinfo=timezone.utc)
    except OverflowError:
        raise HTTPException(status_code=400, detail="El rango de fechas está fuera de los límites permitidos.")

    if end_a_utc > start_b_utc:
        raise HTTPException(
            status_code=400,
            detail="El Periodo A debe finalizar antes de que comience el Periodo B.",
        )

    snapshot_at = datetime.now(timezone.utc)
    try:
        rows_a, pages_a = _select_metric_period(
            sb, endpoint_filter, data_source, start_a_utc, end_a_utc, snapshot_at
        )
        rows_b, pages_b = _select_metric_period(
            sb, endpoint_filter, data_source, start_b_utc, end_b_utc, snapshot_at
        )
    except Exception:
        raise HTTPException(
            status_code=502,
            detail="No se pudieron consultar las métricas para el análisis.",
        )

    sample_a = _build_period_sample("a", start_a_utc, end_a_utc, rows_a, pages_a)
    sample_b = _build_period_sample("b", start_b_utc, end_b_utc, rows_b, pages_b)
    t_calculation = welch_t_test(sample_a["latencies"], sample_b["latencies"])
    contingency = contingency_analysis(
        sample_a["success"],
        sample_a["failure"],
        sample_b["success"],
        sample_b["failure"],
    )

    return StatisticalResponse(
        t_test=_to_t_test_response(t_calculation),
        chi_square=_to_contingency_response(contingency),
        metadata=StatisticalAnalysisMetadata(
            protocol_version="1.0",
            generated_at_utc=datetime.now(timezone.utc),
            snapshot_at_utc=snapshot_at,
            timezone="UTC",
            alpha=0.05,
            endpoint_filter=endpoint_filter,
            data_source=data_source,
            terminal_only=True,
            date_semantics="inclusive_dates_queried_as_utc_half_open_intervals",
            latency_population="successful_terminal_end_to_end",
            outcome_population="recognized_terminal_outcomes",
            effect_direction="period_b_minus_or_versus_period_a",
            time_field="started_at",
            success_states=sorted(_SUCCESS_STATES),
            failure_states=sorted(_FAILURE_STATES),
            periods=[sample_a["metadata"], sample_b["metadata"]],
        ),
    )


_PAGE_SIZE = 1000
_SUCCESS_STATES = frozenset({"success"})
_FAILURE_STATES = frozenset({"error", "timeout"})


def _utc_iso(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _select_metric_period(
    sb: SupabaseClient,
    endpoint_filter: str,
    data_source: str,
    start_utc: datetime,
    end_utc: datetime,
    snapshot_utc: datetime | None = None,
) -> tuple[list[dict], int]:
    """Fetch every matching row using deterministic PostgREST limit/offset pages."""
    rows: list[dict] = []
    offset = 0
    pages = 0
    snapshot_utc = snapshot_utc or datetime.now(timezone.utc)
    while True:
        page = sb.select(
            "metricas_n8n",
            {
                "select": "id,endpoint,end_to_end_latency_seconds,outcome,started_at,completed_at,data_source,is_terminal,workflow_version,attempt_number",
                "endpoint": f"eq.{endpoint_filter}",
                "data_source": f"eq.{data_source}",
                "is_terminal": "eq.true",
                "and": (
                    f"(started_at.gte.{_utc_iso(start_utc)},"
                    f"started_at.lt.{_utc_iso(end_utc)},"
                    f"completed_at.lte.{_utc_iso(snapshot_utc)})"
                ),
                "order": "started_at.asc,id.asc",
                "limit": str(_PAGE_SIZE),
                "offset": str(offset),
            },
        )
        pages += 1
        if not page:
            return rows, pages
        rows.extend(page)
        offset += len(page)


def _build_period_sample(
    period: str,
    start_utc: datetime,
    end_utc: datetime,
    rows: list[dict],
    pages: int,
) -> dict:
    latencies: list[float] = []
    success = 0
    failure = 0
    unknown_status = 0
    latency_non_success = 0
    latency_missing = 0
    latency_invalid = 0
    canonical_rows = []

    for row in rows:
        canonical_rows.append(
            {
                "id": str(row.get("id") or ""),
                "endpoint": str(row.get("endpoint") or ""),
                "started_at": str(row.get("started_at") or ""),
                "completed_at": str(row.get("completed_at") or ""),
                "outcome": str(row.get("outcome") or ""),
                "end_to_end_latency_seconds": row.get("end_to_end_latency_seconds"),
                "workflow_version": row.get("workflow_version"),
                "attempt_number": row.get("attempt_number"),
            }
        )
        state = str(row.get("outcome") or "").strip().casefold()
        is_success = state in _SUCCESS_STATES
        if is_success:
            success += 1
        elif state in _FAILURE_STATES:
            failure += 1
        else:
            unknown_status += 1

        if not is_success:
            latency_non_success += 1
            continue
        raw_latency = row.get("end_to_end_latency_seconds")
        if raw_latency is None or raw_latency == "":
            latency_missing += 1
            continue
        try:
            latency = float(raw_latency)
        except (TypeError, ValueError, OverflowError):
            latency_invalid += 1
            continue
        if not math.isfinite(latency) or latency <= 0:
            latency_invalid += 1
            continue
        latencies.append(latency)

    metadata = PeriodSampleMetadata(
        period=period,
        start_utc=start_utc,
        end_utc_exclusive=end_utc,
        rows_fetched=len(rows),
        pages_fetched=pages,
        pagination_complete=True,
        dataset_sha256=hashlib.sha256(
            json.dumps(canonical_rows, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
        ).hexdigest(),
        outcomes_included=success + failure,
        outcomes_excluded_unknown_status=unknown_status,
        latencies_included=len(latencies),
        latencies_excluded_non_success=latency_non_success,
        latencies_excluded_missing=latency_missing,
        latencies_excluded_invalid=latency_invalid,
    )
    return {
        "latencies": latencies,
        "success": success,
        "failure": failure,
        "metadata": metadata,
    }


def _to_t_test_response(calculation: dict) -> TTestResult:
    group_a = calculation["group_a"]
    group_b = calculation["group_b"]
    if calculation["status"] != "ok":
        conclusion = calculation["reason"] or "La prueba de Welch no es estimable."
        color = "blue"
        direction = "not_estimable"
        conclusion_code = calculation["status"]
    elif calculation["is_significant"]:
        direction = "más rápido" if calculation["mean_difference"] < 0 else "más lento"
        conclusion = f"Diferencia significativa: el Periodo B fue {direction}."
        color = "green" if calculation["mean_difference"] < 0 else "red"
        direction = "improvement" if calculation["mean_difference"] < 0 else "deterioration"
        conclusion_code = f"significant_{direction}"
    else:
        conclusion = "No se observó una diferencia estadísticamente significativa en la latencia."
        color = "blue"
        direction = "no_evidence"
        conclusion_code = "no_evidence_of_difference"
    return TTestResult(
        **{key: value for key, value in calculation.items() if key not in {"group_a", "group_b"}},
        n_a=group_a["n"],
        n_b=group_b["n"],
        mean_a=group_a["mean"],
        mean_b=group_b["mean"],
        mean_a_ci_95_low=group_a["mean_ci_95_low"],
        mean_a_ci_95_high=group_a["mean_ci_95_high"],
        mean_b_ci_95_low=group_b["mean_ci_95_low"],
        mean_b_ci_95_high=group_b["mean_ci_95_high"],
        sd_a=group_a["sd"],
        sd_b=group_b["sd"],
        median_a=group_a["median"],
        median_b=group_b["median"],
        iqr_a=group_a["iqr"],
        iqr_b=group_b["iqr"],
        conclusion=conclusion,
        conclusion_code=conclusion_code,
        direction=direction,
        status_color=color,
    )


def _to_contingency_response(calculation: dict) -> ChiSquareResult:
    counts = calculation["counts"]
    if calculation["status"] != "ok":
        conclusion = calculation["reason"] or "El análisis de resultados no es estimable."
        color = "blue"
        direction = "not_estimable"
        conclusion_code = calculation["status"]
    elif calculation["is_significant"]:
        improved = calculation["risk_difference"] > 0
        conclusion = "La tasa de éxito cambió significativamente entre los periodos."
        color = "green" if improved else "red"
        direction = "improvement" if improved else "deterioration"
        conclusion_code = f"significant_{direction}"
    else:
        conclusion = "No se observó una diferencia estadísticamente significativa en la tasa de éxito."
        color = "blue"
        direction = "no_evidence"
        conclusion_code = "no_evidence_of_difference"
    return ChiSquareResult(
        **calculation,
        success_a=counts[0][0],
        fail_a=counts[0][1],
        success_b=counts[1][0],
        fail_b=counts[1][1],
        conclusion=conclusion,
        conclusion_code=conclusion_code,
        direction=direction,
        status_color=color,
    )
