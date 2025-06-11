import unittest
import os

# Assuming other components are correctly pathed for import
# For tests, we might use mocks, but for basic instantiation, direct imports are fine.
try:
    from farg.report_generation.report_generator import ReportGenerator
    from farg.report_generation.report_template_engine import ReportTemplateEngine
    from farg.report_generation.report_generator_components import (
        CompanyProfileGenerator,
        FinancialPerformanceComparator,
        StrategicOperationalIssueIdentifier
    )
    from farg.insight_generation_recommendation.insight_generator import InsightGenerator
    from farg.insight_generation_recommendation.recommendation_engine import RecommendationEngine
except ImportError:
    import sys
    # Add the project root to sys.path, assuming tests are in farg/tests/some_module/
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))
    from farg.report_generation.report_generator import ReportGenerator
    from farg.report_generation.report_template_engine import ReportTemplateEngine
    from farg.report_generation.report_generator_components import (
        CompanyProfileGenerator,
        FinancialPerformanceComparator,
        StrategicOperationalIssueIdentifier
    )
    from farg.insight_generation_recommendation.insight_generator import InsightGenerator
    from farg.insight_generation_recommendation.recommendation_engine import RecommendationEngine


class TestReportGenerator(unittest.TestCase):
    """
    Unit tests for the ReportGenerator class.
    """

    def setUp(self):
        """Initialize the generator and its dependencies for each test."""
        # Instantiate all dependent components
        self.mock_template_engine = ReportTemplateEngine()
        self.mock_profile_gen = CompanyProfileGenerator()
        self.mock_perf_comp = FinancialPerformanceComparator()
        self.mock_issue_id = StrategicOperationalIssueIdentifier()
        self.mock_insight_gen = InsightGenerator()
        self.mock_reco_engine = RecommendationEngine()

        self.report_generator = ReportGenerator(
            report_template_engine=self.mock_template_engine,
            company_profile_generator=self.mock_profile_gen,
            financial_performance_comparator=self.mock_perf_comp,
            strategic_operational_issue_identifier=self.mock_issue_id,
            insight_generator=self.mock_insight_gen,
            recommendation_engine=self.mock_reco_engine
        )

        # Define placeholder paths for raw data (these files don't need to exist for current simulation)
        self.company_A_dummy_path = "dummy_data/company_A_report.pdf"
        self.company_B_dummy_path = "dummy_data/company_B_report.pdf"

    def test_import_and_instantiation_report_generator(self):
        """Test that ReportGenerator can be imported and instantiated."""
        self.assertIsInstance(self.report_generator, ReportGenerator)

    def test_generate_full_report_returns_string_single_company(self):
        """Test that generate_full_report returns a string for a single company."""
        # Using the single company template for this test
        report_str = self.report_generator.generate_full_report(
            company_A_raw_data_path=self.company_A_dummy_path,
            company_B_raw_data_path=None, # Explicitly None for single company
            template_name="single_company_deep_dive_v1"
        )
        self.assertIsInstance(report_str, str)
        self.assertTrue(len(report_str) > 0, "Generated report string should not be empty.")
        self.assertIn("Alpha Corp (Simulated)", report_str) # Check for some expected content
        self.assertNotIn("Beta LLC (Simulated)", report_str) # Ensure Company B data is not present
        self.assertIn("[Note: This report was populated using a basic simulation.]", report_str)


    def test_generate_full_report_returns_string_comparison(self):
        """Test that generate_full_report returns a string for a comparison."""
        report_str = self.report_generator.generate_full_report(
            company_A_raw_data_path=self.company_A_dummy_path,
            company_B_raw_data_path=self.company_B_dummy_path, # Provide path for Company B
            template_name="standard_comparison_report_v1"
        )
        self.assertIsInstance(report_str, str)
        self.assertTrue(len(report_str) > 0)
        self.assertIn("Alpha Corp (Simulated)", report_str)
        self.assertIn("Beta LLC (Simulated)", report_str) # Check for Company B content
        self.assertIn("financial_comparison_summary", report_str.lower()) # Check if comparison section title is hinted

    def test_generate_full_report_handles_template_not_found(self):
        """Test that generate_full_report handles a non-existent template gracefully."""
        # This test depends on how ReportGenerator handles template loading errors.
        # Assuming it might return an error message string or raise an exception that
        # could be caught and converted to an error string by a higher level.
        # For now, the template engine raises ValueError, which generate_full_report catches.
        report_str = self.report_generator.generate_full_report(
            company_A_raw_data_path=self.company_A_dummy_path,
            template_name="non_existent_template_for_sure_xyz123"
        )
        self.assertIsInstance(report_str, str)
        self.assertIn("Failed to generate report due to template error", report_str)
        self.assertIn("Template 'non_existent_template_for_sure_xyz123' not found", report_str)

if __name__ == '__main__':
    unittest.main()
