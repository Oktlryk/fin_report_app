from typing import Callable, List, Dict, Any
from langchain_core.documents import Document

# Placeholder LLM for simulating extraction from retrieved text for KPIs
class PlaceholderKPIRAGLLM:
    def invoke(self, input_dict: Dict[str, Any]) -> str:
        prompt = input_dict.get("prompt", "")
        context = input_dict.get("context_text", "")
        if "revenue growth drivers" in prompt.lower():
            return f"Revenue growth driven by new product InnovateMax and market expansion (Simulated RAG from: {context[:50]}...)."
        elif "debt components" in prompt.lower():
            return f"Debt primarily consists of long-term bonds and a revolving credit facility (Simulated RAG from: {context[:50]}...)."
        return f"Placeholder KPI LLM response for prompt '{prompt[:30]}...' based on context '{context[:50]}...' (Simulated RAG LLM)."


class KPIExtractor:
    """
    Extracts Key Performance Indicators (KPIs) using financial statements
    and RAG for contextual KPIs that require textual information.
    """

    def __init__(self):
        """
        Initializes the KPIExtractor.
        Uses a placeholder LLM for RAG simulations.
        """
        self.llm = PlaceholderKPIRAGLLM()
        print("KPIExtractor initialized with PlaceholderKPIRAGLLM for RAG.")

    def extract_kpis(self, parsed_report_data: dict,
                     financial_statements: dict,
                     vector_store_search_fn: Callable = None) -> dict: # type: ignore
        """
        Extracts and calculates Key Performance Indicators (KPIs).
        Some KPIs are calculated directly from financial_statements.
        Others might use RAG for contextual information from parsed_report_data via vector_store_search_fn.

        Args:
            parsed_report_data: Dictionary with parsed report content (e.g., from ReportParser).
            financial_statements: Dictionary with extracted financial statements
                                  (e.g., from FinancialStatementExtractor).
            vector_store_search_fn: Optional callable for RAG search. If None, RAG-dependent KPIs
                                    will use fallback placeholders.

        Returns:
            A dictionary of KPIs with their calculated or (simulated) RAG-assisted values.
        """
        if not isinstance(parsed_report_data, dict):
            raise TypeError("parsed_report_data must be a dictionary.")
        if not isinstance(financial_statements, dict):
            raise TypeError("financial_statements must be a dictionary.")
        if vector_store_search_fn and not callable(vector_store_search_fn):
            raise TypeError("vector_store_search_fn must be callable if provided.")

        print(f"Extracting KPIs. Financial statement keys: {list(financial_statements.keys())}.")

        # Simulate using financial_statements for direct calculation (placeholders for now)
        # In a real scenario, these would involve actual calculations based on statement content.
        # For example: financial_statements.get("income_statement", {}).get("Revenue")
        _ = financial_statements.get("income_statement")
        _ = financial_statements.get("balance_sheet")

        kpis = {
            # Direct calculation examples (placeholders)
            "revenue_growth_yoy": "0.10 (10%) placeholder_v2_direct_calc",
            "gross_profit_margin": "0.60 (60%) placeholder_v2_direct_calc",
            "net_profit_margin": "0.15 (15%) placeholder_v2_direct_calc",
            "return_on_equity_roe": "0.20 (20%) placeholder_v2_direct_calc",
            "debt_to_equity_ratio": "0.5 placeholder_v2_direct_calc",
            "current_ratio": "2.0 placeholder_v2_direct_calc",
            "quick_ratio": "1.0 placeholder_v2_direct_calc",

            # KPIs that might benefit from RAG for context/details
            "revenue_growth_drivers_detail": "Placeholder - RAG not used or no info.",
            "debt_structure_detail": "Placeholder - RAG not used or no info."
        }

        if vector_store_search_fn:
            print("  Attempting RAG-assisted KPI context extraction...")
            # Example: Revenue Growth Drivers
            rev_growth_query = "What were the main drivers of revenue growth in the past year?"
            try:
                retrieved_docs_rev = vector_store_search_fn(query=rev_growth_query, k=2)
                context_rev = "\n".join([doc.page_content for doc, score in retrieved_docs_rev]) if retrieved_docs_rev else "No specific context found for revenue drivers."
                kpis["revenue_growth_drivers_detail"] = self.llm.invoke({
                    "prompt": "Summarize revenue growth drivers.",
                    "context_text": context_rev
                })
                print(f"    - RAG for Revenue Growth Drivers: {kpis['revenue_growth_drivers_detail'][:100]}...")
            except Exception as e:
                print(f"    - Error during RAG for revenue growth drivers: {e}")
                kpis["revenue_growth_drivers_detail"] = "Error during RAG processing."

            # Example: Debt Structure Details (context for Debt-to-Equity)
            debt_detail_query = "Describe the company's debt components or structure."
            try:
                retrieved_docs_debt = vector_store_search_fn(query=debt_detail_query, k=2)
                context_debt = "\n".join([doc.page_content for doc, score in retrieved_docs_debt]) if retrieved_docs_debt else "No specific context found for debt structure."
                kpis["debt_structure_detail"] = self.llm.invoke({
                    "prompt": "Describe main debt components.",
                    "context_text": context_debt
                })
                print(f"    - RAG for Debt Structure: {kpis['debt_structure_detail'][:100]}...")
            except Exception as e:
                print(f"    - Error during RAG for debt structure: {e}")
                kpis["debt_structure_detail"] = "Error during RAG processing."
        else:
            print("  Skipping RAG-assisted KPI context extraction as no search function was provided.")

        print("KPI extraction (simulated direct and RAG) complete.")
        return kpis

if __name__ == '__main__':
    print("Starting example usage of KPIExtractor with RAG...")

    # Mock vector_store_search_fn for example
    def mock_kpi_rag_search_fn(query: str, k: int) -> list[tuple[Document, float]]:
        print(f"  Mock KPI RAG Search: Query='{query}', k={k}")
        if "revenue growth" in query.lower():
            return [(Document(page_content="Revenue increased due to strong sales of Product X and expansion into new markets.", metadata={"source":"pg5"}), 0.9)]
        elif "debt components" in query.lower():
            return [(Document(page_content="The company's debt includes $50M in bonds and a $20M credit line.", metadata={"source":"pg15"}), 0.85)]
        return []

    kpi_extractor = KPIExtractor()

    sample_parsed_data = {"text": "Full report text..."} # Used by RAG indirectly
    sample_financial_statements = { # Used for direct calculations (though current are placeholders)
        "income_statement": {"revenue": 1000, "net_income": 150},
        "balance_sheet": {"total_debt": 400, "total_equity": 800}
    }

    print("\n--- Extracting KPIs with RAG (mocked search) ---")
    try:
        kpis_with_rag = kpi_extractor.extract_kpis(sample_parsed_data, sample_financial_statements, mock_kpi_rag_search_fn)
        print("\nSuccessfully extracted KPIs (simulated RAG). Output:")
        for key, value in kpis_with_rag.items():
            print(f"  {key}: {value}")
    except Exception as e:
        print(f"Error during KPI extraction with RAG: {e}")

    print("\n--- Extracting KPIs without RAG search function ---")
    try:
        kpis_no_rag = kpi_extractor.extract_kpis(sample_parsed_data, sample_financial_statements, None)
        print("\nSuccessfully extracted KPIs (no RAG). Output:")
        for key, value in kpis_no_rag.items():
            print(f"  {key}: {value}")
        self.assertTrue("Placeholder - RAG not used" in kpis_no_rag["revenue_growth_drivers_detail"]) # From unittest if run here
    except Exception as e:
        print(f"Error during KPI extraction without RAG: {e}")

    print("\nExample usage of KPIExtractor with RAG complete.")
