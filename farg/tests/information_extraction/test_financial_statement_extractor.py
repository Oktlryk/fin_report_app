import unittest
import os

try:
    from farg.information_extraction.financial_statement_extractor import FinancialStatementExtractor, FinancialStatementExtractionState
except ImportError:
    import sys
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))
    from farg.information_extraction.financial_statement_extractor import FinancialStatementExtractor, FinancialStatementExtractionState

class TestFinancialStatementExtractorLangGraph(unittest.TestCase): # Renamed for clarity
    """
    Unit tests for the FinancialStatementExtractor class with LangGraph outline.
    """

    def setUp(self):
        """Initialize the extractor for each test."""
        self.extractor = FinancialStatementExtractor()
        self.sample_parsed_data = {
            "text": "Report text including Income Statement: Revenue $1M... and a Balance Sheet: Assets $5M...",
            "parsed_sections": {"overview": "Some overview text", "financials_text": "More detailed financials"}
        }
        self.multi_section_text = (
            "Section 1: Intro.\n\n"
            "Section 2: Consolidated income statement of the company.\n\n"
            "Section 3: Details about assets on the balance sheet.\n\n"
            "Section 4: Cash flow from operations was positive.\n\n"
            "Section 5: Other notes."
        )

    def test_import_and_instantiation(self):
        """Test that FinancialStatementExtractor can be imported and instantiated."""
        self.assertIsInstance(self.extractor, FinancialStatementExtractor)
        # Check if the (commented out) app is None initially, or if simulation runs, it's fine
        self.assertIsNone(self.extractor.app, "LangGraph app should be None as it's commented out or failed compilation.")

    def test_graph_related_methods_exist(self):
        """Test that new graph-related methods are defined."""
        self.assertTrue(hasattr(self.extractor, 'start_extraction_node'), "Method start_extraction_node should exist.")
        self.assertTrue(hasattr(self.extractor, 'extract_section_node'), "Method extract_section_node should exist.")
        self.assertTrue(hasattr(self.extractor, 'should_continue_extraction_edge'), "Method should_continue_extraction_edge should exist.")

    def test_extract_financial_statements_returns_modified_placeholder(self):
        """Test that extract_financial_statements returns the new placeholder structure."""
        result = self.extractor.extract_financial_statements(self.sample_parsed_data)
        self.assertIsInstance(result, dict)

        expected_keys = ["income_statement", "balance_sheet", "cash_flow_statement", "notes_to_financial_statements", "graph_simulation_errors"]
        for key in expected_keys:
            self.assertIn(key, result, f"Key '{key}' not found in extraction result.")

        # Check if the placeholder text indicates LangGraph simulation
        if self.extractor.app is None: # If graph wasn't "compiled"
            self.assertTrue("LangGraph app not compiled" in result["income_statement"])
        else: # If graph simulation ran because self.app was mocked or somehow non-None
             self.assertTrue("LangGraph (simulated run)" in result["income_statement"])


    def test_extract_financial_statements_invalid_input(self):
        """Test that the method still raises TypeError for invalid input."""
        with self.assertRaises(TypeError):
            self.extractor.extract_financial_statements("not_a_dict") # type: ignore
        with self.assertRaises(TypeError):
            self.extractor.extract_financial_statements(None) # type: ignore

    def test_start_extraction_node_initializes_state_correctly(self):
        """Test the start_extraction_node logic."""
        initial_state_input: FinancialStatementExtractionState = {
            "report_sections": ["section1"],
            "extracted_statements": {"old_data": "should_be_cleared"}, # type: ignore
            "current_section_index": 5, # Should be reset
            "errors": ["old_error"] # Should be cleared
        }
        processed_state = self.extractor.start_extraction_node(initial_state_input)
        self.assertEqual(processed_state["extracted_statements"], {})
        self.assertEqual(processed_state["errors"], [])
        self.assertEqual(processed_state["current_section_index"], 0)

    def test_should_continue_extraction_edge_logic(self):
        """Test the logic of the conditional edge function."""
        state_continue: FinancialStatementExtractionState = {"report_sections": ["s1", "s2"], "current_section_index": 0, "extracted_statements": {}, "errors": []}
        self.assertEqual(self.extractor.should_continue_extraction_edge(state_continue), "extract_next_section")

        state_continue_last: FinancialStatementExtractionState = {"report_sections": ["s1", "s2"], "current_section_index": 1, "extracted_statements": {}, "errors": []}
        self.assertEqual(self.extractor.should_continue_extraction_edge(state_continue_last), "extract_next_section")

        state_end: FinancialStatementExtractionState = {"report_sections": ["s1", "s2"], "current_section_index": 2, "extracted_statements": {}, "errors": []}
        self.assertEqual(self.extractor.should_continue_extraction_edge(state_end), "end_extraction")

        state_empty_sections: FinancialStatementExtractionState = {"report_sections": [], "current_section_index": 0, "extracted_statements": {}, "errors": []}
        self.assertEqual(self.extractor.should_continue_extraction_edge(state_empty_sections), "end_extraction")


    def test_extract_section_node_simulated_logic(self):
        """Test the simulated processing within extract_section_node."""
        state_income: FinancialStatementExtractionState = {
            "report_sections": ["This section is an income statement."],
            "current_section_index": 0,
            "extracted_statements": {},
            "errors": []
        }
        processed_state = self.extractor.extract_section_node(state_income)
        self.assertIn("income_statement", processed_state["extracted_statements"])
        self.assertTrue("Identified as Income Statement" in processed_state["extracted_statements"]["income_statement"])
        self.assertEqual(processed_state["current_section_index"], 1)
        self.assertEqual(len(processed_state["errors"]), 0)

        state_balance: FinancialStatementExtractionState = {
            "report_sections": ["Text about the balance sheet of the company."],
            "current_section_index": 0,
            "extracted_statements": {},
            "errors": []
        }
        processed_state_b = self.extractor.extract_section_node(state_balance)
        self.assertIn("balance_sheet", processed_state_b["extracted_statements"])
        self.assertTrue("Identified as Balance Sheet" in processed_state_b["extracted_statements"]["balance_sheet"])

    def test_simulated_graph_run_in_extract_financial_statements(self):
        """ Test the full simulated graph execution path within extract_financial_statements """
        parsed_data = {"text": self.multi_section_text}
        result = self.extractor.extract_financial_statements(parsed_data)

        self.assertIn("income_statement", result)
        self.assertTrue("Identified as Income Statement" in result["income_statement"])
        self.assertIn("balance_sheet", result)
        self.assertTrue("Identified as Balance Sheet" in result["balance_sheet"])
        self.assertIn("cash_flow_statement", result)
        self.assertTrue("Identified as Cash Flow Statement" in result["cash_flow_statement"])
        self.assertEqual(len(result["graph_simulation_errors"]), 0)


if __name__ == '__main__':
    unittest.main()
