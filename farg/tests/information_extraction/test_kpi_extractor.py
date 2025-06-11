import unittest
import os

try:
    from farg.information_extraction.kpi_extractor import KPIExtractor
except ImportError:
    import sys
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))
    from farg.information_extraction.kpi_extractor import KPIExtractor

class TestKPIExtractor(unittest.TestCase):
    """
    Unit tests for the KPIExtractor class.
    """

    def setUp(self):
        """Initialize the extractor for each test."""
        self.extractor = KPIExtractor()
        self.sample_parsed_data = {
            "text": "Report text for KPI extraction...",
            "parsed_sections": "some_sections"
        }
        self.sample_financial_statements = {
            "income_statement": "dummy_income_statement_data",
            "balance_sheet": "dummy_balance_sheet_data",
            "cash_flow_statement": "dummy_cash_flow_data"
        }

    def test_import_kpi_extractor(self):
        """Test that KPIExtractor can be imported and instantiated."""
        self.assertIsInstance(self.extractor, KPIExtractor)

    def test_extract_kpis_returns_dict(self):
        """Test that the method returns a dictionary."""
        result = self.extractor.extract_kpis(self.sample_parsed_data, self.sample_financial_statements)
        self.assertIsInstance(result, dict)

    def test_extract_kpis_has_expected_keys(self):
        """Test that the returned dictionary has some expected KPI keys."""
        result = self.extractor.extract_kpis(self.sample_parsed_data, self.sample_financial_statements)
        # Check for a few representative placeholder KPIs
        expected_kpis = [
            "revenue_growth_yoy",
            "net_profit_margin",
            "debt_to_equity_ratio"
        ]
        for kpi_key in expected_kpis:
            self.assertIn(kpi_key, result, f"KPI key '{kpi_key}' not found.")
            self.assertTrue("placeholder" in result[kpi_key], f"Value for '{kpi_key}' should mention 'placeholder'.")

    def test_extract_kpis_invalid_parsed_data_input(self):
        """Test with invalid parsed_report_data type."""
        with self.assertRaises(TypeError):
            self.extractor.extract_kpis("not_a_dict", self.sample_financial_statements) # type: ignore
        with self.assertRaises(TypeError):
            self.extractor.extract_kpis(None, self.sample_financial_statements) # type: ignore

    def test_extract_kpis_invalid_financial_statements_input(self):
        """Test with invalid financial_statements type."""
        with self.assertRaises(TypeError):
            self.extractor.extract_kpis(self.sample_parsed_data, "not_a_dict") # type: ignore
        with self.assertRaises(TypeError):
            self.extractor.extract_kpis(self.sample_parsed_data, None) # type: ignore

    def test_extract_kpis_empty_inputs(self):
        """Test with empty but valid dictionary inputs."""
        try:
            result = self.extractor.extract_kpis({}, {})
            self.assertIsInstance(result, dict)
            # Even with empty inputs, the dummy implementation returns all placeholders
            self.assertIn("net_profit_margin", result)
        except Exception as e:
            self.fail(f"extract_kpis failed with empty dict inputs: {e}")


if __name__ == '__main__':
    unittest.main()
