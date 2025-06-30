import gradio as gr
import os
import datetime

# Import the main FARG Agent
from farg.agent import FARGAgent

# Instantiate the agent globally or within the UI interaction function.
# Global instantiation is fine if the agent is stateless or its state is managed per call.
# For simplicity, let's instantiate it once here.
# If FARGAgent becomes very resource-intensive to initialize, might move instantiation
# into `run_farg_analysis_gradio` or manage a pool.
farg_instance = FARGAgent()

def run_farg_analysis_gradio(company_report_files: list,
                             competitor_report_files: list | None,
                             analysis_options: list[str]) -> str:
    """
    Wrapper function for Gradio interface to call the FARGAgent's run method.
    Extracts file paths from Gradio's file objects.
    """
    print("\n--- Gradio UI: run_farg_analysis_gradio Called ---")

    company_paths = []
    if company_report_files:
        company_paths = [f.name for f in company_report_files]

    competitor_paths = []
    if competitor_report_files:
        competitor_paths = [f.name for f in competitor_report_files]

    print(f"Extracted Company File Paths: {company_paths}")
    print(f"Extracted Competitor File Paths: {competitor_paths if competitor_paths else 'None'}")
    print(f"Selected Analysis Options: {analysis_options}")

    if not company_paths:
        return "Error: Please upload at least one company report for analysis."

    # Call the main FARG agent's run method
    try:
        report_output = farg_instance.run(
            company_report_paths=company_paths,
            competitor_report_paths=competitor_paths if competitor_paths else None,
            analysis_options=analysis_options
        )
    except Exception as e:
        print(f"Error during FARGAgent run: {e}")
        # Potentially log the full traceback here
        report_output = f"An error occurred during report generation: {str(e)}\n\nPlease check the application logs for more details."


    print("--- Gradio UI: run_farg_analysis_gradio Finished ---")
    return report_output

# Define the Gradio interface
# Note: The `farg_agent` function previously defined in this file is now replaced by `run_farg_analysis_gradio`
# which calls the `FARGAgent` class instance.

inputs = [
    gr.File(label="Company Annual Reports (PDF, TXT)", file_count="multiple", type="filepath"),
    gr.File(label="Competitor Annual Reports (PDF, TXT) (Optional)", file_count="multiple", type="filepath"),
    gr.CheckboxGroup(
        label="Analysis Options to Include in Report",
        choices=[
            # "Financial Performance Analysis (Standard)", # This is implicitly always done for company A
            "Financial Performance Comparison (vs Competitor)", # Only if competitor reports are provided
            "SWOT Analysis", # Added based on agent capabilities
            "Strategic and Operational Issue Identification",
            "Key Insights Generation", # Agent generates insights
            "Strategic Recommendations" # Agent generates recommendations
        ],
        value=[ # Default selected options
            # "Financial Performance Analysis (Standard)",
            "SWOT Analysis",
            "Key Insights Generation",
            "Strategic Recommendations"
        ]
    )
]

outputs = [
    gr.Textbox(label="Generated FARG Report", lines=30, show_copy_button=True, max_lines=50) # Increased lines
]

# Ensure 'demo' is defined at the module level for main.py to import
demo = gr.Interface(
    fn=run_farg_analysis_gradio, # Updated function call
    inputs=inputs,
    outputs=outputs,
    title="Financial Analysis Report Generator (FARG) - v0.2 (Agent Integrated)",
    description=(
        "Upload Annual Reports (PDF or TXT) for a primary company and, optionally, for its competitors. "
        "Select the desired analysis components to include in the generated report. "
        "The FARG agent will then process these documents and generate a comprehensive analysis."
        "\n\n(Note: This version uses simulated processing for many internal components. LangChain/LangGraph integration is partial.)"
    ),
    allow_flagging="never",
    # Example usage (paths would need to be valid where Gradio server runs or use temp files)
    # examples=[
    #     [["dummy_agent_reports/co_report.txt"], None, ["SWOT Analysis", "Strategic Recommendations"]],
    #     [["dummy_agent_reports/co_report.txt"], ["dummy_agent_reports/comp_report.txt"], ["Financial Performance Comparison", "Strategic Recommendations"]]
    # ]
)

# The following block should be removed or commented out if main.py is the primary entry point.
# if __name__ == "__main__":
#     print("Launching Gradio UI for FARG (Agent Integrated) directly from app.py...")
#     # Ensure dummy files for examples exist if examples are uncommented and point to local paths.
#     # This is mainly for testing the UI's ability to pass file paths to the agent.
#     # The agent itself has its own dummy file creation in its __main__ block for self-testing.

#     # For the UI examples to work without manual upload, files need to be accessible by Gradio.
#     # This might involve placing them in a specific directory or using Gradio's caching for examples.
#     # For now, manual upload is the primary way.

#     demo.launch()
#     print("Gradio UI closed.")
