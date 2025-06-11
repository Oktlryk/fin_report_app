# information_extraction/__init__.py

"""
The information_extraction package is responsible for extracting structured
information from parsed financial reports. This includes financial statements,
Key Performance Indicators (KPIs), and qualitative company information.

Modules:
    financial_statement_extractor: Extracts income statements, balance sheets, etc.
    kpi_extractor: Calculates financial KPIs from statement data.
    company_info_extractor: Extracts qualitative info like market footprint, maturity.
"""

from .financial_statement_extractor import FinancialStatementExtractor
from .kpi_extractor import KPIExtractor
from .company_info_extractor import CompanyInfoExtractor

__all__ = [
    "FinancialStatementExtractor",
    "KPIExtractor",
    "CompanyInfoExtractor",
]

print("farg.information_extraction package initialized")
