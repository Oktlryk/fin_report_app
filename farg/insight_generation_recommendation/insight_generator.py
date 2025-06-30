from typing import Callable, List, Dict, Any, Optional
from langchain_core.documents import Document

# Placeholder LLM for RAG-enhanced insight generation
class PlaceholderInsightRAGLLM:
    def invoke(self, input_dict: Dict[str, Any]) -> str:
        prompt = input_dict.get("prompt", "")
        context = input_dict.get("context_text", "No context provided.")
        analysis_summary = input_dict.get("analysis_summary", "N/A")

        return (f"RAG Insight based on '{analysis_summary}': "
                f"The retrieved context ('{context[:50]}...') suggests that {prompt} "
                f"(Simulated RAG LLM for Insights).")

class InsightGenerator:
    """
    Generates actionable insights from various analysis results,
    optionally augmented by RAG.
    """

    def __init__(self):
        """
        Initializes the InsightGenerator.
        """
        self.llm = PlaceholderInsightRAGLLM()
        print("InsightGenerator initialized with PlaceholderInsightRAGLLM.")

    def generate_insights(self,
                          financial_analysis_results: dict,
                          competitor_analysis_results: dict,
                          swot_analysis: dict,
                          vector_store_search_fn: Optional[Callable[[str, int], List[tuple[Document, float]]]] = None
                          ) -> list[str]:
        """
        Simulates the generation of insights, with optional RAG enhancement.

        Args:
            financial_analysis_results: Output from FinancialAnalysisModule.
            competitor_analysis_results: Output from CompetitorAnalysisModule.
            swot_analysis: SWOT analysis dictionary.
            vector_store_search_fn: Optional callable for RAG search.

        Returns:
            A list of strings, where each string is a generated insight.
        """
        if not isinstance(financial_analysis_results, dict) or \
           not isinstance(competitor_analysis_results, dict) or \
           not isinstance(swot_analysis, dict):
            raise TypeError("All analysis input arguments must be dictionaries.")
        if vector_store_search_fn and not callable(vector_store_search_fn):
            raise TypeError("vector_store_search_fn must be callable if provided.")

        print(f"Generating insights. Financial Analysis keys: {list(financial_analysis_results.keys())}, "
              f"Competitor Analysis keys: {list(competitor_analysis_results.keys())}, SWOT keys: {list(swot_analysis.keys())}. "
              f"RAG enabled: {vector_store_search_fn is not None}")

        # Base insights (placeholders, as before)
        insights = [
            "Insight (Base): Company's robust net profit margin combined with market opportunity suggests potential for new product investment. - placeholder_v2",
            "Observation (Base): Revenue growth is positive, but benchmarking may reveal market share status. - placeholder_v2",
            "Concern (Base): Liquidity ratio requires monitoring based on industry standards. - placeholder_v2",
        ]

        # Example RAG-enhanced insight generation
        if vector_store_search_fn:
            print("  Attempting RAG-enhanced insight generation...")

            # Example 1: Contextualize a key financial trend
            revenue_trend = financial_analysis_results.get("trends", {}).get("revenue_trend", "not specified")
            if "upward" in revenue_trend.lower() or "improving" in revenue_trend.lower() : # Check if it's a positive trend
                query_trend = f"What are the company's stated reasons or plans supporting the positive revenue trend of '{revenue_trend}'?"
                analysis_summary_for_llm = f"Positive revenue trend: {revenue_trend}"
                try:
                    retrieved_docs = vector_store_search_fn(query_trend, k=1)
                    context = retrieved_docs[0][0].page_content if retrieved_docs else "No specific context found for this trend."
                    rag_insight_trend = self.llm.invoke({
                        "prompt": "explain factors contributing to this positive revenue trend",
                        "context_text": context,
                        "analysis_summary": analysis_summary_for_llm
                    })
                    insights.append(f"Insight (RAG): {rag_insight_trend}")
                    print(f"    - RAG Insight (Trend): {rag_insight_trend[:100]}...")
                except Exception as e:
                    print(f"    - Error during RAG for trend insight: {e}")
                    insights.append(f"Insight (RAG Error): Could not generate RAG context for trend '{revenue_trend}'.")

            # Example 2: Elaborate on a SWOT Opportunity
            opportunities = swot_analysis.get("opportunities", [])
            if opportunities:
                first_opportunity = opportunities[0] # Take the first one for simulation
                query_swot_opp = f"What specific actions or market conditions support the opportunity: '{first_opportunity}'?"
                analysis_summary_for_llm = f"SWOT Opportunity: {first_opportunity}"
                try:
                    retrieved_docs_swot = vector_store_search_fn(query_swot_opp, k=1)
                    context_swot = retrieved_docs_swot[0][0].page_content if retrieved_docs_swot else "No specific context found for this SWOT opportunity."
                    rag_insight_swot = self.llm.invoke({
                        "prompt": "provide more details or evidence for this opportunity",
                        "context_text": context_swot,
                        "analysis_summary": analysis_summary_for_llm
                    })
                    insights.append(f"Insight (RAG): {rag_insight_swot}")
                    print(f"    - RAG Insight (SWOT): {rag_insight_swot[:100]}...")
                except Exception as e:
                     print(f"    - Error during RAG for SWOT insight: {e}")
                     insights.append(f"Insight (RAG Error): Could not generate RAG context for SWOT opportunity '{first_opportunity}'.")
        else:
            print("  Skipping RAG-enhanced insights as no search function was provided.")

        print("Insight generation complete.")
        return insights

if __name__ == '__main__':
    print("Starting example usage of InsightGenerator with RAG...")

    # Mock vector_store_search_fn for example
    def mock_insights_rag_search_fn(query: str, k: int) -> list[tuple[Document, float]]:
        print(f"  Mock Insights RAG Search: Query='{query}', k={k}")
        if "revenue trend" in query.lower():
            return [(Document(page_content="The annual report mentions new market entries and strong product adoption as key to revenue growth.", metadata={"source":"AR_pg10"}), 0.92)]
        elif "SWOT opportunity" in query.lower() or "New market segment N" in query: # Match the placeholder
            return [(Document(page_content="Market analysis shows segment N is underserved and growing at 20% CAGR.", metadata={"source":"MarketResearch_XYZ"}), 0.85)]
        return []

    generator = InsightGenerator()

    sample_financial_analysis = {
        "trends": {"revenue_trend": "upward (strong)"},
        "ratios": {"profitability_ratios": {"net_profit_margin_context": "NPM supported by cost controls."}} # Example from previous step
    }
    sample_competitor_analysis = {"overall_comparison_summary": "CompanyX leads in innovation."}
    sample_swot = { "opportunities": ["New market segment N", "Strategic partnerships"] }

    print("\n--- Generating Insights with RAG (mocked search) ---")
    try:
        insights_with_rag = generator.generate_insights(
            sample_financial_analysis, sample_competitor_analysis, sample_swot, mock_insights_rag_search_fn
        )
        print("\nSuccessfully generated insights (RAG). Output:")
        for i, insight in enumerate(insights_with_rag):
            print(f"  {i+1}. {insight}")
    except Exception as e:
        print(f"Error during insight generation with RAG: {e}")

    print("\n--- Generating Insights without RAG search function ---")
    try:
        insights_no_rag = generator.generate_insights(
            sample_financial_analysis, sample_competitor_analysis, sample_swot, None
        )
        print("\nSuccessfully generated insights (No RAG). Output:")
        for i, insight in enumerate(insights_no_rag):
            print(f"  {i+1}. {insight}")
        # Check that base insights are there, and no RAG insights
        self.assertTrue(any("Insight (Base):" in i for i in insights_no_rag)) # from unittest
        self.assertFalse(any("Insight (RAG):" in i for i in insights_no_rag)) # from unittest

    except Exception as e:
        print(f"Error during insight generation without RAG: {e}")

    print("\nExample usage of InsightGenerator with RAG complete.")
