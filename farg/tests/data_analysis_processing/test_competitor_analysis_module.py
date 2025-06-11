import unittest
import os

try:
    from farg.data_analysis_processing.competitor_analysis_module import CompetitorAnalysisModule
except ImportError:
    import sys
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))
    from farg.data_analysis_processing.competitor_analysis_module import CompetitorAnalysisModule

class TestCompetitorAnalysisModule(unittest.TestCase):
    """
    Unit tests for the CompetitorAnalysisModule class.
    """

    def setUp(self):
        """Initialize the module for each test."""
        self.module = CompetitorAnalysisModule()
        self.sample_company_data = {"name": "CompanyX", "kpis": {"npm": 0.1}}
        self.sample_competitor_data_list = [{"name": "CompA", "kpis": {"npm": 0.08}}]
        self.sample_market_data = {"trend": "growing"}
        self.sample_company_analysis = {"name": "CompanyX", "swot": {"strengths": ["S1"]}}
        self.sample_competitors_analysis_list = [{"name": "CompA", "swot": {"strengths": ["CS1"]}}]

    def test_import_competitor_analysis_module(self):
        """Test that CompetitorAnalysisModule can be imported and instantiated."""
        self.assertIsInstance(self.module, CompetitorAnalysisModule)

    def test_perform_swot_analysis_returns_dict(self):
        """Test SWOT analysis returns a dictionary."""
        result = self.module.perform_swot_analysis(
            self.sample_company_data, self.sample_competitor_data_list, self.sample_market_data
        )
        self.assertIsInstance(result, dict)
        self.assertIn("strengths", result)
        self.assertIn("weaknesses", result)
        self.assertIn("opportunities", result)
        self.assertIn("threats", result)
        self.assertIsInstance(result["strengths"], list)

    def test_perform_swot_analysis_invalid_input(self):
        """Test SWOT analysis with invalid input types."""
        with self.assertRaises(TypeError):
            self.module.perform_swot_analysis("bad", [], {}) # type: ignore
        with self.assertRaises(TypeError):
            self.module.perform_swot_analysis({}, "bad", {}) # type: ignore
        with self.assertRaises(TypeError):
            self.module.perform_swot_analysis({}, ["bad_item"], {}) # type: ignore
        with self.assertRaises(TypeError):
            self.module.perform_swot_analysis({}, [], "bad") # type: ignore

    def test_compare_performance_returns_dict(self):
        """Test performance comparison returns a dictionary."""
        result = self.module.compare_performance(
            self.sample_company_analysis, self.sample_competitors_analysis_list
        )
        self.assertIsInstance(result, dict)
        self.assertIn("overall_comparison_summary", result)

    def test_compare_performance_invalid_input(self):
        """Test performance comparison with invalid input types."""
        with self.assertRaises(TypeError):
            self.module.compare_performance("bad", []) # type: ignore
        with self.assertRaises(TypeError):
            self.module.compare_performance({}, "bad") # type: ignore
        with self.assertRaises(TypeError):
            self.module.compare_performance({}, ["bad_item"]) # type: ignore

    def test_compare_performance_no_competitors(self):
        """Test performance comparison with an empty list of competitors."""
        result = self.module.compare_performance(self.sample_company_analysis, [])
        self.assertIsInstance(result, dict)
        self.assertIn("No competitor data provided", result.get("overall_comparison_summary", ""), "Summary should indicate no competitor data")


if __name__ == '__main__':
    unittest.main()
