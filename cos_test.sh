#!/bin/bash

# Export environment variables for the Python script
export COS_BUCKET_NAME=""
export COS_REGION="ap-singapore"
export COS_SECRET_ID=""
export COS_SECRET_KEY=""

# Run the Python script to test the configuration
python3 list_cos_objects.py

