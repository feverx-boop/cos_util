#!/usr/bin/env python3
"""
Script to list objects in Tencent COS bucket root directory ("/")
to verify configuration is working correctly.
"""

import os
import sys
from qcloud_cos import CosConfig, CosS3Client

def list_cos_objects(bucket_name, region, secret_id, secret_key, prefix="/"):
    """
    List objects in COS bucket with given prefix.

    Args:
        bucket_name (str): COS bucket name
        region (str): COS region
        secret_id (str): Tencent Cloud Secret ID
        secret_key (str): Tencent Cloud Secret Key
        prefix (str): Object prefix to list (default: "/")

    Returns:
        list: List of object keys
    """
    try:
        # Create COS configuration
        config = CosConfig(
            Region=region,
            SecretId=secret_id,
            SecretKey=secret_key
        )

        # Create COS client
        client = CosS3Client(config)

        # List objects
        response = client.list_objects(
            Bucket=bucket_name,
            Prefix=prefix,
            Delimiter="",  # List all objects, not just directories
            MaxKeys=1000  # Maximum number of objects to return
        )

        objects = []
        if 'Contents' in response:
            for obj in response['Contents']:
                objects.append(obj['Key'])

        return objects

    except Exception as e:
        print(f"Error listing COS objects: {e}")
        return None

def main():
    # Configuration - these should match your cos_test.sh values
    bucket_name = os.getenv('COS_BUCKET_NAME', 'property-property-cos-website-one-property-1359404038')
    region = os.getenv('COS_REGION', 'ap-singapore')
    secret_id = os.getenv('COS_SECRET_ID', 'IKIDOo13rRXR7ZrwnSu88tQkpxwDMSQCl8KM')
    secret_key = os.getenv('COS_SECRET_KEY', 'vc8UfcLsJYaR8c5c0EHAwkojW8XqzwgG')

    print("Tencent COS Configuration Test")
    print("=" * 40)
    print(f"Bucket: {bucket_name}")
    print(f"Region: {region}")
    print(f"Secret ID: {secret_id[:8]}...")  # Only show first 8 chars for security
    print()

    # Test connection by listing objects in root directory
    print("Listing objects in root directory (\"/\")...")
    print("-" * 40)

    objects = list_cos_objects(bucket_name, region, secret_id, secret_key, prefix="")

    if objects is not None:
        if objects:
            print(f"✓ Configuration is correct! Found {len(objects)} object(s):")
            for obj in objects[:10]:  # Show first 10 objects
                print(f"  - {obj}")
            if len(objects) > 10:
                print(f"  ... and {len(objects) - 10} more objects")
        else:
            print("✓ Configuration is correct! Bucket is accessible but empty in root directory.")
        print()
        print("✓ SUCCESS: Tencent COS configuration is working correctly!")
        return 0
    else:
        print("✗ FAILED: Unable to access COS bucket. Please check your configuration.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
