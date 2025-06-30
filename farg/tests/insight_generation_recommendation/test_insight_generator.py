import unittest
import os
from unittest.mock import MagicMock
from langchain_core.documents import Document # For mock search results

try:
    from farg.insight_generation_recommendation.insight_generator import InsightGenerator, PlaceholderInsightRAGLLM
except ImportError:
    import sys
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))
    from farg.insight_generation_recommendation.insight_generator import InsightGenerator, PlaceholderInsightRAGLLM

class TestInsightGeneratorRAG(unittest.TestCase): # Renamed
    """
    Unit tests for the InsightGenerator class with RAG integration.
    """

    def setUp(self):
        """Initialize the generator and mock search function for each test."""
        self.generator = InsightGenerator()
        self.mock_vector_search_fn = MagicMock()

        self.sample_financial_analysis = {
            "trends": {"revenue_trend": "upward (strong)"},
            "ratios": {"profitability_ratios": {"net_profit_margin": 0.15, "net_profit_margin_context": "Context for NPM..."}}
        }
        self.sample_competitor_analysis = {"overall_comparison_summary": "On par with Competitor X."}
        self.sample_swot = {"opportunities": ["New market segment Alpha", "Partnership with TechCorp"]}

    def test_import_and_instantiation(self):
        """Test that InsightGenerator can be imported and instantiated."""
        self.assertIsInstance(self.generator, InsightGenerator)
        self.assertIsInstance(self.generator.llm, PlaceholderInsightRAGLLM)


    def test_generate_insights_with_rag_uses_search_fn(self):
        """Test that generate_insights uses vector_store_search_fn when provided."""

        def mock_search_side_effect(query, k):
            if "revenue trend" in query.lower():
                return [(Document(page_content="Company attributes growth to new product line.", metadata={"source":"s1"}), 0.9)]
            if "New market segment Alpha" in query: # Matches the first opportunity
                return [(Document(page_content="Segment Alpha shows 25% YoY growth potential.", metadata={"source":"s2"}), 0.88)]
            return []
        self.mock_vector_search_fn.side_effect = mock_search_side_effect

        result = self.generator.generate_insights(
            self.sample_financial_analysis,
            self.sample_competitor_analysis,
            self.sample_swot,
            vector_store_search_fn=self.mock_vector_search_fn
        )

        self.assertIsInstance(result, list)
        self.assertTrue(any("Insight (RAG):" in item for item in result), "Should contain RAG-generated insights.")

        # Check if search_fn was called (at least for trend and SWOT opportunity)
        self.assertTrue(self.mock_vector_search_fn.call_count >= 1)
        # Example specific calls based on current InsightGenerator logic
        self.mock_vector_search_fn.assert_any_call("What are the company's stated reasons or plans supporting the positive revenue trend of 'upward (strong)'?", k=1)
        self.mock_vector_search_fn.assert_any_call("What specific actions or market conditions support the opportunity: 'New market segment Alpha'?", k=1)


    def test_generate_insights_without_rag_search_fn(self):
        """Test generate_insights when no vector_store_search_fn is provided."""
        result = self.generator.generate_insights(
            self.sample_financial_analysis,
            self.sample_competitor_analysis,
            self.sample_swot,
            vector_store_search_fn=None # Explicitly None
        )
        self.assertIsInstance(result, list)
        self.assertFalse(any("Insight (RAG):" in item for item in result), "Should not contain RAG-generated insights if search_fn is None.")
        self.assertTrue(any("Insight (Base):" in item for item in result), "Should still contain base insights.")
        self.assertEqual(self.mock_vector_search_fn.call_count, 0) # Ensure search_fn was not called


    def test_generate_insights_rag_handles_no_retrieved_docs(self):
        """Test RAG behavior when search_fn returns no documents."""
        self.mock_vector_search_fn.return_value = [] # RAG returns nothing

        result = self.generator.generate_insights(
            self.sample_financial_analysis,
            self.sample_competitor_analysis,
            self.sample_swot,
            self.mock_vector_search_fn
        )
        self.assertIsInstance(result, list)
        # PlaceholderInsightRAGLLM will get "No specific context found..."
        # Check that RAG insights reflect this
        rag_insights = [item for item in result if "Insight (RAG):" in item]
        self.assertTrue(len(rag_insights) > 0, "RAG insights should still be attempted.")
        self.assertTrue(any("No specific context found" in item for item in rag_insights),
                        "RAG insights should reflect no docs found if applicable.")

    def test_generate_insights_invalid_input_types(self):
        """Test generate_insights with invalid input types for main dicts."""
        with self.assertRaises(TypeError):
            self.generator.generate_insights("bad", {}, {}, self.mock_vector_search_fn) # type: ignore
        with self.assertRaises(TypeError):
            self.generator.generate_insights({}, "bad", {}, self.mock_vector_search_fn) # type: ignore
        with self.assertRaises(TypeError):
            self.generator.generate_insights({}, {}, "bad", self.mock_vector_search_fn) # type: ignore
        with self.assertRaises(TypeError): # Invalid search_fn
            self.generator.generate_insights({}, {}, {}, "not_callable") # type: ignore


if __name__ == '__main__':
    unittest.main()
