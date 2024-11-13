#!/bin/bash

# Create a virtual environment named 'venv' (if it doesn't exist)
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Install dependencies from requirements.txt
pip install -r requirements.txt

echo "Virtual environment is set up and Flask is installed!"
