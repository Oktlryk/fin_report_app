# report_generation/__init__.py

"""
The report_generation package is responsible for compiling all analyzed data,
insights, and recommendations into a structured, human-readable report.

Modules:
    report_template_engine: Manages loading and populating report templates.
    report_generator_components: Contains classes that generate specific sections or data
                                 for reports (e.g., company profile, issue identification).
    report_generator: Orchestrates the assembly of the full report using various components
                      and a template engine.
"""

from .report_template_engine import ReportTemplateEngine
from .report_generator_components import (
    CompanyProfileGenerator,
    FinancialPerformanceComparator,
    StrategicOperationalIssueIdentifier
)
from .report_generator import ReportGenerator

__all__ = [
    "ReportTemplateEngine",
    "CompanyProfileGenerator",
    "FinancialPerformanceComparator",
    "StrategicOperationalIssueIdentifier",
    "ReportGenerator",
]

print("farg.report_generation package initialized")
