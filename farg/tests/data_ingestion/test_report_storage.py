import unittest
import os
import shutil

# Ensure the farg package is discoverable
try:
    from farg.data_ingestion.report_storage import ReportStorage
except ImportError:
    import sys
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))
    from farg.data_ingestion.report_storage import ReportStorage

class TestReportStorage(unittest.TestCase):
    """
    Unit tests for the ReportStorage class.
    """

    TEST_STORAGE_DIR_FS = "temp_test_storage_fs" # For file system tests
    TEST_STORAGE_DIR_MEM = "temp_test_storage_mem" # For in-memory (but still creates dir)

    @classmethod
    def setUpClass(cls):
        """Clean up any previous test directories if they exist."""
        if os.path.exists(cls.TEST_STORAGE_DIR_FS):
            shutil.rmtree(cls.TEST_STORAGE_DIR_FS)
        if os.path.exists(cls.TEST_STORAGE_DIR_MEM):
            shutil.rmtree(cls.TEST_STORAGE_DIR_MEM)
        # The ReportStorage class creates the directory if it doesn't exist,
        # so we don't strictly need to os.makedirs here unless we want to pre-control it.

    @classmethod
    def tearDownClass(cls):
        """Remove the temporary storage directories after all tests."""
        if os.path.exists(cls.TEST_STORAGE_DIR_FS):
            shutil.rmtree(cls.TEST_STORAGE_DIR_FS)
        if os.path.exists(cls.TEST_STORAGE_DIR_MEM):
            shutil.rmtree(cls.TEST_STORAGE_DIR_MEM)

    def setUp(self):
        """Initialize ReportStorage instances for tests."""
        # Ensure clean directories for each test method if necessary,
        # though ReportStorage handles its own directory creation.
        # Re-cleaning them here ensures independence if a test fails mid-way.
        if os.path.exists(self.TEST_STORAGE_DIR_FS):
            shutil.rmtree(self.TEST_STORAGE_DIR_FS)
        self.fs_storage = ReportStorage(storage_path=self.TEST_STORAGE_DIR_FS)

        if os.path.exists(self.TEST_STORAGE_DIR_MEM): # Though primarily for in-memory
            shutil.rmtree(self.TEST_STORAGE_DIR_MEM)
        self.mem_storage = ReportStorage(storage_path=self.TEST_STORAGE_DIR_MEM)


    def test_import_report_storage(self):
        """Test that ReportStorage can be imported."""
        self.assertTrue(callable(ReportStorage))

    def test_store_and_retrieve_report_in_memory(self):
        """Test storing and retrieving a single report in memory."""
        report_name = "mem_report_1.txt"
        report_content = "In-memory test content."
        self.mem_storage.store_report(report_name, report_content, use_file_system=False)
        retrieved_content = self.mem_storage.retrieve_report_from_memory(report_name)
        self.assertEqual(retrieved_content, report_content)

        # Test retrieving non-existent report
        self.assertIsNone(self.mem_storage.retrieve_report_from_memory("non_existent_mem_report.txt"))

    def test_store_reports_in_memory(self):
        """Test storing multiple reports in memory."""
        reports_data = {
            "mem_multi_1.txt": "Content for multi 1",
            "mem_multi_2.json": "{'key': 'value'}",
        }
        self.mem_storage.store_reports(reports_data, use_file_system=False)
        self.assertEqual(self.mem_storage.retrieve_report_from_memory("mem_multi_1.txt"), "Content for multi 1")
        self.assertEqual(self.mem_storage.retrieve_report_from_memory("mem_multi_2.json"), "{'key': 'value'}")

    def test_store_report_on_file_system(self):
        """Test storing a single report on the file system."""
        report_name = "fs_report_1.txt"
        report_content = "File system test content."
        self.fs_storage.store_report(report_name, report_content, use_file_system=True)

        expected_file_path = os.path.join(self.TEST_STORAGE_DIR_FS, report_name)
        self.assertTrue(os.path.exists(expected_file_path))
        with open(expected_file_path, "r", encoding="utf-8") as f:
            content_on_disk = f.read()
        self.assertEqual(content_on_disk, report_content)

    def test_store_reports_on_file_system(self):
        """Test storing multiple reports on the file system."""
        reports_data = {
            "fs_multi_1.txt": "FS Content 1",
            "fs_multi_2.log": "FS Log data",
        }
        self.fs_storage.store_reports(reports_data, use_file_system=True)
        for name, content in reports_data.items():
            expected_file_path = os.path.join(self.TEST_STORAGE_DIR_FS, name)
            self.assertTrue(os.path.exists(expected_file_path), f"File {name} should exist.")
            with open(expected_file_path, "r", encoding="utf-8") as f:
                content_on_disk = f.read()
            self.assertEqual(content_on_disk, content, f"Content for {name} mismatch.")

    def test_store_report_invalid_name_memory(self):
        """Test storing with invalid report name (e.g., empty) in memory."""
        # The implementation currently prints an error and returns.
        # We can check if the item was NOT added.
        initial_count = len(self.mem_storage._in_memory_storage)
        self.mem_storage.store_report("", "Test content", use_file_system=False)
        self.assertEqual(len(self.mem_storage._in_memory_storage), initial_count, "Report with empty name should not be stored.")

    def test_store_report_invalid_name_filesystem(self):
        """Test storing with invalid report name on filesystem."""
        # Similar to memory, current implementation prints error.
        # We check that no file with an empty name (or problematic name) is created.
        # os.path.basename('') is '', so it might try to create a file named after the directory itself.
        # This needs careful handling in the main code, but for test, check no unexpected files.
        initial_files = os.listdir(self.TEST_STORAGE_DIR_FS)
        self.fs_storage.store_report("", "Test content", use_file_system=True)
        current_files = os.listdir(self.TEST_STORAGE_DIR_FS)
        self.assertEqual(len(current_files), len(initial_files), "Report with empty name should not create a file.")

    def test_store_report_invalid_content_type_memory(self):
        """Test storing non-string content in memory."""
        initial_count = len(self.mem_storage._in_memory_storage)
        self.mem_storage.store_report("invalid_content.txt", 123, use_file_system=False) # type: ignore
        self.assertEqual(len(self.mem_storage._in_memory_storage), initial_count, "Report with non-string content should not be stored.")

    def test_store_report_invalid_content_type_filesystem(self):
        """Test storing non-string content on filesystem."""
        report_name = "invalid_content_fs.txt"
        self.fs_storage.store_report(report_name, True, use_file_system=True) # type: ignore
        expected_file_path = os.path.join(self.TEST_STORAGE_DIR_FS, report_name)
        # Based on current ReportStorage, it prints an error and returns.
        # So, the file should not be created.
        self.assertFalse(os.path.exists(expected_file_path), "File with non-string content should not be created.")

if __name__ == '__main__':
    unittest.main()
