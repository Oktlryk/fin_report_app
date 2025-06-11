import unittest
import os

try:
    from farg.information_extraction.company_info_extractor import CompanyInfoExtractor
except ImportError:
    import sys
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))
    from farg.information_extraction.company_info_extractor import CompanyInfoExtractor

class TestCompanyInfoExtractor(unittest.TestCase):
    """
    Unit tests for the CompanyInfoExtractor class.
    """

    def setUp(self):
        """Initialize the extractor for each test."""
        self.extractor = CompanyInfoExtractor()
        self.sample_parsed_data = {
            "text": "Company X is a global leader in technology...",
            "parsed_sections": {
                "business_overview": "Some text...",
                "management_discussion": "More text..."
            }
        }

    def test_import_company_info_extractor(self):
        """Test that CompanyInfoExtractor can be imported and instantiated."""
        self.assertIsInstance(self.extractor, CompanyInfoExtractor)

    def test_extract_company_info_returns_dict(self):
        """Test that the method returns a dictionary."""
        result = self.extractor.extract_company_info(self.sample_parsed_data)
        self.assertIsInstance(result, dict)

    def test_extract_company_info_has_expected_keys(self):
        """Test that the returned dictionary has expected company info keys."""
        result = self.extractor.extract_company_info(self.sample_parsed_data)
        expected_keys = [
            "market_footprint",
            "product_service_similarity_to_target",
            "relative_size_category",
            "stage_of_maturity",
            "key_geographies",
            "primary_industry_sector",
            "major_products_services_lines"
        ]
        for key in expected_keys:
            self.assertIn(key, result, f"Key '{key}' not found in extraction result.")
            self.assertTrue("placeholder" in str(result[key]), f"Value for '{key}' should mention 'placeholder'.")


    def test_extract_company_info_invalid_input(self):
        """Test that the method raises TypeError for invalid input."""
        with self.assertRaises(TypeError):
            self.extractor.extract_company_info(123) # type: ignore
        with self.assertRaises(TypeError):
            self.extractor.extract_company_info(None) # type: ignore

    def test_extract_company_info_minimal_input(self):
        """Test with minimal but valid parsed_report_data."""
        minimal_data = {"text": "A small company."}
        try:
            result = self.extractor.extract_company_info(minimal_data)
            self.assertIsInstance(result, dict)
            self.assertIn("market_footprint", result) # Check one key
        except Exception as e:
            self.fail(f"extract_company_info failed with minimal input: {e}")

if __name__ == '__main__':
    unittest.main()
