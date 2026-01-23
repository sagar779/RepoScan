==================================================
RepoScan - Application Depth Analysis Tool
==================================================

RepoScan analyzes your application codebase to measure size, complexity, and technical depth. 
It identifies AJAX patterns, legacy dependencies, modern frameworks, CSS/JavaScript usage, and 
technical debt across your entire project. The tool generates a comprehensive Excel report with 
detailed metrics, file-level analysis, and actionable insights to help assess modernization needs 
and migration planning.

==================================================
WINDOWS USERS
==================================================
1. Double-click "RepoScan.exe"
2. Enter the path to scan when prompted
   Example: C:\Projects\MyApplication
3. Press Enter and wait for completion
4. Find your report in the "output" folder

==================================================
LINUX / MAC USERS
==================================================
1. Make executable: chmod +x RepoScan_Linux
2. Run: ./RepoScan_Linux
3. Enter the path to scan when prompted
   Example: /home/user/projects/myapp
4. Press Enter and wait for completion
5. Find your report in the "output" folder

==================================================
OUTPUT LOCATION
==================================================
By default, the tool creates a folder named "output" in the same 
directory where you run the executable.

Example:
If you run RepoScan.exe from "Downloads", the report will be at:
  Downloads\output\Application_Depth_Tracker_YYYYMMDD_HHMMSS.xlsx

You can specify a custom output folder name when prompted.

==================================================
REQUIREMENTS
==================================================
- Windows: None (Everything included in .exe)
- Linux/Mac: None (Everything included in binary)
