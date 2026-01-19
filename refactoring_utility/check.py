import os
import re
import argparse
from openpyxl import Workbook
from openpyxl.styles import PatternFill, Font

def get_refactorability(filename, content):
    """
    Analyzes code content and filename to determine refactorability status.
    Returns: (Status, Refactorability, Reason)
    """
    # 1. Critical Blockers: Server-Side Syntax
    server_patterns = [
        (r'<%', 'ASP.NET/Classic ASP tags detected'),
        (r'@Model', 'Razor Model syntax detected'),
        (r'@ViewBag', 'Razor ViewBag syntax detected'),
        (r'\{\{', 'Potential Template Syntax ({{) detected'),
        (r'\bResponse\.Write\b', 'Server-side Response.Write detected')
    ]
    
    for pattern, reason in server_patterns:
        if re.search(pattern, content):
            return "Blocked", "Low", f"Contains server-side logic: {reason}"

    # 2. Medium Complexity: Event Handlers and DOM Dependency
    # Check filename for event types
    if any(x in filename.lower() for x in ['onclick', 'onload', 'onmouseover', 'onchange', 'onsubmit']):
        return "Needs Rewrite", "Medium", "Event Handler: Requires moving to addEventListener"
        
    if 'document.write' in content:
        return "Needs Rewrite", "Medium", "Uses document.write (unsafe/deprecated)"

    # 3. High Refactorability: Standard Logic
    return "Ready", "High", "Standard logic, safe to extract"

def analyze_folder(folder_path, sheet, file_type):
    """
    Scans a folder and populates the Excel sheet.
    """
    # Header
    headers = ["File Name", "Refactorability", "Status", "Reason", "Snippet (First 100 chars)"]
    sheet.append(headers)
    
    # Style Header
    for cell in sheet[1]:
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill(start_color="4F81BD", end_color="4F81BD", fill_type="solid")

    if not os.path.exists(folder_path):
        return

    for root, _, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
            except Exception as e:
                print(f"Error reading {file}: {e}")
                continue

            status, refactorability, reason = get_refactorability(file, content)
            snippet = content[:100].replace('\n', ' ').strip()
            
            row = [file, refactorability, status, reason, snippet]
            sheet.append(row)
            
            # Color coding based on Status
            status_cell = sheet.cell(row=sheet.max_row, column=3)
            if status == "Blocked":
                 status_cell.fill = PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid") # Red
                 status_cell.font = Font(color="9C0006")
            elif status == "Needs Rewrite":
                 status_cell.fill = PatternFill(start_color="FFEB9C", end_color="FFEB9C", fill_type="solid") # Yellow
                 status_cell.font = Font(color="9C6500")
            else:
                 status_cell.fill = PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid") # Green
                 status_cell.font = Font(color="006100")


    
def generate_report(extracted_path, output_path):
    """
    Generates the Refactoring Assessment Excel report.
    """
    wb = Workbook()
    
    # JavaScript Sheet
    ws_js = wb.active
    ws_js.title = "JavaScript Assessment"
    js_path = os.path.join(extracted_path, "inline_javascript")
    analyze_folder(js_path, ws_js, "JS")
    
    # CSS Sheet
    ws_css = wb.create_sheet("CSS Assessment")
    css_path = os.path.join(extracted_path, "inline_css")
    analyze_folder(css_path, ws_css, "CSS")
    
    # Save
    try:
        wb.save(output_path)
        print(f"Assessment report generated: {output_path}")
    except Exception as e:
        print(f"Failed to save report: {e}")

def main():
    parser = argparse.ArgumentParser(description="Analyze extracted code for refactorability.")
    parser.add_argument("--extracted", required=True, help="Path to 'extracted_code' folder")
    parser.add_argument("--output", required=False, help="Path for the output Excel file (default: parent of extracted folder)")
    
    args = parser.parse_args()
    
    # Default output path if not specified
    if not args.output:
        # If extracted is "output/extracted_code", we want "output/Refactoring_Assessment.xlsx"
        parent_dir = os.path.dirname(os.path.normpath(args.extracted))
        args.output = os.path.join(parent_dir, "Refactoring_Assessment.xlsx")
    
    generate_report(args.extracted, args.output)

if __name__ == "__main__":
    main()
