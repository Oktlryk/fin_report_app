# Data Ingestion
from farg.data_ingestion.annual_report_loader import AnnualReportLoader
from farg.data_ingestion.report_parser import ReportParser
# from farg.data_ingestion.report_storage import ReportStorage # Not directly used by agent for now

# Information Extraction
from farg.information_extraction.company_info_extractor import CompanyInfoExtractor
from farg.information_extraction.financial_statement_extractor import FinancialStatementExtractor
from farg.information_extraction.kpi_extractor import KPIExtractor

# Data Analysis & Processing
from farg.data_analysis_processing.financial_analysis_module import FinancialAnalysisModule
from farg.data_analysis_processing.competitor_analysis_module import CompetitorAnalysisModule

# Insight Generation & Recommendation
from farg.insight_generation_recommendation.insight_generator import InsightGenerator
from farg.insight_generation_recommendation.recommendation_engine import RecommendationEngine

# Report Generation
from farg.report_generation.report_generator import ReportGenerator
from farg.report_generation.report_template_engine import ReportTemplateEngine
from farg.report_generation.report_generator_components import (
    CompanyProfileGenerator,
    FinancialPerformanceComparator,
    StrategicOperationalIssueIdentifier
)

class FARGAgent:
    """
    Orchestrates the entire Financial Analysis Report Generation (FARG) workflow.
    It integrates all components from data ingestion to report generation.
    """

    def __init__(self):
        """
        Initializes all necessary components of the FARG system.
        """
        self.report_loader = AnnualReportLoader()
        self.report_parser = ReportParser()

        self.company_info_extractor = CompanyInfoExtractor()
        self.financial_statement_extractor = FinancialStatementExtractor()
        self.kpi_extractor = KPIExtractor()

        self.financial_analysis_module = FinancialAnalysisModule()
        self.competitor_analysis_module = CompetitorAnalysisModule()

        self.insight_generator = InsightGenerator()
        self.recommendation_engine = RecommendationEngine()

        # ReportGenerator requires its own sub-components and template engine
        self.report_template_engine = ReportTemplateEngine()
        self.company_profile_generator = CompanyProfileGenerator()
        self.financial_performance_comparator = FinancialPerformanceComparator()
        self.strategic_operational_issue_identifier = StrategicOperationalIssueIdentifier()

        self.report_generator = ReportGenerator(
            report_template_engine=self.report_template_engine,
            company_profile_generator=self.company_profile_generator,
            financial_performance_comparator=self.financial_performance_comparator,
            strategic_operational_issue_identifier=self.strategic_operational_issue_identifier,
            insight_generator=self.insight_generator, # ReportGenerator uses this too
            recommendation_engine=self.recommendation_engine # ReportGenerator uses this too
        )
        print("FARGAgent initialized with all components.")

    def _process_company_data(self, report_paths: list[str], company_id: str) -> dict:
        """
        Helper function to process data for a single company (load, parse, extract).
        """
        if not report_paths:
            print(f"No report paths provided for {company_id}. Skipping processing.")
            return {"id": company_id, "error": "No reports provided."}

        print(f"Processing data for {company_id} using reports: {report_paths}")
        # 1. Data Ingestion (simplified: taking the first report if multiple)
        # In a real scenario, might merge content or process all.
        # For now, assume ReportLoader handles multiple paths and returns a list of contents,
        # and parser handles one content string at a time.
        loaded_reports_content = self.report_loader.load_reports(report_paths)
        if not loaded_reports_content:
            return {"id": company_id, "error": f"Could not load reports for {company_id}."}

        # For simplicity, concatenate content if multiple reports, or use the first one.
        # The parser currently expects a single string.
        # This part needs refinement based on how multiple reports should be handled by parser.
        # Let's assume for now we parse the content of the first successfully loaded report.
        main_report_content = loaded_reports_content[0]

        # 2. Parsing
        parsed_data = self.report_parser.parse_report(main_report_content)

        # 3. Information Extraction
        company_info = self.company_info_extractor.extract_company_info(parsed_data)
        # Add company_name to company_info if not already there, for ReportGenerator
        company_info["company_name"] = company_id

        financial_statements = self.financial_statement_extractor.extract_financial_statements(parsed_data)
        kpis = self.kpi_extractor.extract_kpis(parsed_data, financial_statements)

        # Collate extracted information
        # This structure should align with what analysis modules and report generator expect
        processed_data = {
            "id": company_id,
            "parsed_data": parsed_data, # Includes text and LLM-parsed sections
            "company_info": company_info,
            "financial_statements": financial_statements, # Simulated LangGraph output
            "kpis": kpis,
            # Initial financial summary for profile generation (can be refined)
            "financial_summary": {
                "annual_revenue": kpis.get("revenue_placeholder", "N/A from agent"), # Assuming KPI extractor provides this
                "net_profit_margin": kpis.get("net_profit_margin", "N/A from agent")
            },
            "errors": [] # To accumulate any errors during processing
        }
        print(f"Finished initial data processing for {company_id}.")
        return processed_data

    def run(self, company_report_paths: list[str],
            competitor_report_paths: list[str] = None,
            analysis_options: list[str] = None) -> str:
        """
        Runs the full FARG pipeline.
        """
        print("\n--- FARGAgent Run Initiated ---")
        if analysis_options is None:
            analysis_options = [] # Default to empty list

        # Process Primary Company Data
        company_A_data = self._process_company_data(company_report_paths, "CompanyA")
        if company_A_data.get("error"):
            return f"Failed to process Company A data: {company_A_data['error']}"

        # Process Competitor Company Data (if provided)
        company_B_data = None
        if competitor_report_paths:
            company_B_data = self._process_company_data(competitor_report_paths, "CompanyB")
            if company_B_data.get("error"):
                # Non-fatal for now, proceed with single company analysis
                print(f"Warning: Failed to process Company B data: {company_B_data['error']}")
                company_B_data = None


        # Perform Financial Analysis (using the graph runner method)
        # For historical data, it would need to be sourced or passed in. Placeholder for now.
        company_A_historical_data_sim = [company_A_data["financial_statements"]] # Simplified
        company_A_fin_analysis = self.financial_analysis_module.run_full_analysis_graph(
            company_statements=company_A_data["financial_statements"], # type: ignore
            historical_data=company_A_historical_data_sim, # type: ignore
            # Peer/Industry ratios would ideally be loaded from a database or external source
            peer_ratios={"info": "dummy_peer_ratios_for_agent_run"},
            industry_ratios={"info": "dummy_industry_ratios_for_agent_run"}
        )
        company_A_data["financial_analysis"] = company_A_fin_analysis


        # Competitor and Comparative Analysis
        # The competitor_analysis_module's methods expect more structured input
        # than just raw data. They expect analysis results or comprehensive extracted data.
        # We'll use the processed company_A_data and company_B_data here.

        swot_analysis_results = {}
        performance_comparison_results = {}

        if company_B_data:
            company_B_historical_data_sim = [company_B_data["financial_statements"]]
            company_B_fin_analysis = self.financial_analysis_module.run_full_analysis_graph(
                company_statements=company_B_data["financial_statements"], # type: ignore
                historical_data=company_B_historical_data_sim # type: ignore
            )
            company_B_data["financial_analysis"] = company_B_fin_analysis

            # SWOT analysis (simplified inputs for now)
            # Market data would come from another source or be a general input.
            market_data_sim = {"trend": "general market trend placeholder"}
            swot_analysis_results = self.competitor_analysis_module.perform_swot_analysis(
                company_extracted_data=company_A_data, # Contains info, kpis, etc.
                competitor_extracted_data=[company_B_data], # Expects a list
                market_context_data=market_data_sim
            )

            # Performance comparison
            performance_comparison_results = self.competitor_analysis_module.compare_performance(
                company_analysis_results=company_A_data, # Contains financial_analysis, kpis, etc.
                competitor_analysis_results_list=[company_B_data]
            )
        else: # If no competitor, SWOT is more internal (or could take general market data)
             market_data_sim = {"trend": "general market trend placeholder"}
             swot_analysis_results = self.competitor_analysis_module.perform_swot_analysis(
                company_extracted_data=company_A_data,
                competitor_extracted_data=[], # No specific competitor
                market_context_data=market_data_sim
            )
        company_A_data["swot_analysis"] = swot_analysis_results # Attach to main company's data bundle
        company_A_data["performance_comparison"] = performance_comparison_results


        # Identify Strategic/Operational Issues (using the component from report_generation)
        # This component is designed to create input for recommendations.
        # It needs financial_analysis and competitor_analysis (which includes SWOT).
        # For now, insights are generated after this, but in a real flow, insights might feed into issue ID.
        # Let's assume some preliminary insights or use placeholders for now.
        preliminary_insights_for_issue_id = ["Placeholder insight about market positioning.", "Placeholder concern on costs."]

        identified_issues = self.strategic_operational_issue_identifier.identify_issues(
            company_financial_analysis=company_A_fin_analysis,
            company_competitor_analysis={"swot": swot_analysis_results, "comparison": performance_comparison_results}, # Wrap SWOT here
            generated_insights=preliminary_insights_for_issue_id
        )
        company_A_data["identified_issues"] = identified_issues


        # Insight Generation
        # This should ideally use all available analysis for Company A
        insights = self.insight_generator.generate_insights(
            financial_analysis_results=company_A_fin_analysis,
            competitor_analysis_results={"swot": swot_analysis_results, "comparison": performance_comparison_results},
            swot_analysis=swot_analysis_results # Redundant if already in competitor_analysis_results, but explicit
        )
        company_A_data["insights"] = insights


        # Recommendation Engine
        recommendations = self.recommendation_engine.generate_recommendations(
            insights=insights,
            strategic_issues=identified_issues.get("strategic_issues", {}), # Ensure dict format
            operational_issues=identified_issues.get("operational_issues", {}) # Ensure dict format
        )
        company_A_data["recommendations"] = recommendations


        # Report Generation
        # The ReportGenerator's generate_full_report method is already designed to take paths
        # and run its internal simulation. For this agent, we want it to use the data
        # we've painstakingly gathered and processed.
        # This implies ReportGenerator might need a method like `generate_report_from_processed_data`
        # or its `generate_full_report` needs to be adapted to accept these rich data dicts.

        # For now, we'll adapt the call to `generate_full_report` by passing our processed data
        # conceptually. The `ReportGenerator`'s `generate_full_report` already has logic
        # to structure a `report_data_compiled` dictionary. We need to ensure our
        # `company_A_data` (and `company_B_data`) can be mapped to that structure.

        # Let's call ReportGenerator with the original paths, but acknowledge that
        # in a refined version, the pre-processed data (company_A_data, company_B_data)
        # would be the primary input to avoid re-processing.
        # The current ReportGenerator simulates its own data processing pipeline based on paths.
        # This is a slight architectural mismatch to resolve later.
        # For this step, we'll let ReportGenerator run its course with paths,
        # but the *intent* is that it would use the agent's processed data.

        # To make this work for now, we'll pass the paths as required by ReportGenerator.
        # The ReportGenerator will internally simulate fetching/analysis.
        # This is not ideal but avoids refactoring ReportGenerator in *this* step.
        # The "Assumptions and Limitations" will highlight this.

        report_template = "single_company_deep_dive_v1"
        if company_B_data:
            report_template = "standard_comparison_report_v1"

        final_report_str = self.report_generator.generate_full_report(
            company_A_raw_data_path=company_report_paths[0] if company_report_paths else "N/A", # RG expects a single path for now
            company_B_raw_data_path=competitor_report_paths[0] if competitor_report_paths else None,
            template_name=report_template
            # In future, would pass: company_A_processed_data=company_A_data, company_B_processed_data=company_B_data
        )

        # --- Refined approach for ReportGenerator ---
        # Instead of calling generate_full_report with paths, let's assume ReportGenerator
        # has a way to accept the agent's processed data to fill its template.
        # The `report_data_compiled` in `ReportGenerator.generate_full_report` is the target.
        # We need to map `company_A_data` and `company_B_data` into that structure.

        # This part is a conceptual override of ReportGenerator's internal data gathering
        # by providing the data directly for template population.

        report_data_for_template = self.report_generator._compile_data_for_template( # type: ignore # private but for clarity
            company_A_processed=company_A_data,
            company_B_processed=company_B_data, # Could be None
            # analysis_options=analysis_options # To control sections
        )

        final_template_str = self.report_template_engine.load_template(report_template)
        final_report_str_from_agent_data = self.report_template_engine.populate_template(
            final_template_str, report_data_for_template
        )


        # Append Assumptions and Limitations
        assumptions_limitations = (
            "\n\n--- Assumptions and Limitations ---\n"
            "- Data quality and availability are assumed to be adequate from the provided reports.\n"
            "- Analysis is based on (simulated) NLP extraction and may have limitations.\n"
            "- Financial models used are simplified for this version.\n"
            "- LangChain/LangGraph components are currently using placeholder logic and simulated graph runs.\n"
            "- The ReportGenerator step in the agent currently uses data processed by the agent, overriding ReportGenerator's internal data simulation if it were called with paths only.\n"
        )
        final_report_with_caveats = final_report_str_from_agent_data + assumptions_limitations

        print("--- FARGAgent Run Completed ---")
        return final_report_with_caveats


    # This method would be part of ReportGenerator, but agent needs to prepare data for it.
    # Adding a simplified version here for the agent to use.
    # This method is essentially what ReportGenerator's `generate_full_report` does
    # after its internal (simulated) data gathering.
    # We are moving this responsibility to the agent.
    def _compile_data_for_template(self, company_A_processed: dict, company_B_processed: dict = None, analysis_options: list = None) -> dict:
        """
        Helper to structure the processed data for the template engine,
        mimicking what ReportGenerator's compilation step would do.
        """
        if analysis_options is None: analysis_options = []

        # Company A data mapping
        profile_A_data = company_A_processed.get("company_info", {})
        fin_sum_A = company_A_processed.get("financial_summary", {})
        fin_analysis_A = company_A_processed.get("financial_analysis", {})
        ratios_A = fin_analysis_A.get("ratios", {})
        trends_A = fin_analysis_A.get("trends", {})
        bench_A = fin_analysis_A.get("benchmarking", {})
        swot_A = company_A_processed.get("swot_analysis", {})
        issues_A = company_A_processed.get("identified_issues", {})
        insights_A = company_A_processed.get("insights", [])
        recos_A = company_A_processed.get("recommendations", [])


        report_data = {
            "report_title": f"FARG Analysis: {profile_A_data.get('company_name', 'Company A')}" +
                            (f" vs {company_B_processed.get('company_info', {}).get('company_name', 'Company B')}" if company_B_processed else ""),
            "generation_date": "Today (Agent Sim)",

            "company_A_name": profile_A_data.get('company_name', "N/A"),
            "company_A_market_footprint": profile_A_data.get('market_footprint', "N/A"),
            "company_A_products_services": str(profile_A_data.get('major_products_services_lines', "N/A")),
            "company_A_relative_size": profile_A_data.get('relative_size_category', "N/A"),
            "company_A_maturity_stage": profile_A_data.get('stage_of_maturity', "N/A"),
            "company_A_financial_summary": f"Revenue: {fin_sum_A.get('annual_revenue', 'N/A')}, NPM: {fin_sum_A.get('net_profit_margin', 'N/A')}",

            "financial_ratios": str(ratios_A.get("profitability_ratios", {})), # Example, needs better formatting
            "financial_trends": str(trends_A),
            "benchmarking_summary": str(bench_A.get("overall_performance_summary", "N/A")),

            "swot_strengths": swot_A.get("strengths", []),
            "swot_weaknesses": swot_A.get("weaknesses", []),
            "swot_opportunities": swot_A.get("opportunities", []),
            "swot_threats": swot_A.get("threats", []),

            "strategic_issues": issues_A.get("strategic_issues", []),
            "operational_issues": issues_A.get("operational_issues", []),
            "insights": insights_A,
            "recommendations": recos_A, # List of dicts
        }

        if company_B_processed:
            profile_B_data = company_B_processed.get("company_info", {})
            fin_sum_B = company_B_processed.get("financial_summary", {})
            fin_analysis_B = company_B_processed.get("financial_analysis", {})
            ratios_B = fin_analysis_B.get("ratios", {})

            report_data["company_B_name"] = profile_B_data.get('company_name', "N/A")
            # ... add all company_B fields similar to company_A ...
            report_data["company_B_financial_summary"] = f"Revenue: {fin_sum_B.get('annual_revenue', 'N/A')}, NPM: {fin_sum_B.get('net_profit_margin', 'N/A')}"

            comparison_summary = company_A_processed.get("performance_comparison",{}).get("overall_comparison_summary", "N/A")
            report_data["financial_comparison_summary"] = comparison_summary
            report_data["comp_A_profitability_metric"] = str(ratios_A.get("profitability_ratios",{}).get("net_profit_margin", "N/A"))
            report_data["comp_B_profitability_metric"] = str(ratios_B.get("profitability_ratios",{}).get("net_profit_margin", "N/A"))
            # ... more comparison metrics ...
        else: # Handle fields for single company report
            report_data["company_B_name"] = "N/A"
            report_data["company_B_financial_summary"] = "N/A"
            report_data["financial_comparison_summary"] = "Single company analysis."
            report_data["comp_A_profitability_metric"] = str(ratios_A.get("profitability_ratios",{}).get("net_profit_margin", "N/A"))
            report_data["comp_B_profitability_metric"] = "N/A"


        return report_data

if __name__ == "__main__":
    print("--- FARGAgent Self-Test/Example Run ---")
    # This requires dummy files to exist if ReportLoader is not mocked or adapted
    # For this example, let's assume ReportLoader can handle non-existent paths gracefully (it should raise FileNotFoundError)
    # To make this runnable, we'd need to ensure paths are valid or mock the loader.

    # Create dummy files for the loader to "succeed"
    os.makedirs("dummy_agent_reports", exist_ok=True)
    dummy_co_report_path = "dummy_agent_reports/co_report.txt"
    dummy_comp_report_path = "dummy_agent_reports/comp_report.txt"
    with open(dummy_co_report_path, "w") as f:
        f.write("Company A Report: Income Statement says revenue is 100M. Balance Sheet shows assets of 500M.")
    with open(dummy_comp_report_path, "w") as f:
        f.write("Competitor B Report: Income Statement indicates revenue is 80M. Balance Sheet has assets of 400M.")

    agent = FARGAgent()

    print("\n--- Running Agent for Single Company Analysis ---")
    single_company_options = ["Strategic Recommendations", "Key Insights Generation"]
    single_report = agent.run(
        company_report_paths=[dummy_co_report_path],
        analysis_options=single_company_options
    )
    print("\n--- Generated Report (Single Company - Snippet) ---")
    print(single_report[:1000] + "\n...")

    print("\n--- Running Agent for Comparative Analysis ---")
    comparison_options = ["Financial Performance Comparison", "Strategic Recommendations"]
    comp_report = agent.run(
        company_report_paths=[dummy_co_report_path],
        competitor_report_paths=[dummy_comp_report_path],
        analysis_options=comparison_options
    )
    print("\n--- Generated Report (Comparison - Snippet) ---")
    print(comp_report[:1000] + "\n...")

    # Clean up dummy files
    # os.remove(dummy_co_report_path)
    # os.remove(dummy_comp_report_path)
    # os.rmdir("dummy_agent_reports")
    print("\n--- FARGAgent Self-Test Complete (Dummy files kept for inspection) ---")
