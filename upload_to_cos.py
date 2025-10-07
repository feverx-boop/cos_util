#!/usr/bin/env python3
"""
Cross-platform utility to upload a file to Tencent COS.

This script is designed to work on macOS and Windows.

Configuration can be supplied via command-line flags or environment variables:
  - COS_BUCKET_NAME
  - COS_REGION
  - COS_SECRET_ID
  - COS_SECRET_KEY
  - COS_TOKEN (optional, for temporary credentials)

Examples:
  macOS/Linux:
    export COS_BUCKET_NAME="example-1234567890"
    export COS_REGION="ap-singapore"
    export COS_SECRET_ID="AKID..."
    export COS_SECRET_KEY="SECRET..."
    python3 upload_to_cos.py ./dist/app.zip --key releases/app.zip

  Windows (PowerShell):
    $env:COS_BUCKET_NAME = "example-1234567890"
    $env:COS_REGION = "ap-singapore"
    $env:COS_SECRET_ID = "AKID..."
    $env:COS_SECRET_KEY = "SECRET..."
    python upload_to_cos.py .\dist\app.zip --key releases/app.zip
"""

import os
import sys
import argparse
import mimetypes
from typing import Optional

from qcloud_cos import CosConfig, CosS3Client  # type: ignore


def create_client(region: str, secret_id: str, secret_key: str, token: Optional[str] = None) -> CosS3Client:
    config = CosConfig(
        Region=region,
        SecretId=secret_id,
        SecretKey=secret_key,
        Token=token,
    )
    return CosS3Client(config)


def upload_file_to_cos(
    bucket_name: str,
    region: str,
    secret_id: str,
    secret_key: str,
    local_path: str,
    key: Optional[str] = None,
    storage_class: str = "STANDARD",
    content_type: Optional[str] = None,
    part_size_mb: int = 8,
    max_threads: int = 5,
    enable_md5: bool = False,
    acl: Optional[str] = None,
    token: Optional[str] = None,
) -> str:
    """
    Upload a local file to Tencent COS.

    Returns the object key on success.
    """
    if not os.path.isfile(local_path):
        raise FileNotFoundError(f"Local file not found: {local_path}")

    if key is None or not key.strip():
        key = os.path.basename(local_path)

    guessed_type, _ = mimetypes.guess_type(local_path)
    if content_type is None:
        content_type = guessed_type or "application/octet-stream"

    client = create_client(region=region, secret_id=secret_id, secret_key=secret_key, token=token)

    file_size_bytes = os.path.getsize(local_path)

    # Small files: use put_object to set ContentType explicitly
    # Large files: use upload_file for efficient multipart upload
    SMALL_FILE_THRESHOLD = 5 * 1024 * 1024  # 5 MiB

    if file_size_bytes <= SMALL_FILE_THRESHOLD:
        with open(local_path, "rb") as fp:
            extra = {
                "Bucket": bucket_name,
                "Key": key,
                "Body": fp,
                "StorageClass": storage_class,
                "ContentType": content_type,
            }
            if acl:
                extra["ACL"] = acl
            client.put_object(**extra)
    else:
        # For large files, multipart upload. Note: ContentType isn't directly supported in upload_file;
        # most clients infer on download, but we ensure correctness for small files above.
        client.upload_file(
            Bucket=bucket_name,
            LocalFilePath=local_path,
            Key=key,
            PartSize=max(1, int(part_size_mb)),
            MAXThread=max(1, int(max_threads)),
            EnableMD5=bool(enable_md5),
        )

    return key


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Upload a local file to Tencent COS (cross-platform)",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("local_path", help="Path to the local file to upload")
    parser.add_argument("--key", help="Destination object key in COS (defaults to file name)")
    parser.add_argument("--bucket", default=os.getenv("COS_BUCKET_NAME"), help="COS bucket name")
    parser.add_argument("--region", default=os.getenv("COS_REGION"), help="COS region, e.g. ap-singapore")
    parser.add_argument("--secret-id", default=os.getenv("COS_SECRET_ID"), help="Tencent Cloud Secret ID")
    parser.add_argument("--secret-key", default=os.getenv("COS_SECRET_KEY"), help="Tencent Cloud Secret Key")
    parser.add_argument("--token", default=os.getenv("COS_TOKEN"), help="Temporary credential token (optional)")
    parser.add_argument("--storage-class", default="STANDARD", help="COS storage class (STANDARD, STANDARD_IA, ARCHIVE, etc.)")
    parser.add_argument("--content-type", default=None, help="Override Content-Type for small files (<=5MiB)")
    parser.add_argument("--part-size", type=int, default=8, help="Multipart chunk size in MiB for large files")
    parser.add_argument("--threads", type=int, default=5, help="Max worker threads for multipart upload")
    parser.add_argument("--md5", action="store_true", help="Enable MD5 check for multipart upload")
    parser.add_argument("--acl", default=None, help="ACL, e.g. private, public-read")
    parser.add_argument("--dry-run", action="store_true", help="Print planned upload and exit")

    args = parser.parse_args(argv)

    missing = []
    if not args.bucket:
        missing.append("--bucket or COS_BUCKET_NAME")
    if not args.region:
        missing.append("--region or COS_REGION")
    if not args.secret_id:
        missing.append("--secret-id or COS_SECRET_ID")
    if not args.secret_key:
        missing.append("--secret-key or COS_SECRET_KEY")

    if missing:
        raise SystemExit("Missing required configuration: " + ", ".join(missing))

    return args


def main() -> int:
    args = parse_args(sys.argv[1:])

    if args.dry_run:
        planned_key = args.key or os.path.basename(args.local_path)
        print("Dry run: would upload")
        print(f"  Local: {os.path.abspath(args.local_path)}")
        print(f"  Bucket: {args.bucket}")
        print(f"  Region: {args.region}")
        print(f"  Key: {planned_key}")
        return 0

    print("Tencent COS Upload")
    print("=" * 40)
    print(f"Bucket: {args.bucket}")
    print(f"Region: {args.region}")
    print(f"Key: {args.key or os.path.basename(args.local_path)}")
    print()

    try:
        obj_key = upload_file_to_cos(
            bucket_name=args.bucket,
            region=args.region,
            secret_id=args.secret_id,
            secret_key=args.secret_key,
            token=args.token,
            local_path=args.local_path,
            key=args.key,
            storage_class=args.storage_class,
            content_type=args.content_type,
            part_size_mb=args.part_size,
            max_threads=args.threads,
            enable_md5=args.md5,
            acl=args.acl,
        )
        print("✓ Upload complete")
        print(f"Object Key: {obj_key}")
        return 0
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return 2
    except Exception as e:
        print(f"Upload failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())


