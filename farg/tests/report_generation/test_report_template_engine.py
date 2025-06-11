import unittest
import os

try:
    from farg.report_generation.report_template_engine import ReportTemplateEngine
except ImportError:
    import sys
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))
    from farg.report_generation.report_template_engine import ReportTemplateEngine

class TestReportTemplateEngine(unittest.TestCase):
    """
    Unit tests for the ReportTemplateEngine class.
    """

    def setUp(self):
        """Initialize the engine for each test."""
        self.engine = ReportTemplateEngine()
        self.sample_template_name = "standard_comparison_report_v1" # Assuming this exists in ReportTemplateEngine
        self.sample_data = {"report_title": "Test Title", "company_A_name": "Alpha"}


    def test_import_report_template_engine(self):
        """Test that ReportTemplateEngine can be imported and instantiated."""
        self.assertIsInstance(self.engine, ReportTemplateEngine)

    def test_load_template_returns_string(self):
        """Test that load_template returns a string for existing template."""
        try:
            template_str = self.engine.load_template(self.sample_template_name)
            self.assertIsInstance(template_str, str)
            self.assertTrue(len(template_str) > 0)
        except ValueError:
            self.fail(f"Default template '{self.sample_template_name}' should exist for test.")

    def test_load_template_raises_value_error_for_non_existent(self):
        """Test load_template raises ValueError for a non-existent template."""
        with self.assertRaises(ValueError):
            self.engine.load_template("non_existent_template_xyz123")

    def test_populate_template_returns_string(self):
        """Test that populate_template returns a string."""
        template_str = self.engine.load_template(self.sample_template_name)
        populated_str = self.engine.populate_template(template_str, self.sample_data)
        self.assertIsInstance(populated_str, str)
        self.assertIn("Test Title", populated_str) # Check if a value was inserted
        self.assertIn("Alpha", populated_str)

    def test_populate_template_with_empty_data(self):
        """Test populating with an empty data dictionary."""
        template_str = self.engine.load_template(self.sample_template_name)
        populated_str = self.engine.populate_template(template_str, {})
        self.assertIsInstance(populated_str, str)
        # Check if placeholders for missing keys are handled (e.g., showing KEY_NOT_FOUND)
        self.assertIn("KEY_NOT_FOUND: report_title", populated_str)

    def test_populate_template_invalid_input_types(self):
        """Test populate_template with invalid input types."""
        template_str = self.engine.load_template(self.sample_template_name)
        with self.assertRaises(TypeError):
            self.engine.populate_template(123, self.sample_data) # type: ignore
        with self.assertRaises(TypeError):
            self.engine.populate_template(template_str, "not_a_dict") # type: ignore

    def test_populate_template_handles_lists_and_dicts_in_data(self):
        """Test populating with list/dict values in report_data."""
        template_str = "Title: {{title}}\nItems: {{my_list}}\nDetails: {{my_dict}}"
        data_with_collections = {
            "title": "Collections Test",
            "my_list": ["item1", "item2"],
            "my_dict": {"key1": "val1", "key2": "val2"}
        }
        populated_str = self.engine.populate_template(template_str, data_with_collections)
        self.assertIn("item1", populated_str)
        self.assertIn("item2", populated_str)
        self.assertIn("key1: val1", populated_str)
        self.assertIn("key2: val2", populated_str)


if __name__ == '__main__':
    unittest.main()
