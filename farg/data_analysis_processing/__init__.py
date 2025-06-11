# data_analysis_processing/__init__.py

"""
The data_analysis_processing package is responsible for conducting in-depth
analysis based on the extracted information. This includes financial analysis,
trend identification, benchmarking, and competitor analysis.

Modules:
    financial_analysis_module: Performs ratio, trend, and benchmarking analysis.
    competitor_analysis_module: Conducts SWOT and performance comparison against competitors.
"""

from .financial_analysis_module import FinancialAnalysisModule
from .competitor_analysis_module import CompetitorAnalysisModule

__all__ = [
    "FinancialAnalysisModule",
    "CompetitorAnalysisModule",
]

print("farg.data_analysis_processing package initialized")
