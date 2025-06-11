import unittest
import os
import shutil # For cleaning up test files/directories

# Ensure the farg package is discoverable, assuming tests are run from project root
# This might require adjusting PYTHONPATH or specific test runner configurations
try:
    from farg.data_ingestion.annual_report_loader import AnnualReportLoader
except ImportError:
    # Fallback for cases where the test runner setup might be different
    # This assumes a certain directory structure.
    import sys
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))
    from farg.data_ingestion.annual_report_loader import AnnualReportLoader


class TestAnnualReportLoader(unittest.TestCase):
    """
    Unit tests for the AnnualReportLoader class.
    """

    TEST_REPORTS_DIR = "temp_test_reports_loader"

    @classmethod
    def setUpClass(cls):
        """Create a temporary directory and dummy files for testing."""
        if os.path.exists(cls.TEST_REPORTS_DIR):
            shutil.rmtree(cls.TEST_REPORTS_DIR)
        os.makedirs(cls.TEST_REPORTS_DIR)

        cls.report_txt_path = os.path.join(cls.TEST_REPORTS_DIR, "reportA.txt")
        cls.report_pdf_path = os.path.join(cls.TEST_REPORTS_DIR, "reportB.pdf")
        cls.report_unsupported_path = os.path.join(cls.TEST_REPORTS_DIR, "reportC.doc")

        with open(cls.report_txt_path, "w") as f:
            f.write("This is a test text report.")

        # Dummy PDF, actual content doesn't matter for current loader logic
        with open(cls.report_pdf_path, "w") as f:
            f.write("This is a dummy PDF.")

        with open(cls.report_unsupported_path, "w") as f:
            f.write("This is an unsupported document type.")

    @classmethod
    def tearDownClass(cls):
        """Remove the temporary directory and files after tests."""
        if os.path.exists(cls.TEST_REPORTS_DIR):
            shutil.rmtree(cls.TEST_REPORTS_DIR)

    def setUp(self):
        """Initialize the loader for each test."""
        self.loader = AnnualReportLoader()

    def test_import_annual_report_loader(self):
        """Test that AnnualReportLoader can be imported."""
        self.assertTrue(callable(AnnualReportLoader), "AnnualReportLoader class should be callable (importable).")

    def test_load_text_report_successfully(self):
        """Test loading a valid .txt file."""
        content = self.loader.load_report(self.report_txt_path)
        self.assertEqual(content, "This is a test text report.")

    def test_load_pdf_report_placeholder(self):
        """Test loading a .pdf file (currently placeholder)."""
        content = self.loader.load_report(self.report_pdf_path)
        self.assertEqual(content, f"Placeholder PDF content for {os.path.basename(self.report_pdf_path)}")

    def test_load_unsupported_file_type(self):
        """Test loading an unsupported file type raises ValueError."""
        with self.assertRaises(ValueError):
            self.loader.load_report(self.report_unsupported_path)

    def test_load_non_existent_file(self):
        """Test loading a non-existent file raises FileNotFoundError."""
        with self.assertRaises(FileNotFoundError):
            self.loader.load_report(os.path.join(self.TEST_REPORTS_DIR, "non_existent.txt"))

    def test_load_reports_list(self):
        """Test loading a list of reports, including valid, placeholder, and skippable."""
        file_paths = [
            self.report_txt_path,
            self.report_pdf_path,
            os.path.join(self.TEST_REPORTS_DIR, "non_existent.txt"), # Will be skipped
            self.report_unsupported_path # Will be skipped
        ]
        # Expected: text content, pdf placeholder. Errors for others are printed by loader.
        # Check that the successfully loaded reports are returned
        expected_contents = [
            "This is a test text report.",
            f"Placeholder PDF content for {os.path.basename(self.report_pdf_path)}"
        ]
        loaded_contents = self.loader.load_reports(file_paths)
        self.assertEqual(len(loaded_contents), 2)
        self.assertIn(expected_contents[0], loaded_contents)
        self.assertIn(expected_contents[1], loaded_contents)

    def test_load_reports_list_all_fail(self):
        """Test loading a list where all files cause errors."""
        file_paths = [
            os.path.join(self.TEST_REPORTS_DIR, "non_existent1.txt"),
            os.path.join(self.TEST_REPORTS_DIR, "non_existent2.pdf"),
            self.report_unsupported_path
        ]
        loaded_contents = self.loader.load_reports(file_paths)
        self.assertEqual(len(loaded_contents), 0, "Should return an empty list if all files fail to load.")

if __name__ == '__main__':
    # This allows running the tests directly from this file
    # For more complex projects, a test runner (e.g., `python -m unittest discover`) is preferred.
    unittest.main()
