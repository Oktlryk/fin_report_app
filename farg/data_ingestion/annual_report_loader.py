import os

class AnnualReportLoader:
    """
    Loads annual reports from specified file paths.
    """

    def load_report(self, file_path: str) -> str:
        """
        Loads a single annual report.
        Currently supports text files.
        Placeholder for PDF processing.
        """
        if not os.path.exists(file_path):
            # In a real scenario, you might want to log this or handle it more gracefully
            raise FileNotFoundError(f"Report file not found: {file_path}")

        _, file_extension = os.path.splitext(file_path)

        if file_extension.lower() == ".txt":
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                return content
            except Exception as e:
                # Log error or handle
                print(f"Error reading text file {file_path}: {e}")
                raise
        elif file_extension.lower() == ".pdf":
            # Placeholder for PDF processing logic
            # For a real implementation, libraries like PyPDF2, pdfminer.six, or cloud services would be used.
            print(f"Warning: PDF processing for {file_path} is not yet implemented. Returning placeholder content.")
            return f"Placeholder PDF content for {os.path.basename(file_path)}"
        else:
            raise ValueError(f"Unsupported file type: {file_extension}. Only .txt and .pdf (placeholder) are supported.")

    def load_reports(self, file_paths: list[str]) -> list[str]:
        """
        Loads multiple annual reports from a list of file paths.
        """
        loaded_reports = []
        for file_path in file_paths:
            try:
                report_content = self.load_report(file_path)
                loaded_reports.append(report_content)
            except (FileNotFoundError, ValueError) as e:
                print(f"Skipping file {file_path}: {e}")
                # Optionally, collect information about skipped files
            except Exception as e:
                print(f"An unexpected error occurred while loading {file_path}: {e}")
                # Optionally, collect information about failed files
        return loaded_reports

if __name__ == '__main__':
    # This block is for example usage and basic testing.
    # It's good practice to have such a block for modules that can be run directly.

    print("Starting example usage of AnnualReportLoader...")
    loader = AnnualReportLoader()

    # Create dummy files for testing within a 'dummy_reports' directory
    # This helps keep test files organized.
    dummy_dir = "dummy_reports_loader"
    if not os.path.exists(dummy_dir):
        os.makedirs(dummy_dir)

    report1_path = os.path.join(dummy_dir, "report1.txt")
    report2_path = os.path.join(dummy_dir, "report2.pdf")
    report3_path = os.path.join(dummy_dir, "report3.txt")
    report4_path = os.path.join(dummy_dir, "report4.doc") # Unsupported
    non_existent_report_path = os.path.join(dummy_dir, "non_existent_report.txt")

    with open(report1_path, "w", encoding="utf-8") as f:
        f.write("This is the full content of the first annual report (text file). It contains various sections and financial data.")

    # No actual PDF content, as PDF writing is complex.
    # The loader's PDF part is a placeholder.
    with open(report2_path, "w", encoding="utf-8") as f:
        f.write("This is a dummy file to simulate a PDF report. Actual PDF parsing is not implemented.")

    with open(report3_path, "w", encoding="utf-8") as f:
        f.write("Content of the third report. Financial highlights and company overview.")

    # For report4.doc, we don't need to create it if we expect it to fail the file type check.
    # However, creating it can ensure the error handling for unsupported types is triggered.
    with open(report4_path, "w", encoding="utf-8") as f:
        f.write("This is a document with an unsupported .doc extension.")

    sample_file_paths = [
        report1_path,
        report2_path,
        report3_path,
        report4_path,
        non_existent_report_path
    ]

    # Test loading a single text report
    print(f"\n--- Loading single report ({os.path.basename(report1_path)}) ---")
    try:
        content_single = loader.load_report(report1_path)
        print(f"Successfully loaded. First 50 chars: '{content_single[:50]}...'")
    except Exception as e:
        print(f"Error: {e}")

    # Test loading a single PDF report (placeholder)
    print(f"\n--- Loading single report ({os.path.basename(report2_path)}) ---")
    try:
        content_pdf = loader.load_report(report2_path)
        print(f"Loaded placeholder content: '{content_pdf[:50]}...'")
    except Exception as e:
        print(f"Error: {e}")

    # Test loading an unsupported file type
    print(f"\n--- Loading single report ({os.path.basename(report4_path)}) ---")
    try:
        content_unsupported = loader.load_report(report4_path)
        print(f"Content: {content_unsupported}") # Should not reach here
    except ValueError as e:
        print(f"Correctly caught expected error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


    # Test loading a non-existent file
    print(f"\n--- Loading non-existent report ({os.path.basename(non_existent_report_path)}) ---")
    try:
        loader.load_report(non_existent_report_path)
    except FileNotFoundError as e:
        print(f"Correctly caught expected error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    # Test loading multiple reports
    print("\n--- Loading multiple reports ---")
    contents_multiple = loader.load_reports(sample_file_paths)
    if contents_multiple:
        for i, content in enumerate(contents_multiple):
            print(f"Report {i+1} (from list) - First 50 chars: '{content[:50]}...'")
    else:
        print("No reports were successfully loaded from the list.")

    print("\nExample usage of AnnualReportLoader complete.")
    # Consider cleaning up dummy files, but for now, they are left for inspection.
    # e.g., import shutil; shutil.rmtree(dummy_dir)
    # print(f"Dummy directory '{dummy_dir}' and its contents have been left for inspection.")
