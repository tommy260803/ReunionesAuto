"""Pure statistical calculations for n8n metric comparisons."""

from __future__ import annotations

import math
import statistics as stdlib_stats
from collections.abc import Iterable, Sequence
from typing import Any

from scipy import stats


ANALYSIS_STATUSES = ("ok", "insufficient_data", "not_estimable", "invalid_data")


def _quantile(values: Sequence[float], probability: float) -> float:
    """Return the type-7 sample quantile used by common statistical tools."""
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    position = (len(ordered) - 1) * probability
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    weight = position - lower
    return ordered[lower] * (1.0 - weight) + ordered[upper] * weight


def _prepare_values(values: Iterable[Any]) -> tuple[list[float], str | None]:
    prepared: list[float] = []
    try:
        raw_values = list(values)
    except TypeError:
        return [], "La muestra no es iterable."

    for value in raw_values:
        if isinstance(value, bool):
            return [], "La muestra contiene valores no numéricos."
        try:
            number = float(value)
        except (TypeError, ValueError, OverflowError):
            return [], "La muestra contiene valores no numéricos."
        if not math.isfinite(number):
            return [], "La muestra contiene valores no finitos."
        prepared.append(number)
    return prepared, None


def _summary(values: Sequence[float]) -> dict[str, int | float | None]:
    if not values:
        return {
            "n": 0,
            "mean": None,
            "sd": None,
            "median": None,
            "iqr": None,
            "mean_ci_95_low": None,
            "mean_ci_95_high": None,
        }
    mean = float(stdlib_stats.fmean(values))
    sd = float(stdlib_stats.stdev(values)) if len(values) >= 2 else None
    margin = None
    if sd is not None:
        margin = float(stats.t.ppf(0.975, len(values) - 1)) * sd / math.sqrt(len(values))
    return {
        "n": len(values),
        "mean": mean,
        "sd": sd,
        "median": float(stdlib_stats.median(values)),
        "iqr": float(_quantile(values, 0.75) - _quantile(values, 0.25)),
        "mean_ci_95_low": mean - margin if margin is not None else None,
        "mean_ci_95_high": mean + margin if margin is not None else None,
    }


def welch_t_test(
    sample_a: Iterable[Any], sample_b: Iterable[Any], alpha: float = 0.05
) -> dict[str, Any]:
    """Calculate a robust two-sided Welch test and associated effect estimates."""
    values_a, error_a = _prepare_values(sample_a)
    values_b, error_b = _prepare_values(sample_b)
    summary_a = _summary(values_a)
    summary_b = _summary(values_b)
    result: dict[str, Any] = {
        "status": "ok",
        "reason": None,
        "method": "welch_t_test",
        "alternative": "two_sided",
        "alpha": alpha,
        "group_a": summary_a,
        "group_b": summary_b,
        "t_statistic": None,
        "welch_df": None,
        "p_value": None,
        "mean_difference": None,
        "ci_95_low": None,
        "ci_95_high": None,
        "hedges_g": None,
        "is_significant": None,
    }

    if not isinstance(alpha, (int, float)) or isinstance(alpha, bool) or not 0 < alpha < 1:
        result.update(status="invalid_data", reason="El nivel alfa debe estar entre 0 y 1.")
        return result
    if error_a or error_b:
        result.update(status="invalid_data", reason=error_a or error_b)
        return result
    if len(values_a) < 2 or len(values_b) < 2:
        result.update(
            status="insufficient_data",
            reason="Cada periodo necesita al menos dos latencias válidas.",
        )
        return result

    mean_a = float(summary_a["mean"])
    mean_b = float(summary_b["mean"])
    variance_a = float(summary_a["sd"]) ** 2
    variance_b = float(summary_b["sd"]) ** 2
    component_a = variance_a / len(values_a)
    component_b = variance_b / len(values_b)
    standard_error_squared = component_a + component_b
    mean_difference = mean_b - mean_a
    result["mean_difference"] = mean_difference

    if standard_error_squared <= 0:
        result.update(
            status="not_estimable",
            reason="La prueba de Welch no es estimable porque ambas muestras carecen de variación.",
        )
        return result

    denominator = (
        component_a**2 / (len(values_a) - 1)
        + component_b**2 / (len(values_b) - 1)
    )
    if denominator <= 0:
        result.update(status="not_estimable", reason="No se pueden estimar los grados de libertad.")
        return result

    standard_error = math.sqrt(standard_error_squared)
    welch_df = standard_error_squared**2 / denominator
    t_statistic = mean_difference / standard_error
    p_value = float(2.0 * stats.t.sf(abs(t_statistic), welch_df))
    critical_value = float(stats.t.ppf(0.975, welch_df))

    pooled_df = len(values_a) + len(values_b) - 2
    pooled_variance = (
        (len(values_a) - 1) * variance_a + (len(values_b) - 1) * variance_b
    ) / pooled_df
    hedges_g = None
    if pooled_variance > 0:
        correction = math.exp(
            math.lgamma(pooled_df / 2)
            - 0.5 * math.log(pooled_df / 2)
            - math.lgamma((pooled_df - 1) / 2)
        )
        hedges_g = correction * mean_difference / math.sqrt(pooled_variance)

    estimates = (
        t_statistic,
        welch_df,
        p_value,
        critical_value,
        hedges_g if hedges_g is not None else 0.0,
    )
    if not all(math.isfinite(value) for value in estimates):
        result.update(status="not_estimable", reason="El cálculo produjo estimaciones no finitas.")
        return result

    margin = critical_value * standard_error
    result.update(
        t_statistic=t_statistic,
        welch_df=welch_df,
        p_value=p_value,
        ci_95_low=mean_difference - margin,
        ci_95_high=mean_difference + margin,
        hedges_g=hedges_g,
        is_significant=p_value < alpha,
    )
    return result


def _valid_count(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def contingency_analysis(
    success_a: Any,
    failure_a: Any,
    success_b: Any,
    failure_b: Any,
    alpha: float = 0.05,
) -> dict[str, Any]:
    """Analyze a 2x2 terminal outcome table without an implicit Yates correction."""
    counts = [success_a, failure_a, success_b, failure_b]
    result: dict[str, Any] = {
        "status": "ok",
        "reason": None,
        "method": None,
        "alternative": "two_sided",
        "alpha": alpha,
        "correction": False,
        "counts": [[success_a, failure_a], [success_b, failure_b]],
        "total_a": None,
        "total_b": None,
        "success_rate_a": None,
        "success_rate_b": None,
        "failure_rate_a": None,
        "failure_rate_b": None,
        "expected": None,
        "statistic": None,
        "df": None,
        "p_value": None,
        "odds_ratio": None,
        "odds_ratio_adjustment": None,
        "odds_ratio_ci_95_low": None,
        "odds_ratio_ci_95_high": None,
        "risk_difference": None,
        "risk_difference_ci_95_low": None,
        "risk_difference_ci_95_high": None,
        "cramers_v": None,
        "is_significant": None,
    }

    if not isinstance(alpha, (int, float)) or isinstance(alpha, bool) or not 0 < alpha < 1:
        result.update(status="invalid_data", reason="El nivel alfa debe estar entre 0 y 1.")
        return result
    if not all(_valid_count(value) for value in counts):
        result.update(status="invalid_data", reason="Los conteos deben ser enteros no negativos.")
        return result

    total_a = success_a + failure_a
    total_b = success_b + failure_b
    result.update(total_a=total_a, total_b=total_b)
    if total_a == 0 or total_b == 0:
        result.update(
            status="insufficient_data",
            reason="Cada periodo necesita al menos un resultado terminal.",
        )
        return result

    success_rate_a = success_a / total_a
    success_rate_b = success_b / total_b
    result.update(
        success_rate_a=success_rate_a,
        success_rate_b=success_rate_b,
        failure_rate_a=1.0 - success_rate_a,
        failure_rate_b=1.0 - success_rate_b,
        risk_difference=success_rate_b - success_rate_a,
    )
    risk_difference_se = math.sqrt(
        success_rate_a * (1.0 - success_rate_a) / total_a
        + success_rate_b * (1.0 - success_rate_b) / total_b
    )
    result["risk_difference_ci_95_low"] = result["risk_difference"] - 1.96 * risk_difference_se
    result["risk_difference_ci_95_high"] = result["risk_difference"] + 1.96 * risk_difference_se

    success_total = success_a + success_b
    failure_total = failure_a + failure_b
    grand_total = total_a + total_b
    expected = [
        [total_a * success_total / grand_total, total_a * failure_total / grand_total],
        [total_b * success_total / grand_total, total_b * failure_total / grand_total],
    ]
    result["expected"] = expected

    if success_total == 0 or failure_total == 0:
        result.update(
            status="not_estimable",
            reason="No hay variación en el resultado terminal entre éxito y fallo.",
        )
        return result

    odds_counts = [float(count) for count in counts]
    if any(count == 0 for count in odds_counts):
        odds_counts = [count + 0.5 for count in odds_counts]
        result["odds_ratio_adjustment"] = "haldane_anscombe"
    adjusted_success_a, adjusted_failure_a, adjusted_success_b, adjusted_failure_b = odds_counts
    odds_ratio = (
        adjusted_success_b * adjusted_failure_a
        / (adjusted_failure_b * adjusted_success_a)
    )
    log_odds_ratio = math.log(odds_ratio)
    log_odds_se = math.sqrt(sum(1.0 / count for count in odds_counts))
    result["odds_ratio"] = odds_ratio
    result["odds_ratio_ci_95_low"] = math.exp(log_odds_ratio - 1.96 * log_odds_se)
    result["odds_ratio_ci_95_high"] = math.exp(log_odds_ratio + 1.96 * log_odds_se)

    if all(cell >= 5 for row in expected for cell in row):
        observed = [[success_a, failure_a], [success_b, failure_b]]
        chi_square, p_value, df, _ = stats.chi2_contingency(observed, correction=False)
        result.update(
            method="pearson_chi_square",
            statistic=float(chi_square),
            df=int(df),
            p_value=float(p_value),
            cramers_v=math.sqrt(float(chi_square) / grand_total),
            is_significant=float(p_value) < alpha,
        )
    else:
        # Reverse the rows so Fisher's statistic has the documented B-vs-A direction.
        odds_ratio, p_value = stats.fisher_exact(
            [[success_b, failure_b], [success_a, failure_a]], alternative="two-sided"
        )
        finite_odds_ratio = float(odds_ratio) if math.isfinite(float(odds_ratio)) else None
        result.update(
            method="fisher_exact",
            statistic=finite_odds_ratio,
            df=None,
            p_value=float(p_value),
            cramers_v=None,
            is_significant=float(p_value) < alpha,
        )

    return result
