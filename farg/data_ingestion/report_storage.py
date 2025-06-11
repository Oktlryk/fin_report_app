import os

class ReportStorage:
    """
    Handles the storage of processed annual reports.

    This is a simulation. In a real application, this might involve
    writing to a database, a document store (like Elasticsearch),
    or a file system with proper organization.
    """

    def __init__(self, storage_path: str = "stored_reports"):
        """
        Initializes the ReportStorage.

        Args:
            storage_path: The base path where reports will be "stored".
                          For this simulation, it's a directory in the file system.
        """
        self.storage_path = storage_path
        if not os.path.exists(self.storage_path):
            try:
                os.makedirs(self.storage_path)
                print(f"Storage directory '{self.storage_path}' created.")
            except OSError as e:
                # This could happen if there's a race condition or permission issue
                print(f"Error creating storage directory '{self.storage_path}': {e}")
                # Depending on requirements, might re-raise or handle
        self._in_memory_storage = {} # For a simple in-memory dict simulation

    def store_report(self, report_name: str, report_content: str, use_file_system: bool = False) -> None:
        """
        Stores a single processed report.

        Args:
            report_name: A unique name or identifier for the report (e.g., "companyX_2023.txt").
            report_content: The content of the report to be stored (can be raw text or parsed data string).
            use_file_system: If True, attempts to save to the file system. Otherwise, uses in-memory dict.
        """
        if not isinstance(report_name, str) or not report_name:
            print("Error: report_name must be a non-empty string.")
            return # Or raise ValueError

        if not isinstance(report_content, str):
            print(f"Error: report_content for '{report_name}' must be a string.")
            return # Or raise TypeError

        if use_file_system:
            try:
                # Ensure the report_name is safe for file system paths
                safe_report_name = os.path.basename(report_name) # Basic sanitization
                file_path = os.path.join(self.storage_path, safe_report_name)

                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(report_content)
                print(f"Report '{safe_report_name}' stored successfully in '{self.storage_path}'.")
            except IOError as e:
                print(f"Error storing report '{report_name}' to file system: {e}")
                # Fallback or alternative handling could be added here
            except Exception as e:
                print(f"An unexpected error occurred while storing '{report_name}' to file system: {e}")
        else:
            self._in_memory_storage[report_name] = report_content
            print(f"Report '{report_name}' stored in memory.")


    def store_reports(self, reports: dict[str, str], use_file_system: bool = False) -> None:
        """
        Stores multiple reports.

        Args:
            reports: A dictionary where keys are report names and values are report contents.
            use_file_system: Passed to store_report.
        """
        if not isinstance(reports, dict):
            print("Error: reports argument must be a dictionary.")
            # Or raise TypeError
            return

        for report_name, report_content in reports.items():
            self.store_report(report_name, report_content, use_file_system=use_file_system)

    def retrieve_report_from_memory(self, report_name: str) -> str | None:
        """Retrieves a report from the in-memory storage."""
        return self._in_memory_storage.get(report_name)

if __name__ == '__main__':
    print("Starting example usage of ReportStorage...")

    # Example with file system storage
    fs_storage = ReportStorage(storage_path="dummy_stored_reports_fs")
    print("\n--- Testing File System Storage ---")
    fs_storage.store_report("reportA_2023.txt", "Content of report A.", use_file_system=True)
    fs_storage.store_report("reportB_annual.txt", "Detailed financials for report B.", use_file_system=True)

    reports_to_store_fs = {
        "reportC_summary.txt": "Summary of company C.",
        "reportD_full.txt": "Full text of company D's annual disclosure."
    }
    fs_storage.store_reports(reports_to_store_fs, use_file_system=True)

    # Verify by checking if files exist (optional manual check)
    print(f"Check the directory '{fs_storage.storage_path}' for stored files.")

    # Example with in-memory storage
    mem_storage = ReportStorage() # Uses default "stored_reports" but we'll use in-memory
    print("\n--- Testing In-Memory Storage ---")
    mem_storage.store_report("reportX_q1.json", "{'data': 'quarter 1 data'}", use_file_system=False)
    retrieved = mem_storage.retrieve_report_from_memory("reportX_q1.json")
    print(f"Retrieved reportX_q1.json from memory: {retrieved is not None}")

    reports_to_store_mem = {
        "reportY_notes.txt": "Notes and appendix for Y.",
        "reportZ_outlook.md": "Future outlook for Z."
    }
    mem_storage.store_reports(reports_to_store_mem, use_file_system=False)
    retrieved_Y = mem_storage.retrieve_report_from_memory("reportY_notes.txt")
    print(f"Retrieved reportY_notes.txt from memory: {retrieved_Y is not None}")
    print(f"Content of reportY_notes.txt (first 20): {retrieved_Y[:20] if retrieved_Y else 'Not found'}")

    print("\n--- Testing Edge Cases ---")
    mem_storage.store_report("", "Empty name test", use_file_system=False) # Invalid name
    mem_storage.store_report("valid_name.txt", 12345, use_file_system=False) # Invalid content type

    # Clean up dummy directory for file system storage if desired (manual for now)
    # import shutil
    # if os.path.exists(fs_storage.storage_path):
    #     try:
    #         shutil.rmtree(fs_storage.storage_path)
    #         print(f"Cleaned up dummy directory: {fs_storage.storage_path}")
    #     except OSError as e:
    #         print(f"Error cleaning up dummy directory {fs_storage.storage_path}: {e}")

    print("\nExample usage of ReportStorage complete.")
