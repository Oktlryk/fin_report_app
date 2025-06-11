from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Placeholder for an actual LLM. In a real scenario, this would be:
# from langchain_openai import ChatOpenAI
# self.llm = ChatOpenAI(model="gpt-3.5-turbo")
class PlaceholderLLM:
    """
    A placeholder class for a Language Model.
    Simulates the behavior of an LLM invoke method for LangChain integration.
    """
    def invoke(self, input_dict: dict) -> str:
        """
        Simulates an LLM call. Takes a dictionary (as LangChain prompts do)
        and returns a string.
        """
        text_section = input_dict.get("text_section", "")
        # Simulate some processing, like summarization or key info extraction
        return f"LLM Summary of: {text_section[:100]}..."


class ReportParser:
    """
    Parses the content of an annual report using a LangChain chain.
    This class integrates a prompt, a (placeholder) LLM, and an output parser
    to process sections of a report.
    """

    def __init__(self):
        """
        Initializes the ReportParser, setting up the LangChain prompt,
        placeholder LLM, and the processing chain.
        """
        self.prompt = ChatPromptTemplate.from_template(
            "Extract key information and provide a concise summary of the following text section: \n---BEGIN SECTION---\n{text_section}\n---END SECTION---"
        )

        self.llm = PlaceholderLLM() # Using the placeholder LLM

        self.chain = self.prompt | self.llm | StrOutputParser()

        print("ReportParser initialized with LangChain components (using PlaceholderLLM).")


    def parse_report(self, report_content: str) -> dict:
        """
        Parses the raw string content of an annual report using the defined LangChain chain.

        It simulates processing the entire report content as one section or,
        alternatively, could be modified to split the report into actual sections
        (e.g., "Introduction", "Management Discussion", "Financial Overview") and
        process each with the chain.

        Args:
            report_content: The raw string content of the report.

        Returns:
            A dictionary with keys:
                "text": The original report content.
                "parsed_sections": A dictionary where keys are section names (e.g., "overview_from_llm")
                                   and values are the processed output from the LLM for that section.
                "raw_llm_output_example": The direct output from the LLM for the processed section,
                                          useful for inspection or if no further structuring is done.
        """
        if not isinstance(report_content, str):
            raise TypeError("report_content must be a string.")

        # Simulate processing the whole report_content as one main section for now.
        # In a more advanced version, one might split `report_content` by specific headings
        # (e.g., "Management Discussion and Analysis", "Risk Factors") and run the chain on each.
        # For example:
        # sections = report_content.split("\n\nManagement Discussion and Analysis\n\n")
        # overview_content = sections[0] if sections else report_content
        # mda_content = sections[1] if len(sections) > 1 else ""

        print(f"Invoking LangChain chain for report content (length: {len(report_content)} chars).")
        # For this example, we'll just use the beginning of the report content
        # or a specific known section if we were to parse it out.
        # Let's simulate using the first 1000 characters as a "summary section".

        # If report_content is very long, processing the whole thing might be slow/costly with a real LLM.
        # For simulation, it's fine. Let's just take a slice to represent a "key section".
        key_section_content = report_content[:1500] # Simulate focusing on an initial part

        llm_processed_data = self.chain.invoke({"text_section": key_section_content})

        # Structure the output
        parsed_data_dict = {
            "text": report_content, # The full original text
            "parsed_sections": {
                # "original_overview_simulation": key_section_content, # For reference
                "overview_from_llm": llm_processed_data
            },
            "raw_llm_output_example": llm_processed_data # For direct inspection of one LLM output
        }

        print("Report parsing with LangChain chain complete.")
        return parsed_data_dict

if __name__ == '__main__':
    print("Starting example usage of ReportParser with LangChain integration...")
    parser = ReportParser()

    sample_report_text = (
        "Annual Report 2023 - Global Innovations Inc.\n\n"
        "Introduction\nThis year has been pivotal for Global Innovations Inc. We saw substantial growth in new markets, "
        "driven by our flagship product 'InnovateMax'. Our commitment to research and development has led to breakthroughs "
        "in AI-driven analytics, positioning us as a leader in the tech industry. We continue to focus on sustainable "
        "practices and expanding our global footprint.\n\n"
        "Management Discussion and Analysis\nFinancial Performance: Revenue reached $150M, a 20% increase from the prior year. "
        "Net profit stood at $25M. The growth was primarily attributed to the successful launch of InnovateMax Pro and "
        "increased adoption by enterprise clients. Operating expenses increased by 10% due to investments in R&D and market expansion efforts. "
        "Liquidity remains strong with a current ratio of 2.5.\n\n"
        "Outlook for 2024\nWe are optimistic about the future, with plans to enter the Asian market and further develop our AI capabilities. "
        "Challenges include talent retention and navigating the evolving regulatory landscape for AI technologies."
        "This is a very long section of text to ensure we have enough content for the LLM to process. " * 5
    )

    print("\n--- Parsing a sample report ---")
    try:
        parsed_output = parser.parse_report(sample_report_text)
        print(f"\nSuccessfully parsed. Output keys: {list(parsed_output.keys())}")
        print(f"\nOriginal text (first 100 chars): '{parsed_output.get('text', '')[:100]}...'")

        print("\nParsed Sections:")
        for section_name, section_content in parsed_output.get("parsed_sections", {}).items():
            print(f"  {section_name}: '{str(section_content)[:150]}...'") # Print snippet

        print(f"\nRaw LLM Output Example (first 150 chars): '{parsed_output.get('raw_llm_output_example', '')[:150]}...'")

        # Check if the LLM output is what we expect from the placeholder
        expected_llm_prefix = "LLM Summary of: Annual Report 2023 - Global Innovations Inc."
        actual_llm_output = parsed_output.get("parsed_sections", {}).get("overview_from_llm", "")
        if actual_llm_output.startswith(expected_llm_prefix):
            print("\nPlaceholderLLM output seems correct.")
        else:
            print(f"\nPlaceholderLLM output mismatch. Expected prefix: '{expected_llm_prefix}', Got: '{actual_llm_output[:100]}...'")

    except Exception as e:
        print(f"Error during parsing: {e}")

    print("\n--- Testing with non-string input ---")
    try:
        parser.parse_report(12345) # type: ignore
    except TypeError as e:
        print(f"Correctly caught expected error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

    print("\nExample usage of ReportParser with LangChain integration complete.")
