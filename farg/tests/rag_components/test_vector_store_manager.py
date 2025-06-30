import unittest
import os
import shutil
from langchain_core.documents import Document

# Ensure farg.rag_components.vector_store_manager is discoverable
try:
    from farg.rag_components.vector_store_manager import VectorStoreManager
except ImportError:
    import sys
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
    from farg.rag_components.vector_store_manager import VectorStoreManager

class TestVectorStoreManager(unittest.TestCase):
    """
    Unit tests for the VectorStoreManager class.
    These tests might download embedding models on first run if not cached.
    """
    TEST_INDEX_DIR = "temp_test_faiss_index_vsm" # Main directory for this test class
    INDEX_PATH_A = os.path.join(TEST_INDEX_DIR, "indexA")
    INDEX_PATH_B = os.path.join(TEST_INDEX_DIR, "indexB")


    @classmethod
    def setUpClass(cls):
        """Create a temporary directory for FAISS indexes if it doesn't exist."""
        if os.path.exists(cls.TEST_INDEX_DIR): # Clean up from previous runs
            shutil.rmtree(cls.TEST_INDEX_DIR)
        os.makedirs(cls.TEST_INDEX_DIR, exist_ok=True)


    @classmethod
    def tearDownClass(cls):
        """Remove the temporary directory after all tests."""
        if os.path.exists(cls.TEST_INDEX_DIR):
            shutil.rmtree(cls.TEST_INDEX_DIR)

    def setUp(self):
        """Initialize a new VectorStoreManager for each test."""
        self.manager = VectorStoreManager(embedding_model_name='all-MiniLM-L6-v2', chunk_size=100, chunk_overlap=10)
        # Clean specific index paths before each test if they are created by name
        self.manager.clear_index_directory(self.INDEX_PATH_A)
        self.manager.clear_index_directory(self.INDEX_PATH_B)


    def test_01_initialization(self):
        """Test VectorStoreManager initialization."""
        self.assertIsNotNone(self.manager.embedding_model, "Embedding model should be initialized.")
        self.assertIsNotNone(self.manager.text_splitter, "Text splitter should be initialized.")
        self.assertIsNone(self.manager.vector_store, "Vector store should be None initially.")

    def test_02_create_index_from_texts_new(self):
        """Test creating a new FAISS index from texts."""
        texts = ["This is document one.", "This is document two about AI."]
        metadatas = [{"source": "doc1"}, {"source": "doc2"}]

        self.manager.create_index_from_texts(texts, metadatas, index_path=self.INDEX_PATH_A)
        self.assertIsNotNone(self.manager.vector_store, "Vector store should be created.")
        self.assertTrue(os.path.exists(self.INDEX_PATH_A), f"Index directory {self.INDEX_PATH_A} should be created.")
        self.assertTrue(os.path.exists(os.path.join(self.INDEX_PATH_A, "index.faiss")), "index.faiss file should exist.")
        self.assertTrue(os.path.exists(os.path.join(self.INDEX_PATH_A, "index.pkl")), "index.pkl file should exist.")
        self.assertGreater(self.manager.vector_store.index.ntotal, 0, "FAISS index should contain vectors.") # type: ignore

    def test_03_search_index(self):
        """Test searching the created index."""
        texts = ["Apples are fruits.", "Bananas are also fruits.", "Oranges are citrus fruits."]
        metadatas = [{"source": "apple_doc"}, {"source": "banana_doc"}, {"source": "orange_doc"}]
        self.manager.create_index_from_texts(texts, metadatas, index_path=self.INDEX_PATH_A)

        query = "Information about apples"
        results = self.manager.search(query, k=1)
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 1)
        doc, score = results[0]
        self.assertIsInstance(doc, Document)
        self.assertIn("apple", doc.page_content.lower())
        self.assertEqual(doc.metadata["source"], "apple_doc")

    def test_04_save_and_load_index(self):
        """Test saving an index and then loading it into a new manager."""
        texts = ["Testing save and load functionality."]
        self.manager.create_index_from_texts(texts, index_path=self.INDEX_PATH_A)
        self.manager.save_index() # Save to self.INDEX_PATH_A

        new_manager = VectorStoreManager(embedding_model_name='all-MiniLM-L6-v2')
        new_manager.load_index(self.INDEX_PATH_A)
        self.assertIsNotNone(new_manager.vector_store, "Vector store should be loaded in new manager.")
        self.assertGreater(new_manager.vector_store.index.ntotal, 0, "Loaded FAISS index should contain vectors.") # type: ignore

        query = "functionality"
        results = new_manager.search(query, k=1)
        self.assertEqual(len(results), 1)
        self.assertIn("functionality", results[0][0].page_content)

    def test_05_add_to_existing_index_in_memory_then_save(self):
        """Test adding texts to an index already in memory and then saving."""
        texts1 = ["Document set one, first part."]
        self.manager.create_index_from_texts(texts1, index_path=self.INDEX_PATH_A)
        initial_vector_count = self.manager.vector_store.index.ntotal # type: ignore

        texts2 = ["Second part of document set one."]
        # This call should use the in-memory self.vector_store and add to it
        # The index_path in create_index_from_texts determines where it *would* load from if empty,
        # and where it saves to.
        self.manager.create_index_from_texts(texts2, index_path=self.INDEX_PATH_A)

        self.assertGreater(self.manager.vector_store.index.ntotal, initial_vector_count, "Vector count should increase.") # type: ignore
        self.assertTrue(os.path.exists(os.path.join(self.INDEX_PATH_A, "index.faiss")), "Index should be re-saved.")

    def test_06_add_to_existing_index_from_disk(self):
        """Test loading an index from disk and adding new texts."""
        texts1 = ["Persist this document first."]
        metadatas1 = [{"id": "doc1_orig"}]
        self.manager.create_index_from_texts(texts1, metadatas1, index_path=self.INDEX_PATH_A)
        self.manager.save_index() # Ensure it's saved

        # Create a new manager to simulate loading from disk then adding
        manager2 = VectorStoreManager(embedding_model_name='all-MiniLM-L6-v2')

        texts2 = ["Add this new document to the loaded index."]
        metadatas2 = [{"id": "doc2_new"}]
        # This create_index call should load INDEX_PATH_A and add texts2
        manager2.create_index_from_texts(texts2, metadatas2, index_path=self.INDEX_PATH_A)

        self.assertIsNotNone(manager2.vector_store)
        self.assertEqual(manager2.vector_store.index.ntotal, 2 * len(self.manager.text_splitter.split_texts(texts1+texts2))/2) # Approximation, depends on chunking

        # Verify both old and new documents can be found
        res_old = manager2.search("Persist this", k=1)
        self.assertTrue(any("doc1_orig" == r[0].metadata.get("id") for r in res_old))

        res_new = manager2.search("new document", k=1)
        self.assertTrue(any("doc2_new" == r[0].metadata.get("id") for r in res_new))


    def test_07_no_texts_provided(self):
        """Test behavior when no texts are provided for index creation."""
        self.manager.create_index_from_texts([], index_path=self.INDEX_PATH_A)
        self.assertIsNone(self.manager.vector_store, "Vector store should remain None if no texts are provided.")
        self.assertFalse(os.path.exists(self.INDEX_PATH_A), "Index directory should not be created for no texts.")

    def test_08_search_empty_or_uninitialized_store(self):
        """Test search on an uninitialized or empty store."""
        results = self.manager.search("query")
        self.assertEqual(results, []) # Should return empty list

        # Initialize with no texts
        self.manager.create_index_from_texts([], index_path=self.INDEX_PATH_A)
        results_after_empty_create = self.manager.search("query")
        self.assertEqual(results_after_empty_create, [])


    def test_09_load_non_existent_index(self):
        """Test loading a non-existent index path."""
        non_existent_path = os.path.join(self.TEST_INDEX_DIR, "non_existent_idx")
        self.manager.load_index(non_existent_path)
        self.assertIsNone(self.manager.vector_store, "Vector store should be None after failed load.")

    def test_10_clear_index_directory(self):
        """Test clearing an index directory."""
        texts = ["Sample text for clearing test."]
        self.manager.create_index_from_texts(texts, index_path=self.INDEX_PATH_A)
        self.assertTrue(os.path.exists(self.INDEX_PATH_A))

        self.manager.clear_index_directory(self.INDEX_PATH_A)
        self.assertFalse(os.path.exists(self.INDEX_PATH_A), "Index directory should be removed.")
        self.assertIsNone(self.manager.vector_store, "In-memory vector store should be reset if its path was cleared.")


if __name__ == '__main__':
    unittest.main()
