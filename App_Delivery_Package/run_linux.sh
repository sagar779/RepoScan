#!/bin/bash
echo "=== RepoScan Linux Launcher ==="

# 1. Setup Environment
APP_DIR="_reposcan_app"

# Clean start
if [ -d "$APP_DIR" ]; then
    rm -rf "$APP_DIR"
fi
mkdir "$APP_DIR"

# Unzip Source
if [ -f "source_code.zip" ]; then
    echo "[*] Unpacking application..."
    unzip -q source_code.zip -d "$APP_DIR"
else
    echo "Error: source_code.zip not found!"
    exit 1
fi

cd "$APP_DIR"

if [ ! -d "venv" ]; then
    echo "[*] Creating virtual environment..."
    python3 -m venv venv
fi

# 2. Activate
source venv/bin/activate

# 3. Install Requirements
echo "[*] Ensuring dependencies..."
pip install -r requirements.txt --quiet --disable-pip-version-check

# 4. Run Tool
python3 main.py

# 5. Cleanup
deactivate
cd ..
# Optional: rm -rf "$APP_DIR" to keep it clean, but keeping it speeds up next run? 
# User wants "clean venvs if needed", so maybe we keep it unless user deletes.
# Actually, rebuilding every time ensures "clean" state. Let's keep it clean or make it robust.
# Let's leave it there for now so inspection is possible.
echo "=== Done ==="
