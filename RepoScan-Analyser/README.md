# RepoScan-Analyser v1.0

A professional utility for assessing legacy .NET applications for migration readiness.
Combines Static Analysis and Dynamic Crawling to generate a comprehensive "Master Migration Tracker".

## Features
*   **Inventory Scan**: Catalogues all Inline JS, CSS, and AJAX calls.
*   **Logic Analysis**: Calculates "Logic Density" and "Server Dependency Severity".
*   **Refactoring Assessment**: Generates a developer checklist with Traffic Light status (Ready/Rewrite/Blocked).
*   **.NET Optimized**: Specific detection for Razor, WebForms, and legacy patterns.

## Installation
1.  Ensure Python 3.9+ is installed.
2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Usage (PowerShell/Command Prompt)

### 1. Static Scan (--static-analysis)
Scans the root, generates `Master_Tracker.xlsx` (Inventory + Logic Map + Checklist).
```powershell
python main.py --root "C:\Path\To\LegacyApp" --static-analysis
```

### 2. Dynamic Scan (--dynamic-analysis)
*Requires `Target URL`*. Runs crawler to find external scripts/CSP issues.
```powershell
python main.py --root "C:\Path\To\LegacyApp" --url "http://localhost/App" --dynamic-analysis
```

### 3. Extraction (--extract)
Reads `Master_Tracker.xlsx` and physically extracts code marked as "Ready" or "Rewrite" into the `extracted_code/` folder.
```powershell
python main.py --root "C:\Path\To\LegacyApp" --extract
```

### 4. Combined / All (--all)
Runs Static Scan followed immediately by Extraction.
```powershell
python main.py --root "C:\Path\To\LegacyApp" --all
```

## Output Artifacts
Check the `output/` folder for 4 separate trackers:
1.  `Code_Inventory.xlsx`: Summary, Inline JS/CSS inventory, and External resources.
2.  `AJAX_Assessment.xlsx`: Dedicated analysis of all AJAX calls and logic.
3.  `Refactoring_Tracker.xlsx`: The Developer Checklist with Traffic Light status.
4.  `Crawler_Input.xlsx`: Generated input list for Dynamic Analysis.
5.  `extracted_code/`: Clean `.js` and `.css` files (only if extraction ran).

