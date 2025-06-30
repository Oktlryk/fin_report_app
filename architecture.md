# FARG System Architecture

## 1. Overview

The Financial Analysis Report Generator (FARG) is a Python application designed to automate the process of analyzing corporate annual reports and other financial documents. Its primary goal is to ingest these documents, extract key information, perform financial and qualitative analyses, generate actionable insights, and compile comprehensive reports to aid in financial decision-making.

## 2. Core Architecture Components

FARG's architecture is modular, organized into several Python packages/directories, each with distinct responsibilities:

-   **`farg.agent` (`FARGAgent`):**
    *   The central orchestrator of the entire workflow. It initializes and coordinates all other components, manages data flow between them, and handles RAG context (active vector stores).

-   **`farg.data_ingestion`:**
    *   Responsible for loading and parsing input documents.
    *   `AnnualReportLoader`: Loads raw text content from files (e.g., TXT, PDF placeholders).
    *   `ReportParser`: Processes raw text, currently using a LangChain-based chain with a placeholder LLM to extract initial structured information or summaries.
    *   `ReportStorage`: (Conceptual) Intended for storing processed reports or intermediate data, though not heavily used by the agent in the current simulation.

-   **`farg.rag_components`:**
    *   Manages the Retrieval Augmented Generation (RAG) infrastructure.
    *   `VectorStoreManager`: Handles text splitting, embedding generation (using Sentence Transformers), FAISS vector store creation, persistence (saving/loading), and similarity searches.

-   **`farg.information_extraction`:**
    *   Focuses on extracting specific structured and qualitative data from parsed reports, heavily assisted by RAG.
    *   `CompanyInfoExtractor`: Extracts qualitative details like market footprint, products/services, company size, and maturity using RAG.
    *   `FinancialStatementExtractor`: Aims to identify and extract financial statements (Income Statement, Balance Sheet, Cash Flow) using a RAG-enhanced LangGraph workflow (currently simulated).
    *   `KPIExtractor`: Extracts Key Performance Indicators, combining direct data from (placeholder) financial statements with contextual information retrieved via RAG for certain KPIs.

-   **`farg.data_analysis_processing`:**
    *   Performs various financial and competitive analyses on the extracted information.
    *   `FinancialAnalysisModule`: Conducts ratio analysis, trend analysis, and industry benchmarking. Its LangGraph-outlined workflow uses RAG to fetch contextual details for quantitative findings.
    *   `CompetitorAnalysisModule`: Performs SWOT analysis and compares the primary company's performance against competitors, using data collated by the agent.

-   **`farg.insight_generation_recommendation`:**
    *   Synthesizes analysis results into actionable insights and generates recommendations.
    *   `InsightGenerator`: Produces insights based on financial analysis, SWOT, and competitor comparisons, optionally using RAG to deepen or validate these insights against source documents.
    *   `RecommendationEngine`: Generates strategic and operational recommendations based on the generated insights and identified issues.

-   **`farg.report_generation`:**
    *   Responsible for compiling the final report.
    *   `ReportTemplateEngine`: Loads and populates report templates.
    *   `ReportGeneratorComponents`: Includes helpers like `CompanyProfileGenerator`, `FinancialPerformanceComparator`, `StrategicOperationalIssueIdentifier` that prepare specific data sections for the report.
    *   `ReportGenerator`: (Role largely taken over by `FARGAgent` for data compilation) Originally intended to orchestrate report assembly; now, its sub-components are used by the agent, and the template engine is called by the agent.

-   **`farg.ui`:**
    *   Provides the user interface for the application using Gradio.
    *   `app.py`: Defines the Gradio interface for file uploads, selection of analysis options, and display of the generated report.

## 3. Workflow Orchestration

The `FARGAgent` is central to the FARG workflow, managing the sequence of operations and data flow:

1.  **UI Interaction:** The user uploads company (and optionally competitor) annual reports and selects analysis options via the Gradio UI (`farg.ui.app`).
2.  **Agent Invocation:** The UI triggers the `FARGAgent.run()` method.
3.  **Data Ingestion & RAG Indexing (per company):**
    *   `AnnualReportLoader` loads the raw text from report files.
    *   `FARGAgent` passes these texts to `VectorStoreManager`.
    *   `VectorStoreManager` splits the texts into chunks, generates embeddings using a sentence transformer model, and creates/updates a company-specific FAISS vector store. This index is persisted to disk.
    *   The `ReportParser` (with a placeholder LangChain LLM chain) processes the main report content to produce initial parsed data (e.g., summaries or key sections).
4.  **Information Extraction (RAG-assisted, per company):**
    *   The `FARGAgent` ensures the correct company's FAISS index is active in `VectorStoreManager`.
    *   `CompanyInfoExtractor`, `FinancialStatementExtractor` (simulated LangGraph with RAG), and `KPIExtractor` are called.
    *   These extractors formulate queries, use the `vector_store_manager.search` function to retrieve relevant text chunks from the active index, and then process these chunks (using placeholder LLMs) to extract the required information.
5.  **Data Analysis & Processing (RAG-assisted, per company):**
    *   `FARGAgent` ensures the correct company's FAISS index is active.
    *   `FinancialAnalysisModule.run_full_analysis_graph()` (simulated LangGraph) is executed. Its internal nodes perform placeholder calculations and then use RAG (via the passed search function) to fetch contextual explanations for financial figures or trends.
    *   If competitor data is available, similar analysis is performed for the competitor, using its own RAG index.
    *   `CompetitorAnalysisModule` performs SWOT and comparison (currently without direct RAG calls, but uses RAG-enhanced inputs).
6.  **Insight Generation (RAG-assisted):**
    *   `FARGAgent` ensures the primary company's FAISS index is active.
    *   `InsightGenerator` takes the analysis results and SWOT. It can formulate queries based on these results to find supporting or contradictory evidence in the documents via RAG, enriching the generated insights.
7.  **Recommendation Generation:**
    *   `StrategicOperationalIssueIdentifier` (called by the agent) helps define issues from the analyses.
    *   `RecommendationEngine` uses the insights and identified issues to generate recommendations (currently placeholder logic).
8.  **Report Compilation & Generation:**
    *   `FARGAgent` gathers all processed data (extracted info, analyses, insights, recommendations).
    *   It uses helper components like `CompanyProfileGenerator` and `FinancialPerformanceComparator` to structure data for specific report sections.
    *   This compiled data is then used with `ReportTemplateEngine` to populate a predefined template.
9.  **Display to UI:** The final report string is returned to the Gradio UI for display.

## 4. Retrieval Augmented Generation (RAG) Sub-system

### Purpose
RAG is integrated into FARG to enhance the accuracy, depth, and verifiability of information extraction and analysis. By grounding generated content and analysis in the specific text of the provided annual reports, RAG aims to:
-   Reduce hallucinations and improve factual correctness.
-   Provide context-specific details for financial figures and trends.
-   Enable extraction of information that might be missed by purely pattern-based or non-contextual NLP methods.

### Key Components
-   **`VectorStoreManager` (`farg.rag_components.vector_store_manager`):**
    *   **Embeddings:** Uses `HuggingFaceEmbeddings` with a sentence transformer model (default: 'all-MiniLM-L6-v2') to convert text chunks into dense vector representations.
    *   **Text Splitting:** Employs `RecursiveCharacterTextSplitter` from Langchain to break down large documents into smaller, manageable chunks suitable for embedding and retrieval.
    *   **FAISS Vector Store:** Utilizes `langchain_community.vectorstores.FAISS` as the vector database. It creates, saves, loads, and manages FAISS indices, which store the embeddings and allow for efficient similarity searches. Each company's reports are typically indexed into a separate FAISS store.

### Data Flow (RAG Indexing)
1.  User uploads one or more annual reports for a company.
2.  `AnnualReportLoader` reads the textual content of these reports.
3.  `FARGAgent` collects all text content for a specific company.
4.  `FARGAgent` invokes `vector_store_manager.create_index_from_texts()`, passing the collected texts and associated metadata (e.g., source filename, company ID).
5.  Inside `VectorStoreManager`:
    *   Texts are converted into Langchain `Document` objects.
    *   `RecursiveCharacterTextSplitter` divides these `Document` objects into smaller chunks.
    *   `HuggingFaceEmbeddings` generates vector embeddings for each chunk.
    *   A FAISS index is built from these embeddings and their corresponding chunks (and metadata).
    *   The index is saved to disk in a company-specific location (e.g., `farg_indices/faiss_index_companya/`).

### Data Flow (RAG Retrieval & Usage - Hybrid Approach)
Once indices are created, various components use RAG as follows:

-   **Information Extraction (`CompanyInfoExtractor`, `FinancialStatementExtractor`, `KPIExtractor`):**
    1.  These extractors determine what specific piece of information they need (e.g., "company's market footprint", "details of revenue growth drivers").
    2.  They formulate a natural language query for this information.
    3.  They call the `search` function provided by `FARGAgent` (which is `vector_store_manager.search`, operating on the currently active company's index). This function returns a list of relevant document chunks (typically `Document` objects with `page_content` and `metadata`) and their similarity scores.
    4.  The `page_content` from the top `k` retrieved chunks is concatenated.
    5.  This concatenated text is then passed to a **placeholder LLM** within the extractor. The placeholder LLM simulates a more sophisticated language model that would perform the final extraction or summarization based on the retrieved context and the original query/prompt.

-   **Financial Analysis (`FinancialAnalysisModule` - within its LangGraph outline):**
    1.  Initial quantitative analysis (e.g., calculating a ratio, identifying a trend - currently placeholders) is performed.
    2.  To add qualitative depth, specific queries are formulated based on these quantitative results (e.g., "What factors influenced the calculated net profit margin of X%?", "What are the stated reasons for the observed revenue trend?").
    3.  RAG is used (via the `vector_store_search_fn` in the graph state) to find relevant text from the reports.
    4.  A **placeholder LLM** (`PlaceholderAnalysisRAGLLM`) processes this retrieved text to generate qualitative explanations or contextual summaries, which are then associated with the quantitative results (e.g., `ratio_analysis_results.net_profit_margin_context = "RAG-derived explanation..."`).

-   **Insight Generation (`InsightGenerator`):**
    1.  Initial insights might be derived from structured analysis results or SWOT items.
    2.  To validate, elaborate, or discover new insights, `InsightGenerator` can formulate queries based on these initial points (e.g., if a SWOT opportunity is "expansion into new markets," a query might be "What does the report say about plans or capabilities for market expansion?").
    3.  RAG retrieves relevant sections.
    4.  A **placeholder LLM** (`PlaceholderInsightRAGLLM`) processes the retrieved text to generate or refine an insight string.

### Placeholder LLMs
Currently, all interactions with Language Models (both for initial parsing in `ReportParser` and for processing RAG-retrieved context in various extractors/analyzers) are simulated by **placeholder LLM classes**. These classes mimic the `invoke` method of a LangChain LLM but return predefined or simply formatted strings based on the input, rather than making actual API calls to models like GPT. This allows for testing the RAG pipeline structure and data flow without incurring costs or requiring API keys. Future development will replace these placeholders with actual LangChain LLM chains and models.

## 5. User Interface (`farg.ui.app`)

-   FARG uses a Gradio-based web interface for user interaction.
-   Key features:
    *   File upload components for company annual reports and (optional) competitor reports. Supports multiple file uploads.
    *   Checkbox group for users to select desired analysis options to be included in the final report (e.g., "Financial Performance Comparison", "SWOT Analysis", "Recommendations").
    *   A textbox output area to display the generated report.
-   The UI calls the `FARGAgent` to orchestrate the backend processing when the user submits the inputs.

## 6. Future Development

-   **Full LangChain & LangGraph Integration:** Replace all placeholder LLMs with actual LangChain runnable chains and LLM calls. Fully compile and utilize the outlined LangGraph workflows in `FinancialStatementExtractor` and `FinancialAnalysisModule`.
-   **Advanced NLP & Extraction:** Implement sophisticated NLP techniques for more accurate data extraction from text and tables within reports.
-   **Robust Financial Modeling:** Enhance `FinancialAnalysisModule` with comprehensive financial ratio calculations, trend analysis methods (e.g., CAGR, regression), and more detailed benchmarking.
-   **Sophisticated Insight & Recommendation Logic:** Develop more intelligent algorithms for generating deeper insights and context-aware recommendations.
-   **Error Handling & Logging:** Implement comprehensive error handling, logging, and reporting throughout the application.
-   **Data Persistence & Management:** Improve management of FAISS indices (e.g., naming, versioning, deletion). Potentially integrate a database for storing extracted data, analysis results, and reports.
-   **Configuration Management:** Allow users or administrators to configure LLM choices, API keys, analysis parameters, and report templates.
-   **UI Enhancements:** Improve the Gradio UI with more interactive elements, visualizations (charts, graphs), and better report formatting.
-   **Support for More Document Types:** Extend data ingestion to handle other financial document formats beyond plain text and basic PDF structure.
-   **Testing Coverage:** Increase unit, integration, and end-to-end test coverage.
-   **Scalability & Performance:** Optimize components for handling larger documents and concurrent requests if deployed as a service.
