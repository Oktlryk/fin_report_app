import unittest
import os
from unittest.mock import MagicMock
from langchain_core.documents import Document # For creating mock search results

try:
    from farg.information_extraction.kpi_extractor import KPIExtractor, PlaceholderKPIRAGLLM
except ImportError:
    import sys
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))
    from farg.information_extraction.kpi_extractor import KPIExtractor, PlaceholderKPIRAGLLM

class TestKPIExtractorRAG(unittest.TestCase): # Renamed
    """
    Unit tests for the KPIExtractor class with RAG integration.
    """

    def setUp(self):
        """Initialize the extractor and mock search function for each test."""
        self.extractor = KPIExtractor()
        self.mock_vector_search_fn = MagicMock()

        self.sample_parsed_data = {
            "text": "Report text for KPI extraction... Revenue growth was driven by product X. Debt consists of bonds.",
            "parsed_sections": {"md_and_a": "Management discussion on performance..."}
        }
        self.sample_financial_statements = {
            "income_statement": {"revenue": 1000, "cogs": 400, "net_income": 150},
            "balance_sheet": {"total_debt": 500, "total_equity": 1000, "current_assets": 200, "inventory": 50, "current_liabilities": 100}
        }

    def test_import_and_instantiation(self):
        """Test that KPIExtractor can be imported and instantiated."""
        self.assertIsInstance(self.extractor, KPIExtractor)
        self.assertIsInstance(self.extractor.llm, PlaceholderKPIRAGLLM)

    def test_extract_kpis_with_rag_uses_search_fn(self):
        """Test that extract_kpis uses the vector_store_search_fn when provided."""

        def mock_search_side_effect(query, k):
            if "revenue growth drivers" in query.lower():
                return [(Document(page_content="Product X was a major driver.", metadata={"source": "s1"}), 0.9)]
            if "debt components" in query.lower():
                return [(Document(page_content="Long-term bonds of $300M.", metadata={"source": "s2"}), 0.8)]
            return []
        self.mock_vector_search_fn.side_effect = mock_search_side_effect

        result = self.extractor.extract_kpis(
            self.sample_parsed_data,
            self.sample_financial_statements,
            self.mock_vector_search_fn
        )

        self.assertIsInstance(result, dict)
        # Check that search_fn was called for RAG-dependent KPIs
        self.mock_vector_search_fn.assert_any_call(query="What were the main drivers of revenue growth in the past year?", k=2)
        self.mock_vector_search_fn.assert_any_call(query="Describe the company's debt components or structure.", k=2)

        # Check if RAG-enhanced KPI details are present (using PlaceholderKPIRAGLLM's simulated output)
        self.assertIn("Revenue growth driven by new product InnovateMax", result.get("revenue_growth_drivers_detail", ""))
        self.assertIn("Debt primarily consists of long-term bonds", result.get("debt_structure_detail", ""))

        # Check if direct calculation placeholders are still there
        self.assertTrue("placeholder_v2_direct_calc" in result.get("net_profit_margin", ""))


    def test_extract_kpis_without_rag_search_fn(self):
        """Test extract_kpis when no vector_store_search_fn is provided."""
        result = self.extractor.extract_kpis(
            self.sample_parsed_data,
            self.sample_financial_statements,
            None # No search function
        )
        self.assertIsInstance(result, dict)
        self.assertEqual(self.mock_vector_search_fn.call_count, 0) # Ensure search_fn was not called

        # RAG-dependent KPIs should have their default placeholder text
        self.assertTrue("Placeholder - RAG not used" in result.get("revenue_growth_drivers_detail", ""))
        self.assertTrue("Placeholder - RAG not used" in result.get("debt_structure_detail", ""))
        self.assertTrue("placeholder_v2_direct_calc" in result.get("current_ratio", ""))


    def test_extract_kpis_invalid_input_types(self):
        """Test behavior with invalid input types for main arguments."""
        with self.assertRaises(TypeError):
            self.extractor.extract_kpis("bad_data", self.sample_financial_statements, self.mock_vector_search_fn) # type: ignore
        with self.assertRaises(TypeError):
            self.extractor.extract_kpis(self.sample_parsed_data, "bad_data", self.mock_vector_search_fn) # type: ignore
        with self.assertRaises(TypeError):
            self.extractor.extract_kpis(self.sample_parsed_data, self.sample_financial_statements, "not_callable") # type: ignore


if __name__ == '__main__':
    unittest.main()
