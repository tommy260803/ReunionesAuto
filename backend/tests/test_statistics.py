import math
import unittest

from scipy import stats

from app.metrics.statistics import (
    contingency_analysis,
    welch_t_test,
    shapiro_wilk_test,
    levene_test,
    mann_whitney_u_test,
    friedman_test,
    mcnemar_test,
    cochran_q_test,
    holm_correction,
    cronbach_alpha,
    validate_data_quality,
)


class WelchTTestTests(unittest.TestCase):
    def test_reports_descriptive_inferential_and_effect_statistics(self):
        sample_a = [1.0, 2.0, 3.0, 4.0, 7.0]
        sample_b = [2.0, 4.0, 5.0, 8.0, 10.0, 11.0]

        result = welch_t_test(sample_a, sample_b)
        reference = stats.ttest_ind(sample_b, sample_a, equal_var=False)

        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["alternative"], "two_sided")
        self.assertEqual(result["group_a"]["n"], 5)
        self.assertEqual(result["group_b"]["n"], 6)
        self.assertAlmostEqual(result["group_a"]["median"], 3.0)
        self.assertAlmostEqual(result["group_a"]["iqr"], 2.0)
        self.assertLess(result["group_a"]["mean_ci_95_low"], result["group_a"]["mean"])
        self.assertGreater(result["group_a"]["mean_ci_95_high"], result["group_a"]["mean"])
        self.assertAlmostEqual(result["mean_difference"], 3.266666666666667)
        self.assertAlmostEqual(result["t_statistic"], float(reference.statistic), places=12)
        self.assertAlmostEqual(result["p_value"], float(reference.pvalue), places=12)
        self.assertLess(result["ci_95_low"], result["mean_difference"])
        self.assertGreater(result["ci_95_high"], result["mean_difference"])
        self.assertGreater(result["hedges_g"], 0)

    def test_insufficient_data_does_not_fabricate_probability(self):
        result = welch_t_test([1.0], [2.0, 3.0])

        self.assertEqual(result["status"], "insufficient_data")
        self.assertIsNone(result["p_value"])
        self.assertIsNone(result["is_significant"])
        self.assertEqual(result["group_a"]["n"], 1)

    def test_constant_samples_are_not_estimable(self):
        result = welch_t_test([2.0, 2.0, 2.0], [3.0, 3.0, 3.0])

        self.assertEqual(result["status"], "not_estimable")
        self.assertIsNone(result["p_value"])
        self.assertAlmostEqual(result["mean_difference"], 1.0)

    def test_non_finite_input_is_invalid(self):
        result = welch_t_test([1.0, math.nan], [2.0, 3.0])

        self.assertEqual(result["status"], "invalid_data")
        self.assertIsNone(result["p_value"])


class ContingencyAnalysisTests(unittest.TestCase):
    def test_uses_uncorrected_pearson_when_all_expected_cells_are_at_least_five(self):
        result = contingency_analysis(80, 20, 60, 40)
        reference = stats.chi2_contingency([[80, 20], [60, 40]], correction=False)

        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["method"], "pearson_chi_square")
        self.assertFalse(result["correction"])
        self.assertEqual(result["df"], 1)
        self.assertAlmostEqual(result["statistic"], float(reference.statistic), places=12)
        self.assertAlmostEqual(result["p_value"], float(reference.pvalue), places=12)
        self.assertAlmostEqual(result["success_rate_a"], 0.8)
        self.assertAlmostEqual(result["success_rate_b"], 0.6)
        self.assertAlmostEqual(result["risk_difference"], -0.2)
        self.assertAlmostEqual(result["odds_ratio"], 0.375)
        self.assertLess(result["odds_ratio_ci_95_low"], result["odds_ratio"])
        self.assertGreater(result["odds_ratio_ci_95_high"], result["odds_ratio"])
        self.assertLess(result["risk_difference_ci_95_low"], result["risk_difference"])
        self.assertGreater(result["risk_difference_ci_95_high"], result["risk_difference"])
        self.assertIsNotNone(result["cramers_v"])

    def test_uses_two_sided_fisher_for_sparse_expected_cells(self):
        result = contingency_analysis(1, 9, 8, 2)
        reference = stats.fisher_exact([[8, 2], [1, 9]], alternative="two-sided")

        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["method"], "fisher_exact")
        self.assertFalse(result["correction"])
        self.assertTrue(any(cell < 5 for row in result["expected"] for cell in row))
        self.assertAlmostEqual(result["p_value"], float(reference.pvalue), places=12)
        self.assertAlmostEqual(result["odds_ratio"], 36.0)
        self.assertEqual(result["statistic"], result["odds_ratio"])
        self.assertIsNone(result["df"])
        self.assertIsNone(result["cramers_v"])

    def test_zero_cell_uses_haldane_anscombe_odds_ratio(self):
        result = contingency_analysis(0, 8, 4, 4)

        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["method"], "fisher_exact")
        self.assertEqual(result["odds_ratio_adjustment"], "haldane_anscombe")
        self.assertIsNotNone(result["odds_ratio"])
        self.assertGreater(result["odds_ratio"], 0)
        self.assertLess(result["odds_ratio_ci_95_low"], result["odds_ratio"])
        self.assertGreater(result["odds_ratio_ci_95_high"], result["odds_ratio"])

    def test_empty_period_is_insufficient_without_probability(self):
        result = contingency_analysis(0, 0, 4, 2)

        self.assertEqual(result["status"], "insufficient_data")
        self.assertIsNone(result["p_value"])
        self.assertIsNone(result["method"])

    def test_no_outcome_variation_is_not_estimable(self):
        result = contingency_analysis(5, 0, 7, 0)

        self.assertEqual(result["status"], "not_estimable")
        self.assertEqual(result["success_rate_a"], 1.0)
        self.assertEqual(result["success_rate_b"], 1.0)
        self.assertEqual(result["expected"], [[5.0, 0.0], [7.0, 0.0]])
        self.assertIsNone(result["p_value"])

    def test_rejects_non_integer_or_negative_counts(self):
        for counts in ((1.5, 2, 3, 4), (1, -1, 3, 4), (True, 2, 3, 4)):
            with self.subTest(counts=counts):
                result = contingency_analysis(*counts)
                self.assertEqual(result["status"], "invalid_data")
                self.assertIsNone(result["p_value"])


class ShapiroWilkTestTests(unittest.TestCase):
    def test_normal_data_passes_normality_test(self):
        # Datos normales generados
        import numpy as np
        np.random.seed(42)
        normal_data = np.random.normal(loc=0, scale=1, size=50).tolist()
        
        result = shapiro_wilk_test(normal_data)
        
        self.assertEqual(result["status"], "ok")
        self.assertIsNotNone(result["statistic"])
        self.assertIsNotNone(result["p_value"])
        self.assertEqual(result["n"], 50)
        self.assertTrue(result["is_normal"])  # Datos normales deberían pasar

    def test_insufficient_data_rejected(self):
        result = shapiro_wilk_test([1.0, 2.0])
        
        self.assertEqual(result["status"], "insufficient_data")
        self.assertIsNone(result["p_value"])

    def test_large_sample_warned(self):
        import numpy as np
        np.random.seed(42)
        large_data = np.random.normal(loc=0, scale=1, size=6000).tolist()
        
        result = shapiro_wilk_test(large_data)
        
        self.assertEqual(result["status"], "invalid_data")
        self.assertIn("5000", result["reason"])


class LeveneTestTests(unittest.TestCase):
    def test_equal_variances_detected(self):
        import numpy as np
        np.random.seed(42)
        group1 = np.random.normal(loc=0, scale=1, size=30).tolist()
        group2 = np.random.normal(loc=0, scale=1, size=30).tolist()
        
        result = levene_test(group1, group2)
        
        self.assertEqual(result["status"], "ok")
        self.assertIsNotNone(result["statistic"])
        self.assertIsNotNone(result["p_value"])
        self.assertEqual(result["n_groups"], 2)
        self.assertTrue(result["equal_variances"])  # Varianzas iguales

    def test_insufficient_groups_rejected(self):
        result = levene_test([1.0, 2.0, 3.0])
        
        self.assertEqual(result["status"], "invalid_data")
        self.assertIn("2 grupos", result["reason"])


class MannWhitneyUTestTests(unittest.TestCase):
    def test_independent_samples_compared(self):
        group1 = [1, 2, 3, 4, 5]
        group2 = [6, 7, 8, 9, 10]
        
        result = mann_whitney_u_test(group1, group2)
        
        self.assertEqual(result["status"], "ok")
        self.assertIsNotNone(result["u_statistic"])
        self.assertIsNotNone(result["p_value"])
        self.assertTrue(result["is_significant"])  # Diferencia clara
        self.assertIsNotNone(result["median_difference"])
        self.assertIsNotNone(result["effect_size_r"])

    def test_insufficient_data_rejected(self):
        result = mann_whitney_u_test([1.0], [2.0])
        
        self.assertEqual(result["status"], "insufficient_data")


class FriedmanTestTests(unittest.TestCase):
    def test_related_conditions_compared(self):
        # 3 condiciones, 5 sujetos
        condition1 = [7, 8, 6, 7, 8]
        condition2 = [5, 6, 5, 6, 5]
        condition3 = [9, 8, 9, 8, 9]
        
        result = friedman_test(condition1, condition2, condition3)
        
        self.assertEqual(result["status"], "ok")
        self.assertIsNotNone(result["statistic"])
        self.assertIsNotNone(result["p_value"])
        self.assertEqual(result["n_groups"], 3)
        self.assertEqual(result["n_observations"], 5)
        self.assertIsNotNone(result["kendall_w"])

    def test_insufficient_conditions_rejected(self):
        result = friedman_test([1, 2, 3], [4, 5, 6])
        
        self.assertEqual(result["status"], "invalid_data")
        self.assertIn("3 grupos", result["reason"])


class McNemarTestTests(unittest.TestCase):
    def test_paired_binary_data_compared(self):
        before = [True, True, False, False, True]
        after = [True, False, False, True, True]
        
        result = mcnemar_test(before, after)
        
        self.assertEqual(result["status"], "ok")
        self.assertIsNotNone(result["statistic"])
        self.assertIsNotNone(result["p_value"])
        self.assertIsNotNone(result["contingency_table"])
        self.assertIsNotNone(result["proportion_before"])
        self.assertIsNotNone(result["proportion_after"])

    def test_mismatched_sizes_rejected(self):
        result = mcnemar_test([True, False], [True])
        
        self.assertEqual(result["status"], "invalid_data")
        self.assertIn("mismo tamaño", result["reason"])


class CochranQTestTests(unittest.TestCase):
    def test_multiple_binary_conditions_compared(self):
        # 3 condiciones, 4 sujetos
        condition1 = [True, True, False, True]
        condition2 = [False, True, False, True]
        condition3 = [True, False, True, False]
        
        result = cochran_q_test(condition1, condition2, condition3)
        
        self.assertEqual(result["status"], "ok")
        self.assertIsNotNone(result["statistic"])
        self.assertIsNotNone(result["p_value"])
        self.assertEqual(result["n_conditions"], 3)
        self.assertEqual(result["n_observations"], 4)
        self.assertIsNotNone(result["proportions"])

    def test_insufficient_conditions_rejected(self):
        result = cochran_q_test([True, False], [False, True])
        
        self.assertEqual(result["status"], "invalid_data")
        self.assertIn("3 condiciones", result["reason"])


class HolmCorrectionTests(unittest.TestCase):
    def test_p_values_corrected_step_down(self):
        p_values = [0.01, 0.04, 0.03, 0.02, 0.05]
        
        result = holm_correction(p_values)
        
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["n_comparisons"], 5)
        self.assertEqual(len(result["p_values_corrected"]), 5)
        # Los p-values corregidos deberían ser >= los originales
        for orig, corr in zip(p_values, result["p_values_corrected"]):
            self.assertGreaterEqual(corr, orig)

    def test_empty_p_values_rejected(self):
        result = holm_correction([])
        
        self.assertEqual(result["status"], "insufficient_data")

    def test_invalid_p_values_rejected(self):
        result = holm_correction([0.5, 1.5, 0.3])
        
        self.assertEqual(result["status"], "invalid_data")


class CronbachAlphaTests(unittest.TestCase):
    def test_consistent_scale_measured(self):
        # 5 items, 4 sujetos
        ratings = [
            [5, 4, 5, 4, 5],  # Sujeto 1
            [4, 5, 4, 5, 4],  # Sujeto 2
            [5, 5, 4, 4, 5],  # Sujeto 3
            [4, 4, 5, 5, 4],  # Sujeto 4
        ]
        
        result = cronbach_alpha(ratings)
        
        self.assertEqual(result["status"], "ok")
        self.assertIsNotNone(result["alpha"])
        self.assertEqual(result["n_subjects"], 4)
        self.assertEqual(result["n_items"], 5)
        self.assertGreater(result["alpha"], 0.7)  # Buena consistencia

    def test_insufficient_subjects_rejected(self):
        result = cronbach_alpha([[5, 4, 5]])
        
        self.assertEqual(result["status"], "insufficient_data")

    def test_no_variation_rejected(self):
        result = cronbach_alpha([
            [5, 5, 5],
            [5, 5, 5],
        ])
        
        self.assertEqual(result["status"], "not_estimable")


class DataQualityValidationTests(unittest.TestCase):
    def test_valid_data_passes(self):
        data = {
            "groups": {
                "group1": {"values": [1, 2, 3, 4, 5]},
                "group2": {"values": [2, 3, 4, 5, 6]},
            }
        }
        
        result = validate_data_quality(data, "welch_t_test", "independent")
        
        self.assertEqual(result["status"], "ok")
        self.assertTrue(result["can_proceed"])
        self.assertEqual(len(result["errors"]), 0)

    def test_empty_condition_detected(self):
        data = {
            "groups": {
                "group1": {"values": [1, 2, 3]},
                "group2": {"values": []},
            }
        }
        
        result = validate_data_quality(data, "welch_t_test", "independent")
        
        self.assertFalse(result["can_proceed"])
        self.assertIn("vacía", result["errors"][0])

    def test_missing_values_warned(self):
        data = {
            "groups": {
                "group1": {"values": [1, 2, None, 4, 5]},
                "group2": {"values": [2, 3, 4, 5, 6]},
            }
        }
        
        result = validate_data_quality(data, "welch_t_test", "independent")
        
        self.assertTrue(result["can_proceed"])  # Advertencia, no error
        self.assertEqual(result["status"], "warnings")
        self.assertGreater(len(result["warnings"]), 0)

    def test_paired_design_size_mismatch_detected(self):
        data = {
            "groups": {
                "group1": {"values": [1, 2, 3]},
                "group2": {"values": [1, 2, 3, 4]},
            }
        }
        
        result = validate_data_quality(data, "paired_t_test", "paired")
        
        self.assertFalse(result["can_proceed"])
        self.assertIn("tamaños diferentes", result["errors"][0])


if __name__ == "__main__":
    unittest.main()
