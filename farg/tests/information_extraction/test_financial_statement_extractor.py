import unittest
import os
from unittest.mock import MagicMock
from langchain_core.documents import Document # For creating mock search results

try:
    from farg.information_extraction.financial_statement_extractor import FinancialStatementExtractor, FinancialStatementExtractionState, PlaceholderFSLLM
except ImportError:
    import sys
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))
    from farg.information_extraction.financial_statement_extractor import FinancialStatementExtractor, FinancialStatementExtractionState, PlaceholderFSLLM

class TestFinancialStatementExtractorRAGLangGraph(unittest.TestCase): # Renamed
    """
    Unit tests for the FinancialStatementExtractor class with RAG and LangGraph outline.
    """

    def setUp(self):
        """Initialize the extractor and mock search function for each test."""
        self.extractor = FinancialStatementExtractor()
        self.mock_vector_search_fn = MagicMock()

        self.sample_parsed_data = {
            "text": "Comprehensive annual report including income statement, balance sheet, and cash flow details...",
            # other parsed data like tables or pre-segmented sections could go here
        }

    def test_import_and_instantiation(self):
        """Test that FinancialStatementExtractor can be imported and instantiated."""
        self.assertIsInstance(self.extractor, FinancialStatementExtractor)
        self.assertIsInstance(self.extractor.llm, PlaceholderFSLLM)
        self.assertIsNone(self.extractor.app, "LangGraph app should be None as it's commented out.")

    def test_graph_related_methods_exist(self):
        """Test that new graph-related methods are defined."""
        self.assertTrue(hasattr(self.extractor, 'start_extraction_node'))
        self.assertTrue(hasattr(self.extractor, 'extract_single_statement_node')) # Updated node name
        self.assertTrue(hasattr(self.extractor, 'should_continue_statement_type_edge')) # Updated edge name

    def test_extract_financial_statements_uses_rag_and_returns_structure(self):
        """Test that extract_financial_statements uses RAG (via search_fn) and returns the expected structure."""

        # Mock search results for different statement types
        def mock_search_side_effect(query, k):
            if "income statement" in query.lower():
                return [(Document(page_content="Retrieved text about revenues and expenses.", metadata={"source": "doc1"}), 0.9)]
            elif "balance sheet" in query.lower():
                return [(Document(page_content="Retrieved text detailing assets and liabilities.", metadata={"source": "doc2"}), 0.88)]
            elif "cash flow" in query.lower():
                return [(Document(page_content="Retrieved text on cash from operations.", metadata={"source": "doc3"}), 0.85)]
            return []
        self.mock_vector_search_fn.side_effect = mock_search_side_effect

        result = self.extractor.extract_financial_statements(self.sample_parsed_data, self.mock_vector_search_fn)

        self.assertIsInstance(result, dict)
        expected_keys = ["income_statement", "balance_sheet", "cash_flow_statement", "notes_to_financial_statements", "graph_simulation_errors"]
        for key in expected_keys:
            self.assertIn(key, result, f"Key '{key}' not found in extraction result.")

        # Check if output from PlaceholderFSLLM (which simulates RAG processing) is present
        self.assertTrue("Extracted Income Statement from context" in result["income_statement"])
        self.assertTrue("Extracted Balance Sheet from context" in result["balance_sheet"])
        self.assertTrue("Extracted Cash Flow from context" in result["cash_flow_statement"])

        # Ensure search_fn was called for each statement type
        self.assertEqual(self.mock_vector_search_fn.call_count, 3) # For income, balance, cash flow

    def test_extract_financial_statements_no_search_fn_fallback(self):
        """Test fallback behavior when no vector_store_search_fn is provided."""
        result = self.extractor.extract_financial_statements(self.sample_parsed_data, None)
        self.assertIn("RAG search function not provided", result["income_statement"])
        self.assertIn("vector_store_search_fn was None", result["graph_simulation_errors"])

    def test_start_extraction_node_initializes_state(self):
        """Test the start_extraction_node logic."""
        # Provide all necessary keys for FinancialStatementExtractionState, even if some are None or empty for this test
        initial_state_input: FinancialStatementExtractionState = {
            "parsed_report_data": self.sample_parsed_data,
            "vector_store_search_fn": self.mock_vector_search_fn,
            "statement_types_to_extract": [], # Should be set by node
            "current_statement_type_index": 10, # Should be reset
            "extracted_statements": {"old": "data"}, # Should be cleared
            "errors": ["old_error"] # Should be cleared
        }
        processed_state = self.extractor.start_extraction_node(initial_state_input)
        self.assertEqual(processed_state["extracted_statements"], {})
        self.assertEqual(processed_state["errors"], [])
        self.assertEqual(processed_state["current_statement_type_index"], 0)
        self.assertEqual(processed_state["statement_types_to_extract"], ["income_statement", "balance_sheet", "cash_flow_statement"])

    def test_should_continue_statement_type_edge_logic(self):
        """Test the conditional edge logic for statement types."""
        state_base: FinancialStatementExtractionState = {
            "parsed_report_data": {}, "vector_store_search_fn": self.mock_vector_search_fn,
            "statement_types_to_extract": ["s1", "s2"], "extracted_statements": {}, "errors": []
        }

        state_continue = state_base.copy()
        state_continue["current_statement_type_index"] = 0
        self.assertEqual(self.extractor.should_continue_statement_type_edge(state_continue), "extract_next_statement_type")

        state_last = state_base.copy()
        state_last["current_statement_type_index"] = 1
        self.assertEqual(self.extractor.should_continue_statement_type_edge(state_last), "extract_next_statement_type")

        state_end = state_base.copy()
        state_end["current_statement_type_index"] = 2
        self.assertEqual(self.extractor.should_continue_statement_type_edge(state_end), "END")


    def test_extract_single_statement_node_simulated_rag_logic(self):
        """Test the RAG simulation within extract_single_statement_node."""
        self.mock_vector_search_fn.return_value = [
            (Document(page_content="Relevant text for income statement.", metadata={"source": "doc_a"}), 0.9)
        ]

        state_before: FinancialStatementExtractionState = {
            "parsed_report_data": self.sample_parsed_data,
            "vector_store_search_fn": self.mock_vector_search_fn,
            "statement_types_to_extract": ["income_statement", "balance_sheet"],
            "current_statement_type_index": 0,
            "extracted_statements": {},
            "errors": []
        }

        processed_state = self.extractor.extract_single_statement_node(state_before)

        self.mock_vector_search_fn.assert_called_once_with(query="Retrieve text sections related to the income statement.", k=3)
        self.assertIn("income_statement", processed_state["extracted_statements"])
        self.assertTrue("Extracted Income Statement from context" in processed_state["extracted_statements"]["income_statement"])
        self.assertEqual(processed_state["current_statement_type_index"], 1)
        self.assertEqual(len(processed_state["errors"]), 0)

if __name__ == '__main__':
    unittest.main()
