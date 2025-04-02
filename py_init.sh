#!/bin/bash

# Update package list and install necessary system packages
apt-get update
apt-get install -y libasound-dev libportaudio2 libportaudiocpp0 portaudio19-dev gcc

# Install Python packages from requirements.txt
pip3 install -r requirements.txt