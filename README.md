# Financial Analysis Report Generator (FARG)

FARG is a Python application designed to analyze company Annual Reports and other financial documents to automate the generation of financial analysis reports, including insights and recommendations.

## Current Status

This project is in its initial development phase (v0.2). It provides a foundational framework for:
- Ingesting and processing annual reports (PDFs, text files).
- Indexing report content for Retrieval Augmented Generation (RAG).
- Extracting key information (company details, financial statement data, KPIs) using a RAG-assisted approach (currently simulated with placeholder LLMs).
- Performing financial analysis (ratios, trends, benchmarking) with RAG-assisted contextualization (currently simulated).
- Generating qualitative insights, optionally enhanced by RAG.
- Compiling a structured report from the processed information.
- A Gradio-based User Interface for uploading reports, selecting analysis options, and viewing the generated report.

LangChain is used for basic text processing and RAG components. LangGraph workflows are outlined for some modules but are currently simulated. Advanced NLP and LLM-based understanding are represented by placeholder components.

## Features

FARG aims to provide a comprehensive suite for financial document analysis:

-   **Data Ingestion:**
    *   Upload multiple annual reports (PDF or TXT format) for a primary company.
    *   Optionally, upload reports for a competitor company for comparative analysis.

-   **Retrieval Augmented Generation (RAG) Powered Analysis:**
    FARG leverages a RAG approach to ground its analysis in the content of the provided documents. This is designed to improve accuracy and provide context-specific information.
    *   **Indexing:** When reports are uploaded, their textual content is extracted, split into manageable chunks, and then converted into vector embeddings using a sentence transformer model (`all-MiniLM-L6-v2`). These embeddings are stored in a company-specific FAISS vector store, creating a searchable index for each company's documents.
    *   **RAG-Assisted Information Extraction:** Components like `CompanyInfoExtractor`, `FinancialStatementExtractor`, and `KPIExtractor` formulate queries for specific data points. These queries are used to search the relevant company's FAISS index to retrieve the most relevant text chunks. Placeholder LLMs then simulate processing these chunks to extract structured information.
    *   **RAG-Contextualized Financial Analysis:** The `FinancialAnalysisModule` (LangGraph outlined) uses RAG to fetch textual context from the reports that can explain or support quantitative findings (e.g., reasons behind a specific financial ratio's value or an observed trend). This retrieved context is then (simulatedly) processed by a placeholder LLM.
    *   **RAG-Enhanced Insight Generation:** The `InsightGenerator` can use RAG to find supporting evidence or further details related to initial analytical findings or SWOT items, leading to more grounded and comprehensive insights (currently simulated).

-   **Automated Report Generation:**
    *   Generates a structured report based on the selected analyses.
    *   The report content is populated using a template engine, with different sections for company profiles, financial analysis, SWOT, insights, and recommendations. (Currently, many analytical outputs are placeholders).

-   **User Interface:**
    *   A simple web-based UI built with Gradio allows users to upload documents, choose analysis types, and view the generated report.

-   **Modular Design:**
    *   Built with distinct components for each phase of the process, aiming for maintainability and extensibility.

*Note: The core NLP/LLM processing for understanding and extracting information from text (especially RAG-retrieved chunks) is currently simulated by placeholder Python classes. Full integration with advanced LangChain LLMs and compiled LangGraph workflows is part of future development.*

## Setup

1.  **Prerequisites:**
    *   Python 3.9 or higher is recommended.
    *   `pip` (Python package installer).

2.  **Clone the repository:**
    ```bash
    git clone <repository_url> # Replace <repository_url> with the actual URL
    cd farg-financial-analysis # Or your chosen directory name for the project
    ```

3.  **Create and activate a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Linux/macOS
    # OR
    # venv\Scripts\activate  # On Windows
    ```
    This keeps project dependencies isolated.

4.  **Install dependencies:**
    Navigate to the project root directory (where `requirements.txt` is located) and run:
    ```bash
    pip install -r requirements.txt
    ```
    This will install Gradio, LangChain components, FAISS, sentence transformers, and other necessary libraries. The first run involving sentence transformers might download the embedding model ('all-MiniLM-L6-v2'), which requires an internet connection.

## Running the Application

To start the FARG application, ensure your virtual environment is activated and you are in the project's root directory. Then run:

```bash
python main.py
```

This will launch the Gradio web interface. Typically, it will be available at:
`http://127.0.0.1:7860`

Open this URL in your web browser to access the application. You can then:
1.  Upload annual report files for the primary company.
2.  Optionally, upload reports for a competitor company.
3.  Select the analysis options you want to include in the report.
4.  Click "Submit" (or the equivalent button in Gradio) to generate the report.

## Project Structure

-   `main.py`: The main entry point to launch the Gradio UI application.
-   `architecture.md`: Provides an overview of the system architecture and workflow.
-   `requirements.txt`: Lists all Python dependencies for the project.
-   `README.md`: This file.
-   `farg/`: Contains the core source code for the FARG application.
    -   `__init__.py`: Marks `farg` as a Python package.
    -   `agent.py`: The `FARGAgent` class that orchestrates the entire analysis workflow.
    -   `data_ingestion/`: Modules for loading (`annual_report_loader.py`), parsing (`report_parser.py`), and (conceptually) storing reports.
    -   `rag_components/`: Modules related to Retrieval Augmented Generation, including `vector_store_manager.py`.
    -   `information_extraction/`: Modules for extracting specific types of information (company info, financial statements, KPIs) using RAG.
    -   `data_analysis_processing/`: Modules for performing financial and competitor analysis, with RAG integration for contextualization.
    -   `insight_generation_recommendation/`: Modules for deriving insights and generating recommendations, with RAG integration.
    -   `report_generation/`: Modules for compiling and formatting the final output report.
    -   `ui/`: Contains the Gradio user interface code (`app.py`).
    -   `tests/`: Contains unit and integration tests for various components.

## Known Issues & Limitations (v0.2)

-   **Placeholder Core Logic:** The core analytical intelligence of most components (information extraction, financial calculations, insight generation, recommendations) relies on placeholder logic. Output is often simulated or hardcoded.
-   **Simulated LLM Processing for RAG:** While the RAG pipeline (text splitting, embedding, indexing, retrieval) is implemented, the subsequent processing of retrieved text chunks uses placeholder LLMs. These placeholders mimic the expected interaction but do not perform actual sophisticated NLP understanding or generation.
-   **LangGraph Outlines:** LangGraph workflows defined in `FinancialStatementExtractor` and `FinancialAnalysisModule` are structural outlines and are not compiled or executed as actual graphs. The `langgraph` library is not yet a hard dependency.
-   **Performance:** Not yet optimized for very large documents or a high volume of reports. Indexing and embedding generation can be time-consuming for large inputs on CPU.
-   **Error Handling:** Basic error handling is in place, but it can be significantly improved with more specific error types and user feedback.
-   **Report Customization:** Limited options for customizing the content or format of the generated report.
-   **PDF Parsing Robustness:** The current PDF handling (via `AnnualReportLoader`) is basic. Complex PDFs with scanned images, intricate tables, or non-standard layouts may not be parsed accurately.

## Future Development

-   **Full LLM and LangChain Integration:** Replace all placeholder LLMs with actual LangChain chains connected to powerful language models (e.g., GPT, Claude, local open-source models) for genuine NLP-driven extraction, analysis, and generation.
-   **Activate LangGraph Workflows:** Install the `langgraph` library and fully implement and compile the outlined stateful graphs for managing complex extraction and analysis processes.
-   **Sophisticated Financial Analysis:** Implement robust calculations for a wide range of financial ratios, detailed trend analysis (e.g., CAGR, regression), and comprehensive benchmarking against industry and peer data.
-   **Advanced Information Extraction:** Develop more reliable methods for extracting data from diverse report structures, including complex tables and nuanced textual disclosures.
-   **Contextual Insight and Recommendation Engines:** Build more intelligent systems for deriving meaningful insights and generating actionable, context-aware recommendations.
-   **Enhanced RAG Capabilities:** Explore more advanced RAG techniques, such as re-ranking retrieved documents, query transformation, and hybrid search.
-   **Improved UI/UX:** Enhance the Gradio interface with better visualizations, more interactive controls, and improved report presentation (e.g., allowing download in different formats like PDF or DOCX).
-   **Robust PDF and Document Processing:** Integrate advanced libraries (e.g., PyMuPDF, Unstructured.io) for more accurate text and table extraction from various PDF layouts and potentially other document formats (e.g., HTML, DOCX).
-   **Configuration and Extensibility:** Allow users to configure models, analysis parameters, and report templates. Make the system more extensible for adding new analysis modules or data sources.
-   **Comprehensive Testing:** Expand test coverage, including more integration and end-to-end tests, especially once real LLMs are integrated.

## Contributing

Currently, the project is in early development. If you are interested in contributing, please first open an issue on the project's repository to discuss your ideas or proposed changes.
