import argparse
import os
import sys
import time
from datetime import datetime
from src.scanner import Scanner
from src.reporter import Reporter

def print_banner():
    """Display professional branded banner"""
    width = 66
    banner = f"""
{'=' * width}
{'RepoScan v1.0'.center(width)}
{'Powered by Castellum Labs'.center(width)}
{'Application Depth Analysis & Reporting Tool'.center(width)}
{'=' * width}
"""
    print(banner)

def print_footer(summary_stats, output_file):
    """Display completion footer with summary"""
    print("\n" + "=" * 66)
    print("           Castellum Labs RepoScan - Analysis Complete")
    print("=" * 66)
    print("\nSCAN SUMMARY:")
    print("-" * 66)
    print(f"  Total Files Scanned:    {summary_stats.get('total_files', 0):,}")
    print(f"  Total Directories:      {summary_stats.get('total_dirs', 0):,}")
    print(f"  AJAX Calls Detected:    {summary_stats.get('ajax_calls', 0):,}")
    print(f"  Lines of Code:          {summary_stats.get('total_lines', 0):,}")
    print("-" * 66)
    print(f"\nOutput Location:")
    print(f"  {output_file}")
    print("\nAnalysis complete. Report ready for review.\n")

def main():
    start_time = time.time()
    
    # Display banner
    print_banner()
    
    # Check if arguments provided
    if len(sys.argv) > 1:
        parser = argparse.ArgumentParser(description="RepoScan - Application Depth Analyser")
        parser.add_argument('path', help="Path to the target directory to scan")
        parser.add_argument('--output', help="Path to output directory", default='output')
        args = parser.parse_args()
        target_path = args.path
        output_path = args.output
    else:
        # Interactive Mode
        print("Enter the full path of the code folder to scan:")
        target_path = input("> ").strip().strip('"').strip("'")
        print("\nEnter output directory name [default: output]:")
        output_path = input("> ").strip()
        if not output_path:
            output_path = 'output'

    
    target_path = os.path.abspath(target_path)
    output_path = os.path.abspath(output_path)
    
    if not os.path.exists(target_path):
        print(f"\nError: Target path '{target_path}' does not exist.")
        if len(sys.argv) <= 1: input("\nPress Enter to exit...")
        sys.exit(1)
    
    # Ask for verbose mode (only in interactive mode)
    verbose = False
    if len(sys.argv) <= 1:
        print("\nEnable verbose output? (Show detailed folder scanning progress)")
        verbose_input = input("(y/n) [default: n]: ").strip().lower()
        verbose = verbose_input in ['y', 'yes']
    
    print(f"\nStarting scan...")
    print(f"  Target: {target_path}")
    print(f"  Output: {output_path}")
    print(f"  Time:   {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    if verbose:
        print(f"  Mode:   Verbose (detailed progress)")
    print("\n" + "=" * 66)
    
    # Initialize components
    scanner = Scanner(target_path)
    reporter = Reporter(output_path)
    
    # Run scan
    print("\nAnalyzing codebase structure...")
    inventory, dir_stats, ajax_details = scanner.scan(verbose=verbose)
    
    if not inventory:
        print("\nWarning: No files found to report.")
        if len(sys.argv) <= 1: input("\nPress Enter to exit...")
        return

    # Calculate summary stats
    total_files = len(inventory)
    total_dirs = len(dir_stats)
    ajax_calls = sum(1 for detail in ajax_details if detail.get('Is_Counted') == 'Yes')
    total_lines = sum(item.get('Total_Lines', 0) for item in inventory)
    
    summary_stats = {
        'total_files': total_files,
        'total_dirs': total_dirs,
        'ajax_calls': ajax_calls,
        'total_lines': total_lines
    }
    
    # Generate Report
    print("\nGenerating Excel report...")
    report_file = reporter.generate_report(inventory, dir_stats, ajax_details)
    
    elapsed_time = time.time() - start_time
    print(f"  Completed in {elapsed_time:.2f} seconds")
    
    if report_file:
        print_footer(summary_stats, report_file)
        if len(sys.argv) <= 1: input("Press Enter to exit...")

if __name__ == "__main__":
    main()


