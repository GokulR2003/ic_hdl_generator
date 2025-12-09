#!/bin/bash
# Install dependencies

echo "Installing IC HDL Generator dependencies..."

# Check Python version
python3 --version || { echo "Python3 is required"; exit 1; }

# Install Python packages
pip3 install -r requirements.txt

# Make scripts executable
chmod +x template_engine.py
chmod +x scripts/*.sh

echo "Installation complete!"
echo "Run: python template_engine.py list"
