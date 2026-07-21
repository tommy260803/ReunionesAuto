"""Pure statistical calculations for n8n metric comparisons and scientific evaluation."""

from __future__ import annotations

import math
import statistics as stdlib_stats
from collections import Counter
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


# ==============================================================================
# FUNCIONES PARA EVALUACIÓN CIENTÍFICA
# ==============================================================================

def calculate_inter_rater_agreement(
    ratings_a: Sequence[Any],
    ratings_b: Sequence[Any],
    method: str = "kappa"
) -> dict[str, Any]:
    """
    Calcula el acuerdo entre evaluadores usando Kappa de Cohen o ICC.
    
    Args:
        ratings_a: Calificaciones del primer evaluador
        ratings_b: Calificaciones del segundo evaluador
        method: "kappa" para Cohen's Kappa, "icc" para ICC
    
    Returns:
        Diccionario con estadísticas de acuerdo
    """
    result: dict[str, Any] = {
        "status": "ok",
        "reason": None,
        "method": method,
        "n": len(ratings_a),
        "agreement_coefficient": None,
        "standard_error": None,
        "ci_95_low": None,
        "ci_95_high": None,
        "p_value": None,
        "interpretation": None,
    }
    
    if len(ratings_a) != len(ratings_b):
        result.update(
            status="invalid_data",
            reason="Los evaluadores deben tener el mismo número de calificaciones."
        )
        return result
    
    if len(ratings_a) < 2:
        result.update(
            status="insufficient_data",
            reason="Se requieren al menos 2 calificaciones por evaluador."
        )
        return result
    
    try:
        ratings_a_clean = [float(r) for r in ratings_a]
        ratings_b_clean = [float(r) for r in ratings_b]
    except (TypeError, ValueError):
        result.update(
            status="invalid_data",
            reason="Las calificaciones deben ser numéricas."
        )
        return result
    
    if method == "kappa":
        # Cohen's Kappa para datos ordinales/categóricos
        try:
            kappa, p_value = stats.stats.kappa(ratings_a_clean, ratings_b_clean)
            result["agreement_coefficient"] = float(kappa)
            result["p_value"] = float(p_value)
            
            # Interpretación de Landis & Koch (1977)
            if kappa < 0:
                interpretation = "Acuerdo pobre (menor que el azar)"
            elif kappa <= 0.20:
                interpretation = "Acuerdo ligero"
            elif kappa <= 0.40:
                interpretation = "Acuerdo justo"
            elif kappa <= 0.60:
                interpretation = "Acuerdo moderado"
            elif kappa <= 0.80:
                interpretation = "Acuerdo sustancial"
            else:
                interpretation = "Acuerdo casi perfecto"
            
            result["interpretation"] = interpretation
        except Exception as e:
            result.update(
                status="not_estimable",
                reason=f"No se pudo calcular Kappa: {str(e)}"
            )
    
    elif method == "icc":
        # Intraclass Correlation Coefficient para datos continuos
        try:
            # Reorganizar datos para ICC: [rater1_item1, rater2_item1, rater1_item2, rater2_item2, ...]
            data = []
            for ra, rb in zip(ratings_a_clean, ratings_b_clean):
                data.append([ra, rb])
            
            # ICC(3,1) - Two-way mixed effects, absolute agreement, single rater
            icc = stats.intraclass_corr(data, rater=1, model="mixed", type="absolute")
            if len(icc) > 0:
                result["agreement_coefficient"] = float(icc[0][0])
                result["ci_95_low"] = float(icc[0][2])
                result["ci_95_high"] = float(icc[0][3])
                
                # Interpretación de ICC
                icc_value = result["agreement_coefficient"]
                if icc_value < 0.5:
                    interpretation = "Confiabilidad pobre"
                elif icc_value < 0.75:
                    interpretation = "Confiabilidad moderada"
                elif icc_value < 0.9:
                    interpretation = "Confiabilidad buena"
                else:
                    interpretation = "Confiabilidad excelente"
                
                result["interpretation"] = interpretation
            else:
                result.update(
                    status="not_estimable",
                    reason="No se pudo calcular ICC"
                )
        except Exception as e:
            result.update(
                status="not_estimable",
                reason=f"No se pudo calcular ICC: {str(e)}"
            )
    
    else:
        result.update(
            status="invalid_data",
            reason=f"Método no reconocido: {method}. Use 'kappa' o 'icc'."
        )
    
    return result


def calculate_classification_metrics(
    true_positives: int,
    false_positives: int,
    false_negatives: int,
    true_negatives: int = 0
) -> dict[str, Any]:
    """
    Calcula métricas de clasificación: Precision, Recall, F1.
    
    Args:
        true_positives: Verdaderos positivos
        false_positives: Falsos positivos
        false_negatives: Falsos negativos
        true_negatives: Verdaderos negativos (opcional)
    
    Returns:
        Diccionario con precision, recall, f1 y estadísticas relacionadas
    """
    result: dict[str, Any] = {
        "status": "ok",
        "reason": None,
        "true_positives": true_positives,
        "false_positives": false_positives,
        "false_negatives": false_negatives,
        "true_negatives": true_negatives,
        "precision": None,
        "recall": None,
        "f1_score": None,
        "accuracy": None,
        "specificity": None,
        "support": None,
    }
    
    total_predictions = true_positives + false_positives
    total_actual = true_positives + false_negatives
    total_instances = true_positives + false_positives + false_negatives + true_negatives
    
    result["support"] = total_actual
    
    # Precision = TP / (TP + FP)
    if total_predictions > 0:
        result["precision"] = true_positives / total_predictions
    
    # Recall = TP / (TP + FN)
    if total_actual > 0:
        result["recall"] = true_positives / total_actual
    
    # F1 = 2 * (Precision * Recall) / (Precision + Recall)
    if result["precision"] is not None and result["recall"] is not None:
        if result["precision"] + result["recall"] > 0:
            result["f1_score"] = (
                2 * result["precision"] * result["recall"]
            ) / (result["precision"] + result["recall"])
    
    # Accuracy = (TP + TN) / Total
    if total_instances > 0:
        result["accuracy"] = (true_positives + true_negatives) / total_instances
    
    # Specificity = TN / (TN + FP)
    if true_negatives + false_positives > 0:
        result["specificity"] = true_negatives / (true_negatives + false_positives)
    
    return result


def paired_t_test(
    before: Sequence[Any],
    after: Sequence[Any],
    alpha: float = 0.05
) -> dict[str, Any]:
    """
    Prueba t pareada para comparar mediciones antes/después.
    
    Útil para comparar tiempos manuales vs automatizados en los mismos participantes.
    
    Args:
        before: Mediciones antes (ej: tiempo manual)
        after: Mediciones después (ej: tiempo con sistema)
        alpha: Nivel de significancia
    
    Returns:
        Diccionario con resultados de la prueba t pareada
    """
    values_before, error_before = _prepare_values(before)
    values_after, error_after = _prepare_values(after)
    
    result: dict[str, Any] = {
        "status": "ok",
        "reason": None,
        "method": "paired_t_test",
        "alternative": "two_sided",
        "alpha": alpha,
        "n": len(values_before),
        "mean_before": None,
        "mean_after": None,
        "mean_difference": None,
        "std_difference": None,
        "t_statistic": None,
        "df": None,
        "p_value": None,
        "ci_95_low": None,
        "ci_95_high": None,
        "cohens_d": None,
        "is_significant": None,
    }
    
    if not isinstance(alpha, (int, float)) or isinstance(alpha, bool) or not 0 < alpha < 1:
        result.update(status="invalid_data", reason="El nivel alfa debe estar entre 0 y 1.")
        return result
    
    if error_before or error_after:
        result.update(status="invalid_data", reason=error_before or error_after)
        return result
    
    if len(values_before) != len(values_after):
        result.update(
            status="invalid_data",
            reason="Las muestras deben tener el mismo tamaño para prueba pareada."
        )
        return result
    
    if len(values_before) < 2:
        result.update(
            status="insufficient_data",
            reason="Se requieren al menos 2 pares de mediciones."
        )
        return result
    
    # Calcular diferencias
    differences = [a - b for a, b in zip(values_after, values_before)]
    mean_diff = stdlib_stats.fmean(differences)
    std_diff = stdlib_stats.stdev(differences) if len(differences) >= 2 else 0
    
    result["mean_before"] = float(stdlib_stats.fmean(values_before))
    result["mean_after"] = float(stdlib_stats.fmean(values_after))
    result["mean_difference"] = float(mean_diff)
    result["std_difference"] = float(std_diff) if std_diff else None
    
    # Prueba t pareada
    try:
        t_statistic, p_value = stats.ttest_rel(values_after, values_before)
        result["t_statistic"] = float(t_statistic)
        result["p_value"] = float(p_value)
        result["df"] = len(differences) - 1
        result["is_significant"] = p_value < alpha
        
        # Intervalo de confianza para la diferencia
        if std_diff > 0:
            se = std_diff / math.sqrt(len(differences))
            critical_t = stats.t.ppf(1 - alpha / 2, len(differences) - 1)
            margin = critical_t * se
            result["ci_95_low"] = mean_diff - margin
            result["ci_95_high"] = mean_diff + margin
        
        # Cohen's d para muestras pareadas
        if std_diff > 0:
            result["cohens_d"] = mean_diff / std_diff
    except Exception as e:
        result.update(
            status="not_estimable",
            reason=f"No se pudo calcular la prueba t pareada: {str(e)}"
        )
    
    return result


def bonferroni_correction(
    p_values: Sequence[float],
    alpha: float = 0.05
) -> dict[str, Any]:
    """
    Aplica corrección de Bonferroni para comparaciones múltiples.
    
    Args:
        p_values: Lista de p-values
        alpha: Nivel de significancia original
    
    Returns:
        Diccionario con p-values corregidos y resultados
    """
    result: dict[str, Any] = {
        "status": "ok",
        "reason": None,
        "method": "bonferroni",
        "original_alpha": alpha,
        "n_comparisons": len(p_values),
        "corrected_alpha": alpha / len(p_values) if p_values else alpha,
        "p_values_original": list(p_values),
        "p_values_corrected": [],
        "significant_original": [],
        "significant_corrected": [],
    }
    
    if not p_values:
        result.update(status="insufficient_data", reason="No se proporcionaron p-values.")
        return result
    
    corrected_alpha = alpha / len(p_values)
    result["corrected_alpha"] = corrected_alpha
    
    for p in p_values:
        if not isinstance(p, (int, float)) or p < 0 or p > 1:
            result.update(
                status="invalid_data",
                reason="Los p-values deben estar entre 0 y 1."
            )
            return result
        
        corrected_p = min(p * len(p_values), 1.0)
        result["p_values_corrected"].append(corrected_p)
        result["significant_original"].append(p < alpha)
        result["significant_corrected"].append(corrected_p < corrected_alpha)
    
    return result


def analyze_sus_scores(
    scores: Sequence[float],
    benchmark: float = 68.0
) -> dict[str, Any]:
    """
    Analiza puntajes SUS con estadísticas descriptivas y comparación con benchmark.
    
    Args:
        scores: Puntajes SUS (0-100)
        benchmark: Puntaje de referencia (default: 68 = promedio industry)
    
    Returns:
        Diccionario con análisis de puntajes SUS
    """
    values, error = _prepare_values(scores)
    
    result: dict[str, Any] = {
        "status": "ok",
        "reason": None,
        "n": len(values),
        "mean": None,
        "std": None,
        "median": None,
        "min": None,
        "max": None,
        "q25": None,
        "q75": None,
        "benchmark": benchmark,
        "above_benchmark": None,
        "below_benchmark": None,
        "percent_above_benchmark": None,
        "interpretation": None,
    }
    
    if error:
        result.update(status="invalid_data", reason=error)
        return result
    
    if len(values) < 1:
        result.update(status="insufficient_data", reason="Se requiere al menos 1 puntaje.")
        return result
    
    result["mean"] = float(stdlib_stats.fmean(values))
    result["std"] = float(stdlib_stats.stdev(values)) if len(values) >= 2 else 0.0
    result["median"] = float(stdlib_stats.median(values))
    result["min"] = float(min(values))
    result["max"] = float(max(values))
    result["q25"] = float(_quantile(values, 0.25))
    result["q75"] = float(_quantile(values, 0.75))
    
    above = sum(1 for s in values if s >= benchmark)
    below = len(values) - above
    result["above_benchmark"] = above
    result["below_benchmark"] = below
    result["percent_above_benchmark"] = (above / len(values)) * 100 if values else 0
    
    # Interpretación según Bangor et al. (2008)
    mean_score = result["mean"]
    if mean_score < 50:
        interpretation = "No aceptable"
    elif mean_score < 60:
        interpretation = "Pobre"
    elif mean_score < 70:
        interpretation = "OK"
    elif mean_score < 80:
        interpretation = "Bueno"
    elif mean_score < 90:
        interpretation = "Excelente"
    else:
        interpretation = "La mejor imaginable"
    
    result["interpretation"] = interpretation
    
    return result


# ==============================================================================
# PRUEBAS DE SUPUESTOS ESTADÍSTICOS
# ==============================================================================

def shapiro_wilk_test(
    values: Sequence[Any],
    alpha: float = 0.05
) -> dict[str, Any]:
    """
    Prueba de Shapiro-Wilk para evaluar normalidad de datos.
    
    Útil para verificar supuestos de normalidad antes de aplicar pruebas paramétricas.
    
    Args:
        values: Muestra de datos numéricos
        alpha: Nivel de significancia
    
    Returns:
        Diccionario con resultados de la prueba Shapiro-Wilk
    """
    prepared_values, error = _prepare_values(values)
    
    result: dict[str, Any] = {
        "status": "ok",
        "reason": None,
        "method": "shapiro_wilk",
        "alpha": alpha,
        "n": len(prepared_values),
        "statistic": None,
        "p_value": None,
        "is_normal": None,
        "interpretation": None,
    }
    
    if error:
        result.update(status="invalid_data", reason=error)
        return result
    
    if len(prepared_values) < 3:
        result.update(
            status="insufficient_data",
            reason="Shapiro-Wilk requiere al menos 3 observaciones."
        )
        return result
    
    if len(prepared_values) > 5000:
        result.update(
            status="invalid_data",
            reason="Shapiro-Wilk no es recomendable para muestras > 5000."
        )
        return result
    
    try:
        statistic, p_value = stats.shapiro(prepared_values)
        result["statistic"] = float(statistic)
        result["p_value"] = float(p_value)
        result["is_normal"] = p_value > alpha
        
        if p_value > alpha:
            result["interpretation"] = "No se rechaza la hipótesis de normalidad (datos parecen normales)"
        else:
            result["interpretation"] = "Se rechaza la hipótesis de normalidad (datos no parecen normales)"
    except Exception as e:
        result.update(
            status="not_estimable",
            reason=f"No se pudo calcular Shapiro-Wilk: {str(e)}"
        )
    
    return result


def levene_test(
    *samples: Sequence[Any],
    alpha: float = 0.05,
    center: str = "median"
) -> dict[str, Any]:
    """
    Prueba de Levene para evaluar igualdad de varianzas entre grupos.
    
    Útil para verificar el supuesto de homocedasticidad antes de aplicar pruebas paramétricas.
    
    Args:
        *samples: Dos o más muestras de datos numéricos
        alpha: Nivel de significancia
        center: "median" (Brown-Forsythe) o "mean" (Levene clásico)
    
    Returns:
        Diccionario con resultados de la prueba de Levene
    """
    result: dict[str, Any] = {
        "status": "ok",
        "reason": None,
        "method": f"levene_{center}",
        "alpha": alpha,
        "n_groups": len(samples),
        "group_sizes": [],
        "statistic": None,
        "p_value": None,
        "equal_variances": None,
        "interpretation": None,
    }
    
    if len(samples) < 2:
        result.update(
            status="invalid_data",
            reason="Se requieren al menos 2 grupos para Levene."
        )
        return result
    
    prepared_samples = []
    for sample in samples:
        prepared, error = _prepare_values(sample)
        if error:
            result.update(status="invalid_data", reason=error)
            return result
        if len(prepared) < 2:
            result.update(
                status="insufficient_data",
                reason="Cada grupo debe tener al menos 2 observaciones."
            )
            return result
        prepared_samples.append(prepared)
        result["group_sizes"].append(len(prepared))
    
    try:
        statistic, p_value = stats.levene(*prepared_samples, center=center)
        result["statistic"] = float(statistic)
        result["p_value"] = float(p_value)
        result["equal_variances"] = p_value > alpha
        
        if p_value > alpha:
            result["interpretation"] = "No se rechaza la hipótesis de igualdad de varianzas (homocedasticidad)"
        else:
            result["interpretation"] = "Se rechaza la hipótesis de igualdad de varianzas (heterocedasticidad)"
    except Exception as e:
        result.update(
            status="not_estimable",
            reason=f"No se pudo calcular Levene: {str(e)}"
        )
    
    return result


# ==============================================================================
# PRUEBAS NO PARAMÉTRICAS
# ==============================================================================

def mann_whitney_u_test(
    sample_a: Sequence[Any],
    sample_b: Sequence[Any],
    alpha: float = 0.05,
    alternative: str = "two_sided"
) -> dict[str, Any]:
    """
    Prueba de Mann-Whitney U para comparar dos muestras independientes.
    
    Alternativa no paramétrica a la t de Welch cuando no se cumple normalidad.
    
    Args:
        sample_a: Primera muestra
        sample_b: Segunda muestra
        alpha: Nivel de significancia
        alternative: "two_sided", "less", "greater"
    
    Returns:
        Diccionario con resultados de la prueba Mann-Whitney U
    """
    values_a, error_a = _prepare_values(sample_a)
    values_b, error_b = _prepare_values(sample_b)
    summary_a = _summary(values_a)
    summary_b = _summary(values_b)
    
    result: dict[str, Any] = {
        "status": "ok",
        "reason": None,
        "method": "mann_whitney_u",
        "alternative": alternative,
        "alpha": alpha,
        "group_a": summary_a,
        "group_b": summary_b,
        "u_statistic": None,
        "p_value": None,
        "median_difference": None,
        "effect_size_r": None,
        "is_significant": None,
        "interpretation": None,
    }
    
    if error_a or error_b:
        result.update(status="invalid_data", reason=error_a or error_b)
        return result
    
    if len(values_a) < 2 or len(values_b) < 2:
        result.update(
            status="insufficient_data",
            reason="Cada grupo debe tener al menos 2 observaciones."
        )
        return result
    
    try:
        u_statistic, p_value = stats.mannwhitneyu(
            values_a, values_b, alternative=alternative
        )
        result["u_statistic"] = float(u_statistic)
        result["p_value"] = float(p_value)
        result["is_significant"] = p_value < alpha
        
        # Diferencia de medianas
        median_a = float(stdlib_stats.median(values_a))
        median_b = float(stdlib_stats.median(values_b))
        result["median_difference"] = median_b - median_a
        
        # Tamaño del efecto r = Z / sqrt(N)
        n = len(values_a) + len(values_b)
        # Aproximación de Z desde U
        z_score = (u_statistic - len(values_a) * len(values_b) / 2) / (
            math.sqrt(len(values_a) * len(values_b) * (n + 1) / 12)
        )
        result["effect_size_r"] = abs(z_score) / math.sqrt(n)
        
        if p_value < alpha:
            result["interpretation"] = "Se encontró una diferencia estadísticamente significativa entre los grupos"
        else:
            result["interpretation"] = "No se encontró una diferencia estadísticamente significativa entre los grupos"
    except Exception as e:
        result.update(
            status="not_estimable",
            reason=f"No se pudo calcular Mann-Whitney U: {str(e)}"
        )
    
    return result


def friedman_test(
    *samples: Sequence[Any],
    alpha: float = 0.05
) -> dict[str, Any]:
    """
    Prueba de Friedman para comparar 3+ condiciones relacionadas.
    
    Alternativa no paramétrica al ANOVA de medidas repetidas.
    
    Args:
        *samples: Tres o más muestras relacionadas (mismo tamaño)
        alpha: Nivel de significancia
    
    Returns:
        Diccionario con resultados de la prueba de Friedman
    """
    result: dict[str, Any] = {
        "status": "ok",
        "reason": None,
        "method": "friedman",
        "alpha": alpha,
        "n_groups": len(samples),
        "n_observations": 0,
        "statistic": None,
        "p_value": None,
        "kendall_w": None,
        "is_significant": None,
        "interpretation": None,
    }
    
    if len(samples) < 3:
        result.update(
            status="invalid_data",
            reason="Friedman requiere al menos 3 grupos."
        )
        return result
    
    prepared_samples = []
    n_obs = None
    for sample in samples:
        prepared, error = _prepare_values(sample)
        if error:
            result.update(status="invalid_data", reason=error)
            return result
        if len(prepared) < 2:
            result.update(
                status="insufficient_data",
                reason="Cada grupo debe tener al menos 2 observaciones."
            )
            return result
        if n_obs is None:
            n_obs = len(prepared)
        elif len(prepared) != n_obs:
            result.update(
                status="invalid_data",
                reason="Todos los grupos deben tener el mismo número de observaciones (diseño pareado)."
            )
            return result
        prepared_samples.append(prepared)
    
    result["n_observations"] = n_obs
    
    try:
        statistic, p_value = stats.friedmanchisquare(*prepared_samples)
        result["statistic"] = float(statistic)
        result["p_value"] = float(p_value)
        result["is_significant"] = p_value < alpha
        
        # Kendall's W como tamaño del efecto
        k = len(samples)
        n = n_obs
        kendall_w = statistic / (n * (k - 1))
        result["kendall_w"] = kendall_w
        
        if p_value < alpha:
            result["interpretation"] = "Se encontraron diferencias estadísticamente significativas entre las condiciones"
        else:
            result["interpretation"] = "No se encontraron diferencias estadísticamente significativas entre las condiciones"
    except Exception as e:
        result.update(
            status="not_estimable",
            reason=f"No se pudo calcular Friedman: {str(e)}"
        )
    
    return result


# ==============================================================================
# PRUEBAS PARA DATOS BINARIOS
# ==============================================================================

def mcnemar_test(
    before: Sequence[bool | int],
    after: Sequence[bool | int],
    alpha: float = 0.05,
    exact: bool = False
) -> dict[str, Any]:
    """
    Prueba de McNemar para comparar proporciones en datos binarios pareados.
    
    Útil para comparar error/no error entre dos configuraciones en los mismos sujetos.
    
    Args:
        before: Valores binarios antes (ej: errores en configuración A)
        after: Valores binarios después (ej: errores en configuración B)
        alpha: Nivel de significancia
        exact: Si True, usa prueba exacta de McNemar para muestras pequeñas
    
    Returns:
        Diccionario con resultados de la prueba de McNemar
    """
    result: dict[str, Any] = {
        "status": "ok",
        "reason": None,
        "method": "mcnemar",
        "alpha": alpha,
        "exact": exact,
        "n_pairs": len(before),
        "contingency_table": None,
        "statistic": None,
        "p_value": None,
        "is_significant": None,
        "proportion_before": None,
        "proportion_after": None,
        "difference": None,
        "interpretation": None,
    }
    
    if len(before) != len(after):
        result.update(
            status="invalid_data",
            reason="Las muestras deben tener el mismo tamaño para prueba pareada."
        )
        return result
    
    if len(before) < 2:
        result.update(
            status="insufficient_data",
            reason="Se requieren al menos 2 pares de mediciones."
        )
        return result
    
    # Convertir a binarios si es necesario
    try:
        before_bin = [bool(b) for b in before]
        after_bin = [bool(a) for a in after]
    except (TypeError, ValueError):
        result.update(
            status="invalid_data",
            reason="Los datos deben ser binarios (True/False o 1/0)."
        )
        return result
    
    # Construir tabla de contingencia 2x2
    # a: True antes, True después
    # b: True antes, False después (cambio de True a False)
    # c: False antes, True después (cambio de False a True)
    # d: False antes, False después
    a = sum(1 for b, a in zip(before_bin, after_bin) if b and a)
    b = sum(1 for b, a in zip(before_bin, after_bin) if b and not a)
    c = sum(1 for b, a in zip(before_bin, after_bin) if not b and a)
    d = sum(1 for b, a in zip(before_bin, after_bin) if not b and not a)
    
    result["contingency_table"] = {"a": a, "b": b, "c": c, "d": d}
    result["proportion_before"] = (a + b) / len(before_bin)
    result["proportion_after"] = (a + c) / len(after_bin)
    result["difference"] = result["proportion_before"] - result["proportion_after"]
    
    try:
        if exact or b + c < 25:
            # Prueba exacta de McNemar-Bowker para muestras pequeñas
            from scipy.stats import mcnemar as mcnemar_exact
            statistic, p_value = mcnemar_exact([[a, b], [c, d]], exact=True, correction=False)
        else:
            # Prueba aproximada con corrección de continuidad
            statistic, p_value = stats.mcnemar([[a, b], [c, d]], correction=True)
        
        result["statistic"] = float(statistic)
        result["p_value"] = float(p_value)
        result["is_significant"] = p_value < alpha
        
        if p_value < alpha:
            result["interpretation"] = "Se encontró una diferencia estadísticamente significativa en las proporciones"
        else:
            result["interpretation"] = "No se encontró una diferencia estadísticamente significativa en las proporciones"
    except Exception as e:
        result.update(
            status="not_estimable",
            reason=f"No se pudo calcular McNemar: {str(e)}"
        )
    
    return result


def cochran_q_test(
    *samples: Sequence[bool | int],
    alpha: float = 0.05
) -> dict[str, Any]:
    """
    Prueba Q de Cochran para comparar 3+ proporciones en datos binarios pareados.
    
    Extensión de McNemar para múltiples condiciones.
    
    Args:
        *samples: Tres o más muestras binarias relacionadas (mismo tamaño)
        alpha: Nivel de significancia
    
    Returns:
        Diccionario con resultados de la prueba Q de Cochran
    """
    result: dict[str, Any] = {
        "status": "ok",
        "reason": None,
        "method": "cochran_q",
        "alpha": alpha,
        "n_conditions": len(samples),
        "n_observations": 0,
        "statistic": None,
        "p_value": None,
        "df": None,
        "is_significant": None,
        "proportions": None,
        "interpretation": None,
    }
    
    if len(samples) < 3:
        result.update(
            status="invalid_data",
            reason="Q de Cochran requiere al menos 3 condiciones."
        )
        return result
    
    prepared_samples = []
    n_obs = None
    for sample in samples:
        try:
            prepared = [bool(s) for s in sample]
        except (TypeError, ValueError):
            result.update(
                status="invalid_data",
                reason="Los datos deben ser binarios (True/False o 1/0)."
            )
            return result
        
        if len(prepared) < 2:
            result.update(
                status="insufficient_data",
                reason="Cada condición debe tener al menos 2 observaciones."
            )
            return result
        
        if n_obs is None:
            n_obs = len(prepared)
        elif len(prepared) != n_obs:
            result.update(
                status="invalid_data",
                reason="Todas las condiciones deben tener el mismo número de observaciones (diseño pareado)."
            )
            return result
        
        prepared_samples.append(prepared)
    
    result["n_observations"] = n_obs
    
    # Calcular proporciones por condición
    proportions = [sum(s) / len(s) for s in prepared_samples]
    result["proportions"] = proportions
    
    try:
        # Calcular estadístico Q de Cochran
        # L = número de sujetos con al menos un éxito
        # G_j = número de éxitos en condición j
        # Q = k(k-1) * sum((G_j - L/k)^2) / (k*L - sum(G_j))
        
        k = len(samples)
        n = n_obs
        
        # Éxitos por condición
        G = [sum(s) for s in prepared_samples]
        
        # Éxitos por sujeto (número de condiciones donde el sujeto tuvo éxito)
        L_per_subject = []
        for i in range(n):
            successes = sum(1 for sample in prepared_samples if sample[i])
            L_per_subject.append(successes)
        
        # L = número de sujetos con al menos un éxito
        L = sum(1 for l in L_per_subject if l > 0)
        
        if L == 0:
            result.update(
                status="invalid_data",
                reason="No hay éxitos en ninguna condición."
            )
            return result
        
        # Calcular Q
        mean_G = sum(G) / k
        numerator = sum((g - mean_G) ** 2 for g in G)
        denominator = k * L - sum(G)
        
        if denominator == 0:
            result.update(
                status="not_estimable",
                reason="No se puede calcular Q (denominador cero)."
            )
            return result
        
        Q = (k * (k - 1) * numerator) / denominator
        result["statistic"] = Q
        result["df"] = k - 1
        
        # P-value usando chi-cuadrado
        p_value = 1 - stats.chi2.cdf(Q, k - 1)
        result["p_value"] = p_value
        result["is_significant"] = p_value < alpha
        
        if p_value < alpha:
            result["interpretation"] = "Se encontraron diferencias estadísticamente significativas entre las condiciones"
        else:
            result["interpretation"] = "No se encontraron diferencias estadísticamente significativas entre las condiciones"
    except Exception as e:
        result.update(
            status="not_estimable",
            reason=f"No se pudo calcular Q de Cochran: {str(e)}"
        )
    
    return result


# ==============================================================================
# ACUERDO ENTRE EVALUADORES Y CONSISTENCIA INTERNA
# ==============================================================================

def krippendorff_alpha(
    ratings: Sequence[Sequence[float | int]],
    level: str = "ordinal"
) -> dict[str, Any]:
    """
    Calcula Krippendorff's alpha para acuerdo entre evaluadores.
    
    Más robusto que Cohen's Kappa para múltiples evaluadores y datos faltantes.
    
    Args:
        ratings: Matriz de calificaciones [evaluador][item]
        level: "nominal", "ordinal", "interval", "ratio"
    
    Returns:
        Diccionario con resultados de Krippendorff's alpha
    """
    result: dict[str, Any] = {
        "status": "ok",
        "reason": None,
        "method": "krippendorff_alpha",
        "level": level,
        "n_raters": len(ratings),
        "n_items": 0,
        "alpha": None,
        "interpretation": None,
    }
    
    if len(ratings) < 2:
        result.update(
            status="insufficient_data",
            reason="Se requieren al menos 2 evaluadores."
        )
        return result
    
    # Determinar número de items (longitud máxima)
    n_items = max(len(r) for r in ratings)
    result["n_items"] = n_items
    
    if n_items < 2:
        result.update(
            status="insufficient_data",
            reason="Se requieren al menos 2 items."
        )
        return result
    
    try:
        # Intentar usar krippendorff si está disponible
        try:
            import krippendorff
            # Convertir a formato esperado por la librería
            # ratings debe ser una lista de listas donde cada sublista es un item
            ratings_transposed = []
            for i in range(n_items):
                item_ratings = []
                for rater in ratings:
                    if i < len(rater):
                        item_ratings.append(rater[i])
                ratings_transposed.append(item_ratings)
            
            alpha = krippendorff.alpha(ratings_transposed, level_of_measurement=level)
            result["alpha"] = float(alpha)
            
            # Interpretación según Krippendorff (2011)
            if alpha < 0:
                interpretation = "Acuerdo menor que el azar (discrepancia sistemática)"
            elif alpha <= 0.33:
                interpretation = "Acuerdo pobre"
            elif alpha <= 0.67:
                interpretation = "Acuerdo tentativo"
            else:
                interpretation = "Acuerdo definitivo"
            
            result["interpretation"] = interpretation
        except ImportError:
            # Implementación manual si krippendorff no está disponible
            result.update(
                status="not_estimable",
                reason="La librería krippendorff no está instalada. Agregar a requirements.txt: krippendorff"
            )
    except Exception as e:
        result.update(
            status="not_estimable",
            reason=f"No se pudo calcular Krippendorff's alpha: {str(e)}"
        )
    
    return result


def cronbach_alpha(
    ratings: Sequence[Sequence[float | int]]
) -> dict[str, Any]:
    """
    Calcula alfa de Cronbach para consistencia interna de escalas.
    
    Útil para evaluar la confiabilidad interna de cuestionarios como SUS.
    
    Args:
        ratings: Matriz de respuestas [sujeto][item]
    
    Returns:
        Diccionario con resultados de alfa de Cronbach
    """
    result: dict[str, Any] = {
        "status": "ok",
        "reason": None,
        "method": "cronbach_alpha",
        "n_subjects": len(ratings),
        "n_items": 0,
        "alpha": None,
        "interpretation": None,
    }
    
    if len(ratings) < 2:
        result.update(
            status="insufficient_data",
            reason="Se requieren al menos 2 sujetos."
        )
        return result
    
    # Determinar número de items
    n_items = len(ratings[0])
    result["n_items"] = n_items
    
    if n_items < 2:
        result.update(
            status="insufficient_data",
            reason="Se requieren al menos 2 items."
        )
        return result
    
    # Verificar que todos los sujetos tengan el mismo número de items
    for subject in ratings:
        if len(subject) != n_items:
            result.update(
                status="invalid_data",
                reason="Todos los sujetos deben tener el mismo número de items."
            )
            return result
    
    try:
        # Convertir a array de numpy
        import numpy as np
        ratings_array = np.array(ratings)
        
        # Calcular varianza de cada item
        item_variances = np.var(ratings_array, axis=0, ddof=1)
        
        # Calcular varianza de los totales
        totals = np.sum(ratings_array, axis=1)
        total_variance = np.var(totals, ddof=1)
        
        # Alfa de Cronbach
        if total_variance == 0:
            result.update(
                status="not_estimable",
                reason="La varianza de los totales es cero (no hay variación entre sujetos)."
            )
            return result
        
        alpha = (n_items / (n_items - 1)) * (1 - (np.sum(item_variances) / total_variance))
        result["alpha"] = float(alpha)
        
        # Interpretación según DeVellis (2012)
        if alpha < 0.5:
            interpretation = "Confiabilidad inaceptable"
        elif alpha < 0.6:
            interpretation = "Confiabilidad pobre"
        elif alpha < 0.7:
            interpretation = "Confiabilidad cuestionable"
        elif alpha < 0.8:
            interpretation = "Confiabilidad aceptable"
        elif alpha < 0.9:
            interpretation = "Confiabilidad buena"
        else:
            interpretation = "Confiabilidad excelente"
        
        result["interpretation"] = interpretation
    except ImportError:
        result.update(
            status="not_estimable",
            reason="NumPy no está disponible."
        )
    except Exception as e:
        result.update(
            status="not_estimable",
            reason=f"No se pudo calcular alfa de Cronbach: {str(e)}"
        )
    
    return result


# ==============================================================================
# CORRECCIÓN POR COMPARACIONES MÚLTIPLES
# ==============================================================================

def holm_correction(
    p_values: Sequence[float],
    alpha: float = 0.05
) -> dict[str, Any]:
    """
    Aplica corrección de Holm-Bonferroni para comparaciones múltiples.
    
    Método step-down más potente que Bonferroni, recomendado como predeterminado.
    
    Args:
        p_values: Lista de p-values
        alpha: Nivel de significancia original
    
    Returns:
        Diccionario con p-values corregidos y resultados
    """
    result: dict[str, Any] = {
        "status": "ok",
        "reason": None,
        "method": "holm",
        "original_alpha": alpha,
        "n_comparisons": len(p_values),
        "p_values_original": list(p_values),
        "p_values_corrected": [],
        "significant_original": [],
        "significant_corrected": [],
        "rejection_order": [],
    }
    
    if not p_values:
        result.update(status="insufficient_data", reason="No se proporcionaron p-values.")
        return result
    
    # Validar p-values
    for p in p_values:
        if not isinstance(p, (int, float)) or p < 0 or p > 1:
            result.update(
                status="invalid_data",
                reason="Los p-values deben estar entre 0 y 1."
            )
            return result
    
    # Ordenar p-values y mantener índices originales
    indexed_pvalues = list(enumerate(p_values))
    indexed_pvalues.sort(key=lambda x: x[1])  # Ordenar por p-value
    
    # Aplicar corrección de Holm
    corrected_pvalues = [None] * len(p_values)
    n = len(p_values)
    
    for i, (original_idx, p) in enumerate(indexed_pvalues):
        # Holm: p_corrected = p * (n - i)
        corrected = p * (n - i)
        corrected_pvalues[original_idx] = min(corrected, 1.0)
        result["rejection_order"].append(original_idx)
    
    result["p_values_corrected"] = corrected_pvalues
    
    # Determinar significancia
    for i, p in enumerate(p_values):
        result["significant_original"].append(p < alpha)
        result["significant_corrected"].append(corrected_pvalues[i] < alpha)
    
    return result


# ==============================================================================
# VALIDACIÓN DE CALIDAD DE DATOS
# ==============================================================================

def validate_data_quality(
    data: dict[str, Any],
    test_type: str,
    design: str = "independent",
    min_observations: int = 5
) -> dict[str, Any]:
    """
    Valida la calidad de los datos antes de ejecutar un análisis estadístico.
    
    Realiza verificaciones exhaustivas según Sección 17.1.2 de las especificaciones.
    
    Args:
        data: Diccionario con los datos a validar
        test_type: Tipo de prueba estadística planificada
        design: "independent", "paired", "repeated_measures"
        min_observations: Mínimo de observaciones requeridas
    
    Returns:
        Diccionario con reporte de calidad de datos y recomendaciones
    """
    result: dict[str, Any] = {
        "status": "ok",
        "reason": None,
        "can_proceed": True,
        "warnings": [],
        "errors": [],
        "quality_report": {
            "total_records": 0,
            "usable_records": 0,
            "duplicates": 0,
            "missing_values": 0,
            "out_of_range_values": 0,
            "incomplete_pairs": 0,
            "empty_conditions": [],
            "missing_evaluators": 0,
            "inconsistent_scales": 0,
            "negative_durations": 0,
            "orphan_ids": 0,
        },
        "test_type": test_type,
        "design": design,
    }
    
    # Extraer datos según estructura esperada
    groups = data.get("groups", {})
    if not groups:
        result.update(
            status="invalid_data",
            reason="No se proporcionaron grupos de datos."
        )
        result["can_proceed"] = False
        return result
    
    # Análisis básico de registros
    total_records = sum(len(g.get("values", [])) for g in groups.values())
    result["quality_report"]["total_records"] = total_records
    
    if total_records < min_observations:
        result["errors"].append(f"Insuficientes observaciones: {total_records} < {min_observations}")
        result["can_proceed"] = False
    
    # Verificar condiciones vacías
    for group_name, group_data in groups.items():
        values = group_data.get("values", [])
        if len(values) == 0:
            result["quality_report"]["empty_conditions"].append(group_name)
            result["errors"].append(f"Condición '{group_name}' está vacía.")
            result["can_proceed"] = False
    
    # Verificar pares incompletos para diseños pareados
    if design in ["paired", "repeated_measures"]:
        group_names = list(groups.keys())
        if len(group_names) >= 2:
            sizes = [len(groups[g].get("values", [])) for g in group_names]
            if len(set(sizes)) > 1:
                result["errors"].append(f"Diseño pareado pero los grupos tienen tamaños diferentes: {sizes}")
                result["can_proceed"] = False
    
    # Verificar valores faltantes
    for group_name, group_data in groups.items():
        values = group_data.get("values", [])
        missing = sum(1 for v in values if v is None or (isinstance(v, float) and math.isnan(v)))
        result["quality_report"]["missing_values"] += missing
        if missing > 0:
            result["warnings"].append(f"Grupo '{group_name}' tiene {missing} valores faltantes.")
    
    # Verificar valores fuera de rango
    for group_name, group_data in groups.items():
        values = group_data.get("values", [])
        min_val = group_data.get("min_value")
        max_val = group_data.get("max_value")
        
        if min_val is not None or max_val is not None:
            out_of_range = 0
            for v in values:
                if v is None or (isinstance(v, float) and math.isnan(v)):
                    continue
                if min_val is not None and v < min_val:
                    out_of_range += 1
                if max_val is not None and v > max_val:
                    out_of_range += 1
            result["quality_report"]["out_of_range_values"] += out_of_range
            if out_of_range > 0:
                result["warnings"].append(f"Grupo '{group_name}' tiene {out_of_range} valores fuera de rango.")
    
    # Verificar duraciones negativas (si aplica)
    if data.get("has_durations", False):
        for group_name, group_data in groups.items():
            values = group_data.get("values", [])
            negative = sum(1 for v in values if isinstance(v, (int, float)) and v < 0)
            result["quality_report"]["negative_durations"] += negative
            if negative > 0:
                result["errors"].append(f"Grupo '{group_name}' tiene {negative} duraciones negativas.")
                result["can_proceed"] = False
    
    # Verificar que no todos los valores sean idénticos
    all_values = []
    for group_data in groups.values():
        all_values.extend(group_data.get("values", []))
    
    all_values = [v for v in all_values if v is not None and not (isinstance(v, float) and math.isnan(v))]
    
    if len(all_values) > 1:
        if all(v == all_values[0] for v in all_values):
            result["errors"].append("Todos los valores son idénticos, no se puede calcular variación.")
            result["can_proceed"] = False
    
    # Verificar escalas inconsistentes (para datos ordinales)
    if data.get("is_ordinal", False):
        expected_scale = data.get("scale", [1, 2, 3, 4, 5])
        for group_name, group_data in groups.items():
            values = group_data.get("values", [])
            inconsistent = sum(1 for v in values if v not in expected_scale)
            result["quality_report"]["inconsistent_scales"] += inconsistent
            if inconsistent > 0:
                result["warnings"].append(f"Grupo '{group_name}' tiene {inconsistent} valores fuera de la escala esperada.")
    
    # Calcular registros utilizables
    usable = total_records - result["quality_report"]["missing_values"] - result["quality_report"]["out_of_range_values"]
    result["quality_report"]["usable_records"] = usable
    
    if usable < min_observations:
        result["errors"].append(f"Registros utilizables insuficientes: {usable} < {min_observations}")
        result["can_proceed"] = False
    
    # Determinar estado final
    if result["errors"]:
        result["status"] = "invalid_data"
        result["reason"] = "Errores críticos en calidad de datos impiden el análisis."
    elif result["warnings"]:
        result["status"] = "warnings"
        result["reason"] = "Datos analizables pero con advertencias."
    
    return result
