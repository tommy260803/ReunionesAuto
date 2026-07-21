"""Módulo de ejecución de análisis estadístico."""

from typing import Any

from app.metrics.statistics import (
    bonferroni_correction,
    calculate_classification_metrics,
    calculate_inter_rater_agreement,
    cronbach_alpha,
    friedman_test,
    holm_correction,
    krippendorff_alpha,
    mann_whitney_u_test,
    mcnemar_test,
    paired_t_test,
    shapiro_wilk_test,
    validate_data_quality,
    welch_t_test,
)


def select_statistical_test(
    variable_type: str,
    n_conditions: int,
    design: str,
    sample_size: int,
    is_normal: bool | None = None,
    equal_variances: bool | None = None,
) -> dict[str, Any]:
    """
    Selector automático de prueba estadística según Sección 18.
    
    Analiza el tipo de variable, número de condiciones y diseño para sugerir
    la prueba estadística apropiada.
    
    Args:
        variable_type: Tipo de variable (continuous, ordinal, binary)
        n_conditions: Número de condiciones/grupos
        design: Diseño del estudio (independent, paired, repeated_measures)
        sample_size: Tamaño de muestra total
        is_normal: Si se conoce, si los datos son normales
        equal_variances: Si se conoce, si las varianzas son iguales
    
    Returns:
        Diccionario con prueba sugerida y justificación
    """
    result: dict[str, Any] = {
        "suggested_test": None,
        "alternative_tests": [],
        "justification": "",
        "assumptions": [],
        "warnings": [],
    }
    
    # Validar entradas
    if variable_type not in ["continuous", "ordinal", "binary"]:
        result["warnings"].append("Tipo de variable no reconocido")
        variable_type = "continuous"  # Default
    
    if design not in ["independent", "paired", "repeated_measures"]:
        result["warnings"].append("Diseño no reconocido, asumiendo independiente")
        design = "independent"
    
    # Lógica de selección según especificaciones
    if variable_type == "binary":
        # Datos binarios
        if design == "paired" and n_conditions == 2:
            result["suggested_test"] = "mcnemar"
            result["justification"] = "Datos binarios pareados con 2 condiciones"
            result["assumptions"] = ["Datos pareados", "Muestras dependientes"]
            result["alternative_tests"] = ["cochran_q"] if n_conditions >= 3 else []
        elif design in ["paired", "repeated_measures"] and n_conditions >= 3:
            result["suggested_test"] = "cochran_q"
            result["justification"] = "Datos binarios pareados con 3+ condiciones"
            result["assumptions"] = ["Datos pareados", "Muestras dependientes"]
            result["alternative_tests"] = []
        else:
            result["suggested_test"] = "contingency_analysis"
            result["justification"] = "Datos binarios independientes"
            result["assumptions"] = ["Muestras independientes"]
            result["alternative_tests"] = []
    
    elif variable_type == "ordinal":
        # Datos ordinales
        if design == "independent" and n_conditions == 2:
            result["suggested_test"] = "mann_whitney_u"
            result["justification"] = "Datos ordinales independientes con 2 condiciones"
            result["assumptions"] = ["Muestras independientes", "Distribución similar"]
            result["alternative_tests"] = ["welch_t_test"] if is_normal and equal_variances else []
        elif design in ["paired", "repeated_measures"] and n_conditions == 2:
            result["suggested_test"] = "wilcoxon"
            result["justification"] = "Datos ordinales pareados con 2 condiciones"
            result["assumptions"] = ["Datos pareados", "Distribución simétrica de diferencias"]
            result["alternative_tests"] = ["paired_t_test"] if is_normal else []
        elif design in ["paired", "repeated_measures"] and n_conditions >= 3:
            result["suggested_test"] = "friedman"
            result["justification"] = "Datos ordinales pareados con 3+ condiciones"
            result["assumptions"] = ["Datos pareados", "Bloques completos"]
            result["alternative_tests"] = []
        else:
            result["suggested_test"] = "kruskal_wallis"
            result["justification"] = "Datos ordinales independientes con 3+ condiciones"
            result["assumptions"] = ["Muestras independientes", "Distribución similar"]
            result["alternative_tests"] = []
    
    else:  # continuous
        # Datos continuos
        if design == "independent" and n_conditions == 2:
            if is_normal is None:
                # No se conoce normalidad, usar Welch por defecto (más robusto)
                result["suggested_test"] = "welch_t_test"
                result["justification"] = "Datos continuos independientes con 2 condiciones (Welch es robusto a desigualdad de varianzas)"
                result["assumptions"] = ["Muestras independientes", "Normalidad (recomendado)"]
                result["alternative_tests"] = ["mann_whitney_u"]
                result["warnings"].append("Se recomienda verificar normalidad con Shapiro-Wilk")
            elif is_normal and equal_variances:
                result["suggested_test"] = "t_test"
                result["justification"] = "Datos continuos independientes con 2 condiciones, normalidad y varianzas iguales"
                result["assumptions"] = ["Muestras independientes", "Normalidad", "Varianzas iguales"]
                result["alternative_tests"] = ["welch_t_test"]
            elif is_normal:
                result["suggested_test"] = "welch_t_test"
                result["justification"] = "Datos continuos independientes con 2 condiciones, normalidad pero varianzas posiblemente diferentes"
                result["assumptions"] = ["Muestras independientes", "Normalidad"]
                result["alternative_tests"] = ["mann_whitney_u"]
            else:
                result["suggested_test"] = "mann_whitney_u"
                result["justification"] = "Datos continuos independientes con 2 condiciones, sin normalidad"
                result["assumptions"] = ["Muestras independientes", "Distribución similar"]
                result["alternative_tests"] = ["welch_t_test"]
        
        elif design in ["paired", "repeated_measures"] and n_conditions == 2:
            if is_normal:
                result["suggested_test"] = "paired_t_test"
                result["justification"] = "Datos continuos pareados con 2 condiciones, normalidad"
                result["assumptions"] = ["Datos pareados", "Normalidad de diferencias"]
                result["alternative_tests"] = ["wilcoxon"]
            else:
                result["suggested_test"] = "wilcoxon"
                result["justification"] = "Datos continuos pareados con 2 condiciones, sin normalidad"
                result["assumptions"] = ["Datos pareados", "Distribución simétrica de diferencias"]
                result["alternative_tests"] = ["paired_t_test"]
        
        elif design in ["paired", "repeated_measures"] and n_conditions >= 3:
            if is_normal:
                result["suggested_test"] = "repeated_measures_anova"
                result["justification"] = "Datos continuos pareados con 3+ condiciones, normalidad"
                result["assumptions"] = ["Datos pareados", "Normalidad", "Esfericidad"]
                result["alternative_tests"] = ["friedman"]
                result["warnings"].append("Prueba no implementada aún, usar Friedman como alternativa")
                result["suggested_test"] = "friedman"
            else:
                result["suggested_test"] = "friedman"
                result["justification"] = "Datos continuos pareados con 3+ condiciones, sin normalidad"
                result["assumptions"] = ["Datos pareados", "Bloques completos"]
                result["alternative_tests"] = []
        
        elif design == "independent" and n_conditions >= 3:
            if is_normal and equal_variances:
                result["suggested_test"] = "one_way_anova"
                result["justification"] = "Datos continuos independientes con 3+ condiciones, normalidad y varianzas iguales"
                result["assumptions"] = ["Muestras independientes", "Normalidad", "Varianzas iguales"]
                result["alternative_tests"] = ["kruskal_wallis"]
                result["warnings"].append("Prueba no implementada aún, usar Kruskal-Wallis como alternativa")
                result["suggested_test"] = "kruskal_wallis"
            else:
                result["suggested_test"] = "kruskal_wallis"
                result["justification"] = "Datos continuos independientes con 3+ condiciones, sin normalidad o varianzas desiguales"
                result["assumptions"] = ["Muestras independientes", "Distribución similar"]
                result["alternative_tests"] = []
    
    # Advertencias sobre tamaño de muestra
    if sample_size < 30:
        result["warnings"].append("Tamaño de muestra pequeño (<30), considerar pruebas no paramétricas")
    
    return result


def execute_analysis(
    data: dict[str, Any],
    test_type: str,
    design: str = "independent",
    alpha: float = 0.05,
    correction: str | None = None,
) -> dict[str, Any]:
    """
    Ejecuta un análisis estadístico basado en el tipo de prueba solicitado.
    
    Args:
        data: Diccionario con los datos a analizar
        test_type: Tipo de prueba estadística
        design: Diseño del análisis (independent, paired, repeated_measures)
        alpha: Nivel de significancia
        correction: Tipo de corrección múltiple (bonferroni, holm, none)
    
    Returns:
        Diccionario con resultado del análisis
    """
    result: dict[str, Any] = {
        "status": "ok",
        "test_type": test_type,
        "design": design,
        "alpha": alpha,
        "correction": correction,
        "resultado": None,
        "descriptivos": None,
        "supuestos": None,
        "efecto": None,
        "intervalos": None,
        "advertencias": [],
        "interpretacion": None,
    }
    
    # Validar calidad de datos
    validation = validate_data_quality(data, test_type, design)
    if not validation["can_proceed"]:
        result["status"] = "invalid_data"
        result["reason"] = validation["reason"]
        result["advertencias"] = validation["errors"]
        return result
    
    # Extraer grupos
    groups = data.get("groups", {})
    group_names = list(groups.keys())
    
    # Ejecutar prueba según tipo
    if test_type == "welch_t_test":
        if len(group_names) != 2:
            result["status"] = "invalid_data"
            result["reason"] = "Welch t-test requiere exactamente 2 grupos"
            return result
        
        sample_a = groups[group_names[0]]["values"]
        sample_b = groups[group_names[1]]["values"]
        
        test_result = welch_t_test(sample_a, sample_b, alpha=alpha)
        result["resultado"] = test_result
        result["descriptivos"] = {
            "group_a": test_result["group_a"],
            "group_b": test_result["group_b"],
        }
        result["efecto"] = {
            "hedges_g": test_result["hedges_g"],
        }
        result["intervalos"] = {
            "mean_difference_ci": [test_result["ci_95_low"], test_result["ci_95_high"]],
        }
        
    elif test_type == "mann_whitney_u":
        if len(group_names) != 2:
            result["status"] = "invalid_data"
            result["reason"] = "Mann-Whitney U requiere exactamente 2 grupos"
            return result
        
        sample_a = groups[group_names[0]]["values"]
        sample_b = groups[group_names[1]]["values"]
        
        test_result = mann_whitney_u_test(sample_a, sample_b, alpha=alpha)
        result["resultado"] = test_result
        result["efecto"] = {
            "effect_size_r": test_result["effect_size_r"],
        }
        
    elif test_type == "paired_t_test":
        if len(group_names) != 2:
            result["status"] = "invalid_data"
            result["reason"] = "Prueba t pareada requiere exactamente 2 grupos"
            return result
        
        sample_a = groups[group_names[0]]["values"]
        sample_b = groups[group_names[1]]["values"]
        
        test_result = paired_t_test(sample_a, sample_b, alpha=alpha)
        result["resultado"] = test_result
        result["efecto"] = {
            "hedges_g": test_result["hedges_g"],
        }
        
    elif test_type == "friedman":
        if len(group_names) < 3:
            result["status"] = "invalid_data"
            result["reason"] = "Friedman requiere al menos 3 grupos"
            return result
        
        samples = [groups[name]["values"] for name in group_names]
        test_result = friedman_test(*samples, alpha=alpha)
        result["resultado"] = test_result
        result["efecto"] = {
            "kendall_w": test_result["kendall_w"],
        }
        
    elif test_type == "mcnemar":
        if len(group_names) != 2:
            result["status"] = "invalid_data"
            result["reason"] = "McNemar requiere exactamente 2 grupos"
            return result
        
        before = groups[group_names[0]]["values"]
        after = groups[group_names[1]]["values"]
        
        test_result = mcnemar_test(before, after, alpha=alpha)
        result["resultado"] = test_result
        
    elif test_type == "cochran_q":
        if len(group_names) < 3:
            result["status"] = "invalid_data"
            result["reason"] = "Q de Cochran requiere al menos 3 grupos"
            return result
        
        samples = [groups[name]["values"] for name in group_names]
        test_result = cochran_q_test(*samples, alpha=alpha)
        result["resultado"] = test_result
        
    elif test_type == "cronbach_alpha":
        ratings = [groups[name]["values"] for name in group_names]
        test_result = cronbach_alpha(ratings)
        result["resultado"] = test_result
        
    else:
        result["status"] = "invalid_data"
        result["reason"] = f"Tipo de prueba no soportado: {test_type}"
        return result
    
    # Aplicar corrección múltiple si se solicita
    if correction and correction != "none" and test_result.get("p_value"):
        if correction == "bonferroni":
            correction_result = bonferroni_correction([test_result["p_value"]], alpha)
        elif correction == "holm":
            correction_result = holm_correction([test_result["p_value"]], alpha)
        else:
            correction_result = None
        
        if correction_result:
            result["correction_result"] = correction_result
    
    # Generar interpretación
    result["interpretacion"] = generate_interpretation(test_result, test_type)
    
    return result


def generate_interpretation(test_result: dict[str, Any], test_type: str) -> str:
    """Genera una interpretación controlada del resultado."""
    if test_result["status"] != "ok":
        return f"No se pudo interpretar el resultado: {test_result.get('reason', 'Error desconocido')}"
    
    p_value = test_result.get("p_value")
    is_significant = test_result.get("is_significant")
    
    if p_value is None:
        return "No se dispone de p-value para interpretación."
    
    if is_significant:
        return f"El resultado es estadísticamente significativo (p = {p_value:.4f}). Se rechaza la hipótesis nula."
    else:
        return f"El resultado no es estadísticamente significativo (p = {p_value:.4f}). No se puede rechazar la hipótesis nula."
