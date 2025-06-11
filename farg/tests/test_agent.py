import unittest
import os
import shutil # For managing dummy files/dirs

# Ensure farg.agent and its dependencies are discoverable
# This might require careful sys.path manipulation if tests are run from a sub-directory
# or if a proper package installation (e.g., editable install) is not used.
try:
    from farg.agent import FARGAgent
    # Import other components if we need to mock them or check their instantiation by the agent
except ImportError:
    import sys
    # Assuming tests are in farg/tests/
    # Adjust this path if your test structure is different
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
    from farg.agent import FARGAgent


class TestFARGAgent(unittest.TestCase):
    """
    Unit tests for the FARGAgent class.
    These are integration tests of sorts, verifying the flow through components.
    """
    DUMMY_REPORTS_DIR = "temp_test_agent_reports"

    @classmethod
    def setUpClass(cls):
        """Create a temporary directory for dummy report files."""
        if os.path.exists(cls.DUMMY_REPORTS_DIR):
            shutil.rmtree(cls.DUMMY_REPORTS_DIR)
        os.makedirs(cls.DUMMY_REPORTS_DIR)

        # Create some dummy report files
        cls.company_report_path_1 = os.path.join(cls.DUMMY_REPORTS_DIR, "companyA_report1.txt")
        cls.company_report_path_2 = os.path.join(cls.DUMMY_REPORTS_DIR, "companyA_report2.pdf") # Extension for loader
        cls.competitor_report_path_1 = os.path.join(cls.DUMMY_REPORTS_DIR, "competitorB_report1.txt")

        with open(cls.company_report_path_1, "w") as f:
            f.write("Company A Report Content: Year 2023. Revenue $120M. Net Profit $15M. Focus on AI.")
        with open(cls.company_report_path_2, "w") as f: # Dummy PDF content
            f.write("Company A Supplementary PDF Content. Market discussion.")
        with open(cls.competitor_report_path_1, "w") as f:
            f.write("Competitor B Report: Year 2023. Revenue $90M. Net Profit $10M. Strong in European market.")

    @classmethod
    def tearDownClass(cls):
        """Remove the temporary directory and files after tests."""
        if os.path.exists(cls.DUMMY_REPORTS_DIR):
            shutil.rmtree(cls.DUMMY_REPORTS_DIR)

    def setUp(self):
        """Initialize the agent for each test."""
        self.agent = FARGAgent()

    def test_agent_instantiation(self):
        """Test that FARGAgent and its components are instantiated."""
        self.assertIsInstance(self.agent, FARGAgent)
        # Check a few key components to ensure they are initialized (as per agent's __init__)
        self.assertTrue(hasattr(self.agent, 'report_loader'))
        self.assertTrue(hasattr(self.agent, 'report_parser'))
        self.assertTrue(hasattr(self.agent, 'financial_analysis_module'))
        self.assertTrue(hasattr(self.agent, 'report_generator'))

    def test_run_single_company_analysis(self):
        """Test the agent's run method for a single company."""
        report_paths = [self.company_report_path_1, self.company_report_path_2]
        options = ["Key Insights Generation", "Strategic Recommendations"] # Sample options

        report_output = self.agent.run(company_report_paths=report_paths, analysis_options=options)

        self.assertIsInstance(report_output, str)
        self.assertTrue(len(report_output) > 0)

        # Check for key sections / phrases expected from the agent's orchestration
        self.assertIn("FARG Analysis: CompanyA", report_output) # From _compile_data_for_template
        self.assertIn("Company A Report Content: Year 2023", report_output) # From loaded content via parser via LLM placeholder
        self.assertIn("LLM Summary of: Company A Report Content", report_output) # From ReportParser's LLM
        self.assertIn("Simulating financial statement extraction using LangGraph structure", report_output) # From FinancialStatementExtractor
        self.assertIn("Simulating full financial analysis graph run", report_output) # From FinancialAnalysisModule
        self.assertIn("Simulating insight generation", report_output) # From InsightGenerator
        self.assertIn("Simulating recommendation generation", report_output) # From RecommendationEngine
        self.assertIn("--- Assumptions and Limitations ---", report_output)
        self.assertNotIn("CompanyB", report_output) # Ensure no competitor data is shown

    def test_run_comparative_analysis(self):
        """Test the agent's run method for company vs. competitor analysis."""
        company_paths = [self.company_report_path_1]
        competitor_paths = [self.competitor_report_path_1]
        options = ["Financial Performance Comparison", "SWOT Analysis"]

        report_output = self.agent.run(
            company_report_paths=company_paths,
            competitor_report_paths=competitor_paths,
            analysis_options=options
        )

        self.assertIsInstance(report_output, str)
        self.assertIn("FARG Analysis: CompanyA vs CompanyB", report_output) # Title check
        self.assertIn("Company A Report Content", report_output)
        self.assertIn("Competitor B Report", report_output) # Check if competitor content was processed by parser
        self.assertIn("Simulating SWOT analysis for company CompanyA against 1 competitor(s)", report_output) # From CompetitorAnalysisModule
        self.assertIn("Simulating performance comparison of company CompanyA against 1 competitor(s)", report_output) # From CompetitorAnalysisModule
        self.assertIn("financial_comparison_summary", report_output.lower()) # Key in template for comparison
        self.assertIn("--- Assumptions and Limitations ---", report_output)

    def test_run_no_company_reports(self):
        """Test agent behavior when no company reports are provided."""
        # The agent's _process_company_data should handle this.
        # The UI wrapper in app.py also has a check, but agent should be robust.
        report_output = self.agent.run(company_report_paths=[])
        self.assertIsInstance(report_output, str)
        self.assertIn("Failed to process Company A data: No reports provided.", report_output)

    def test_run_company_report_load_failure(self):
        """Test agent behavior if a company report path is invalid."""
        # AnnualReportLoader is designed to raise FileNotFoundError or skip.
        # The agent's _process_company_data should catch this.
        invalid_path = [os.path.join(self.DUMMY_REPORTS_DIR, "non_existent_report.txt")]
        report_output = self.agent.run(company_report_paths=invalid_path)
        self.assertIsInstance(report_output, str)
        self.assertIn("Failed to process Company A data: Could not load reports for CompanyA.", report_output)

    def test_run_competitor_report_load_failure(self):
        """Test agent behavior if competitor report path is invalid but company is valid."""
        company_paths = [self.company_report_path_1]
        invalid_competitor_path = [os.path.join(self.DUMMY_REPORTS_DIR, "non_existent_competitor.txt")]

        # Agent should print a warning for competitor but proceed with single company analysis
        report_output = self.agent.run(
            company_report_paths=company_paths,
            competitor_report_paths=invalid_competitor_path
        )
        self.assertIsInstance(report_output, str)
        self.assertIn("FARG Analysis: CompanyA", report_output) # Single company title
        self.assertNotIn("CompanyB", report_output) # No competitor data in final report structure
        self.assertIn("--- Assumptions and Limitations ---", report_output)
        # Check logs/stdout for the warning (not directly testable in output string here)
        # This test mainly ensures it doesn't crash and falls back gracefully.

if __name__ == '__main__':
    unittest.main()
