#!/bin/bash

# Update package list and install necessary system packages
sudo apt update

python3 -m venv reader-env
source reader-env/bin/activate

# Install Python packages from requirements.txt
pip3 install -r requirements.txt