import unittest
import os

# Ensure the farg package is discoverable
try:
    from farg.data_ingestion.report_parser import ReportParser, PlaceholderLLM
except ImportError:
    import sys
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))
    from farg.data_ingestion.report_parser import ReportParser, PlaceholderLLM

class TestReportParserLangChain(unittest.TestCase): # Renamed class for clarity
    """
    Unit tests for the ReportParser class, now with LangChain integration.
    """

    def setUp(self):
        """Initialize the parser for each test."""
        self.parser = ReportParser()

    def test_import_report_parser_and_placeholder_llm(self):
        """Test that ReportParser and PlaceholderLLM can be imported."""
        self.assertTrue(callable(ReportParser), "ReportParser class should be callable (importable).")
        self.assertTrue(callable(PlaceholderLLM), "PlaceholderLLM class should be callable.")
        self.assertIsInstance(self.parser.llm, PlaceholderLLM, "Parser should use PlaceholderLLM.")

    def test_parse_report_returns_expected_structure(self):
        """Test that parse_report returns the new dictionary structure."""
        sample_content = "This is a simple report content for testing the LangChain parser."
        parsed_data = self.parser.parse_report(sample_content)

        self.assertIsInstance(parsed_data, dict)
        self.assertIn("text", parsed_data)
        self.assertEqual(parsed_data["text"], sample_content)

        self.assertIn("parsed_sections", parsed_data)
        self.assertIsInstance(parsed_data["parsed_sections"], dict)
        self.assertIn("overview_from_llm", parsed_data["parsed_sections"])

        self.assertIn("raw_llm_output_example", parsed_data)
        # Check that the LLM output is a string (StrOutputParser)
        self.assertIsInstance(parsed_data["parsed_sections"]["overview_from_llm"], str)
        self.assertIsInstance(parsed_data["raw_llm_output_example"], str)

    def test_parse_report_placeholder_llm_output(self):
        """Test the content of the placeholder LLM's output."""
        sample_content = "Annual Report Highlights: Revenue growth at 20%. New product InnovateMax launched successfully."
        # The PlaceholderLLM summarizes the first 100 chars of the (potentially sliced) input section.
        # The parser slices the input to 1500 chars.
        # So, the LLM will see min(len(sample_content), 1500)

        effective_input_to_llm = sample_content[:100] # PlaceholderLLM slices to 100 chars
        expected_llm_summary_part = f"LLM Summary of: {effective_input_to_llm}..."

        parsed_data = self.parser.parse_report(sample_content)

        llm_output = parsed_data["parsed_sections"]["overview_from_llm"]
        self.assertEqual(llm_output, expected_llm_summary_part)
        self.assertEqual(parsed_data["raw_llm_output_example"], expected_llm_summary_part)

    def test_parse_report_empty_content(self):
        """Test parsing with empty string content."""
        sample_content = ""
        effective_input_to_llm = "" # PlaceholderLLM will get ""
        expected_llm_summary_part = f"LLM Summary of: {effective_input_to_llm}..."

        parsed_data = self.parser.parse_report(sample_content)

        self.assertEqual(parsed_data["text"], sample_content)
        llm_output = parsed_data["parsed_sections"]["overview_from_llm"]
        self.assertEqual(llm_output, expected_llm_summary_part)

    def test_parse_report_invalid_input_type(self):
        """Test that parse_report still raises TypeError for non-string input."""
        with self.assertRaises(TypeError):
            self.parser.parse_report(None) # type: ignore
        with self.assertRaises(TypeError):
            self.parser.parse_report(12345) # type: ignore
        with self.assertRaises(TypeError):
            self.parser.parse_report(["list", "of", "strings"]) # type: ignore

if __name__ == '__main__':
    unittest.main()
