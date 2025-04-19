#!/bin/sh

# Activate the virtual environment
source .venv/bin/activate

# Install dependencies within the virtual environment
python -m pip install -r requirements.txt

python main.py