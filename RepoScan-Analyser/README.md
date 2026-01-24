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
Check the `output/` folder for 3 separate trackers:
1.  **`Code_Inventory.xlsx`** (Master Inventory):
    *   **Summary**: Metrics & Volumetrics.
    *   **Inventories**: Lists of all JS, CSS, and External Resources.
    *   **AJAX Code**: Dedicated tab for all API/AJAX calls logic.
    *   **Legend**: Explains metrics like "Dynamic Code" and "Total Issues".
2.  **`Refactoring_Tracker.xlsx`**:
    *   **JS Refactoring**: Traffic Light status for Scripts.
    *   **CSS Refactoring**: Traffic Light status for Styles.
3.  **`Crawler_Input.xlsx`**: Input list for Dynamic Security Scanners (ZAP/Burp).
4.  **`extracted_code/`**:
    *   `inline_js/`: Code extracted from `<script>` tags.
    *   `internal_js/`: Local `.js` files.
    *   `inline_css/`: Code extracted from `<style>` tags.
    *   `internal_css/`: Local `.css` files.

