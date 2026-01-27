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
from src.reporter import Reporter
from src.logger import setup_logger
from src.crawler.crawler import Crawler
from src.crawler.tracker import CorrelationTracker
try:
    from refactoring_utility.check import generate_report
except ImportError:
    generate_report = None
    logging.warning("Could not import refactoring_utility.check. Assessment tracker will not be generated.")

def cleanup_old_reports(output_folder: str):
    """Removes previous scan reports to keep the output folder clean."""
    if not os.path.exists(output_folder):
        return
        
    pattern = os.path.join(output_folder, "Analysis.xlsx")
    files = glob.glob(pattern)
    if files:
        logging.info(f"Cleaning up old report(s) in {output_folder}...")
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
    print("RepoScan-Analyser v1.0")
    print("Static & Dynamic Assessment Utility")
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

    print(f"Operational Mode: {config.mode.upper()}")

    # Mode Handling
    if config.mode == "static":
        run_static_scan(config)
    elif config.mode == "extract":
        run_extraction(config)
    elif config.mode == "dynamic":
        print(f"\n[Mode: Dynamic] - Running Crawler Only")
        run_dynamic_scan(config)
    elif config.mode == "all":
        print("\n[Mode: ALL] - Running Static Scan + Dynamic Analysis")
        run_static_scan(config)
        # Note: Static scan must complete first to populate findings for correlation, 
        # but current run_static_scan doesn't return findings. 
        # For now, we run them independently or chained if we refactor return types.
        # Assuming run_dynamic_scan handles missing static data gracefully (as 'New' findings).
        run_dynamic_scan(config)
    
    print("\nDone.")

def run_static_scan(config):
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

            print("Reports generation successful.")
            print("- Code_Inventory.xlsx")
            print("- Refactoring_Tracker.xlsx")
            print("- Crawler_Input.xlsx")

        except Exception as e:
            logging.error(f"Failed to generate report: {e}")
            print("Failed to generate report. Check logs.")
    else:
        print("No inline code findings detected. Skipping report generation.")

def run_extraction(config):
    print("\n[Phase: Extraction]")
    print(f"Logic: SELECTIVE extraction based on Master Tracker assessment.")
    print("This feature separates analysis from modification.")
    # In future step: Load Excel, check status, extract only 'Ready' items.
    # reporter.bundle_specific_items(...)
    pass

def run_dynamic_scan(config):
    # 5. Dynamic Analysis
    print("\n[Phase: Dynamic Analysis]")
    
    if not config.target_url:
        print("Error: --url parameter is required for Dynamic Analysis.")
        return

    print(f"Target URL: {config.target_url}")
    print("Starting Crawler...")
    
    try:
        crawler = Crawler(config.target_url)
        crawler.crawl()
        
        assets = crawler.get_assets()
        external = crawler.get_external_assets()
        
        print(f"\nCrawl Complete.")
        print(f"- Internal Assets Found: {len(assets)}")
        print(f"- External Resources: {len(external)}")
        
        # Generate Correlation Report
        # Since we are not passing static findings here (architecture limitation), 
        # we treat all dynamic findings as "New/Web Only" or just list them.
        # Ideally, we would load 'Code_Inventory.xlsx' to correlate.
        
        print("Generating Correlation Report...")
        tracker = CorrelationTracker()
        output_file = os.path.join(config.output_folder, "Correlation_Report.xlsx")
        
        # Matches = [] (No static correlation yet in this mode)
        # New Findings = Assets found
        # Missing = []
        
        # Convert assets to dict format expected by tracker
        new_findings = []
        for url, asset_type in assets:
            new_findings.append({
                'endpoint_url': url,
                'ajax_type': asset_type,
                'dynamic_url': url,
                'snippet': f"Discovered via Crawl: {url}"
            })
            
        tracker.generate_report(matches=[], new_findings=new_findings, missing_findings=[], external_assets=external, output_path=output_file)
        
    except Exception as e:
        logging.error(f"Dynamic Analysis failed: {e}")
        print(f"Dynamic Analysis failed. Check logs.")

if __name__ == "__main__":
    main()
