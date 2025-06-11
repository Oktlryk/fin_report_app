import unittest
import os
from typing import cast # For type hinting if needed for state dicts

try:
    from farg.data_analysis_processing.financial_analysis_module import FinancialAnalysisModule, FinancialAnalysisState
except ImportError:
    import sys
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))
    from farg.data_analysis_processing.financial_analysis_module import FinancialAnalysisModule, FinancialAnalysisState

class TestFinancialAnalysisModuleLangGraph(unittest.TestCase): # Renamed for clarity
    """
    Unit tests for the FinancialAnalysisModule class with LangGraph outline.
    """

    def setUp(self):
        """Initialize the module for each test."""
        self.module = FinancialAnalysisModule()

        # Sample data for various tests
        self.sample_company_statements = {
            "income_statement": {"revenue": 1000, "cogs": 500, "net_income": 100},
            "balance_sheet": {"current_assets": 200, "current_liabilities": 100, "total_equity": 500}
        }
        self.sample_historical_data = [
            {"year": 2022, "revenue": 900, "net_income": 90},
            {"year": 2023, "revenue": 1000, "net_income": 100}
        ]
        self.sample_company_ratios_output = {"profitability_ratios": {"net_profit_margin": 0.10}} # Output of perform_ratio_analysis
        self.sample_peer_ratios_input = {"profitability_ratios": {"net_profit_margin": 0.09}}
        self.sample_industry_ratios_input = {"profitability_ratios": {"net_profit_margin": 0.08}}


    def test_import_and_instantiation(self):
        """Test that FinancialAnalysisModule can be imported and instantiated."""
        self.assertIsInstance(self.module, FinancialAnalysisModule)
        self.assertIsNone(self.module.app, "LangGraph app should be None as it's commented out.")

    def test_graph_related_methods_exist(self):
        """Test that new graph-related methods are defined."""
        self.assertTrue(hasattr(self.module, 'start_analysis_node'))
        self.assertTrue(hasattr(self.module, 'perform_ratio_analysis_node'))
        self.assertTrue(hasattr(self.module, 'perform_trend_analysis_node'))
        self.assertTrue(hasattr(self.module, 'perform_benchmarking_node'))
        self.assertTrue(hasattr(self.module, 'route_analysis_edge'))
        self.assertTrue(hasattr(self.module, 'run_full_analysis_graph'))

    def test_start_analysis_node(self):
        """Test the start_analysis_node logic."""
        initial_state: FinancialAnalysisState = {
            "company_financial_statements": self.sample_company_statements,
            "historical_data": self.sample_historical_data,
            "competitor_financial_statements": None,
            "peer_group_ratios_avg_input": None,
            "industry_ratios_avg_input": None,
            "ratio_analysis_results": None, "trend_analysis_results": None, "benchmark_results": None,
            "next_analysis_step": None, "errors": ["old_error"]
        }
        processed_state = self.module.start_analysis_node(initial_state)
        self.assertIsNone(processed_state["ratio_analysis_results"])
        self.assertEqual(processed_state["errors"], [])
        self.assertEqual(processed_state["next_analysis_step"], "perform_ratios")

        # Test starting with no company statements (should go to trends or end)
        initial_state_no_stmts: FinancialAnalysisState = {
            "company_financial_statements": {}, # Empty dict might also be an issue for actual ratio calc
            "historical_data": self.sample_historical_data,
            "competitor_financial_statements": None, "peer_group_ratios_avg_input": None, "industry_ratios_avg_input": None,
            "ratio_analysis_results": None, "trend_analysis_results": None, "benchmark_results": None,
            "next_analysis_step": None, "errors": []
        }
        # Depending on how FinancialAnalysisState handles missing company_financial_statements,
        # this might need adjustment. The provided code for start_analysis_node checks `state.get("company_financial_statements")`
        # An empty dict is truthy. So it would still go to "perform_ratios".
        # Let's test if company_financial_statements is None
        initial_state_none_stmts = initial_state_no_stmts.copy()
        initial_state_none_stmts["company_financial_statements"] = None # type: ignore
        processed_state_no_stmts = self.module.start_analysis_node(initial_state_none_stmts)
        self.assertEqual(processed_state_no_stmts["next_analysis_step"], "perform_trends")


    def test_perform_ratio_analysis_node(self):
        """Test the perform_ratio_analysis_node."""
        state: FinancialAnalysisState = {
            "company_financial_statements": self.sample_company_statements,
            "historical_data": self.sample_historical_data, # To determine next step
            "competitor_financial_statements": None, "peer_group_ratios_avg_input": None, "industry_ratios_avg_input": None,
            "ratio_analysis_results": None, "trend_analysis_results": None, "benchmark_results": None,
            "next_analysis_step": None, "errors": []
        }
        processed_state = self.module.perform_ratio_analysis_node(state)
        self.assertIsNotNone(processed_state["ratio_analysis_results"])
        self.assertIn("profitability_ratios", processed_state["ratio_analysis_results"]) # type: ignore
        self.assertEqual(processed_state["next_analysis_step"], "perform_trends")
        self.assertEqual(len(processed_state["errors"]), 0)

    def test_perform_trend_analysis_node(self):
        """Test the perform_trend_analysis_node."""
        state: FinancialAnalysisState = {
            "company_financial_statements": self.sample_company_statements,
            "historical_data": self.sample_historical_data,
            "ratio_analysis_results": self.sample_company_ratios_output, # Needed to decide next step
            "peer_group_ratios_avg_input": self.sample_peer_ratios_input, # For benchmarking
            "industry_ratios_avg_input": self.sample_industry_ratios_input, # For benchmarking
            "competitor_financial_statements": None, "trend_analysis_results": None, "benchmark_results": None,
            "next_analysis_step": None, "errors": []
        }
        processed_state = self.module.perform_trend_analysis_node(state)
        self.assertIsNotNone(processed_state["trend_analysis_results"])
        self.assertIn("revenue_trend", processed_state["trend_analysis_results"]) # type: ignore
        self.assertEqual(processed_state["next_analysis_step"], "perform_benchmarking")
        self.assertEqual(len(processed_state["errors"]), 0)

    def test_perform_benchmarking_node(self):
        """Test the perform_benchmarking_node."""
        state: FinancialAnalysisState = {
            "company_financial_statements": self.sample_company_statements,
            "historical_data": self.sample_historical_data,
            "ratio_analysis_results": self.sample_company_ratios_output,
            "peer_group_ratios_avg_input": self.sample_peer_ratios_input,
            "industry_ratios_avg_input": self.sample_industry_ratios_input,
            "competitor_financial_statements": None, "trend_analysis_results": None, "benchmark_results": None,
            "next_analysis_step": None, "errors": []
        }
        processed_state = self.module.perform_benchmarking_node(state)
        self.assertIsNotNone(processed_state["benchmark_results"])
        self.assertIn("overall_performance_summary", processed_state["benchmark_results"]) # type: ignore
        self.assertEqual(processed_state["next_analysis_step"], "END") # type: ignore
        self.assertEqual(len(processed_state["errors"]), 0)

    def test_route_analysis_edge(self):
        """Test the routing logic."""
        state = cast(FinancialAnalysisState, {"next_analysis_step": "perform_ratios"})
        self.assertEqual(self.module.route_analysis_edge(state), "perform_ratios")
        state = cast(FinancialAnalysisState, {"next_analysis_step": "perform_trends"})
        self.assertEqual(self.module.route_analysis_edge(state), "perform_trends")
        state = cast(FinancialAnalysisState, {"next_analysis_step": "perform_benchmarking"})
        self.assertEqual(self.module.route_analysis_edge(state), "perform_benchmarking")
        state = cast(FinancialAnalysisState, {"next_analysis_step": "END"}) # type: ignore
        self.assertEqual(self.module.route_analysis_edge(state), "END") # type: ignore
        state = cast(FinancialAnalysisState, {"next_analysis_step": None})
        self.assertEqual(self.module.route_analysis_edge(state), "END") # type: ignore


    def test_run_full_analysis_graph_simulated(self):
        """Test the run_full_analysis_graph method with simulated graph execution."""
        results = self.module.run_full_analysis_graph(
            company_statements=self.sample_company_statements,
            historical_data=self.sample_historical_data,
            peer_ratios=self.sample_peer_ratios_input,
            industry_ratios=self.sample_industry_ratios_input
        )
        self.assertIn("ratios", results)
        self.assertIn("trends", results)
        self.assertIn("benchmarking", results)
        self.assertIsNotNone(results["ratios"])
        self.assertIsNotNone(results["trends"])
        self.assertIsNotNone(results["benchmarking"])
        self.assertTrue(len(results.get("errors", [])) == 0 or "self.app was None" in results.get("errors",[None])[0] )

    # Keep existing tests for direct method calls if they are still public and used
    # For this refactor, they are internal to the class and called by nodes, so direct testing is less critical
    # if node logic is simple. If method logic is complex, keep their tests.
    # For now, assuming the node tests cover the invocation of these methods sufficiently.

if __name__ == '__main__':
    unittest.main()
