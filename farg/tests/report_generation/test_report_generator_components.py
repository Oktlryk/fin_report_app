import unittest
import os

try:
    from farg.report_generation.report_generator_components import (
        CompanyProfileGenerator,
        FinancialPerformanceComparator,
        StrategicOperationalIssueIdentifier
    )
except ImportError:
    import sys
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))
    from farg.report_generation.report_generator_components import (
        CompanyProfileGenerator,
        FinancialPerformanceComparator,
        StrategicOperationalIssueIdentifier
    )

class TestReportGeneratorComponents(unittest.TestCase):
    """
    Unit tests for components in report_generator_components.py.
    """

    def setUp(self):
        """Initialize components for each test."""
        self.profile_generator = CompanyProfileGenerator()
        self.performance_comparator = FinancialPerformanceComparator()
        self.issue_identifier = StrategicOperationalIssueIdentifier()

        # Sample data for CompanyProfileGenerator
        self.sample_company_info = {"company_name": "TestCo", "market_footprint": "Global"}
        self.sample_financial_summary = {"annual_revenue": "1B", "net_profit_margin": "10%"}

        # Sample data for FinancialPerformanceComparator
        self.comp_A_fin = {"profitability_ratios": {"net_profit_margin": 0.15}}
        self.comp_B_fin = {"profitability_ratios": {"net_profit_margin": 0.12}}

        # Sample data for StrategicOperationalIssueIdentifier
        self.sample_fin_analysis = {"benchmarking": {"liquidity_vs_industry": "below_average"}}
        self.sample_comp_analysis = {"swot": {"threats": ["New tech"]}}
        self.sample_insights = ["Concern: Liquidity is low."]


    # --- CompanyProfileGenerator Tests ---
    def test_company_profile_generator_instantiation(self):
        self.assertIsInstance(self.profile_generator, CompanyProfileGenerator)

    def test_generate_profile_data_returns_dict(self):
        result = self.profile_generator.generate_profile_data(self.sample_company_info, self.sample_financial_summary)
        self.assertIsInstance(result, dict)
        self.assertIn("name", result)
        self.assertIn("financial_summary_profile", result)
        self.assertIsInstance(result["financial_summary_profile"], dict)


    def test_generate_profile_data_invalid_input(self):
        with self.assertRaises(TypeError):
            self.profile_generator.generate_profile_data("bad", {}) # type: ignore
        with self.assertRaises(TypeError):
            self.profile_generator.generate_profile_data({}, "bad") # type: ignore

    # --- FinancialPerformanceComparator Tests ---
    def test_financial_performance_comparator_instantiation(self):
        self.assertIsInstance(self.performance_comparator, FinancialPerformanceComparator)

    def test_generate_comparison_data_returns_dict(self):
        result = self.performance_comparator.generate_comparison_data(self.comp_A_fin, self.comp_B_fin)
        self.assertIsInstance(result, dict)
        self.assertIn("comparison_summary", result)
        self.assertIn("profitability_comparison", result)

    def test_generate_comparison_data_invalid_input(self):
        with self.assertRaises(TypeError):
            self.performance_comparator.generate_comparison_data("bad", {}) # type: ignore
        with self.assertRaises(TypeError):
            self.performance_comparator.generate_comparison_data({}, "bad") # type: ignore

    # --- StrategicOperationalIssueIdentifier Tests ---
    def test_strategic_operational_issue_identifier_instantiation(self):
        self.assertIsInstance(self.issue_identifier, StrategicOperationalIssueIdentifier)

    def test_identify_issues_returns_dict_with_keys(self):
        result = self.issue_identifier.identify_issues(self.sample_fin_analysis, self.sample_comp_analysis, self.sample_insights)
        self.assertIsInstance(result, dict)
        self.assertIn("strategic_issues", result)
        self.assertIn("operational_issues", result)
        self.assertIsInstance(result["strategic_issues"], list)
        self.assertIsInstance(result["operational_issues"], list)
        # Check if insights trigger issue creation (based on dummy logic)
        self.assertTrue(any("Liquidity is low" in issue for issue in result["operational_issues"]))
        self.assertTrue(any("New tech" in issue for issue in result["strategic_issues"]))


    def test_identify_issues_invalid_input(self):
        with self.assertRaises(TypeError):
            self.issue_identifier.identify_issues("bad", {}, []) # type: ignore
        with self.assertRaises(TypeError):
            self.issue_identifier.identify_issues({}, "bad", []) # type: ignore
        with self.assertRaises(TypeError):
            self.issue_identifier.identify_issues({}, {}, "bad") # type: ignore

    def test_identify_issues_empty_insights(self):
        """Test that it runs with empty insights list."""
        result = self.issue_identifier.identify_issues(self.sample_fin_analysis, self.sample_comp_analysis, [])
        self.assertIsInstance(result, dict)
        self.assertIn("strategic_issues", result)
        # Check that it still produces some baseline issues even without insights if logic allows
        self.assertTrue(len(result["strategic_issues"]) > 0 or len(result["operational_issues"]) > 0)


if __name__ == '__main__':
    unittest.main()
