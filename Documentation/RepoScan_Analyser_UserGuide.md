# RepoScan-Analyser User Guide

## Overview
**RepoScan-Analyser** is a tool to scan legacy .NET web apps (ASP.NET, MVC, Classic ASP) to find and catalogue JavaScript, CSS, and AJAX code. It tells you how difficult it will be to migrate to a modern framework (React/Angular).

## Installation
Prerequisites: Python 3.9+
```bash
pip install -r requirements.txt
```

## Commands

### 1. Static Scan (File System)
Scans a local folder for all code.
```bash
python main.py --root "C:\Path\To\Your\Project" --static-analysis
```

### 2. Dynamic Scan (Crawler)
Crawls a running URL to find AJAX calls and external scripts.
```bash
python main.py --url "http://localhost:3000" --dynamic-analysis
```

### 3. Combined Analysis (Best Coverage)
Runs both static scan and dynamic crawler.
```bash
python main.py --root "C:\Path\To\Your\Project" --url "http://localhost:3000" --all
```

## Options
| Flag | Description | Required For |
| :--- | :--- | :--- |
| `--root` | Path to the source code folder. | Static Scan |
| `--url` | Full URL of the running application. | Dynamic Scan |
| `--output` | Folder to save reports (default: `./output`). | Optional |
| `--static-analysis` | Run file system scan. | Mode Selection |
| `--dynamic-analysis` | Run URL crawler. | Mode Selection |
| `--all` | Run both modes. | Mode Selection |

## Expected Output (`output/` folder)

| File Name | Description |
| :--- | :--- |
| **`Code_Inventory.xlsx`** | **The Master List**. Contains every script block, inline `onclick`, and `.js` file found. |
| **`Refactoring_Tracker.xlsx`** | **The Migration Plan**. Tells you if code is "Ready to Move" (Green) or "Blocked" by server-code (Red). |
| **`Dynamic_Analysis_Report.xlsx`** | **Network Analysis**. Shows AJAX calls found by the crawler and matches them to source code. |
| **`extracted_code/`** | **The Code Files**. A folder containing all the extracted JavaScript and CSS code, organized by file type. |
