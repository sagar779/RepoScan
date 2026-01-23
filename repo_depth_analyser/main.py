import argparse
import os
import sys
from src.scanner import Scanner
from src.reporter import Reporter

def main():
    print("=== RepoScan Utility ===")
    
    # Check if arguments provided
    if len(sys.argv) > 1:
        parser = argparse.ArgumentParser(description="Repo Depth Analyser - Metadata & Structure Scan")
        parser.add_argument('path', help="Path to the target directory to scan")
        parser.add_argument('--output', help="Path to output directory", default='output')
        args = parser.parse_args()
        target_path = args.path
        output_path = args.output
    else:
        # Interactive Mode
        print("\nInteractive Mode (No arguments detected)")
        target_path = input("Enter the full path of the folder to scan: ").strip().strip('"').strip("'")
        output_path = input("Enter output directory name [default: output]: ").strip()
        if not output_path:
            output_path = 'output'

    
    target_path = os.path.abspath(target_path)
    output_path = os.path.abspath(output_path)
    
    if not os.path.exists(target_path):
        print(f"Error: Target path '{target_path}' does not exist.")
        if len(sys.argv) <= 1: input("Press Enter to exit...")
        sys.exit(1)
        
    print(f"\nStarting analysis on: {target_path}")
    
    # Initialize components
    scanner = Scanner(target_path)
    reporter = Reporter(output_path)
    
    # Run scan
    inventory, dir_stats, ajax_details = scanner.scan()
    
    if not inventory:
        print("No files found to report.")
        if len(sys.argv) <= 1: input("Press Enter to exit...")
        return

    # Generate Report
    report_file = reporter.generate_report(inventory, dir_stats, ajax_details)
    
    if report_file:
        print(f"\nSUCCESS! Tracker created: {report_file}")
        if len(sys.argv) <= 1: input("Press Enter to exit...")

if __name__ == "__main__":
    main()
