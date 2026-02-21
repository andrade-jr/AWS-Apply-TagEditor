#!/usr/bin/env bash

# Stop script if any command fails
set -e

echo "Installing required Python packages..."
pip install --upgrade pip
pip install boto3 pandas openpyxl

echo "Running Python script..."
python IN01001464.py

echo "Done."