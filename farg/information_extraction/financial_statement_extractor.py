from typing import TypedDict, List, Dict, Any, Callable # Added Callable
# from langgraph.graph import StatefulGraph, START, END # Commented out for now
from langchain_core.documents import Document # For type hinting search results

# Placeholder for an actual LLM or a more sophisticated local one
class PlaceholderFSLLM: # Specific placeholder for this extractor
    def invoke(self, input_dict: Dict[str, Any]) -> str:
        # context_text is from RAG, query is the original question for the statement type
        context_text = input_dict.get("context_text", "")
        query = input_dict.get("query", "")

        # Simulate identifying statement type based on query and context
        if "income statement" in query.lower():
            return f"Extracted Income Statement from context: '{context_text[:100]}...' (Simulated RAG LLM)"
        elif "balance sheet" in query.lower():
            return f"Extracted Balance Sheet from context: '{context_text[:100]}...' (Simulated RAG LLM)"
        elif "cash flow" in query.lower():
            return f"Extracted Cash Flow from context: '{context_text[:100]}...' (Simulated RAG LLM)"
        return f"No specific financial statement identified for query '{query}' from context: '{context_text[:70]}...' (Simulated RAG LLM)"

class FinancialStatementExtractionState(TypedDict):
    """
    Represents the state of the financial statement extraction graph.
    Now includes vector_store_search_fn for RAG.
    """
    parsed_report_data: Dict[str, Any] # Input: full parsed report for metadata or fallback
    vector_store_search_fn: Callable[[str, int], List[tuple[Document, float]]] # Function for RAG searches

    # For iterative processing if we choose to identify one statement type at a time
    statement_types_to_extract: List[str] # e.g., ["income_statement", "balance_sheet", "cash_flow"]
    current_statement_type_index: int

    extracted_statements: Dict[str, str]  # Output: {"income_statement": "...", "balance_sheet": "...", ...}
    errors: List[str]


class FinancialStatementExtractor:
    """
    Extracts financial statements (Income Statement, Balance Sheet, Cash Flow)
    from parsed annual report data using a RAG-enhanced LangGraph workflow (simulated).
    """

    def __init__(self):
        """
        Initializes the FinancialStatementExtractor.
        Defines graph node functions and the graph structure (commented out).
        """
        self.llm = PlaceholderFSLLM()
        print("FinancialStatementExtractor initialized with RAG-aware PlaceholderFSLLM.")
        self.app = None
        print("LangGraph workflow definition outlined but not compiled (as LangGraph library might not be installed).")

    # --- Graph Node Definitions (Conceptual for LangGraph) ---
    def start_extraction_node(self, state: FinancialStatementExtractionState) -> FinancialStatementExtractionState:
        print("Node: start_extraction_node called.")
        state["extracted_statements"] = {}
        state["errors"] = []
        # Define the order of statements to look for if processing iteratively
        state["statement_types_to_extract"] = ["income_statement", "balance_sheet", "cash_flow_statement"]
        state["current_statement_type_index"] = 0
        return state

    def extract_single_statement_node(self, state: FinancialStatementExtractionState) -> FinancialStatementExtractionState:
        """
        Uses RAG to find and extract the current statement type.
        """
        current_type_idx = state["current_statement_type_index"]
        statement_type_to_find = state["statement_types_to_extract"][current_type_idx]

        print(f"Node: extract_single_statement_node for type: {statement_type_to_find}")
        search_fn = state["vector_store_search_fn"]

        # Formulate a query for RAG
        query = f"Retrieve text sections related to the {statement_type_to_find.replace('_', ' ')}."
        print(f"  RAG Query: {query}")

        try:
            retrieved_docs_with_scores = search_fn(query=query, k=3) # Get top 3 chunks

            retrieved_texts = []
            if retrieved_docs_with_scores:
                for doc, score in retrieved_docs_with_scores:
                    retrieved_texts.append(doc.page_content)
                    print(f"    - Retrieved chunk (score {score:.2f}): '{doc.page_content[:70]}...'")
            else:
                print(f"    - No documents retrieved for {statement_type_to_find}.")

            concatenated_retrieved_text = "\n\n---\n\n".join(retrieved_texts) if retrieved_texts else "No relevant information found in documents."

            # Simulate LLM call to "extract" the statement from the retrieved context
            llm_output = self.llm.invoke({
                "query": statement_type_to_find, # Pass the original query for context
                "context_text": concatenated_retrieved_text
            })
            state["extracted_statements"][statement_type_to_find] = llm_output
            print(f"    - LLM Simulated Extraction for '{statement_type_to_find}': '{llm_output[:100]}...'")

        except Exception as e:
            error_msg = f"Error during RAG extraction for {statement_type_to_find}: {str(e)}"
            print(error_msg)
            state["errors"].append(error_msg)
            state["extracted_statements"][statement_type_to_find] = f"Error extracting {statement_type_to_find}."

        state["current_statement_type_index"] += 1
        return state

    def should_continue_statement_type_edge(self, state: FinancialStatementExtractionState) -> str:
        """
        Determines if there are more statement types to extract.
        """
        print(f"Edge: should_continue_statement_type_edge. Index: {state['current_statement_type_index']}, Total Types: {len(state['statement_types_to_extract'])}")
        if state["current_statement_type_index"] < len(state["statement_types_to_extract"]):
            return "extract_next_statement_type" # Route to extract_single_statement_node
        return END # type: ignore # LangGraph's END sentinel

    def extract_financial_statements(self, parsed_report_data: dict, vector_store_search_fn: Callable = None) -> dict: # type: ignore
        """
        Extracts key financial statements using RAG (simulated LangGraph workflow).

        Args:
            parsed_report_data: Dictionary with parsed report content.
            vector_store_search_fn: Callable for RAG search (e.g., vector_store_manager.search).

        Returns:
            A dictionary with extracted statements.
        """
        if not isinstance(parsed_report_data, dict):
            raise TypeError("parsed_report_data must be a dictionary.")
        if vector_store_search_fn and not callable(vector_store_search_fn):
            raise TypeError("vector_store_search_fn must be callable if provided.")

        print("Simulating financial statement extraction using RAG-enhanced LangGraph structure.")

        if not vector_store_search_fn:
            # Fallback or error if RAG is essential
            print("Warning: vector_store_search_fn not provided. Returning basic placeholders.")
            return {
                "income_statement": "Placeholder - RAG search function not provided",
                "balance_sheet": "Placeholder - RAG search function not provided",
                "cash_flow_statement": "Placeholder - RAG search function not provided",
                "notes_to_financial_statements": "Placeholder - Notes",
                "graph_simulation_errors": ["vector_store_search_fn was None"]
            }

        initial_graph_state: FinancialStatementExtractionState = {
            "parsed_report_data": parsed_report_data,
            "vector_store_search_fn": vector_store_search_fn,
            "statement_types_to_extract": [], # Will be set by start_node
            "current_statement_type_index": 0,
            "extracted_statements": {},
            "errors": []
        }

        if self.app: # If LangGraph app was compiled
            # final_state = self.app.invoke(initial_graph_state)
            # For now, simulate the graph run manually as self.app is None
            print("Simulating manual graph invocation (as self.app is likely None).")
            current_state = self.start_extraction_node(initial_graph_state)
            while self.should_continue_statement_type_edge(current_state) != END: # type: ignore
                current_state = self.extract_single_statement_node(current_state)

            final_simulated_statements = current_state.get("extracted_statements", {})
            final_errors = current_state.get("errors", [])
            print(f"Simulated RAG graph run complete. Statements found: {list(final_simulated_statements.keys())}, Errors: {final_errors}")

            return {
                "income_statement": final_simulated_statements.get("income_statement", "Not found or error during RAG."),
                "balance_sheet": final_simulated_statements.get("balance_sheet", "Not found or error during RAG."),
                "cash_flow_statement": final_simulated_statements.get("cash_flow_statement", "Not found or error during RAG."),
                "notes_to_financial_statements": "Placeholder - Notes (RAG for notes TBD)",
                "graph_simulation_errors": final_errors
            }
        else: # Fallback if self.app is not compiled (current state of the code)
            print("LangGraph self.app not compiled. Manually calling RAG-based node logic for simulation.")
            current_state = self.start_extraction_node(initial_graph_state)
            while current_state["current_statement_type_index"] < len(current_state["statement_types_to_extract"]):
                current_state = self.extract_single_statement_node(current_state)

            final_simulated_statements = current_state.get("extracted_statements", {})
            final_errors = current_state.get("errors", [])
            return {
                "income_statement": final_simulated_statements.get("income_statement", "Simulated: Not found via RAG"),
                "balance_sheet": final_simulated_statements.get("balance_sheet", "Simulated: Not found via RAG"),
                "cash_flow_statement": final_simulated_statements.get("cash_flow_statement", "Simulated: Not found via RAG"),
                "notes_to_financial_statements": "Placeholder - Notes (RAG for notes TBD)",
                "graph_simulation_errors": final_errors + ["self.app was None, manual RAG simulation"]
            }


if __name__ == '__main__':
    print("Starting example usage of FinancialStatementExtractor with RAG-LangGraph outline...")

    # Mock vector_store_search_fn for example usage
    def mock_rag_search_fn(query: str, k: int) -> list[tuple[Document, float]]:
        print(f"  Mock RAG Search: Query='{query}', k={k}")
        if "income statement" in query.lower():
            return [(Document(page_content="This document discusses revenue and expenses, forming the income statement.", metadata={"source":"doc1_secA"}), 0.9)]
        elif "balance sheet" in query.lower():
            return [(Document(page_content="Assets include cash and inventory. Liabilities are also listed here on the balance sheet.", metadata={"source":"doc1_secB"}), 0.88)]
        # No mock for cash flow to test "not found"
        return []

    extractor = FinancialStatementExtractor()
    sample_parsed_data = {"text": "Full annual report text..."}

    print("\n--- Extracting financial statements (simulating RAG and LangGraph) ---")
    try:
        statements = extractor.extract_financial_statements(sample_parsed_data, mock_rag_search_fn)
        print("\nSuccessfully extracted (simulated RAG/LangGraph). Output:")
        for key, value in statements.items():
            if key == "graph_simulation_errors" and not value: continue
            print(f"  {key}: {str(value)[:200] + '...' if isinstance(value, str) and len(value) > 200 else value}")
    except Exception as e:
        print(f"Error during extraction: {e}")

    print("\n--- Testing with no RAG search function (should use fallback) ---")
    try:
        statements_no_rag = extractor.extract_financial_statements(sample_parsed_data, None) # type: ignore
        print("\nOutput with no RAG function (simulated RAG/LangGraph):")
        for key, value in statements_no_rag.items():
             if key == "graph_simulation_errors" and not value: continue
             print(f"  {key}: {str(value)[:200] + '...' if isinstance(value, str) and len(value) > 200 else value}")
        self.assertTrue("RAG search function not provided" in statements_no_rag["income_statement"]) # From unittest if run here
    except Exception as e:
        print(f"Error (expected for None search_fn if not handled gracefully by test): {e}")

    print("\nExample usage of FinancialStatementExtractor with RAG-LangGraph outline complete.")
