import argparse
import os
import sys
import time
from datetime import datetime
from src.scanner import Scanner
from src.reporter import Reporter

def get_banner():
    """Generate professional branded banner string"""
    width = 80
    # ASCII Art for "RepoScan"
    ascii_art = r"""
 ____                  ____                  
|  _ \ ___ _ __   ___ / ___|  ___ __ _ _ __  
| |_) / _ \ '_ \ / _ \\___ \ / __/ _` | '_ \ 
|  _ <  __/ |_) | (_) |___) | (_| (_| | | | |
|_| \_\___| .__/ \___/|____/ \___\__,_|_| |_|
          |_|                                
"""
    banner = ["=" * width]
    for line in ascii_art.splitlines():
        if line.strip():
            banner.append(line.center(width))
    
    banner.append("Software Depth Analysis & Reporting Utility".center(width))
    banner.append("")
    banner.append("RepoScan v1.0. Property owned by Castellum Labs.".center(width))
    banner.append("Authors: Gopikrishna Manikyala, Sushanth Pasham, Brijith K Biju".center(width))
    banner.append("=" * width)
    return "\n".join(banner)

def print_footer(summary_stats, output_file, header_info=""):
    """Display completion footer with summary and save full execution log to text file"""
    
    summary_text = f"""
{'=' * 66}
           Castellum Labs RepoScan - Analysis Complete
{'=' * 66}

SCAN SUMMARY:
{'-' * 66}
  Total Files Scanned:      {summary_stats.get('total_files', 0):,}
  Total Directories:        {summary_stats.get('total_dirs', 0):,}
  Total File Size:          {summary_stats.get('total_size_mb', 0):.2f} MB
  Lines of Code:            {summary_stats.get('total_lines', 0):,}

  AJAX Calls Detected:      {summary_stats.get('ajax_calls', 0):,}
  Inline CSS:               {summary_stats.get('inline_css', 0):,}
  Inline JS:                {summary_stats.get('inline_js', 0):,}
  Internal Style Blocks:    {summary_stats.get('internal_css', 0):,}
  Internal Script Blocks:   {summary_stats.get('internal_js', 0):,}
  External Stylesheets:     {summary_stats.get('external_css', 0):,}
  External Scripts:         {summary_stats.get('external_js', 0):,}
{'-' * 66}

Output Location:
  {output_file}

Analysis complete. Report ready for review.
"""
    print(summary_text)
    
    # Save to file (Banner + Start Info + Summary)
    try:
        full_log = (header_info + "\n" + summary_text) if header_info else summary_text
        output_dir = os.path.dirname(output_file)
        summary_path = os.path.join(output_dir, "scan_summary.txt")
        with open(summary_path, "w", encoding='utf-8') as f:
            f.write(full_log)
    except Exception as e:
        print(f"Warning: Could not save summary text file: {e}")

def main():
    start_time_obj = datetime.now()
    start_time = time.time()
    
    # Display banner
    banner = get_banner()
    print(banner)
    
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
    
    # Clean paths
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
    
    # Prepare Start Info
    start_info = f"""
Starting scan...
  Target: {target_path}
  Output: {output_path}
  Time:   {start_time_obj.strftime('%Y-%m-%d %H:%M:%S')}
  Mode:   {'Verbose (detailed progress)' if verbose else 'Standard (summary only)'}
"""
    print(start_info)
    print("=" * 66)
    
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
    total_lines = sum(item.get('Line_Count', 0) for item in inventory)
    total_size_kb = sum(item.get('Size_KB', 0) for item in inventory)
    total_size_mb = total_size_kb / 1024
    
    inline_css = sum(item.get('Inline_CSS_Count', 0) for item in inventory)
    inline_js = sum(item.get('Inline_JS_Count', 0) for item in inventory)
    internal_css = sum(item.get('Internal_Style_Blocks_Count', 0) for item in inventory)
    internal_js = sum(item.get('Internal_Script_Blocks_Count', 0) for item in inventory)
    external_css = sum(item.get('External_Stylesheet_Links_Count', 0) for item in inventory)
    external_js = sum(item.get('External_Script_Tags_Count', 0) for item in inventory)
    
    summary_stats = {
        'total_files': total_files,
        'total_dirs': total_dirs,
        'ajax_calls': ajax_calls,
        'total_lines': total_lines,
        'total_size_mb': total_size_mb,
        'inline_css': inline_css,
        'inline_js': inline_js,
        'internal_css': internal_css,
        'internal_js': internal_js,
        'external_css': external_css,
        'external_js': external_js
    }
    
    # Generate Report
    print("\nGenerating Excel report...")
    report_file = reporter.generate_report(inventory, dir_stats, ajax_details)
    
    elapsed_time = time.time() - start_time
    print(f"  Completed in {elapsed_time:.2f} seconds")
    
    if report_file:
        header_for_log = banner + "\n" + start_info
        print_footer(summary_stats, report_file, header_info=header_for_log)
        if len(sys.argv) <= 1: input("Press Enter to exit...")

if __name__ == "__main__":
    main()
