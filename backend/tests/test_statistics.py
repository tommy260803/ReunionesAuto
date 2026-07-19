import math
import unittest

from scipy import stats

from app.metrics.statistics import contingency_analysis, welch_t_test


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


if __name__ == "__main__":
    unittest.main()
