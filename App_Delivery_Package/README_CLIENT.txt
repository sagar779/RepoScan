==================================================
RepoScan - .NET & Modern Web Scope Analysis Tool
==================================================

WHAT IS THIS?
This tool scans your codebase to identify all AJAX calls, Technical Debt, 
Legacy Patterns, and Modern Dependencies. It produces a detailed Excel report.

--------------------------------------------------
HOW TO USE (WINDOWS)
--------------------------------------------------
1. Double-click "RepoScan.exe".
2. If no arguments are provided, it will ask for:
   - The path to scan (e.g., C:\Projects\MyApp)
   - The output folder name
3. Check the created folder for your "Application_Depth_Tracker.xlsx".

--------------------------------------------------
HOW TO USE (LINUX / MAC)
--------------------------------------------------
OPTION 1: Standalone Binary (Recommended)
1. Make executable: chmod +x RepoScan_Linux
2. Run: ./RepoScan_Linux
   (No Python installation required!)

OPTION 2: Script-based (If binary doesn't work)
1. Run: ./run_linux.sh
   (This will auto-unzip source code, install dependencies, and launch)

--------------------------------------------------
OUTPUT LOCATION (IMPORTANT)
--------------------------------------------------
By default, the tool creates a new folder named "output" in the same directory 
where you are running the executable.

Example:
If you run RepoScan.exe from "Downloads", the report will be at:
  Downloads\output\Application_Depth_Tracker_YYYYMMDD_HHMMSS.xlsx

Interactive Mode:
When asked "Enter output directory name", you can type a specific name 
(e.g., "MyClientScan") and it will create that folder instead.

--------------------------------------------------
REQUIREMENTS
--------------------------------------------------
- Windows: None (Everything is included in .exe)
- Linux: Python 3.x installed. The script handles the rest.
