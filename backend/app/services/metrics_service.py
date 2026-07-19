"""One-row-per-invocation telemetry for n8n calls."""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone

from app.core.config import settings
from app.core.supabase_client import SupabaseClient
from app.core.supabase_client import get_supabase


TERMINAL_OUTCOMES = {"success", "error", "timeout", "cancelled"}
LEGACY_STATES = {
    "pending": "en_proceso",
    "success": "éxito",
    "error": "error",
    "timeout": "timeout",
    "cancelled": "cancelado",
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class N8nInvocation:
    sb: SupabaseClient
    invocation_id: str
    endpoint: str
    started_at: str
    started_perf: float
    reunion_id: str | None
    attempt_number: int
    correlation_id: str | None
    inserted: bool = True
    finalized: bool = False
    transport_latency_seconds: float | None = None

    def elapsed(self) -> float:
        return max(0.0, time.perf_counter() - self.started_perf)


def start_invocation(
    sb: SupabaseClient,
    endpoint: str,
    *,
    reunion_id: str | None = None,
    attempt_number: int = 1,
    correlation_id: str | None = None,
) -> N8nInvocation:
    """Insert the sole metric row for an n8n invocation in pending state."""
    metrics_sb = _metrics_client(sb)
    invocation = N8nInvocation(
        sb=metrics_sb,
        invocation_id=str(uuid.uuid4()),
        endpoint=endpoint,
        started_at=_utc_now(),
        started_perf=time.perf_counter(),
        reunion_id=reunion_id,
        attempt_number=max(1, attempt_number),
        correlation_id=correlation_id,
    )
    if correlation_id:
        _cancel_pending_invocations(metrics_sb, correlation_id)
    row = {
        "invocation_id": invocation.invocation_id,
        "data_source": "production",
        "started_at": invocation.started_at,
        "completed_at": None,
        "transport_latency_seconds": None,
        "end_to_end_latency_seconds": None,
        "outcome": "pending",
        "is_terminal": False,
        "attempt_number": invocation.attempt_number,
        "correlation_id": correlation_id,
        "workflow_version": settings.N8N_WORKFLOW_VERSION,
        # Compatibility fields consumed by the existing metrics UI.
        "endpoint": endpoint,
        "tiempo_respuesta": 0.0,
        "estado": LEGACY_STATES["pending"],
        "fecha": invocation.started_at,
        "codigo_estado": None,
        "reunion_id": reunion_id,
        "tamano_respuesta": None,
        "detalles": None,
    }
    try:
        metrics_sb.insert("metricas_n8n", [row])
    except Exception as exc:
        invocation.inserted = False
        print(f"Error registrando inicio de métrica n8n: {exc}")
    # Exclude telemetry persistence overhead from n8n latency measurements.
    invocation.started_perf = time.perf_counter()
    return invocation


def record_transport(
    invocation: N8nInvocation,
    *,
    status_code: int,
    response_size: int = 0,
    transport_latency_seconds: float | None = None,
    details: str | None = None,
) -> None:
    """Record a completed transport while leaving asynchronous work pending."""
    if invocation.finalized:
        return
    latency = (
        invocation.elapsed()
        if transport_latency_seconds is None
        else max(0.0, transport_latency_seconds)
    )
    invocation.transport_latency_seconds = latency
    if not invocation.inserted:
        return
    try:
        invocation.sb.update(
            "metricas_n8n",
            {
                "transport_latency_seconds": latency,
                "tiempo_respuesta": latency,
                "codigo_estado": status_code,
                "tamano_respuesta": response_size,
                "detalles": details,
            },
            {
                "invocation_id": f"eq.{invocation.invocation_id}",
                "is_terminal": "eq.false",
            },
        )
    except Exception as exc:
        print(f"Error registrando transporte de métrica n8n: {exc}")


def finalize_invocation(
    invocation: N8nInvocation,
    outcome: str,
    *,
    status_code: int | None = None,
    response_size: int | None = None,
    transport_latency_seconds: float | None = None,
    details: str | None = None,
) -> None:
    """Finalize an invocation by updating its existing row exactly once."""
    if outcome not in TERMINAL_OUTCOMES:
        raise ValueError(f"Resultado terminal inválido: {outcome}")
    if invocation.finalized:
        return
    invocation.finalized = True

    end_to_end_latency = invocation.elapsed()
    transport_latency = transport_latency_seconds
    if transport_latency is None:
        transport_latency = invocation.transport_latency_seconds
    if transport_latency is None:
        transport_latency = end_to_end_latency
    transport_latency = max(0.0, transport_latency)
    invocation.transport_latency_seconds = transport_latency

    if not invocation.inserted:
        return
    try:
        invocation.sb.update(
            "metricas_n8n",
            {
                "completed_at": _utc_now(),
                "transport_latency_seconds": transport_latency,
                "end_to_end_latency_seconds": end_to_end_latency,
                "outcome": outcome,
                "is_terminal": True,
                "tiempo_respuesta": end_to_end_latency,
                "estado": LEGACY_STATES[outcome],
                "codigo_estado": status_code,
                "tamano_respuesta": response_size,
                "detalles": details,
            },
            {"invocation_id": f"eq.{invocation.invocation_id}"},
        )
    except Exception as exc:
        print(f"Error finalizando métrica n8n: {exc}")


def finalize_async_invocation(
    sb: SupabaseClient,
    correlation_id: str,
    outcome: str,
    *,
    details: str | None = None,
) -> bool:
    """Finalize the latest pending asynchronous invocation for a job."""
    if outcome not in TERMINAL_OUTCOMES:
        raise ValueError(f"Resultado terminal inválido: {outcome}")
    metrics_sb = _metrics_client(sb)
    try:
        rows = metrics_sb.select(
            "metricas_n8n",
            {
                "select": "invocation_id,started_at,transport_latency_seconds",
                "correlation_id": f"eq.{correlation_id}",
                "is_terminal": "eq.false",
                "order": "started_at.desc",
                "limit": "1",
            },
        )
        if not rows:
            return False
        row = rows[0]
        completed_at = datetime.now(timezone.utc)
        started_at = _parse_utc(row.get("started_at"))
        end_to_end_latency = None
        if started_at is not None:
            end_to_end_latency = max(0.0, (completed_at - started_at).total_seconds())
        data = {
            "completed_at": completed_at.isoformat(),
            "end_to_end_latency_seconds": end_to_end_latency,
            "outcome": outcome,
            "is_terminal": True,
            "estado": LEGACY_STATES[outcome],
            "detalles": details,
        }
        if end_to_end_latency is not None:
            data["tiempo_respuesta"] = end_to_end_latency
        metrics_sb.update(
            "metricas_n8n",
            data,
            {
                "invocation_id": f"eq.{row['invocation_id']}",
                "is_terminal": "eq.false",
            },
        )
        return True
    except Exception as exc:
        print(f"Error finalizando métrica asíncrona n8n: {exc}")
        raise


def _metrics_client(fallback: SupabaseClient) -> SupabaseClient:
    if settings.SUPABASE_SERVICE_ROLE_KEY:
        return get_supabase(service_role=True)
    return fallback


def _parse_utc(value: object) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _cancel_pending_invocations(sb: SupabaseClient, correlation_id: str) -> None:
    """Prevent retries from leaving more than one pending row for a job."""
    try:
        sb.update(
            "metricas_n8n",
            {
                "completed_at": _utc_now(),
                "outcome": "cancelled",
                "is_terminal": True,
                "estado": LEGACY_STATES["cancelled"],
                "detalles": "Reemplazada por un nuevo intento del mismo trabajo.",
            },
            {
                "correlation_id": f"eq.{correlation_id}",
                "is_terminal": "eq.false",
            },
        )
    except Exception as exc:
        print(f"Error cerrando métricas pendientes anteriores: {exc}")
