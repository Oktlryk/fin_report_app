import unittest
import os
from unittest.mock import MagicMock # For mocking Gradio file objects if needed later

# Ensure farg.ui.app is discoverable
try:
    from farg.ui.app import farg_agent, generate_report_gradio
except ImportError:
    import sys
    # Assuming tests are in farg/tests/ui/
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))
    from farg.ui.app import farg_agent, generate_report_gradio


class TestAppUI(unittest.TestCase):
    """
    Unit tests for the Gradio UI application (app.py).
    Focuses on the non-Gradio specific logic first.
    """

    def test_import_app_components(self):
        """Test that necessary functions can be imported from farg.ui.app."""
        self.assertTrue(callable(farg_agent), "farg_agent should be callable.")
        self.assertTrue(callable(generate_report_gradio), "generate_report_gradio should be callable.")

    def test_farg_agent_returns_string(self):
        """Test the placeholder farg_agent directly."""
        company_paths = ["dummy_company_report.pdf"]
        competitor_paths = ["dummy_competitor_report.pdf"]
        options = ["Financial Performance Comparison"]

        result = farg_agent(company_paths, competitor_paths, options)
        self.assertIsInstance(result, str)
        self.assertIn("Report Generation Initiated", result)
        self.assertIn("dummy_company_report.pdf", result)
        self.assertIn("dummy_competitor_report.pdf", result)
        self.assertIn("Financial Performance Comparison", result)

    def test_farg_agent_handles_no_competitor(self):
        """Test farg_agent with no competitor reports."""
        company_paths = ["company.txt"]
        competitor_paths = [] # Empty list
        options = ["Key Insights Generation"]

        result = farg_agent(company_paths, competitor_paths, options)
        self.assertIsInstance(result, str)
        self.assertIn("Competitor Company Reports Received:\n- None", result)

        result_none = farg_agent(company_paths, None, options) # None object
        self.assertIsInstance(result_none, str)
        self.assertIn("Competitor Company Reports Received:\n- None", result_none)


    def test_farg_agent_handles_no_options(self):
        """Test farg_agent with no analysis options selected."""
        company_paths = ["report.pdf"]
        competitor_paths = None
        options = [] # Empty list for options

        result = farg_agent(company_paths, competitor_paths, options)
        self.assertIsInstance(result, str)
        self.assertIn("Selected Analysis Options:\n- None", result)

    def test_generate_report_gradio_simulated_call(self):
        """
        Test the generate_report_gradio function by simulating Gradio FileData objects.
        This doesn't test Gradio UI interaction, but the data flow.
        """
        # Mock Gradio FileData object structure (gr.File returns a FileData object, which has a .name attribute)
        # In Gradio versions >= 4.x, when type="filepath", it directly gives path strings.
        # However, the original `gr.File` used to return FileData objects.
        # Let's assume `gr.File(type="filepath")` passes list of strings directly for paths.
        # If it were FileData objects, we'd mock them:
        # mock_company_file = MagicMock()
        # mock_company_file.name = "temp/company_report.pdf"
        # mock_competitor_file = MagicMock()
        # mock_competitor_file.name = "temp/competitor_report.pdf"
        # company_files_input = [mock_company_file]
        # competitor_files_input = [mock_competitor_file]

        # With type="filepath", Gradio provides a list of path strings directly.
        company_files_input = ["/tmp/gradio_company_report.pdf"]
        competitor_files_input = ["/tmp/gradio_competitor_report.pdf"]
        options_input = ["Strategic Recommendations"]

        result = generate_report_gradio(company_files_input, competitor_files_input, options_input)
        self.assertIsInstance(result, str)
        self.assertIn("gradio_company_report.pdf", result)
        self.assertIn("gradio_competitor_report.pdf", result)
        self.assertIn("Strategic Recommendations", result)

    def test_generate_report_gradio_no_files(self):
        """Test generate_report_gradio with no files uploaded (empty lists or None)."""
        options_input = ["Key Insights Generation"]

        # Test with empty lists
        result_empty_lists = generate_report_gradio([], [], options_input)
        self.assertIsInstance(result_empty_lists, str)
        self.assertIn("Primary Company Reports Received:\n- None", result_empty_lists)
        self.assertIn("Competitor Company Reports Received:\n- None", result_empty_lists)

        # Test with None for file lists (Gradio might pass None if file_count is optional and nothing uploaded)
        result_none_lists = generate_report_gradio(None, None, options_input) # type: ignore
        self.assertIsInstance(result_none_lists, str)
        self.assertIn("Primary Company Reports Received:\n- None", result_none_lists)
        self.assertIn("Competitor Company Reports Received:\n- None", result_none_lists)


if __name__ == '__main__':
    unittest.main()
