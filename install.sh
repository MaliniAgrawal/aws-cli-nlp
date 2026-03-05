#!/bin/bash
echo "=== Starting Installation for aws-cli-nlp ==="

# 1. Create Virtual Environment
python3 -m venv venv

# 2. Install Dependencies
source venv/bin/activate
pip install --upgrade pip
if [ -f requirements.txt ]; then
    pip install -r requirements.txt
    echo "=== Installation Complete! ==="
else
    echo "Warning: requirements.txt not found."
fi
