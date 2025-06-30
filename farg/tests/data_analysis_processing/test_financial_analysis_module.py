import unittest
import os
from typing import cast
from unittest.mock import MagicMock
from langchain_core.documents import Document

try:
    from farg.data_analysis_processing.financial_analysis_module import FinancialAnalysisModule, FinancialAnalysisState, PlaceholderAnalysisRAGLLM
except ImportError:
    import sys
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))
    from farg.data_analysis_processing.financial_analysis_module import FinancialAnalysisModule, FinancialAnalysisState, PlaceholderAnalysisRAGLLM

class TestFinancialAnalysisModuleRAGLangGraph(unittest.TestCase): # Renamed
    """
    Unit tests for the FinancialAnalysisModule class with RAG and LangGraph outline.
    """

    def setUp(self):
        """Initialize the module and mock search function for each test."""
        self.module = FinancialAnalysisModule()
        self.mock_vector_search_fn = MagicMock()

        self.sample_company_statements = {
            "income_statement": {"revenue": 1000, "net_income": 100},
            "balance_sheet": {} # Simplified
        }
        self.sample_historical_data = [{"year": 2023, "revenue": 1000}]
        self.sample_peer_ratios = {"profitability_ratios": {"net_profit_margin": 0.09}}
        self.sample_industry_ratios = {"profitability_ratios": {"net_profit_margin": 0.08}}

        # Base state for many node tests, ensuring vector_store_search_fn is present
        self.base_state_with_search: FinancialAnalysisState = {
            "company_financial_statements": self.sample_company_statements,
            "vector_store_search_fn": self.mock_vector_search_fn,
            "competitor_financial_statements": None,
            "historical_data": self.sample_historical_data,
            "peer_group_ratios_avg_input": self.sample_peer_ratios,
            "industry_ratios_avg_input": self.sample_industry_ratios,
            "ratio_analysis_results": None, "trend_analysis_results": None, "benchmark_results": None,
            "next_analysis_step": None, "errors": []
        }


    def test_import_and_instantiation(self):
        self.assertIsInstance(self.module, FinancialAnalysisModule)
        self.assertIsInstance(self.module.llm, PlaceholderAnalysisRAGLLM)
        self.assertIsNone(self.module.app, "LangGraph app should be None.")

    def test_perform_ratio_analysis_node_with_rag(self):
        """Test ratio analysis node, including RAG call."""
        self.mock_vector_search_fn.return_value = [
            (Document(page_content="Market demand increased significantly.", metadata={"source":"s1"}), 0.9)
        ]
        state = self.base_state_with_search.copy()

        processed_state = self.module.perform_ratio_analysis_node(state)

        self.assertIsNotNone(processed_state["ratio_analysis_results"])
        ratios = processed_state["ratio_analysis_results"]
        self.assertIn("profitability_ratios", ratios) # type: ignore
        self.assertIn("net_profit_margin_context", ratios["profitability_ratios"]) # type: ignore
        self.assertIn("Factors include market demand", ratios["profitability_ratios"]["net_profit_margin_context"]) # type: ignore
        self.mock_vector_search_fn.assert_called_once() # Ensure RAG was attempted
        self.assertEqual(processed_state["next_analysis_step"], "perform_trends")


    def test_perform_trend_analysis_node_with_rag(self):
        """Test trend analysis node, including RAG call."""
        self.mock_vector_search_fn.return_value = [
            (Document(page_content="New contracts secured in Q4 boosted revenue.", metadata={"source":"s2"}), 0.8)
        ]
        state = self.base_state_with_search.copy()
        # Assume ratio analysis has run and populated its part of the state
        state["ratio_analysis_results"] = {"profitability_ratios": {"net_profit_margin": 0.12}}

        processed_state = self.module.perform_trend_analysis_node(state)

        self.assertIsNotNone(processed_state["trend_analysis_results"])
        trends = processed_state["trend_analysis_results"] # type: ignore
        self.assertIn("revenue_trend", trends)
        self.assertIn("revenue_trend_explanation_rag", trends)
        self.assertIn("new contracts secured", trends["revenue_trend_explanation_rag"].lower())
        self.mock_vector_search_fn.assert_called_once()
        self.assertEqual(processed_state["next_analysis_step"], "perform_benchmarking")

    def test_perform_benchmarking_node_with_rag(self):
        """Test benchmarking node, including RAG call."""
        self.mock_vector_search_fn.return_value = [
            (Document(page_content="Company's innovative R&D gives it an edge.", metadata={"source":"s3"}), 0.85)
        ]
        state = self.base_state_with_search.copy()
        state["ratio_analysis_results"] = {"profitability_ratios": {"net_profit_margin": 0.12}} # From ratio node
        state["trend_analysis_results"] = {"revenue_trend": "upward"} # From trend node

        processed_state = self.module.perform_benchmarking_node(state)

        self.assertIsNotNone(processed_state["benchmark_results"])
        benchmarks = processed_state["benchmark_results"] # type: ignore
        self.assertIn("overall_performance_summary", benchmarks)
        self.assertIn("profitability_vs_peer_commentary_rag", benchmarks)
        self.assertIn("innovative R&D", benchmarks["profitability_vs_peer_commentary_rag"].lower())
        self.mock_vector_search_fn.assert_called_once()
        self.assertEqual(processed_state["next_analysis_step"], "END") # type: ignore


    def test_run_full_analysis_graph_simulated_with_rag(self):
        """Test the run_full_analysis_graph method with RAG search_fn passed."""
        # This mock will be used by all RAG calls in the simulated graph run
        self.mock_vector_search_fn.return_value = [
            (Document(page_content="Mocked RAG context for test run.", metadata={"source":"test_doc"}), 0.75)
        ]

        results = self.module.run_full_analysis_graph(
            company_statements=self.sample_company_statements,
            vector_store_search_fn=self.mock_vector_search_fn, # Pass the mock
            historical_data=self.sample_historical_data,
            peer_ratios=self.sample_peer_ratios,
            industry_ratios=self.sample_industry_ratios
        )
        self.assertIn("ratios", results)
        self.assertIn("trends", results)
        self.assertIn("benchmarking", results)

        # Check if RAG context was added (presence of specific keys)
        self.assertIn("net_profit_margin_context", results.get("ratios", {}).get("profitability_ratios", {}))
        self.assertIn("revenue_trend_explanation_rag", results.get("trends", {}))
        self.assertIn("profitability_vs_peer_commentary_rag", results.get("benchmarking", {}))

        self.assertTrue(self.mock_vector_search_fn.call_count >= 1) # Should be called at least once (actually 3 times for 3 nodes)


    def test_run_full_analysis_graph_no_rag_fn(self):
        """Test run_full_analysis_graph without providing a RAG search_fn."""
        results = self.module.run_full_analysis_graph(
            company_statements=self.sample_company_statements,
            vector_store_search_fn=None, # Explicitly None
            historical_data=self.sample_historical_data
        )
        self.assertIn("ratios", results)
        self.assertNotIn("net_profit_margin_context", results.get("ratios", {}).get("profitability_ratios", {}))
        self.assertIn("trends", results)
        self.assertNotIn("revenue_trend_explanation_rag", results.get("trends", {}))

        self.assertEqual(self.mock_vector_search_fn.call_count, 0)


if __name__ == '__main__':
    unittest.main()
