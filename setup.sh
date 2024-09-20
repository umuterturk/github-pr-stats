#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# Create a virtual environment in the 'venv' directory
echo "Creating virtual environment..."
python3 -m venv venv

# Activate the virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install the required packages
echo "Installing dependencies..."
pip install -r requirements.txt

echo "Setup complete. To activate the virtual environment, run:"
echo "source venv/bin/activate"
