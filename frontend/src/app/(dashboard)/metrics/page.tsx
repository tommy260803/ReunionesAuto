"use client";

import { useEffect, useState, type FormEvent } from "react";
import { AxiosError } from "axios";
import { useRouter } from "next/navigation";
import {
  Bar,
  BarChart,
  CartesianGrid,
  ErrorBar,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { Activity, CheckCircle2, Clock3, Loader2, ServerCrash } from "lucide-react";
import api from "@/lib/api";
import { useAuth } from "@/context/AuthContext";
import { useLanguage } from "@/context/LanguageContext";
import type {
  AnalysisDirection,
  AnalysisStatus,
  CategoricalTestResult,
  MetricDataSource,
  MetricsStats,
  StatisticalResponse,
  WelchTestResult,
} from "./types";

type Translate = (key: string) => string;

const successStatuses = new Set(["exito", "exitoso", "success", "successful", "ok"]);

function isSuccessStatus(status: string) {
  const normalized = status.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase().trim();
  return successStatuses.has(normalized);
}

const analysisStatuses = new Set<AnalysisStatus>(["ok", "insufficient_data", "not_estimable", "invalid_data"]);
const analysisDirections = new Set<AnalysisDirection>(["improvement", "deterioration", "no_evidence", "not_estimable"]);

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null;
}

function isStatisticalResponse(value: unknown): value is StatisticalResponse {
  if (!isRecord(value) || !isRecord(value.t_test) || !isRecord(value.chi_square) || !isRecord(value.metadata)) {
    return false;
  }
  const periods = value.metadata.periods;
  return analysisStatuses.has(value.t_test.status as AnalysisStatus)
    && analysisStatuses.has(value.chi_square.status as AnalysisStatus)
    && analysisDirections.has(value.t_test.direction as AnalysisDirection)
    && analysisDirections.has(value.chi_square.direction as AnalysisDirection)
    && typeof value.metadata.endpoint_filter === "string"
    && Array.isArray(periods)
    && periods.every((period) => isRecord(period)
      && (period.period === "a" || period.period === "b")
      && typeof period.start_utc === "string"
      && typeof period.end_utc_exclusive === "string"
      && typeof period.dataset_sha256 === "string");
}

function isEndpointList(value: unknown): value is string[] {
  return Array.isArray(value) && value.every((endpoint) => typeof endpoint === "string");
}

function getErrorMessage(error: unknown, fallback: string, exposeServerDetail: boolean) {
  if (error instanceof AxiosError) {
    const detail = (error.response?.data as { detail?: unknown } | undefined)?.detail;
    return exposeServerDetail && typeof detail === "string" ? detail : fallback;
  }
  return fallback;
}

function statusLabel(status: AnalysisStatus, t: Translate) {
  const labels: Record<AnalysisStatus, string> = {
    ok: t("metrics.statusOk"),
    insufficient_data: t("metrics.statusInsufficient"),
    not_estimable: t("metrics.statusNotEstimable"),
    invalid_data: t("metrics.statusError"),
  };
  return labels[status];
}

function ResultNotice({
  status,
  direction,
  t,
}: {
  status: AnalysisStatus;
  direction: AnalysisDirection;
  t: Translate;
}) {
  const statusContent: Record<Exclude<AnalysisStatus, "ok">, { text: string; classes: string }> = {
    insufficient_data: {
      text: t("metrics.statusInsufficientText"),
      classes: "border-amber-200 bg-amber-50 text-amber-900 dark:border-amber-900 dark:bg-amber-950/40 dark:text-amber-200",
    },
    not_estimable: {
      text: t("metrics.statusNotEstimableText"),
      classes: "border-slate-300 bg-slate-100 text-slate-800 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-200",
    },
    invalid_data: {
      text: t("metrics.statusErrorText"),
      classes: "border-red-200 bg-red-50 text-red-800 dark:border-red-900 dark:bg-red-950/40 dark:text-red-200",
    },
  };
  const directionalContent: Record<Exclude<AnalysisDirection, "not_estimable">, { text: string; classes: string }> = {
    improvement: {
      text: t("metrics.evidenceImprovement"),
      classes: "border-emerald-200 bg-emerald-50 text-emerald-900 dark:border-emerald-900 dark:bg-emerald-950/40 dark:text-emerald-200",
    },
    deterioration: {
      text: t("metrics.evidenceDeterioration"),
      classes: "border-red-200 bg-red-50 text-red-900 dark:border-red-900 dark:bg-red-950/40 dark:text-red-200",
    },
    no_evidence: {
      text: t("metrics.noEvidence"),
      classes: "border-blue-200 bg-blue-50 text-blue-900 dark:border-blue-900 dark:bg-blue-950/40 dark:text-blue-200",
    },
  };
  const content = status === "ok"
    ? directionalContent[direction === "not_estimable" ? "no_evidence" : direction]
    : statusContent[status];

  return (
    <div role="status" className={`rounded-lg border p-3 text-sm ${content.classes}`}>
      <p className="font-semibold">{statusLabel(status, t)}</p>
      <p className="mt-1">{content.text}</p>
    </div>
  );
}

export default function MetricsPage() {
  const { user, loading: authLoading } = useAuth();
  const { language, t } = useLanguage();
  const router = useRouter();
  const [stats, setStats] = useState<MetricsStats | null>(null);
  const [error, setError] = useState("");
  const [statStartA, setStatStartA] = useState("");
  const [statEndA, setStatEndA] = useState("");
  const [statStartB, setStatStartB] = useState("");
  const [statEndB, setStatEndB] = useState("");
  const [statEndpoint, setStatEndpoint] = useState("");
  const [statDataSource, setStatDataSource] = useState<MetricDataSource>("production");
  const [availableEndpoints, setAvailableEndpoints] = useState<string[]>([]);
  const [endpointsLoading, setEndpointsLoading] = useState(true);
  const [endpointLoadError, setEndpointLoadError] = useState(false);
  const [endpointRequestKey, setEndpointRequestKey] = useState(0);
  const [statResult, setStatResult] = useState<StatisticalResponse | null>(null);
  const [statLoading, setStatLoading] = useState(false);
  const [statError, setStatError] = useState("");

  useEffect(() => {
    if (!authLoading && !user?.is_admin) {
      router.replace("/dashboard");
      return;
    }
    if (user?.is_admin) {
      api.get<MetricsStats>("/metrics/n8n/stats")
        .then((response) => setStats(response.data))
        .catch(() => setError(t("metrics.loadError")));
    }
  }, [authLoading, router, t, user?.is_admin]);

  useEffect(() => {
    if (!user?.is_admin) return;
    let active = true;
    api.get<unknown>("/metrics/n8n/endpoints", { params: { data_source: statDataSource } })
      .then((response) => {
        if (!isEndpointList(response.data)) throw new Error("Invalid endpoint list");
        if (active) {
          setAvailableEndpoints(response.data);
          setEndpointLoadError(false);
        }
      })
      .catch(() => {
        if (active) {
          setAvailableEndpoints([]);
          setEndpointLoadError(true);
        }
      })
      .finally(() => {
        if (active) setEndpointsLoading(false);
      });
    return () => { active = false; };
  }, [endpointRequestKey, statDataSource, user?.is_admin]);

  const clearStatFeedback = () => {
    setStatResult(null);
    setStatError("");
  };

  const downloadAnalysis = () => {
    if (!statResult) return;
    const blob = new Blob([JSON.stringify(statResult, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `n8n-statistics-${statResult.metadata.endpoint_filter}-${Date.now()}.json`;
    link.click();
    URL.revokeObjectURL(url);
  };

  const runStatistics = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setStatResult(null);
    setStatError("");

    if (!statEndpoint || !statStartA || !statEndA || !statStartB || !statEndB) {
      setStatError(t("metrics.validationRequired"));
      return;
    }
    if (statStartA > statEndA || statStartB > statEndB) {
      setStatError(t("metrics.validationWithinRange"));
      return;
    }
    if (statEndA >= statStartB) {
      setStatError(t("metrics.validationRangeOrder"));
      return;
    }

    setStatLoading(true);
    try {
      const response = await api.get<unknown>("/metrics/n8n/statistics", {
        params: {
          start_a: statStartA,
          end_a: statEndA,
          start_b: statStartB,
          end_b: statEndB,
          endpoint_filter: statEndpoint,
          data_source: statDataSource,
        },
      });
      if (!isStatisticalResponse(response.data)) {
        throw new Error("Invalid statistical response");
      }
      setStatResult(response.data);
    } catch (requestError: unknown) {
      setStatError(getErrorMessage(requestError, t("metrics.analysisError"), language === "es"));
    } finally {
      setStatLoading(false);
    }
  };

  if (authLoading || (!stats && !error)) {
    return (
      <div role="status" aria-label={t("common.loadingApp")} className="flex h-[calc(100vh-8rem)] items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-brand-600" aria-hidden="true" />
      </div>
    );
  }
  if (!user?.is_admin) return null;

  const locale = language === "es" ? "es-ES" : "en-US";
  const formatNumber = (value: number | null, maximumFractionDigits = 3) => value === null || !Number.isFinite(value)
    ? t("metrics.notAvailable")
    : new Intl.NumberFormat(locale, { maximumFractionDigits }).format(value);
  const formatPValue = (value: number | null) => {
    if (value === null || !Number.isFinite(value)) return t("metrics.notAvailable");
    return value < 0.0001 ? "< 0.0001" : value.toFixed(4);
  };
  const formatPercentage = (value: number) => `${formatNumber(value, 1)}%`;
  const endpointOptions = availableEndpoints;
  const executedPeriodA = statResult?.metadata.periods.find(({ period }) => period === "a");
  const executedPeriodB = statResult?.metadata.periods.find(({ period }) => period === "b");
  const cards = [
    { label: t("metrics.successRate"), value: `${stats?.tasa_exito || 0}%`, icon: CheckCircle2, color: "text-emerald-600" },
    { label: t("metrics.avgTime"), value: `${stats?.tiempo_promedio || 0}s`, icon: Clock3, color: "text-brand-600" },
    { label: t("metrics.requests"), value: stats?.total_peticiones || 0, icon: Activity, color: "text-violet-600" },
    { label: t("metrics.errors"), value: stats?.fallidas || 0, icon: ServerCrash, color: "text-red-600" },
  ];

  const renderWelchPanel = (result: WelchTestResult) => {
    const latencyChartAvailable = result.status === "ok"
      && result.mean_a !== null
      && result.mean_b !== null
      && result.mean_a_ci_95_low !== null
      && result.mean_a_ci_95_high !== null
      && result.mean_b_ci_95_low !== null
      && result.mean_b_ci_95_high !== null;
    const latencyChartData = [
      {
        period: t("metrics.periodA"),
        mean: result.mean_a,
        error: result.mean_a !== null && result.mean_a_ci_95_low !== null && result.mean_a_ci_95_high !== null
          ? [result.mean_a - result.mean_a_ci_95_low, result.mean_a_ci_95_high - result.mean_a]
          : undefined,
      },
      {
        period: t("metrics.periodB"),
        mean: result.mean_b,
        error: result.mean_b !== null && result.mean_b_ci_95_low !== null && result.mean_b_ci_95_high !== null
          ? [result.mean_b - result.mean_b_ci_95_low, result.mean_b_ci_95_high - result.mean_b]
          : undefined,
      },
    ];
    return (
      <section className="rounded-xl border border-border bg-slate-50 p-4 dark:bg-slate-900/50 sm:p-5" aria-labelledby="welch-title">
        <div className="mb-4">
          <h3 id="welch-title" className="flex items-center gap-2 font-semibold">
            <Activity className="h-4 w-4 text-brand-600" aria-hidden="true" />
            {t("metrics.welchTitle")}
          </h3>
          <p className="mt-1 text-sm app-muted">{t("metrics.welchSubtitle")}</p>
        </div>
        <ResultNotice status={result.status} direction={result.direction} t={t} />

        <div className="mt-5 overflow-x-auto" tabIndex={0} role="region" aria-label={t("metrics.descriptiveStatistics")}>
          <table className="w-full min-w-[34rem] text-sm">
            <caption className="mb-2 text-left font-semibold">{t("metrics.descriptiveStatistics")}</caption>
            <thead className="border-b border-border text-xs uppercase text-slate-500">
              <tr>
                <th scope="col" className="px-2 py-2 text-left">{t("metrics.period")}</th>
                <th scope="col" className="px-2 py-2 text-right">{t("metrics.sampleSize")}</th>
                <th scope="col" className="px-2 py-2 text-right">{t("metrics.meanSeconds")}</th>
                <th scope="col" className="px-2 py-2 text-right">{t("metrics.sdSeconds")}</th>
                <th scope="col" className="px-2 py-2 text-right">{t("metrics.medianSeconds")}</th>
                <th scope="col" className="px-2 py-2 text-right">{t("metrics.iqrSeconds")}</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {([
                [t("metrics.periodA"), { n: result.n_a, mean: result.mean_a, sd: result.sd_a, median: result.median_a, iqr: result.iqr_a }],
                [t("metrics.periodB"), { n: result.n_b, mean: result.mean_b, sd: result.sd_b, median: result.median_b, iqr: result.iqr_b }],
              ] as const).map(([label, period]) => (
                <tr key={label}>
                  <th scope="row" className="px-2 py-3 text-left font-medium">{label}</th>
                  <td className="px-2 py-3 text-right tabular-nums">{period.n}</td>
                  <td className="px-2 py-3 text-right tabular-nums">{formatNumber(period.mean)}</td>
                  <td className="px-2 py-3 text-right tabular-nums">{formatNumber(period.sd)}</td>
                  <td className="px-2 py-3 text-right tabular-nums">{formatNumber(period.median)}</td>
                  <td className="px-2 py-3 text-right tabular-nums">{formatNumber(period.iqr)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="mt-5">
          <h4 className="text-sm font-semibold">{t("metrics.inference")}</h4>
          <dl className="mt-2 grid grid-cols-1 gap-px overflow-hidden rounded-lg border border-border bg-border text-sm sm:grid-cols-2">
            <MetricDefinition label={t("metrics.meanDifference")} value={formatNumber(result.mean_difference)} />
            <MetricDefinition
              label={t("metrics.confidenceInterval")}
              value={`[${formatNumber(result.ci_95_low)}, ${formatNumber(result.ci_95_high)}]`}
            />
            <MetricDefinition label={t("metrics.tStatistic")} value={formatNumber(result.t_statistic)} />
            <MetricDefinition label={t("metrics.degreesFreedom")} value={formatNumber(result.welch_df)} />
            <MetricDefinition label={t("metrics.pValue")} value={formatPValue(result.p_value)} />
            <MetricDefinition label={t("metrics.hedgesG")} value={formatNumber(result.hedges_g)} />
          </dl>
        </div>

        {latencyChartAvailable && (
          <figure className="mt-5" aria-labelledby="latency-chart-title" aria-describedby="latency-chart-description">
            <figcaption id="latency-chart-title" className="text-sm font-semibold">{t("metrics.latencyChart")}</figcaption>
            <p id="latency-chart-description" className="mt-1 text-xs app-muted">{t("metrics.latencyChartDescription")}</p>
            <div className="mt-3 h-56" aria-hidden="true">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={latencyChartData}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--border)" />
                  <XAxis dataKey="period" tick={{ fontSize: 12, fill: "var(--muted)" }} />
                  <YAxis tick={{ fontSize: 12, fill: "var(--muted)" }} unit="s" />
                  <Tooltip
                    formatter={(value) => `${formatNumber(Number(value))} s`}
                    contentStyle={{ borderRadius: 10, border: "1px solid var(--border)", background: "var(--surface-raised)", color: "var(--foreground)" }}
                  />
                  <Bar dataKey="mean" fill="#6366f1" name={t("metrics.meanSeconds")} radius={[4, 4, 0, 0]}>
                    <ErrorBar dataKey="error" width={6} strokeWidth={2} stroke="#312e81" direction="y" />
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </figure>
        )}
      </section>
    );
  };

  const renderCategoricalPanel = (result: CategoricalTestResult) => {
    const method = result.method === "pearson_chi_square"
      ? t("metrics.methodChiSquare")
      : result.method === "fisher_exact"
        ? t("metrics.methodFisher")
        : t("metrics.methodUnavailable");
    const chartData = [
      {
        period: t("metrics.periodA"),
        success: (result.success_rate_a ?? 0) * 100,
        failure: (result.failure_rate_a ?? 0) * 100,
      },
      {
        period: t("metrics.periodB"),
        success: (result.success_rate_b ?? 0) * 100,
        failure: (result.failure_rate_b ?? 0) * 100,
      },
    ];
    const categoricalChartAvailable = result.success_rate_a !== null
      && result.failure_rate_a !== null
      && result.success_rate_b !== null
      && result.failure_rate_b !== null;

    return (
      <section className="rounded-xl border border-border bg-slate-50 p-4 dark:bg-slate-900/50 sm:p-5" aria-labelledby="categorical-title">
        <div className="mb-4">
          <h3 id="categorical-title" className="flex items-center gap-2 font-semibold">
            <CheckCircle2 className="h-4 w-4 text-brand-600" aria-hidden="true" />
            {t("metrics.categoricalTitle")}
          </h3>
          <p className="mt-1 text-sm app-muted">{t("metrics.categoricalSubtitle")}</p>
        </div>
        <ResultNotice status={result.status} direction={result.direction} t={t} />

        <dl className="mt-5 grid grid-cols-1 gap-px overflow-hidden rounded-lg border border-border bg-border text-sm sm:grid-cols-2">
          <MetricDefinition label={t("metrics.method")} value={method} />
          <MetricDefinition label={t("metrics.statistic")} value={formatNumber(result.statistic)} />
          <MetricDefinition label={t("metrics.degreesFreedom")} value={formatNumber(result.df)} />
          <MetricDefinition label={t("metrics.pValue")} value={formatPValue(result.p_value)} />
          {result.odds_ratio !== null && <MetricDefinition label={t("metrics.oddsRatio")} value={formatNumber(result.odds_ratio)} />}
          {result.odds_ratio_adjustment === "haldane_anscombe" && (
            <MetricDefinition label={t("metrics.oddsAdjustment")} value={t("metrics.haldaneAnscombe")} />
          )}
          {result.odds_ratio_ci_95_low !== null && result.odds_ratio_ci_95_high !== null && (
            <MetricDefinition
              label={`${t("metrics.oddsRatio")} · ${t("metrics.confidenceInterval")}`}
              value={`[${formatNumber(result.odds_ratio_ci_95_low)}, ${formatNumber(result.odds_ratio_ci_95_high)}]`}
            />
          )}
          {result.risk_difference !== null && <MetricDefinition label={t("metrics.riskDifference")} value={formatNumber(result.risk_difference)} />}
          {result.risk_difference_ci_95_low !== null && result.risk_difference_ci_95_high !== null && (
            <MetricDefinition
              label={`${t("metrics.riskDifference")} · ${t("metrics.confidenceInterval")}`}
              value={`[${formatNumber(result.risk_difference_ci_95_low)}, ${formatNumber(result.risk_difference_ci_95_high)}]`}
            />
          )}
          {result.cramers_v !== null && <MetricDefinition label={t("metrics.cramersV")} value={formatNumber(result.cramers_v)} />}
        </dl>

        <div className="mt-5 overflow-x-auto" tabIndex={0} role="region" aria-label={t("metrics.outcomeCounts")}>
          <table className="w-full min-w-[32rem] text-sm">
            <caption className="mb-2 text-left font-semibold">{t("metrics.outcomeCounts")}</caption>
            <thead className="border-b border-border text-xs uppercase text-slate-500">
              <tr>
                <th scope="col" className="px-2 py-2 text-left">{t("metrics.period")}</th>
                <th scope="col" className="px-2 py-2 text-right">{t("metrics.total")}</th>
                <th scope="col" className="px-2 py-2 text-right">{t("metrics.successes")}</th>
                <th scope="col" className="px-2 py-2 text-right">{t("metrics.successPercentage")}</th>
                <th scope="col" className="px-2 py-2 text-right">{t("metrics.failures")}</th>
                <th scope="col" className="px-2 py-2 text-right">{t("metrics.failurePercentage")}</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {([
                [t("metrics.periodA"), { total: result.total_a, success: result.success_a, failure: result.fail_a, successRate: result.success_rate_a, failureRate: result.failure_rate_a }],
                [t("metrics.periodB"), { total: result.total_b, success: result.success_b, failure: result.fail_b, successRate: result.success_rate_b, failureRate: result.failure_rate_b }],
              ] as const).map(([label, period]) => (
                <tr key={label}>
                  <th scope="row" className="px-2 py-3 text-left font-medium">{label}</th>
                  <td className="px-2 py-3 text-right tabular-nums">{period.total}</td>
                  <td className="px-2 py-3 text-right tabular-nums">{period.success}</td>
                  <td className="px-2 py-3 text-right tabular-nums">{period.successRate === null ? t("metrics.notAvailable") : formatPercentage(period.successRate * 100)}</td>
                  <td className="px-2 py-3 text-right tabular-nums">{period.failure}</td>
                  <td className="px-2 py-3 text-right tabular-nums">{period.failureRate === null ? t("metrics.notAvailable") : formatPercentage(period.failureRate * 100)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {categoricalChartAvailable && <figure className="mt-5" aria-labelledby="proportion-chart-title" aria-describedby="proportion-chart-description">
          <figcaption id="proportion-chart-title" className="text-sm font-semibold">{t("metrics.proportionChart")}</figcaption>
          <p id="proportion-chart-description" className="mt-1 text-xs app-muted">{t("metrics.proportionChartDescription")}</p>
          <div className="mt-3 h-56" aria-hidden="true">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData} layout="vertical" margin={{ left: 8, right: 12 }}>
                <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="var(--border)" />
                <XAxis type="number" domain={[0, 100]} tickFormatter={(value: number) => `${value}%`} tick={{ fontSize: 12, fill: "var(--muted)" }} />
                <YAxis type="category" dataKey="period" width={76} tick={{ fontSize: 12, fill: "var(--muted)" }} />
                <Tooltip
                  formatter={(value) => formatPercentage(Number(value))}
                  contentStyle={{ borderRadius: 10, border: "1px solid var(--border)", background: "var(--surface-raised)", color: "var(--foreground)" }}
                />
                <Legend wrapperStyle={{ fontSize: 12 }} />
                <Bar dataKey="success" stackId="outcomes" fill="#10b981" name={t("metrics.successes")} />
                <Bar dataKey="failure" stackId="outcomes" fill="#ef4444" name={t("metrics.failures")} radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </figure>}
      </section>
    );
  };

  return (
    <div className="space-y-7">
      <div>
        <p className="command-eyebrow">{t("metrics.eyebrow")}</p>
        <h1 className="mt-1 text-3xl font-semibold tracking-tight">{t("metrics.title")}</h1>
        <p className="mt-2 text-base app-muted">{t("metrics.subtitle")}</p>
      </div>

      {error ? (
        <div role="alert" className="rounded-lg border border-red-200 bg-red-50 p-4 text-red-700 dark:border-red-900 dark:text-red-300">{error}</div>
      ) : stats ? (
        <>
          <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
            {cards.map((card) => (
              <section key={card.label} className="telemetry-card p-5 transition-all duration-200">
                <card.icon className={`h-5 w-5 ${card.color}`} aria-hidden="true" />
                <p className="mt-4 text-3xl font-semibold">{card.value}</p>
                <p className="mt-1 text-sm app-muted">{card.label}</p>
                <div className="metric-line" />
              </section>
            ))}
          </div>

          <div className="grid gap-6 xl:grid-cols-2">
            <section className="command-panel p-6">
              <h2 className="mb-5 font-semibold">{t("metrics.last7Days")}</h2>
              <div className="h-72">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={stats.por_dia}>
                    <CartesianGrid stroke="var(--border)" strokeDasharray="3 3" vertical={false} />
                    <XAxis dataKey="fecha" tickFormatter={(value: string) => value.slice(5)} tick={{ fill: "var(--muted)", fontSize: 12 }} />
                    <YAxis allowDecimals={false} tick={{ fill: "var(--muted)", fontSize: 12 }} />
                    <Tooltip contentStyle={{ borderRadius: 10, border: "1px solid var(--border)", background: "var(--surface-raised)", color: "var(--foreground)" }} />
                    <Line type="monotone" dataKey="cantidad" stroke="#6366f1" strokeWidth={3} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </section>

            <section className="command-panel p-6">
              <h2 className="mb-5 font-semibold">{t("metrics.avgLatencyEndpoint")}</h2>
              <div className="h-72">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={stats.por_endpoint}>
                    <CartesianGrid stroke="var(--border)" strokeDasharray="3 3" vertical={false} />
                    <XAxis dataKey="endpoint" tick={{ fontSize: 12, fill: "var(--muted)" }} />
                    <YAxis tick={{ fontSize: 12, fill: "var(--muted)" }} />
                    <Tooltip contentStyle={{ borderRadius: 10, border: "1px solid var(--border)", background: "var(--surface-raised)", color: "var(--foreground)" }} />
                    <Bar dataKey="tiempo_promedio" fill="#6366f1" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </section>
          </div>

          <section className="command-panel overflow-hidden">
            <div className="border-b border-border p-5"><h2 className="font-semibold">{t("metrics.recentLogs")}</h2></div>
            <div className="overflow-x-auto" tabIndex={0} role="region" aria-label={t("metrics.recentLogs")}>
              <table className="w-full text-sm">
                <caption className="sr-only">{t("metrics.recentLogs")}</caption>
                <thead className="border-b border-border text-xs uppercase text-slate-500">
                  <tr>
                    <th scope="col" className="p-4 text-left">{t("metrics.endpoint")}</th>
                    <th scope="col" className="p-4 text-left">{t("common.status")}</th>
                    <th scope="col" className="p-4 text-left">{t("metrics.code")}</th>
                    <th scope="col" className="p-4 text-left">{t("metrics.avgTime")}</th>
                    <th scope="col" className="p-4 text-left">{t("common.date")}</th>
                    <th scope="col" className="p-4 text-left">{t("metrics.details")}</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border">
                  {stats.logs.map((log) => {
                    const success = isSuccessStatus(log.estado);
                    return (
                      <tr key={log.id}>
                        <td className="p-4 font-medium">{log.endpoint}</td>
                        <td className="p-4">
                          <span className={`rounded-full px-2.5 py-1 text-xs font-semibold ${success ? "bg-emerald-100 text-emerald-700" : "bg-red-100 text-red-700"}`}>
                            {success ? t("metrics.logSuccess") : t("metrics.logError")}
                          </span>
                        </td>
                        <td className="p-4 text-slate-500">{log.codigo_estado ?? "-"}</td>
                        <td className="p-4 text-slate-500">{log.tiempo_respuesta}s</td>
                        <td className="p-4 text-slate-500">{new Date(log.fecha).toLocaleString(locale)}</td>
                        <td className="max-w-xs truncate p-4 text-slate-500">{log.detalles || "-"}</td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </section>

          <section className="command-panel p-4 sm:p-6" aria-labelledby="statistics-title">
            <div className="max-w-3xl">
              <h2 id="statistics-title" className="text-xl font-semibold">{t("metrics.statisticsTitle")}</h2>
              <p className="mt-2 text-sm app-muted">{t("metrics.statisticsSubtitle")}</p>
            </div>

            <form onSubmit={runStatistics} className="mt-6" noValidate>
              <fieldset disabled={statLoading} className="grid gap-4 lg:grid-cols-2 xl:grid-cols-6">
                <legend className="sr-only">{t("metrics.statisticsTitle")}</legend>
                <div className="xl:col-span-1">
                  <label htmlFor="stat-data-source" className="mb-1.5 block text-xs font-medium">{t("metrics.dataSource")}</label>
                  <select
                    id="stat-data-source"
                    value={statDataSource}
                    onChange={(event) => {
                      clearStatFeedback();
                      setStatEndpoint("");
                      setEndpointsLoading(true);
                      setEndpointLoadError(false);
                      setStatDataSource(event.target.value as MetricDataSource);
                    }}
                    className="form-input w-full rounded-lg border p-2 text-sm disabled:cursor-not-allowed disabled:opacity-60"
                  >
                    <option value="production">{t("metrics.productionData")}</option>
                    <option value="demo">{t("metrics.demoData")}</option>
                  </select>
                </div>
                <div className="lg:col-span-2 xl:col-span-2">
                  <label htmlFor="stat-endpoint" className="mb-1.5 block text-xs font-medium">{t("metrics.endpointRequired")}</label>
                  <select
                    id="stat-endpoint"
                    name="endpoint_filter"
                    required
                    value={statEndpoint}
                    onChange={(event) => { clearStatFeedback(); setStatEndpoint(event.target.value); }}
                    className="form-input w-full rounded-lg border p-2 text-sm disabled:cursor-not-allowed disabled:opacity-60"
                  >
                    <option value="">
                      {endpointsLoading
                        ? t("metrics.loadingEndpoints")
                        : endpointOptions.length === 0
                          ? t("metrics.noEndpoints")
                          : t("metrics.selectEndpoint")}
                    </option>
                    {endpointOptions.map((endpoint) => <option key={endpoint} value={endpoint}>{endpoint}</option>)}
                  </select>
                </div>
                <DateField id="stat-start-a" label={t("metrics.startA")} value={statStartA} onChange={(value) => { clearStatFeedback(); setStatStartA(value); }} />
                <DateField id="stat-end-a" label={t("metrics.endA")} value={statEndA} onChange={(value) => { clearStatFeedback(); setStatEndA(value); }} />
                <DateField id="stat-start-b" label={t("metrics.startB")} value={statStartB} onChange={(value) => { clearStatFeedback(); setStatStartB(value); }} />
                <DateField id="stat-end-b" label={t("metrics.endB")} value={statEndB} onChange={(value) => { clearStatFeedback(); setStatEndB(value); }} />
                <button
                  type="submit"
                  className="flex h-10 w-full items-center justify-center gap-2 rounded-lg bg-brand-600 px-4 text-sm font-medium text-white hover:bg-brand-700 disabled:cursor-not-allowed disabled:opacity-60 lg:col-span-2 xl:col-span-6 xl:justify-self-end xl:w-auto"
                >
                  {statLoading && <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" />}
                  {statLoading ? t("metrics.runningAnalysis") : t("metrics.runAnalysis")}
                </button>
              </fieldset>
            </form>

            {endpointLoadError && (
              <div className="mt-3 flex flex-wrap items-center gap-3 rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-800 dark:border-red-900 dark:bg-red-950/40 dark:text-red-200">
                <span>{t("metrics.endpointLoadError")}</span>
                <button
                  type="button"
                  onClick={() => {
                    setEndpointsLoading(true);
                    setEndpointLoadError(false);
                    setEndpointRequestKey((value) => value + 1);
                  }}
                  className="rounded border border-current px-2 py-1 font-medium"
                >
                  {t("metrics.retry")}
                </button>
              </div>
            )}

            {statDataSource === "demo" && (
              <p className="mt-3 rounded-lg border border-amber-300 bg-amber-50 p-3 text-sm text-amber-900 dark:border-amber-800 dark:bg-amber-950/40 dark:text-amber-200">
                {t("metrics.demoWarning")}
              </p>
            )}

            <div aria-live="polite" aria-atomic="true" className="mt-5">
              {statError && <div role="alert" className="rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700 dark:border-red-900 dark:bg-red-950/40 dark:text-red-200">{statError}</div>}
              {statLoading && <p role="status" className="text-sm app-muted">{t("metrics.runningAnalysis")}</p>}
              {statResult && <p role="status" className="sr-only">{t("metrics.analysisReady")}</p>}
            </div>

            {statResult && (
              <div className="mt-6 space-y-6">
                <section className="rounded-xl border border-border bg-slate-50 p-4 dark:bg-slate-900/50" aria-labelledby="executed-parameters-title">
                  <h3 id="executed-parameters-title" className="font-semibold">{t("metrics.executedParameters")}</h3>
                  <dl className="mt-3 grid gap-4 text-sm sm:grid-cols-2 xl:grid-cols-4">
                    <div><dt className="app-muted">{t("metrics.executedEndpoint")}</dt><dd className="mt-1 break-all font-medium">{statResult.metadata.endpoint_filter}</dd></div>
                    <div><dt className="app-muted">{t("metrics.timezone")}</dt><dd className="mt-1 font-medium">UTC</dd></div>
                    <div><dt className="app-muted">{t("metrics.dataSource")}</dt><dd className="mt-1 font-medium">{statResult.metadata.data_source}</dd></div>
                    <div><dt className="app-muted">{t("metrics.alpha")}</dt><dd className="mt-1 font-medium tabular-nums">{formatNumber(statResult.t_test.alpha)}</dd></div>
                    <div><dt className="app-muted">{t("metrics.protocolVersion")}</dt><dd className="mt-1 font-medium">{statResult.metadata.protocol_version}</dd></div>
                    <div><dt className="app-muted">{t("metrics.generatedAt")}</dt><dd className="mt-1 font-medium">{new Date(statResult.metadata.generated_at_utc).toLocaleString(locale)}</dd></div>
                    <div className="sm:col-span-2 xl:col-span-1">
                      <dt className="app-muted">{t("metrics.periodA")} · {t("metrics.exactRange")}</dt>
                      <dd className="mt-1 break-words font-mono text-xs">
                        {executedPeriodA ? `${executedPeriodA.start_utc} ≤ t < ${executedPeriodA.end_utc_exclusive}` : t("metrics.notAvailable")}
                      </dd>
                    </div>
                    <div className="sm:col-span-2 xl:col-span-4">
                      <dt className="app-muted">{t("metrics.periodB")} · {t("metrics.exactRange")}</dt>
                      <dd className="mt-1 break-words font-mono text-xs">
                        {executedPeriodB ? `${executedPeriodB.start_utc} ≤ t < ${executedPeriodB.end_utc_exclusive}` : t("metrics.notAvailable")}
                      </dd>
                    </div>
                    <div className="sm:col-span-2">
                      <dt className="app-muted">{t("metrics.datasetHash")} · {t("metrics.periodA")}</dt>
                      <dd className="mt-1 break-all font-mono text-xs">{executedPeriodA?.dataset_sha256 ?? t("metrics.notAvailable")}</dd>
                    </div>
                    <div className="sm:col-span-2">
                      <dt className="app-muted">{t("metrics.datasetHash")} · {t("metrics.periodB")}</dt>
                      <dd className="mt-1 break-all font-mono text-xs">{executedPeriodB?.dataset_sha256 ?? t("metrics.notAvailable")}</dd>
                    </div>
                  </dl>
                  <button
                    type="button"
                    onClick={downloadAnalysis}
                    className="mt-4 rounded-lg border border-border px-3 py-2 text-sm font-medium hover:bg-slate-100 dark:hover:bg-slate-800"
                  >
                    {t("metrics.downloadAnalysis")}
                  </button>
                </section>

                <div className="grid items-start gap-6 xl:grid-cols-2">
                  {renderWelchPanel(statResult.t_test)}
                  {renderCategoricalPanel(statResult.chi_square)}
                </div>
              </div>
            )}
          </section>
        </>
      ) : null}
    </div>
  );
}

function MetricDefinition({ label, value }: { label: string; value: string }) {
  return (
    <div className="bg-slate-50 p-3 dark:bg-slate-900">
      <dt className="text-xs app-muted">{label}</dt>
      <dd className="mt-1 font-medium tabular-nums">{value}</dd>
    </div>
  );
}

function DateField({ id, label, value, onChange }: { id: string; label: string; value: string; onChange: (value: string) => void }) {
  return (
    <div>
      <label htmlFor={id} className="mb-1.5 block text-xs font-medium">{label}</label>
      <input
        id={id}
        name={id}
        type="date"
        required
        value={value}
        onChange={(event) => onChange(event.target.value)}
        className="form-input w-full rounded-lg border p-2 text-sm disabled:cursor-not-allowed disabled:opacity-60"
      />
    </div>
  );
}
