import argparse
import os
import sys
from src.scanner import Scanner
from src.reporter import Reporter

def main():
    parser = argparse.ArgumentParser(description="Repo Depth Analyser - Metadata & Structure Scan")
    parser.add_argument('path', help="Path to the target directory to scan")
    parser.add_argument('--output', help="Path to output directory", default='output')
    
    args = parser.parse_args()
    
    target_path = os.path.abspath(args.path)
    output_path = os.path.abspath(args.output)
    
    if not os.path.exists(target_path):
        print(f"Error: Target path '{target_path}' does not exist.")
        sys.exit(1)
        
    print(f"Starting analysis on: {target_path}")
    
    # Initialize components
    scanner = Scanner(target_path)
    reporter = Reporter(output_path)
    
    # Run scan
    inventory, dir_stats = scanner.scan()
    
    if not inventory:
        print("No files found to report.")
        return

    # Generate Report
    report_file = reporter.generate_report(inventory, dir_stats)
    
    if report_file:
        print(f"\nSUCCESS! Tracker created: {report_file}")

if __name__ == "__main__":
    main()
