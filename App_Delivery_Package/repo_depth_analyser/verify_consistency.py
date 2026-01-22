"""
Consistency Verification Tool
Compares manual PowerShell check results with tool output to detect discrepancies.
"""

import pandas as pd
import os
import sys
import glob
from datetime import datetime


class ConsistencyVerifier:
    def __init__(self, excel_path, manual_results):
        """
        Initialize verifier with tool output and manual check results.
        
        Args:
            excel_path: Path to the Application_Depth_Tracker Excel file
            manual_results: Dictionary with manual check counts
        """
        self.excel_path = excel_path
        self.manual_results = manual_results
        self.tool_results = {}
        self.discrepancies = []
        
    def load_tool_output(self):
        """Load complexity metrics from the tool's Excel output."""
        try:
            df = pd.read_excel(self.excel_path, sheet_name='Complexity_Metrics')
            
            # Sum up all counts from the tool
            self.tool_results = {
                'Inline_CSS': df['Inline_CSS_Count'].sum(),
                'Internal_Style': df['Internal_Style_Blocks_Count'].sum(),
                'Inline_JS': df['Inline_JS_Count'].sum(),
                'Internal_Script': df['Internal_Script_Blocks_Count'].sum(),
                'Ajax_Calls': df['AJAX_Calls_Count'].sum(),
                'Dynamic_JS': df['Dynamic_JS_Gen_Count'].sum(),
                'Dynamic_CSS': df['Dynamic_CSS_Gen_Count'].sum()
            }
            
            print(f"✓ Loaded tool output from: {self.excel_path}")
            return True
        except Exception as e:
            print(f"✗ Error loading tool output: {e}")
            return False
    
    def compare_results(self):
        """Compare manual vs tool results and identify discrepancies."""
        print("\n" + "="*70)
        print("CONSISTENCY VERIFICATION REPORT")
        print("="*70)
        
        # Map manual keys to tool keys
        metric_mapping = {
            'Inline_CSS': 'Inline_CSS',
            'Internal_Style': 'Internal_Style',
            'Inline_JS': 'Inline_JS',
            'Internal_Script': 'Internal_Script',
            'Ajax_Calls': 'Ajax_Calls'
        }
        
        all_match = True
        
        for manual_key, tool_key in metric_mapping.items():
            manual_count = self.manual_results.get(manual_key, 0)
            tool_count = self.tool_results.get(tool_key, 0)
            
            match = "✓" if manual_count == tool_count else "✗"
            status = "MATCH" if manual_count == tool_count else "MISMATCH"
            
            print(f"\n{match} {manual_key}:")
            print(f"   Manual Check: {manual_count}")
            print(f"   Tool Output:  {tool_count}")
            print(f"   Difference:   {tool_count - manual_count}")
            print(f"   Status:       {status}")
            
            if manual_count != tool_count:
                all_match = False
                self.discrepancies.append({
                    'Metric': manual_key,
                    'Manual': manual_count,
                    'Tool': tool_count,
                    'Difference': tool_count - manual_count
                })
        
        # Additional metrics only in tool output
        print(f"\n--- Additional Tool Metrics (No Manual Comparison) ---")
        print(f"   Dynamic_JS_Gen:  {self.tool_results.get('Dynamic_JS', 0)}")
        print(f"   Dynamic_CSS_Gen: {self.tool_results.get('Dynamic_CSS', 0)}")
        
        print("\n" + "="*70)
        if all_match:
            print("✓ ALL METRICS MATCH - 100% Consistency Verified!")
        else:
            print(f"✗ DISCREPANCIES FOUND - {len(self.discrepancies)} metric(s) mismatch")
            print("\nRecommended Actions:")
            print("1. Review the files listed in Complexity_Metrics tab")
            print("2. Check if manual regex patterns match tool patterns")
            print("3. Verify file extensions being scanned")
        print("="*70)
        
        return all_match
    
    def generate_discrepancy_report(self, output_dir='output'):
        """Generate a detailed discrepancy report if mismatches found."""
        if not self.discrepancies:
            print("\n✓ No discrepancies to report.")
            return None
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = os.path.join(output_dir, f"Consistency_Report_{timestamp}.txt")
        
        with open(report_path, 'w') as f:
            f.write("="*70 + "\n")
            f.write("CONSISTENCY VERIFICATION DISCREPANCY REPORT\n")
            f.write("="*70 + "\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Tool Output: {self.excel_path}\n\n")
            
            f.write("DISCREPANCIES FOUND:\n")
            f.write("-"*70 + "\n")
            for disc in self.discrepancies:
                f.write(f"\nMetric: {disc['Metric']}\n")
                f.write(f"  Manual Check: {disc['Manual']}\n")
                f.write(f"  Tool Output:  {disc['Tool']}\n")
                f.write(f"  Difference:   {disc['Difference']}\n")
            
            f.write("\n" + "="*70 + "\n")
            f.write("RECOMMENDATIONS:\n")
            f.write("1. Review Complexity_Metrics tab for file-level details\n")
            f.write("2. Cross-check regex patterns in manual_check.ps1 vs scanner.py\n")
            f.write("3. Verify excluded folders and file extensions\n")
            f.write("4. Check for encoding issues in specific files\n")
        
        print(f"\n✓ Discrepancy report saved: {report_path}")
        return report_path


def find_latest_tracker(output_dir='output'):
    """Find the most recent Application_Depth_Tracker Excel file."""
    pattern = os.path.join(output_dir, "Application_Depth_Tracker_*.xlsx")
    files = glob.glob(pattern)
    
    if not files:
        return None
    
    # Sort by modification time, most recent first
    latest = max(files, key=os.path.getmtime)
    return latest


def main():
    """
    Main entry point for consistency verification.
    
    Usage:
        python verify_consistency.py <manual_inline_css> <manual_internal_style> <manual_inline_js> <manual_internal_script> <manual_ajax>
    
    Example:
        python verify_consistency.py 45 12 78 23 15
    """
    
    if len(sys.argv) < 6:
        print("Usage: python verify_consistency.py <inline_css> <internal_style> <inline_js> <internal_script> <ajax_calls>")
        print("\nExample: python verify_consistency.py 45 12 78 23 15")
        print("\nOr run manual_check.ps1 first, then provide those counts here.")
        sys.exit(1)
    
    # Parse manual results from command line
    manual_results = {
        'Inline_CSS': int(sys.argv[1]),
        'Internal_Style': int(sys.argv[2]),
        'Inline_JS': int(sys.argv[3]),
        'Internal_Script': int(sys.argv[4]),
        'Ajax_Calls': int(sys.argv[5])
    }
    
    print("Manual Check Results Provided:")
    for key, value in manual_results.items():
        print(f"  {key}: {value}")
    
    # Find latest tracker
    latest_tracker = find_latest_tracker()
    
    if not latest_tracker:
        print("\n✗ Error: No Application_Depth_Tracker Excel file found in output/")
        print("Please run the depth analyzer first: python main.py <target_dir>")
        sys.exit(1)
    
    print(f"\n✓ Found latest tracker: {latest_tracker}")
    
    # Run verification
    verifier = ConsistencyVerifier(latest_tracker, manual_results)
    
    if verifier.load_tool_output():
        all_match = verifier.compare_results()
        
        if not all_match:
            verifier.generate_discrepancy_report()
        
        sys.exit(0 if all_match else 1)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
