import sys
import os
import shutil
import time
import glob
import logging
from src.config import parse_arguments
from src.scanner import Scanner
from src.reader import FileReader
from src.parser import Parser
from src.reporter import Reporter
from src.logger import setup_logger

def cleanup_old_reports(output_folder: str):
    """Removes previous scan reports to keep the output folder clean."""
    if not os.path.exists(output_folder):
        return
        
    pattern = os.path.join(output_folder, "InlineCode_Scan_*.xlsx")
    files = glob.glob(pattern)
    if files:
        logging.info(f"Cleaning up {len(files)} old report(s) in {output_folder}...")
        for f in files:
            try:
                os.remove(f)
            except OSError as e:
                logging.error(f"Could not delete {f}: {e}")
    
    # Clean up extracted_code folder
    extracted_code_dir = os.path.join(output_folder, "extracted_code")
    if os.path.exists(extracted_code_dir):
        try:
            logging.info(f"Removing old extracted code in {extracted_code_dir}...")
            shutil.rmtree(extracted_code_dir)
        except OSError as e:
            logging.error(f"Could not delete extracted codes directory {extracted_code_dir}: {e}")

def main():
    # 0. Setup Logging
    logger, log_file = setup_logger()
    
    print("="*60)
    print("Inline Code Detection Utility")
    print("="*60)
    print(f"Error Logs: {os.path.abspath(log_file)}")

    # 1. Configuration
    try:
        config = parse_arguments()
        
        # Ensure Output Directory Exists
        if not os.path.exists(config.output_folder):
            os.makedirs(config.output_folder)
            
        print(f"Root Folder: {os.path.abspath(config.root_folder)}")
        print(f"Output Folder: {os.path.abspath(config.output_folder)}")
        
        # Cleanup before starting
        cleanup_old_reports(config.output_folder)
        
    except ValueError as e:
        logging.error(f"Configuration Error: {e}")
        sys.exit(1)

    # 2. Scanning
    print("\n[Phase 1] Discovery...")
    try:
        scanner = Scanner(config)
        files_to_scan = list(scanner.scan())
        print(f"Found {len(files_to_scan)} files to process.")
    except Exception as e:
        logging.error(f"Scanning failed: {e}")
        sys.exit(1)

    parser = Parser()
    all_findings = []
    
    # 3. Processing
    print("\n[Phase 2] Analysis...")
    processed_count = 0
    start_time = time.time()

    for file_path in files_to_scan:
        processed_count += 1
        
        if processed_count % 10 == 0 or processed_count == len(files_to_scan):
            sys.stdout.write(f"\rProcessing: {processed_count}/{len(files_to_scan)}")
            sys.stdout.flush()

        # Read
        content, encoding = FileReader.read_file(file_path)
        if content is None:
            logging.warning(f"Skipping file {file_path}: {encoding}")
            continue

        # Parse
        try:
            findings = parser.parse(file_path, content)
            all_findings.extend(findings)
        except Exception as e:
            logging.error(f"Error parsing {file_path}: {e}")

    duration = time.time() - start_time
    print(f"\n\nAnalysis complete in {duration:.2f} seconds.")
    print(f"Total findings: {len(all_findings)}")

    # 4. Reporting
    print("\n[Phase 3] Generating Report...")
    if all_findings:
        try:
            reporter = Reporter(config, all_findings)
            reporter.generate_report()
            print("Report generation successful.")
        except Exception as e:
            logging.error(f"Failed to generate report: {e}")
            print("Failed to generate report. Check logs.")
    else:
        print("No inline code findings detected. Skipping report generation.")

    print("\nDone.")

if __name__ == "__main__":
    main()
