import os
import re
import argparse
from openpyxl import Workbook
from openpyxl.styles import PatternFill, Font, Alignment

def parse_metadata(filename):
    """
    Parses original file info from the extracted filename.
    Format: OriginalPath_Type_lineStart-End.ext
    Returns: (OriginalPath, LineRange, Type)
    """
    try:
        # Match the standard format defined in the tool
        # Example: Views_Home_Index.cshtml_scriptblock_line10-25.js
        match = re.search(r'(.+)_([a-zA-Z0-9]+)_line(\d+)-(\d+)\.(js|css)$', filename)
        if match:
            sanitized, code_type, start, end, ext = match.groups()
            # Best effort to restore path readability (replace underscores with slashes)
            # This is visual only for the report
            orig_path = sanitized.replace('_', '/')
            return orig_path, f"{start}-{end}", code_type
    except:
        pass
    return filename, "Unknown", "Unknown"

def get_refactorability(filename, content):
    """
    Analyzes code content and filename to determine refactorability status.
    Returns: (Status, Complexity, Reason, Action)
    """
    # 1. Critical Blockers: Server-Side Syntax
    server_patterns = [
        (r'<%', 'ASP.NET/Classic ASP tags detected'),
        (r'@Model', 'Razor Model syntax detected'),
        (r'@ViewBag', 'Razor ViewBag syntax detected'),
        (r'@ViewData', 'Razor ViewData syntax detected'),
        (r'@Url\.Action', 'Razor Url.Action detected'),
        (r'@Url\.Content', 'Razor Url.Content detected'),
        (r'<%\s', 'Classic ASP block detected'),
        (r'<%:', 'ASP.NET Output detected'),
        (r'\{\{', 'Potential Template Syntax ({{) detected'),
        (r'\bResponse\.Write\b', 'Server-side Response.Write detected'),
        (r'\bRequest\.Form\b', 'Server-side Request.Form detected')
    ]
    
    for pattern, reason in server_patterns:
        if re.search(pattern, content):
            return "Blocked", "Low", f"Contains server-side logic: {reason}", "NOT MOVED - Requires Manual Fix"

    # 2. Medium Complexity: Event Handlers and DOM Dependency
    # Check filename for event types (onclick, etc.)
    code_type = parse_metadata(filename)[2]
    if 'on' in code_type and 'line' not in code_type: # heuristic for onclick, onload etc
         return "Needs Rewrite", "Medium", "Event Handler: Requires moving to addEventListener", "NOT MOVED - Inserted TODO Comment"
         
    if any(x in filename.lower() for x in ['onclick', 'onload', 'onmouseover', 'onchange', 'onsubmit']):
        return "Needs Rewrite", "Medium", "Event Handler: Requires moving to addEventListener", "NOT MOVED - Inserted TODO Comment"
        
    if 'document.write' in content:
        return "Needs Rewrite", "Medium", "Uses document.write (unsafe/deprecated)", "NOT MOVED - Unsafe Logic"

    # 3. High Refactorability: Standard Logic
    return "Ready", "High", "Standard logic, safe to extract", "EXTERNALIZED - Moved to file"

def analyze_folder(folder_path, sheet, file_type):
    """
    Scans a folder and populates the Excel sheet with enhanced metadata.
    """
    # Enhanced Header
    headers = ["Original File", "Lines", "Code Type", "Complexity", "Status", "Action Taken", "Reason", "Snippet"]
    sheet.append(headers)
    
    # Style Header
    for cell in sheet[1]:
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill(start_color="4F81BD", end_color="4F81BD", fill_type="solid")
        cell.alignment = Alignment(horizontal="center", vertical="center")

    if not os.path.exists(folder_path):
        return

    # Auto-adjust column widths helper
    for i, width in enumerate([40, 15, 15, 12, 15, 30, 40, 50], 1):
        sheet.column_dimensions[chr(64+i)].width = width

    for root, _, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
            except Exception as e:
                print(f"Error reading {file}: {e}")
                continue

            # Parse Metadata
            orig_path, lines, code_type = parse_metadata(file)

            # Analyze
            status, complexity, reason, action = get_refactorability(file, content)
            snippet = content[:150].replace('\n', ' ').strip()
            
            row = [orig_path, lines, code_type, complexity, status, action, reason, snippet]
            sheet.append(row)
            
            # Color coding based on Status (Column E is 5)
            status_cell = sheet.cell(row=sheet.max_row, column=5)
            action_cell = sheet.cell(row=sheet.max_row, column=6)
            
            if status == "Blocked":
                 fill = PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid") # Red
                 font = Font(color="9C0006")
            elif status == "Needs Rewrite":
                 fill = PatternFill(start_color="FFEB9C", end_color="FFEB9C", fill_type="solid") # Yellow
                 font = Font(color="9C6500")
            else:
                 fill = PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid") # Green
                 font = Font(color="006100")
            
            status_cell.fill = fill
            status_cell.font = font
            action_cell.fill = fill # Color action too for visibility

    
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
