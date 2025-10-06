#!/bin/bash

# Tencent COS Configuration Test Script
# This script tests your Tencent COS configuration by listing objects in the root directory

set -e  # Exit on any error

echo "Tencent COS Configuration Test Script"
echo "====================================="
echo

# Configuration - Update these values to match your Tencent COS setup
BUCKET_NAME=""
REGION="ap-singapore"  # or your region
SECRET_ID=""
SECRET_KEY=""

echo "Configuration:"
echo "  Bucket Name: $BUCKET_NAME"
echo "  Region: $REGION"
echo "  Secret ID: ${SECRET_ID:0:8}..."  # Show only first 8 chars for security
echo

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ ERROR: Python 3 is not installed or not in PATH"
    exit 1
fi

echo "✓ Python 3 found"

# Check if cos-python-sdk-v5 is installed
echo "Checking if cos-python-sdk-v5 is installed..."
if ! python3 -c "import qcloud_cos" &> /dev/null; then
    echo "❌ cos-python-sdk-v5 is not installed"
    echo
    echo "Installing cos-python-sdk-v5..."
    if command -v pip3 &> /dev/null; then
        pip3 install cos-python-sdk-v5
    else
        python3 -m pip install cos-python-sdk-v5
    fi

    if [ $? -ne 0 ]; then
        echo "❌ Failed to install cos-python-sdk-v5"
        echo "Please install it manually: pip3 install cos-python-sdk-v5"
        exit 1
    fi
    echo "✓ cos-python-sdk-v5 installed successfully"
else
    echo "✓ cos-python-sdk-v5 is already installed"
fi

echo
echo "Testing COS configuration..."

# Export environment variables for the Python script
export COS_BUCKET_NAME="$BUCKET_NAME"
export COS_REGION="$REGION"
export COS_SECRET_ID="$SECRET_ID"
export COS_SECRET_KEY="$SECRET_KEY"

# Run the Python script to test the configuration
python3 list_cos_objects.py

