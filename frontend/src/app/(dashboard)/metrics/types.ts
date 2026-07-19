export type AnalysisStatus = "ok" | "insufficient_data" | "not_estimable" | "invalid_data";
export type AnalysisDirection = "improvement" | "deterioration" | "no_evidence" | "not_estimable";

export interface Log {
  id: string;
  endpoint: string;
  tiempo_respuesta: number;
  estado: string;
  fecha: string;
  codigo_estado?: number;
  detalles?: string;
}

export interface MetricsStats {
  total_peticiones: number;
  exitosas: number;
  fallidas: number;
  tasa_exito: number;
  tiempo_promedio: number;
  por_dia: { fecha: string; cantidad: number }[];
  por_endpoint: { endpoint: string; tiempo_promedio: number; cantidad: number }[];
  logs: Log[];
}

export interface WelchTestResult {
  status: AnalysisStatus;
  reason: string | null;
  method: "welch_t_test";
  alternative: "two_sided";
  alpha: number;
  n_a: number;
  n_b: number;
  mean_a: number | null;
  mean_b: number | null;
  mean_a_ci_95_low: number | null;
  mean_a_ci_95_high: number | null;
  mean_b_ci_95_low: number | null;
  mean_b_ci_95_high: number | null;
  sd_a: number | null;
  sd_b: number | null;
  median_a: number | null;
  median_b: number | null;
  iqr_a: number | null;
  iqr_b: number | null;
  mean_difference: number | null;
  ci_95_low: number | null;
  ci_95_high: number | null;
  t_statistic: number | null;
  welch_df: number | null;
  p_value: number | null;
  hedges_g: number | null;
  is_significant: boolean | null;
  conclusion: string;
  conclusion_code: string;
  direction: AnalysisDirection;
  status_color: string;
}

export interface CategoricalTestResult {
  status: AnalysisStatus;
  reason: string | null;
  method: "pearson_chi_square" | "fisher_exact" | null;
  alternative: "two_sided";
  alpha: number;
  correction: boolean;
  counts: number[][];
  success_a: number;
  fail_a: number;
  success_b: number;
  fail_b: number;
  total_a: number;
  total_b: number;
  success_rate_a: number | null;
  success_rate_b: number | null;
  failure_rate_a: number | null;
  failure_rate_b: number | null;
  expected: number[][] | null;
  statistic: number | null;
  df: number | null;
  p_value: number | null;
  odds_ratio: number | null;
  odds_ratio_adjustment: "haldane_anscombe" | null;
  odds_ratio_ci_95_low: number | null;
  odds_ratio_ci_95_high: number | null;
  risk_difference: number | null;
  risk_difference_ci_95_low: number | null;
  risk_difference_ci_95_high: number | null;
  cramers_v: number | null;
  is_significant: boolean | null;
  conclusion: string;
  conclusion_code: string;
  direction: AnalysisDirection;
  status_color: string;
}

export interface PeriodSampleMetadata {
  period: "a" | "b";
  start_utc: string;
  end_utc_exclusive: string;
  rows_fetched: number;
  pages_fetched: number;
  pagination_complete: boolean;
  dataset_sha256: string;
  outcomes_included: number;
  outcomes_excluded_unknown_status: number;
  latencies_included: number;
  latencies_excluded_non_success: number;
  latencies_excluded_missing: number;
  latencies_excluded_invalid: number;
}

export interface StatisticalAnalysisMetadata {
  protocol_version: string;
  generated_at_utc: string;
  snapshot_at_utc: string;
  timezone: "UTC";
  alpha: number;
  endpoint_filter: string;
  data_source: string;
  terminal_only: boolean;
  date_semantics: "inclusive_dates_queried_as_utc_half_open_intervals";
  latency_population: "successful_terminal_end_to_end";
  outcome_population: "recognized_terminal_outcomes";
  effect_direction: "period_b_minus_or_versus_period_a";
  time_field: "started_at";
  success_states: string[];
  failure_states: string[];
  periods: PeriodSampleMetadata[];
}

export interface StatisticalResponse {
  t_test: WelchTestResult;
  chi_square: CategoricalTestResult;
  metadata: StatisticalAnalysisMetadata;
}

export type MetricDataSource = "production" | "demo";
