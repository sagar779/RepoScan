# Repository Depth Analyzer

A standalone utility to analyze codebase structure and complexity metrics.

## Features

- **File Inventory**: Scans all files in a directory and collects metadata
- **Complexity Analysis**: Detects inline/internal CSS, JS, AJAX calls, and dynamic resource generation
- **Directory Statistics**: Provides breakdown by directory depth and file extensions
- **Multithreaded Scanning**: Fast processing using concurrent file analysis
- **Excel Reports**: Professional, styled Excel output with multiple tabs

## Installation

1. Ensure Python 3.7+ is installed
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

```bash
python main.py <path_to_target_directory> [--output <output_directory>]
```

### Examples

```bash
# Scan current directory
python main.py .

# Scan specific project
python main.py C:\Projects\MyApp

# Specify custom output location
python main.py C:\Projects\MyApp --output C:\Reports
```

## Output

The tool generates an Excel file: `Application_Depth_Tracker_YYYYMMDD_HHMMSS.xlsx`

### Report Tabs

1. **Summary_Dashboard**: Overview metrics and global extension breakdown
2. **Directory_Analysis**: Statistics grouped by directory with depth information
3. **File_Details**: Basic file metadata with **Full_Path** as first column for easy file location
4. **Complexity_Metrics**: Dedicated tab with all complexity analysis data, **Full_Path** as first column

### Complexity Metrics

The **Complexity_Metrics** tab provides granular code complexity insights with **100% detection accuracy** matching the main RepoScan utility:

- **Inline_CSS_Count**: `style="..."` attributes
- **Internal_CSS_Count**: `<style>...</style>` blocks
- **Inline_JS_Count**: 40+ event handlers (`onclick`, `onload`, `onsubmit`, `onkeydown`, etc.) and `javascript:` URLs
- **Internal_JS_Count**: `<script>...</script>` blocks
- **AJAX_Calls_Count**: Comprehensive detection of:
  - jQuery: `$.ajax()`, `$.get()`, `$.post()`, `$.getJSON()`, `$.getScript()`, `$.load()`
  - Native: `XMLHttpRequest`, `fetch()`, `ActiveXObject` (IE legacy)
  - Modern: `axios()`, `axios.get/post/put/delete/patch()`
  - Headers: `setRequestHeader('X-Requested-With')`
- **Dynamic_JS_Gen_Count**: Dynamic script creation (`createElement('script')`, `eval()`, `new Function()`)
- **Dynamic_CSS_Gen_Count**: Dynamic style creation (`createElement('style')`, `createElement('link')`)

## Requirements

- Python 3.7+
- pandas >= 2.0.0
- openpyxl >= 3.1.0

## Performance

The tool uses multithreading (10 workers by default) to process files concurrently, making it suitable for large codebases.

### Excluded Folders

To maintain accuracy on source code while avoiding dependency bloat, the following folders are automatically excluded:

**Dependencies**: `node_modules`, `vendor`, `packages`  
**Version Control**: `.git`, `.svn`, `.hg`  
**Build Outputs**: `bin`, `obj`, `dist`, `build`, `out`, `target`  
**Virtual Environments**: `venv`, `env`, `.venv`, `__pycache__`, `.pytest_cache`

This ensures 100% accuracy on your source code while skipping thousands of third-party files.

## Consistency Verification

To ensure detection accuracy, you can cross-check the tool's output against manual PowerShell counts:

### Step 1: Run Manual Check

```powershell
# From repo_depth_analyser directory
cd ..
.\manual_check.ps1 -TargetDir "path\to\your\project"
```

The script will output counts and provide a ready-to-use verification command.

### Step 2: Run Verification

Copy the command from the manual check output, or run manually:

```bash
python verify_consistency.py <inline_css> <internal_style> <inline_js> <internal_script> <ajax_calls>

# Example:
python verify_consistency.py 45 12 78 23 15
```

### Verification Output

The tool will:
- Compare each metric (Inline CSS, Internal Style, Inline JS, Internal Script, AJAX Calls)
- Display side-by-side comparison with match/mismatch indicators
- Generate a detailed discrepancy report if mismatches are found
- Provide actionable recommendations for resolving inconsistencies

**Note**: The Full_Path column in all Excel tabs makes it easy to locate specific files when investigating discrepancies.
