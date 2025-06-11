import re

class ReportTemplateEngine:
    """
    Manages loading and populating report templates.

    In a real application, this might use a more robust templating engine
    like Jinja2, Handlebars, or even just more sophisticated string formatting.
    """

    def __init__(self):
        """
        Initializes the ReportTemplateEngine.
        """
        self.templates = {
            "standard_comparison_report_v1": """
Report Title: {{report_title}}
Date: {{generation_date}}

Company A Profile:
Name: {{company_A_name}}
Market Footprint: {{company_A_market_footprint}}
Products/Services: {{company_A_products_services}}
Relative Size: {{company_A_relative_size}}
Maturity Stage: {{company_A_maturity_stage}}
Financial Summary: {{company_A_financial_summary}}

Company B Profile (if applicable):
Name: {{company_B_name}}
Market Footprint: {{company_B_market_footprint}}
Products/Services: {{company_B_products_services}}
Relative Size: {{company_B_relative_size}}
Maturity Stage: {{company_B_maturity_stage}}
Financial Summary: {{company_B_financial_summary}}

Financial Performance Comparison:
{{financial_comparison_summary}}
Profitability: Company A ({{comp_A_profitability_metric}}) vs Company B ({{comp_B_profitability_metric}})
Liquidity: Company A ({{comp_A_liquidity_metric}}) vs Company B ({{comp_B_liquidity_metric}})

Identified Strategic Issues for Company A:
{{strategic_issues}}

Identified Operational Issues for Company A:
{{operational_issues}}

Key Insights:
{{insights}}

Recommendations for Company A:
{{recommendations}}

--- End of Report ---
""",
            "single_company_deep_dive_v1": """
Report Title: Deep Dive Analysis for {{company_A_name}}
Date: {{generation_date}}

Company Profile:
Name: {{company_A_name}}
Market Footprint: {{company_A_market_footprint}}
Products/Services: {{company_A_products_services}}
Relative Size: {{company_A_relative_size}}
Maturity Stage: {{company_A_maturity_stage}}

Financial Analysis:
Key Ratios: {{financial_ratios}}
Trends: {{financial_trends}}
Benchmarking: {{benchmarking_summary}}

SWOT Analysis:
Strengths: {{swot_strengths}}
Weaknesses: {{swot_weaknesses}}
Opportunities: {{swot_opportunities}}
Threats: {{swot_threats}}

Identified Strategic Issues:
{{strategic_issues}}

Identified Operational Issues:
{{operational_issues}}

Key Insights:
{{insights}}

Recommendations:
{{recommendations}}

--- End of Report ---
"""
        }

    def load_template(self, template_name: str) -> str:
        """
        Simulates loading a report template string by name.

        Args:
            template_name: The name of the template to load.

        Returns:
            The template string.

        Raises:
            ValueError: If the template_name is not found.
        """
        if template_name not in self.templates:
            raise ValueError(f"Template '{template_name}' not found.")
        print(f"Template '{template_name}' loaded.")
        return self.templates[template_name]

    def populate_template(self, template_str: str, report_data: dict) -> str:
        """
        Simulates populating the template string with data from report_data.

        This is a very basic find-and-replace for {{key}}.
        A real implementation would use a proper templating engine for loops,
        conditionals, formatting, etc.

        Args:
            template_str: The template string (e.g., loaded by `load_template`).
            report_data: A comprehensive dictionary containing all data to populate
                         the template with. Keys should match placeholders in the template.

        Returns:
            The populated report string.
        """
        if not isinstance(template_str, str):
            raise TypeError("template_str must be a string.")
        if not isinstance(report_data, dict):
            raise TypeError("report_data must be a dictionary.")

        populated_report = template_str

        # Simple regex to find all {{key}} placeholders
        placeholders = re.findall(r"\{\{([\w_]+)\}\}", populated_report)

        for key in placeholders:
            # Get value from report_data, default to a "NOT_FOUND" string if key is missing
            # This makes it clear in the output if data is missing.
            value = report_data.get(key, f"{{{{KEY_NOT_FOUND: {key}}}}}")

            # Ensure value is a string for substitution. If it's a list or dict,
            # convert it to a simple string representation for this basic templating.
            if isinstance(value, list):
                # Format list items with newlines and indentation for readability
                value_str = "\n".join([f"  - {item}" for item in value])
            elif isinstance(value, dict):
                 # Format dict items with newlines and indentation
                value_str = "\n".join([f"  {k}: {v}" for k, v in value.items()])
            else:
                value_str = str(value) # Ensure it's a string

            populated_report = populated_report.replace(f"{{{{{key}}}}}", value_str)

        print(f"Template populated with data (keys used: {list(report_data.keys())}).")
        # For verification, one might add:
        # print(f"Populated report snippet: {populated_report[:500]}")
        return populated_report + "\n\n[Note: This report was populated using a basic simulation.]"

if __name__ == '__main__':
    print("Starting example usage of ReportTemplateEngine...")
    engine = ReportTemplateEngine()

    # Load a template
    try:
        template = engine.load_template("standard_comparison_report_v1")
        print(f"\n--- Loaded Template (standard_comparison_report_v1 snippet) ---")
        print(template[:300] + "...")
    except ValueError as e:
        print(f"Error loading template: {e}")
        template = "" # Ensure template is defined for next step

    # Sample data to populate
    sample_data = {
        "report_title": "Comparative Analysis: Alpha Corp vs Beta LLC",
        "generation_date": "2023-10-27",
        "company_A_name": "Alpha Corp",
        "company_A_market_footprint": "Global",
        "company_A_products_services": "Software, Cloud Services",
        "company_A_relative_size": "Large",
        "company_A_maturity_stage": "Mature",
        "company_A_financial_summary": "Revenue: $5B, NPM: 15%",
        "company_B_name": "Beta LLC",
        "company_B_market_footprint": "North America",
        "company_B_products_services": "Consulting, Analytics",
        "company_B_relative_size": "Medium",
        "company_B_maturity_stage": "Growth",
        "company_B_financial_summary": "Revenue: $500M, NPM: 10%",
        "financial_comparison_summary": "Alpha Corp shows stronger profitability and scale.",
        "comp_A_profitability_metric": "NPM: 15%",
        "comp_B_profitability_metric": "NPM: 10%",
        "comp_A_liquidity_metric": "Current Ratio: 2.0",
        "comp_B_liquidity_metric": "Current Ratio: 1.5",
        "strategic_issues": ["Intense competition in cloud services.", "Need for diversification."],
        "operational_issues": ["Supply chain delays for hardware.", "High employee turnover in R&D."],
        "insights": ["Alpha Corp's global reach is a key advantage.", "Beta LLC's agility allows rapid market adaptation."],
        "recommendations": [
            {"recommendation": "Alpha Corp should explore acquisition targets in AI.", "justification": "To counter Beta's agility."},
            {"recommendation": "Beta LLC should expand service offerings.", "justification": "To reduce reliance on consulting."}
        ]
    }

    print("\n--- Populating Template ---")
    if template:
        populated_content = engine.populate_template(template, sample_data)
        print("\n--- Populated Report Content (Snippet) ---")
        print(populated_content[:1000] + "...") # Print a longer snippet
    else:
        print("Skipping population as template loading failed.")

    print("\n--- Testing with a missing key in data ---")
    faulty_data = {"report_title": "Test Report Only"}
    if template:
        populated_faulty = engine.populate_template(template, faulty_data)
        print("\n--- Populated Report with Missing Data (Snippet) ---")
        print(populated_faulty[:500] + "...")
        if "{{KEY_NOT_FOUND: company_A_name}}" in populated_faulty:
            print("\nSuccessfully shows KEY_NOT_FOUND for missing data.")


    print("\nExample usage of ReportTemplateEngine complete.")
