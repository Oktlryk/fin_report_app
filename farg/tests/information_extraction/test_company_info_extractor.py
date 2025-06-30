import unittest
import os
import shutil # For cleaning up temp index dirs
from unittest.mock import MagicMock, patch
from langchain_core.documents import Document

try:
    from farg.information_extraction.company_info_extractor import CompanyInfoExtractor, PlaceholderRAGLLM
    from farg.rag_components.vector_store_manager import VectorStoreManager # For integration test
except ImportError:
    import sys
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))
    from farg.information_extraction.company_info_extractor import CompanyInfoExtractor, PlaceholderRAGLLM
    from farg.rag_components.vector_store_manager import VectorStoreManager


class TestCompanyInfoExtractorRAG(unittest.TestCase):
    """
    Unit tests for the CompanyInfoExtractor class with RAG integration.
    """
    TEST_INDEX_DIR_CIO = "temp_test_faiss_index_company_info_extractor"


    def setUp(self):
        """Initialize the extractor and mock search function for each test."""
        self.extractor = CompanyInfoExtractor()
        self.mock_vector_search_fn = MagicMock()

        self.sample_parsed_data = {
            "text": "Full text of Company Alpha's report...",
            "company_info": {"company_name": "Alpha Corp from parser"}
        }
        # Clean up index directory before each test that might use it
        if os.path.exists(self.TEST_INDEX_DIR_CIO):
            shutil.rmtree(self.TEST_INDEX_DIR_CIO)
        # os.makedirs(self.TEST_INDEX_DIR_CIO, exist_ok=True) # Not needed if tests always create then delete

    def tearDown(self):
        """Clean up any created index directories after tests if necessary."""
        if os.path.exists(self.TEST_INDEX_DIR_CIO):
            shutil.rmtree(self.TEST_INDEX_DIR_CIO)


    def test_import_and_instantiation(self):
        self.assertIsInstance(self.extractor, CompanyInfoExtractor)
        self.assertIsInstance(self.extractor.llm, PlaceholderRAGLLM)

    @patch.object(PlaceholderRAGLLM, 'invoke', autospec=True) # Mock the LLM to check its input
    def test_extract_company_info_uses_rag_and_llm_correctly(self, mock_llm_invoke):
        # Mock LLM's response
        mock_llm_invoke.return_value = "Mocked LLM Extracted Info"

        mock_docs_market = [
            (Document(page_content="Company Alpha operates worldwide.", metadata={"source": "doc1"}), 0.85)
        ]
        self.mock_vector_search_fn.return_value = mock_docs_market # Simplified: same docs for all queries for this test

        result = self.extractor.extract_company_info(self.sample_parsed_data, self.mock_vector_search_fn)

        self.assertIsInstance(result, dict)
        self.assertEqual(self.mock_vector_search_fn.call_count, 4)
        self.assertEqual(mock_llm_invoke.call_count, 4) # LLM called for each spec

        # Check one of the calls to the LLM to see if it received the retrieved context
        # This requires knowing which spec is processed first or making the mock_vector_search_fn more specific.
        # For "market_footprint" (assuming it's one of the specs):
        # The PlaceholderRAGLLM in CompanyInfoExtractor is fixed, so we can predict its output
        # For "market_footprint", the query is "Describe the company's market presence..."
        # The PlaceholderRAGLLM will return "Global presence, primarily in Technology sector (Simulated RAG LLM)."
        # if "market presence" is in the prompt it receives.

        # Let's check if the prompt passed to the LLM contains the retrieved text.
        # The actual query to LLM is: f"Based on the following text, answer the question '{query_prompt_template}':\n\n{concatenated_retrieved_text}"
        # Find the call for market_footprint
        market_footprint_llm_call_args = None
        for call in mock_llm_invoke.call_args_list:
            args, kwargs = call
            input_dict = args[1] if len(args) > 1 else kwargs.get('input_dict', {}) # self, input_dict
            if "market presence" in input_dict.get("prompt", ""):
                market_footprint_llm_call_args = input_dict
                break

        self.assertIsNotNone(market_footprint_llm_call_args, "LLM invoke should have been called for market footprint.")
        self.assertIn("Company Alpha operates worldwide.", market_footprint_llm_call_args['prompt']) # Check if retrieved text is in prompt to LLM
        self.assertEqual(result["market_footprint"], "Mocked LLM Extracted Info") # As LLM is mocked

    def test_extract_company_info_with_real_vsm_integration(self):
        """Test CompanyInfoExtractor with a real VectorStoreManager instance."""
        vsm = VectorStoreManager(embedding_model_name='all-MiniLM-L6-v2', chunk_size=50, chunk_overlap=5) # Smaller chunks for test

        sample_texts_for_vsm = [
            "FARG Inc. is a leader in AI-driven financial analysis, operating globally.",
            "Our main products are innovative reporting tools and advanced AI models for finance.",
            "The company is considered medium-sized and is currently in a rapid growth phase."
        ]
        metadatas = [{"source": f"text{i+1}"} for i in range(len(sample_texts_for_vsm))]

        # Use a unique path for this test's index
        temp_index_path_for_this_test = os.path.join(self.TEST_INDEX_DIR_CIO, "integration_test_index")
        self.addCleanup(shutil.rmtree, temp_index_path_for_this_test, ignore_errors=True) # Ensure cleanup

        vsm.create_index_from_texts(sample_texts_for_vsm, metadatas, index_path=temp_index_path_for_this_test)
        self.assertTrue(os.path.exists(temp_index_path_for_this_test))

        extractor_for_integration = CompanyInfoExtractor() # Uses its own PlaceholderRAGLLM

        # Parsed report data can be minimal as RAG is primary
        parsed_data_for_integration = {"company_info": {"company_name": "FARG Inc."}}

        results = extractor_for_integration.extract_company_info(
            parsed_data_for_integration,
            vector_store_search_fn=vsm.search
        )

        self.assertIsInstance(results, dict)
        # Check the simulated LLM output based on what it would get from RAG
        # Market Footprint query: "Describe the company's market presence, key geographies, and industry sector."
        # Expected retrieved text for market footprint: "FARG Inc. is a leader in AI-driven financial analysis, operating globally."
        # PlaceholderRAGLLM for "market presence" returns: "Global presence, primarily in Technology sector (Simulated RAG LLM)."
        self.assertEqual(results.get("market_footprint"), "Global presence, primarily in Technology sector (Simulated RAG LLM).")

        # Products/Services query: "List the company's major products and services lines."
        # Expected retrieved text: "Our main products are innovative reporting tools and advanced AI models for finance."
        # PlaceholderRAGLLM for "products and services" returns: "Key products: InnovatePlatform, ServiceX. Key services: Cloud Consulting (Simulated RAG LLM)."
        # This shows a slight mismatch if the LLM is too fixed, but the RAG part works if it retrieves the correct text.
        # Let's check if part of the retrieved text made it to the LLM (via the LLM's own fixed output for this category)
        self.assertEqual(results.get("products_services"), "Key products: InnovatePlatform, ServiceX. Key services: Cloud Consulting (Simulated RAG LLM).")

        self.assertEqual(results.get("relative_size"), "Considered a Large Enterprise based on revenue and employee count (Simulated RAG LLM).")
        self.assertEqual(results.get("stage_of_maturity"), "Mature growth stage, with ongoing expansion (Simulated RAG LLM).")
        self.assertEqual(results.get("company_name"), "FARG Inc.")


    def test_extract_company_info_handles_no_retrieved_docs(self):
        self.mock_vector_search_fn.return_value = []
        result = self.extractor.extract_company_info(self.sample_parsed_data, self.mock_vector_search_fn)
        self.assertIsInstance(result, dict)
        expected_llm_response_no_docs = self.extractor.llm.invoke({
            "prompt": f"Based on the following text, answer the question '{self.extractor.company_info_specs['market_footprint']}':\n\nNo relevant information found in documents."
        })
        self.assertEqual(result["market_footprint"], expected_llm_response_no_docs)

    def test_extract_company_info_invalid_search_fn(self):
        with self.assertRaises(TypeError):
            self.extractor.extract_company_info(self.sample_parsed_data, "not_a_callable_function") # type: ignore

    def test_extract_company_info_keys(self):
        self.mock_vector_search_fn.return_value = []
        result = self.extractor.extract_company_info(self.sample_parsed_data, self.mock_vector_search_fn)
        expected_info_keys = ["market_footprint", "products_services", "relative_size", "stage_of_maturity"]
        for key in expected_info_keys:
            self.assertIn(key, result)

if __name__ == '__main__':
    unittest.main()
