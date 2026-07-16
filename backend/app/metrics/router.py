"""
Router de métricas.

Permite consultar el historial de ejecuciones y tiempos de respuesta de n8n.
"""

from fastapi import APIRouter, Depends, HTTPException
from collections import defaultdict
from datetime import datetime, timedelta
from typing import List
from app.metrics.schemas import N8nMetricResponse, N8nMetricsStatsResponse
from app.core.dependencies import get_current_admin
from app.core.supabase_client import SupabaseClient, get_supabase

router = APIRouter(prefix="/metrics", tags=["Métricas"])


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
    sb: SupabaseClient = Depends(get_supabase)
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
            "limit": "100"
        }
    )
    
    return [serialize_metric(row) for row in rows]


@router.get("/n8n/stats", response_model=N8nMetricsStatsResponse, summary="Obtener estadísticas de n8n")
async def get_n8n_metrics_stats(
    admin: dict = Depends(get_current_admin),
    sb: SupabaseClient = Depends(get_supabase),
):
    rows = sb.select(
        "metricas_n8n",
        {
            "select": "id,endpoint,tiempo_respuesta,estado,fecha,codigo_estado,reunion_id,tamano_respuesta,detalles",
            "order": "fecha.desc",
            "limit": "500",
        },
    )
    endpoint_values: dict[str, list[float]] = defaultdict(list)
    day_counts: dict[str, int] = defaultdict(int)
    successful = 0
    for row in rows:
        endpoint_values[row.get("endpoint", "Sin endpoint")].append(float(row.get("tiempo_respuesta") or 0))
        if row.get("estado", "").lower() == "éxito":
            successful += 1
        try:
            day_counts[datetime.fromisoformat(row.get("fecha", "").replace("Z", "+00:00")).date().isoformat()] += 1
        except (TypeError, ValueError):
            continue

    today = datetime.now().date()
    days = [(today - timedelta(days=offset)).isoformat() for offset in range(6, -1, -1)]
    total = len(rows)
    average = sum(float(row.get("tiempo_respuesta") or 0) for row in rows) / total if total else 0.0
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
