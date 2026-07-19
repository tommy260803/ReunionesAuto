"""
Esquemas Pydantic para el módulo de métricas.
"""

from typing import Literal, Optional, List
from pydantic import BaseModel
from datetime import datetime

class N8nMetricResponse(BaseModel):
    id: str
    endpoint: str
    tiempo_respuesta: float
    estado: str
    fecha: str
    codigo_estado: Optional[int] = None
    reunion_id: Optional[str] = None
    tamano_respuesta: Optional[int] = None
    detalles: Optional[str] = None


class MetricDailyCount(BaseModel):
    fecha: str
    cantidad: int


class EndpointLatency(BaseModel):
    endpoint: str
    tiempo_promedio: float
    cantidad: int


class N8nMetricsStatsResponse(BaseModel):
    total_peticiones: int
    exitosas: int
    fallidas: int
    tasa_exito: float
    tiempo_promedio: float
    por_dia: List[MetricDailyCount]
    por_endpoint: List[EndpointLatency]
    logs: List[N8nMetricResponse]


class TTestResult(BaseModel):
    status: Literal["ok", "insufficient_data", "not_estimable", "invalid_data"]
    reason: Optional[str] = None
    method: Literal["welch_t_test"]
    alternative: Literal["two_sided"]
    alpha: float
    n_a: int
    n_b: int
    mean_a: Optional[float] = None
    mean_b: Optional[float] = None
    mean_a_ci_95_low: Optional[float] = None
    mean_a_ci_95_high: Optional[float] = None
    mean_b_ci_95_low: Optional[float] = None
    mean_b_ci_95_high: Optional[float] = None
    sd_a: Optional[float] = None
    sd_b: Optional[float] = None
    median_a: Optional[float] = None
    median_b: Optional[float] = None
    iqr_a: Optional[float] = None
    iqr_b: Optional[float] = None
    t_statistic: Optional[float] = None
    welch_df: Optional[float] = None
    p_value: Optional[float] = None
    mean_difference: Optional[float] = None
    ci_95_low: Optional[float] = None
    ci_95_high: Optional[float] = None
    hedges_g: Optional[float] = None
    is_significant: Optional[bool] = None
    conclusion: str
    conclusion_code: str
    direction: Literal["improvement", "deterioration", "no_evidence", "not_estimable"]
    status_color: str


class ChiSquareResult(BaseModel):
    status: Literal["ok", "insufficient_data", "not_estimable", "invalid_data"]
    reason: Optional[str] = None
    method: Optional[Literal["pearson_chi_square", "fisher_exact"]] = None
    alternative: Literal["two_sided"]
    alpha: float
    correction: bool
    p_value: Optional[float] = None
    is_significant: Optional[bool] = None
    conclusion: str
    status_color: str
    success_a: int
    fail_a: int
    success_b: int
    fail_b: int
    counts: List[List[int]]
    total_a: int
    total_b: int
    success_rate_a: Optional[float] = None
    success_rate_b: Optional[float] = None
    failure_rate_a: Optional[float] = None
    failure_rate_b: Optional[float] = None
    expected: Optional[List[List[float]]] = None
    statistic: Optional[float] = None
    df: Optional[int] = None
    odds_ratio: Optional[float] = None
    odds_ratio_adjustment: Optional[Literal["haldane_anscombe"]] = None
    odds_ratio_ci_95_low: Optional[float] = None
    odds_ratio_ci_95_high: Optional[float] = None
    risk_difference: Optional[float] = None
    risk_difference_ci_95_low: Optional[float] = None
    risk_difference_ci_95_high: Optional[float] = None
    cramers_v: Optional[float] = None
    conclusion_code: str
    direction: Literal["improvement", "deterioration", "no_evidence", "not_estimable"]


class PeriodSampleMetadata(BaseModel):
    period: Literal["a", "b"]
    start_utc: datetime
    end_utc_exclusive: datetime
    rows_fetched: int
    pages_fetched: int
    pagination_complete: bool
    dataset_sha256: str
    outcomes_included: int
    outcomes_excluded_unknown_status: int
    latencies_included: int
    latencies_excluded_non_success: int
    latencies_excluded_missing: int
    latencies_excluded_invalid: int


class StatisticalAnalysisMetadata(BaseModel):
    protocol_version: str
    generated_at_utc: datetime
    snapshot_at_utc: datetime
    timezone: Literal["UTC"]
    alpha: float
    endpoint_filter: str
    data_source: str
    terminal_only: bool
    date_semantics: Literal["inclusive_dates_queried_as_utc_half_open_intervals"]
    latency_population: Literal["successful_terminal_end_to_end"]
    outcome_population: Literal["recognized_terminal_outcomes"]
    effect_direction: Literal["period_b_minus_or_versus_period_a"]
    time_field: Literal["started_at"]
    success_states: List[str]
    failure_states: List[str]
    periods: List[PeriodSampleMetadata]


class StatisticalResponse(BaseModel):
    t_test: TTestResult
    chi_square: ChiSquareResult
    metadata: StatisticalAnalysisMetadata
