#!/bin/bash
echo "=== RepoScan Linux Launcher ==="

# 1. Setup Environment
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
# Interactive mode in main.py will handle the prompt
python3 main.py

# 5. Cleanup (Optional - uncomment if you want ephemeral runs)
# deactivate
# rm -rf venv
echo "=== Done ==="
