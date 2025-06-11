# data_ingestion/__init__.py

"""
The data_ingestion package is responsible for loading, parsing, and storing
annual financial reports and other relevant documents.

Modules:
    annual_report_loader: Classes and functions for loading report files (e.g., TXT, PDF).
    report_parser: Classes and functions for parsing the content of reports.
    report_storage: Classes and functions for storing raw or parsed reports.
"""

from .annual_report_loader import AnnualReportLoader
from .report_parser import ReportParser
from .report_storage import ReportStorage

# You can define a list of public objects for `from data_ingestion import *`
# but it's often better to encourage specific imports.
__all__ = [
    "AnnualReportLoader",
    "ReportParser",
    "ReportStorage",
]

print("farg.data_ingestion package initialized")
