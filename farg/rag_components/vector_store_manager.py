import os
import shutil # For cleaning up directories if needed
# import faiss # Not directly used if using LangchainFAISS wrapper, but good to note dependency
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings # Updated import path
from langchain_community.vectorstores import FAISS as LangchainFAISS # Corrected variable name
from langchain_core.documents import Document
from langchain_core.documents import Document

class VectorStoreManager:
    def __init__(self, embedding_model_name='all-MiniLM-L6-v2', chunk_size=1000, chunk_overlap=200):
        """
        Initializes the VectorStoreManager.

        Args:
            embedding_model_name: Name of the HuggingFace model for embeddings.
            chunk_size: Size of chunks for text splitting.
            chunk_overlap: Overlap between chunks.
        """
        print(f"Initializing VectorStoreManager with embedding model: {embedding_model_name}")
        try:
            self.embedding_model = HuggingFaceEmbeddings(model_name=embedding_model_name)
        except Exception as e:
            print(f"Error initializing HuggingFaceEmbeddings model '{embedding_model_name}': {e}")
            print("Ensure 'sentence-transformers' is installed and the model name is correct.")
            print("Falling back to a default SentenceTransformer model if possible, or this will fail later.")
            # As a fallback or for environments without specific model pre-loading,
            # this might still fail if the library itself can't initialize.
            # Consider raising an error or having a "no-op" mode.
            raise  # Re-raise for now, as embeddings are critical

        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            add_start_index=True, # Useful for context/linking back to original doc
        )
        self.vector_store = None
        self.index_path = None # Will store the path to the folder where FAISS index is saved
        print("VectorStoreManager initialized.")

    def create_index_from_texts(self, texts: list[str], metadatas: list[dict] = None, index_path: str = "farg_faiss_index"):
        """
        Creates or updates a FAISS index from a list of texts.

        Args:
            texts: A list of raw text strings to index.
            metadatas: An optional list of dictionaries, where each dictionary is metadata
                       associated with the corresponding text in the `texts` list.
            index_path: The folder path to save/load the FAISS index.
        """
        if not texts:
            print("No texts provided to create or update index.")
            return

        print(f"Attempting to create/update index at path: {index_path}")

        langchain_documents = []
        for i, text_content in enumerate(texts):
            doc_metadata = (metadatas[i] if metadatas and i < len(metadatas) else {}).copy() # Use copy
            # Ensure basic source identification if not provided
            if "source" not in doc_metadata:
                doc_metadata["source"] = f"doc_id_{i}"
            langchain_documents.append(Document(page_content=text_content, metadata=doc_metadata))

        chunked_documents = self.text_splitter.split_documents(langchain_documents)
        print(f"Split {len(texts)} input text(s) into {len(chunked_documents)} chunks.")

        if not chunked_documents:
            print("No chunks were generated from the provided texts. Cannot create/update index.")
            return

        # If an index_path is provided and exists, try to load and merge.
        # Otherwise, create a new one.
        if self.vector_store is None and os.path.exists(index_path):
            try:
                print(f"Loading existing index from {index_path}...")
                self.load_index(index_path) # This sets self.vector_store and self.index_path
                print(f"Successfully loaded existing index. Adding {len(chunked_documents)} new chunked documents.")
                # Ensure vector_store is not None after load_index (it should be if load was successful)
                if self.vector_store:
                    self.vector_store.add_documents(chunked_documents) # Add new documents to existing store
                else: # Should not happen if load_index is correct
                    print("Error: vector_store is None after attempting to load. Creating new index instead.")
                    self.vector_store = LangchainFAISS.from_documents(chunked_documents, self.embedding_model)

            except Exception as e:
                print(f"Error loading existing index from '{index_path}': {e}. Creating a new one.")
                # If loading fails, overwrite by creating a new index
                # Potentially, consider a backup or different handling for production
                self.vector_store = LangchainFAISS.from_documents(chunked_documents, self.embedding_model)

        elif self.vector_store is None: # No existing in-memory store and no loadable path, create new.
            print(f"No existing index found at {index_path} or in memory. Creating a new index.")
            self.vector_store = LangchainFAISS.from_documents(chunked_documents, self.embedding_model)

        else: # self.vector_store already exists in memory (e.g., from previous calls without saving)
            print(f"Adding {len(chunked_documents)} new chunked documents to existing in-memory index.")
            self.vector_store.add_documents(chunked_documents)

        self.index_path = index_path # Set the intended save path
        if self.vector_store:
            self.save_index() # Save to the specified or updated index_path
        else:
            print("Vector store is None after processing. Cannot save index.")


    def search(self, query: str, k: int = 5) -> list[tuple[Document, float]]:
        """
        Performs similarity search in the vector store.

        Args:
            query: The query string.
            k: The number of top results to retrieve.

        Returns:
            A list of tuples, where each tuple contains a Document and its similarity score.
            Returns an empty list if the vector store is not initialized or search fails.
        """
        if self.vector_store:
            try:
                results = self.vector_store.similarity_search_with_score(query, k=k)
                print(f"Search for '{query[:50]}...' returned {len(results)} results.")
                return results
            except Exception as e:
                print(f"Error during similarity search: {e}")
                return []
        else:
            print("Vector store not initialized. Cannot perform search.")
            return []

    def save_index(self, index_path: str = None):
        """Saves the FAISS index to disk."""
        path_to_save = index_path or self.index_path
        if self.vector_store and path_to_save:
            try:
                self.vector_store.save_local(folder_path=path_to_save)
                print(f"FAISS index saved to {path_to_save}")
            except Exception as e:
                print(f"Error saving FAISS index to '{path_to_save}': {e}")
        else:
            print("No vector store instance or index path provided for saving.")

    def load_index(self, index_path: str):
        """
        Loads a FAISS index from disk.
        The `allow_dangerous_deserialization` flag is set to True for FAISS.load_local,
        which is necessary if the index was saved by one version of FAISS/Langchain
        and loaded by another, or if there are custom functions involved.
        Ensure you trust the source of the index file.
        """
        if not index_path or not isinstance(index_path, str):
            print("Error: Valid index_path (string) must be provided for loading.")
            self.vector_store = None
            return

        if os.path.exists(index_path):
            try:
                # Note: allow_dangerous_deserialization=True can be a security risk if loading untrusted index files.
                self.vector_store = LangchainFAISS.load_local(
                    folder_path=index_path,
                    embeddings=self.embedding_model,
                    allow_dangerous_deserialization=True
                )
                self.index_path = index_path
                print(f"FAISS index successfully loaded from {index_path}")
            except Exception as e:
                print(f"Error loading FAISS index from '{index_path}': {e}")
                print("Ensure the index was created with a compatible FAISS version and the correct embedding model.")
                self.vector_store = None
        else:
            print(f"Index folder not found at {index_path}. Cannot load index.")
            self.vector_store = None

    def clear_index_directory(self, index_path: str = None):
        """Utility to remove an index directory, e.g., for testing."""
        path_to_clear = index_path or self.index_path
        if path_to_clear and os.path.exists(path_to_clear):
            try:
                shutil.rmtree(path_to_clear)
                print(f"Successfully removed index directory: {path_to_clear}")
                if self.index_path == path_to_clear:
                    self.vector_store = None # Reset in-memory store if its physical backup was deleted
                    self.index_path = None
            except Exception as e:
                print(f"Error removing index directory '{path_to_clear}': {e}")
        else:
            print(f"Index directory '{path_to_clear}' not found or not specified, nothing to remove.")


if __name__ == '__main__':
    print("--- VectorStoreManager Self-Test/Example ---")

    # Example texts and metadatas
    texts_initial = [
        "The quick brown fox jumps over the lazy dog.",
        "Apple Inc. reported strong earnings in the last quarter.",
        "Artificial intelligence is transforming various industries."
    ]
    metadatas_initial = [
        {"source": "proverb1", "category": "general"},
        {"source": "news_apple_q4", "category": "finance"},
        {"source": "article_ai_impact", "category": "technology"}
    ]

    test_index_path = "temp_test_farg_faiss_index"
    manager = VectorStoreManager()

    # Clean up any previous test index
    if os.path.exists(test_index_path):
        print(f"Removing pre-existing test index at: {test_index_path}")
        shutil.rmtree(test_index_path)

    # 1. Create index from initial texts
    print("\n1. Creating index from initial texts...")
    manager.create_index_from_texts(texts_initial, metadatas_initial, index_path=test_index_path)
    if manager.vector_store:
        print(f"Index created. Index has {manager.vector_store.index.ntotal} vectors.") # type: ignore
    else:
        print("Failed to create vector store from initial texts.")
        # Exit if initial creation fails, as other steps depend on it
        exit()

    # 2. Search the index
    print("\n2. Searching the index...")
    query1 = "What did Apple report?"
    results1 = manager.search(query1, k=1)
    print(f"Search results for '{query1}':")
    for doc, score in results1:
        print(f"  - Score: {score:.4f}, Content: '{doc.page_content[:50]}...', Metadata: {doc.metadata}")

    query2 = "Information about AI"
    results2 = manager.search(query2, k=1)
    print(f"Search results for '{query2}':")
    for doc, score in results2:
        print(f"  - Score: {score:.4f}, Content: '{doc.page_content[:50]}...', Metadata: {doc.metadata}")

    # 3. Add more texts to the existing index
    print("\n3. Adding more texts to the existing index...")
    texts_additional = [
        "The lazy dog slept under the tree.",
        "Google announced new AI models."
    ]
    metadatas_additional = [
        {"source": "proverb2", "category": "general"},
        {"source": "news_google_ai", "category": "technology"}
    ]
    # This should load the existing index from test_index_path and add to it
    manager.create_index_from_texts(texts_additional, metadatas_additional, index_path=test_index_path)
    if manager.vector_store:
         print(f"Index updated. Index now has {manager.vector_store.index.ntotal} vectors.") # type: ignore
    else:
        print("Failed to update vector store with additional texts.")


    # 4. Search again to see if new texts are found
    print("\n4. Searching again...")
    query3 = "What did Google announce?"
    results3 = manager.search(query3, k=1)
    print(f"Search results for '{query3}':")
    for doc, score in results3:
        print(f"  - Score: {score:.4f}, Content: '{doc.page_content[:50]}...', Metadata: {doc.metadata}")

    # 5. Test loading the index from disk into a new manager instance
    print("\n5. Testing loading index into a new manager instance...")
    manager_loaded = VectorStoreManager()
    manager_loaded.load_index(test_index_path)
    if manager_loaded.vector_store:
        print(f"Loaded index into new manager. Index has {manager_loaded.vector_store.index.ntotal} vectors.") # type: ignore
        query4 = "Tell me about the lazy dog"
        results4 = manager_loaded.search(query4, k=2)
        print(f"Search results for '{query4}' using loaded index:")
        for doc, score in results4:
            print(f"  - Score: {score:.4f}, Content: '{doc.page_content[:50]}...', Metadata: {doc.metadata}")
    else:
        print("Failed to load index into new manager instance.")

    # Clean up
    print("\n--- Self-Test Complete ---")
    print(f"Index files are in '{test_index_path}'. Remove manually if desired or use manager.clear_index_directory().")
    # Example cleanup:
    # manager.clear_index_directory(test_index_path)
    # Or, to be safe in a script, always remove if it was created by the script:
    # if os.path.exists(test_index_path):
    #     shutil.rmtree(test_index_path)
    #     print(f"Cleaned up test index directory: {test_index_path}")
