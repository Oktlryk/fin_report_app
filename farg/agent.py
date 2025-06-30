import os # For os.path.basename

# Data Ingestion
from farg.data_ingestion.annual_report_loader import AnnualReportLoader
from farg.data_ingestion.report_parser import ReportParser

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
from farg.report_generation.report_generator import ReportGenerator # Though agent takes over its orchestration role
from farg.report_generation.report_template_engine import ReportTemplateEngine
from farg.report_generation.report_generator_components import (
    CompanyProfileGenerator,
    FinancialPerformanceComparator,
    StrategicOperationalIssueIdentifier
)

# RAG Components
from farg.rag_components.vector_store_manager import VectorStoreManager


class FARGAgent:
    def __init__(self):
        self.report_loader = AnnualReportLoader()
        self.report_parser = ReportParser()
        self.vector_store_manager = VectorStoreManager()

        self.company_info_extractor = CompanyInfoExtractor()
        self.financial_statement_extractor = FinancialStatementExtractor()
        self.kpi_extractor = KPIExtractor()

        self.financial_analysis_module = FinancialAnalysisModule()
        self.competitor_analysis_module = CompetitorAnalysisModule()

        self.insight_generator = InsightGenerator()
        self.recommendation_engine = RecommendationEngine()

        self.report_template_engine = ReportTemplateEngine()
        # ReportGenerator sub-components are used by the agent directly now for compiling report data
        self.company_profile_generator = CompanyProfileGenerator()
        self.financial_performance_comparator = FinancialPerformanceComparator()
        self.strategic_operational_issue_identifier = StrategicOperationalIssueIdentifier()

        # The agent itself will now compile the final report_data and use the template engine directly,
        # effectively taking on the orchestration previously envisioned for ReportGenerator.
        # self.report_generator = ReportGenerator(...) # Not needed if agent does full orchestration
        print("FARGAgent initialized with all components, including VectorStoreManager.")

    def _process_company_data(self, report_paths: list[str], company_id_prefix: str, index_base_path: str) -> dict:
        company_id = company_id_prefix # e.g. "companya"
        if not report_paths:
            print(f"No report paths provided for {company_id}. Skipping processing.")
            return {"id": company_id, "error": "No reports provided."}

        print(f"Processing data for {company_id} using reports: {report_paths}")

        loaded_reports_content_list = []
        metadatas_list = []
        for path in report_paths:
            try:
                content = self.report_loader.load_report(path)
                loaded_reports_content_list.append(content)
                metadatas_list.append({"source": os.path.basename(path), "company_id": company_id})
            except Exception as e:
                print(f"Warning: Could not load report {path} for {company_id}: {e}")

        if not loaded_reports_content_list:
            return {"id": company_id, "error": f"Could not load any reports for {company_id}."}

        company_specific_index_path = os.path.join(index_base_path, f"faiss_index_{company_id.lower().replace(' ', '_')}")
        print(f"Creating/updating vector index for {company_id} at {company_specific_index_path}")
        self.vector_store_manager.create_index_from_texts(
            texts=loaded_reports_content_list,
            metadatas=metadatas_list,
            index_path=company_specific_index_path
        )
        # Explicitly load this index to make it active for this company
        self.vector_store_manager.load_index(company_specific_index_path)
        print(f"Index for {company_id} is now active in VectorStoreManager.")

        main_report_content = loaded_reports_content_list[0] # Simplified: use first report for parsing
        parsed_data = self.report_parser.parse_report(main_report_content)

        search_fn = self.vector_store_manager.search

        company_info = self.company_info_extractor.extract_company_info(parsed_data, vector_store_search_fn=search_fn)
        # Ensure company_name is consistently set, using the one from company_info if RAG found it, else the id_prefix
        company_info["company_name"] = company_info.get("company_name") or company_id_prefix.capitalize()

        financial_statements = self.financial_statement_extractor.extract_financial_statements(parsed_data, vector_store_search_fn=search_fn)
        kpis = self.kpi_extractor.extract_kpis(parsed_data, financial_statements, vector_store_search_fn=search_fn)

        processed_data = {
            "id": company_id,
            "parsed_data": parsed_data,
            "company_info": company_info,
            "financial_statements": financial_statements,
            "kpis": kpis,
            "financial_summary": { # Placeholder, could be derived from kpis or financial_statements more robustly
                "annual_revenue": kpis.get("total_revenue_placeholder", "N/A"),
                "net_profit_margin": kpis.get("net_profit_margin", "N/A")
            },
            "vector_index_path": company_specific_index_path,
            "errors": []
        }
        print(f"Finished RAG-enhanced data processing for {company_id}.")
        return processed_data

    def run(self, company_report_paths: list[str],
            competitor_report_paths: list[str] = None,
            analysis_options: list[str] = None,
            rag_index_base_path: str = "farg_indices") -> str:
        print("\n--- FARGAgent Run Initiated (RAG Enabled) ---")
        if analysis_options is None: analysis_options = []
        os.makedirs(rag_index_base_path, exist_ok=True)

        # Process Primary Company Data
        company_A_data = self._process_company_data(company_report_paths, "CompanyA", rag_index_base_path)
        if company_A_data.get("error"):
            return f"Failed to process Company A data: {company_A_data['error']}"

        # Company A's index is now active in self.vector_store_manager
        search_fn_A = self.vector_store_manager.search
        company_A_data["financial_analysis"] = self.financial_analysis_module.run_full_analysis_graph(
            company_statements=company_A_data.get("financial_statements", {}),
            vector_store_search_fn=search_fn_A,
            historical_data=[company_A_data.get("financial_statements", {})], # Simplified historical
            peer_ratios={}, industry_ratios={} # Provide empty dicts if None
        )

        company_B_data = None
        analysis_results_B = None
        if competitor_report_paths:
            company_B_data = self._process_company_data(competitor_report_paths, "CompanyB", rag_index_base_path)
            if company_B_data.get("error"):
                print(f"Warning: Failed to process Company B data: {company_B_data['error']}")
                company_B_data = None
            else:
                # Company B's index is now active
                search_fn_B = self.vector_store_manager.search
                analysis_results_B = self.financial_analysis_module.run_full_analysis_graph(
                    company_statements=company_B_data.get("financial_statements", {}),
                    vector_store_search_fn=search_fn_B,
                    historical_data=[company_B_data.get("financial_statements", {})],
                     peer_ratios={}, industry_ratios={}
                )
                company_B_data['financial_analysis'] = analysis_results_B

        # For subsequent steps primarily about Company A, ensure its RAG context is active
        if company_A_data.get("vector_index_path"):
            print(f"AGENT: Ensuring Company A's RAG context is active for subsequent steps: {company_A_data['vector_index_path']}")
            self.vector_store_manager.load_index(company_A_data['vector_index_path'])
        # search_fn_A is already set, and load_index makes it point to the correct store.

        swot_results = self.competitor_analysis_module.perform_swot_analysis(
            company_A_data, [company_B_data] if company_B_data else [], {}
        )
        company_A_data["swot_analysis"] = swot_results

        if company_B_data:
            company_A_data["performance_comparison"] = self.competitor_analysis_module.compare_performance(
                 company_A_data, [company_B_data]
            )

        identified_issues = self.strategic_operational_issue_identifier.identify_issues(
            company_A_data.get("financial_analysis", {}),
            {"swot": swot_results, "comparison": company_A_data.get("performance_comparison", {})},
            [] # Placeholder for initial insights list if needed by identify_issues
        )
        company_A_data["identified_issues"] = identified_issues

        insights = self.insight_generator.generate_insights(
            company_A_data.get("financial_analysis", {}),
            {"swot": swot_results, "comparison": company_A_data.get("performance_comparison", {})},
            swot_results, # Passing SWOT again explicitly
            vector_store_search_fn=self.vector_store_manager.search # Uses Company A's active index
        )
        company_A_data["insights"] = insights

        recommendations = self.recommendation_engine.generate_recommendations(
            insights,
            identified_issues.get("strategic_issues", {}),
                            identified_issues.get("operational_issues", {})
        )
        company_A_data["recommendations"] = recommendations

        report_template_name = "standard_comparison_report_v1" if company_B_data else "single_company_deep_dive_v1"
        report_data_for_template = self._compile_data_for_template(company_A_data, company_B_data, analysis_options)

        final_template_str = self.report_template_engine.load_template(report_template_name)
        final_report_str = self.report_template_engine.populate_template(final_template_str, report_data_for_template)

        assumptions_limitations = (
            "\n\n--- Assumptions and Limitations ---\n"
            "- Data quality and availability assumed adequate from provided reports.\n"
            "- NLP extraction and analysis are simulated and have limitations.\n"
            "- Financial models are simplified.\n"
            "- LangChain/LangGraph components use placeholder logic; RAG is partially integrated with simulated LLM processing.\n"
            "- Agent orchestrates data flow; ReportGenerator's role is primarily template filling with agent-processed data."
        )
        return final_report_str + assumptions_limitations

    def _compile_data_for_template(self, company_A_processed: dict, company_B_processed: dict = None, analysis_options: list = None) -> dict:
        if analysis_options is None: analysis_options = []
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
            "company_A_products_services": str(profile_A_data.get('products_services', "N/A")),
            "company_A_relative_size": profile_A_data.get('relative_size', "N/A"),
            "company_A_maturity_stage": profile_A_data.get('stage_of_maturity', "N/A"),
            "company_A_financial_summary": f"Revenue: {fin_sum_A.get('annual_revenue', 'N/A')}, NPM: {fin_sum_A.get('net_profit_margin', 'N/A')}",
            "financial_ratios": str(ratios_A.get("profitability_ratios", {})),
            "financial_trends": str(trends_A),
            "benchmarking_summary": str(bench_A.get("overall_performance_summary", "N/A")),
            "swot_strengths": swot_A.get("strengths", []),
            "swot_weaknesses": swot_A.get("weaknesses", []),
            "swot_opportunities": swot_A.get("opportunities", []),
            "swot_threats": swot_A.get("threats", []),
            "strategic_issues": issues_A.get("strategic_issues", []),
            "operational_issues": issues_A.get("operational_issues", []),
            "insights": insights_A,
            "recommendations": recos_A,
        }

        if company_B_processed:
            profile_B_data = company_B_processed.get("company_info", {})
            fin_sum_B = company_B_processed.get("financial_summary", {})
            fin_analysis_B = company_B_processed.get("financial_analysis", {}) # Note: This was analysis_results_B before
            ratios_B = fin_analysis_B.get("ratios", {})

            report_data["company_B_name"] = profile_B_data.get('company_name', "N/A")
            report_data["company_B_market_footprint"] = profile_B_data.get('market_footprint', "N/A")
            report_data["company_B_products_services"] = str(profile_B_data.get('products_services', "N/A"))
            report_data["company_B_relative_size"] = profile_B_data.get('relative_size', "N/A")
            report_data["company_B_maturity_stage"] = profile_B_data.get('stage_of_maturity', "N/A")
            report_data["company_B_financial_summary"] = f"Revenue: {fin_sum_B.get('annual_revenue', 'N/A')}, NPM: {fin_sum_B.get('net_profit_margin', 'N/A')}"

            comparison_summary = company_A_processed.get("performance_comparison",{}).get("overall_comparison_summary", "N/A")
            report_data["financial_comparison_summary"] = comparison_summary
            report_data["comp_A_profitability_metric"] = str(ratios_A.get("profitability_ratios",{}).get("net_profit_margin", "N/A"))
            report_data["comp_B_profitability_metric"] = str(ratios_B.get("profitability_ratios",{}).get("net_profit_margin", "N/A"))
        else: # Default values for single company report for keys used in comparison template
            report_data["company_B_name"] = "N/A"
            report_data["company_B_market_footprint"] = "N/A"
            report_data["company_B_products_services"] = "N/A"
            report_data["company_B_relative_size"] = "N/A"
            report_data["company_B_maturity_stage"] = "N/A"
            report_data["company_B_financial_summary"] = "N/A"
            report_data["financial_comparison_summary"] = "Single company analysis."
            report_data["comp_A_profitability_metric"] = str(ratios_A.get("profitability_ratios",{}).get("net_profit_margin", "N/A"))
            report_data["comp_B_profitability_metric"] = "N/A"
        return report_data

if __name__ == "__main__":
    print("--- FARGAgent Self-Test/Example Run ---")
    os.makedirs("dummy_agent_reports", exist_ok=True)
    # Ensure base RAG index path exists for the test
    rag_test_base = "temp_farg_agent_indices"
    if os.path.exists(rag_test_base):
        shutil.rmtree(rag_test_base) # Clean start for test
    os.makedirs(rag_test_base, exist_ok=True)
    # No need to pre-create companya/companyb subdirs for faiss index, save_local will do it.

    dummy_co_report_path = "dummy_agent_reports/co_report.txt"
    dummy_comp_report_path = "dummy_agent_reports/comp_report.txt"
    with open(dummy_co_report_path, "w") as f:
        f.write("Company A Report: Income Statement says revenue is 100M. Balance Sheet shows assets of 500M. We operate worldwide in the technology sector. Our main products are CloudSuite and DataSpark. We are a large, mature company.")
    with open(dummy_comp_report_path, "w") as f:
        f.write("Competitor B Report: Income Statement indicates revenue is 80M. Balance Sheet has assets of 400M. We focus on North America in the software services sector. Our solutions include CustomAppDev and SupportPro. We are a medium-sized, growing entity.")

    agent = FARGAgent()

    print("\n--- Running Agent for Single Company Analysis ---")
    single_company_options = ["Strategic Recommendations", "Key Insights Generation"]
    single_report = agent.run(
        company_report_paths=[dummy_co_report_path],
        analysis_options=single_company_options,
        rag_index_base_path=rag_test_base
    )
    print("\n--- Generated Report (Single Company - Snippet) ---")
    print(single_report[:1200] + "\n...")

    print("\n--- Running Agent for Comparative Analysis ---")
    comparison_options = ["Financial Performance Comparison", "Strategic Recommendations"]
    comp_report = agent.run(
        company_report_paths=[dummy_co_report_path],
        competitor_report_paths=[dummy_comp_report_path],
        analysis_options=comparison_options,
        rag_index_base_path=rag_test_base
    )
    print("\n--- Generated Report (Comparison - Snippet) ---")
    print(comp_report[:1200] + "\n...")

    print(f"\n--- FARGAgent Self-Test Complete (Dummy files and indices in '{rag_test_base}' and 'dummy_agent_reports' kept for inspection) ---")
    # shutil.rmtree(rag_test_base) # Optional: cleanup test indices
    # shutil.rmtree("dummy_agent_reports") # Optional: cleanup test reports
