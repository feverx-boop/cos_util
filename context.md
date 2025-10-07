## Project Context: cos_test

This repository contains small, focused utilities to interact with Tencent Cloud Object Storage (COS) for quick validation and file operations. Utilities are designed to be cross-platform (macOS and Windows) and easy to automate in CI/CD.

### Files
- `list_cos_objects.py`: Lists objects in a COS bucket to verify credentials and connectivity.
- `upload_to_cos.py`: Uploads a local file to COS with sensible defaults; supports small and large files.
- `cos_test.sh`: Bash helper to validate configuration on macOS/Linux (checks Python and installs `cos-python-sdk-v5` if missing, then runs `list_cos_objects.py`).

### Dependencies
- Python 3.9+ recommended (3.8+ should work; 3.9+ preferred)
- Python package: `cos-python-sdk-v5`

Install dependency:
- macOS/Linux:
```bash
pip3 install cos-python-sdk-v5
```
- Windows (PowerShell):
```powershell
python -m pip install cos-python-sdk-v5
```

### Configuration
Provide configuration via environment variables or CLI flags. Environment variables are convenient for both macOS and Windows.

- `COS_BUCKET_NAME`: COS bucket name including appid (example: `example-1234567890`)
- `COS_REGION`: Region (example: `ap-singapore`)
- `COS_SECRET_ID`: Tencent Cloud Secret ID
- `COS_SECRET_KEY`: Tencent Cloud Secret Key
- `COS_TOKEN` (optional): Temporary credential token if using STS

Notes:
- COS bucket names typically include the appid suffix. Confirm exact bucket format in your console.
- Keep credentials out of source control. Prefer environment variables or secure secret stores.

### Usage

List objects (quick connectivity test):
- macOS/Linux:
```bash
export COS_BUCKET_NAME="example-1234567890"
export COS_REGION="ap-singapore"
export COS_SECRET_ID="AKID..."
export COS_SECRET_KEY="SECRET..."
python3 list_cos_objects.py
```

- Windows (PowerShell):
```powershell
$env:COS_BUCKET_NAME = "example-1234567890"
$env:COS_REGION = "ap-singapore"
$env:COS_SECRET_ID = "AKID..."
$env:COS_SECRET_KEY = "SECRET..."
python .\list_cos_objects.py
```

Upload a file:
- macOS/Linux:
```bash
python3 upload_to_cos.py ./dist/app.zip --key releases/app.zip
```

- Windows (PowerShell):
```powershell
python .\upload_to_cos.py .\dist\app.zip --key releases/app.zip
```

Optional flags for `upload_to_cos.py`:
- `--bucket`, `--region`, `--secret-id`, `--secret-key`, `--token` (override env vars)
- `--content-type` (sets Content-Type for small files ≤ 5 MiB)
- `--storage-class` (default `STANDARD`)
- `--part-size` MiB and `--threads` for multipart uploads of large files
- `--md5` to enable MD5 checks on multipart uploads
- `--acl` (e.g. `public-read` or `private`) for small file uploads
- `--dry-run` to print the planned upload without performing it

Behavior notes:
- Files ≤ 5 MiB use a single `put_object` request, allowing explicit `Content-Type` and `ACL`.
- Larger files use `upload_file` (multipart). The SDK does not accept metadata parameters for multipart in this helper; downstream consumers typically infer type by key suffix. If you require explicit metadata on large uploads, consider post-upload metadata updates per object key.

### Windows and macOS Compatibility
- Both utilities are plain Python and run with `python3` (macOS/Linux) or `python` (Windows). Paths can be provided in platform-native formats.
- Dependency installation commands differ by platform as shown above.

### Security Guidance
- Never commit secrets to source control.
- Use environment variables or a secret manager in CI.
- Rotate credentials regularly and prefer temporary STS credentials with `COS_TOKEN`.

### Extensibility Guidelines (for AI agents and contributors)
- Keep utilities single-purpose, small, and composable.
- Favor explicit CLI flags with safe defaults; continue supporting env vars.
- Maintain cross-platform behavior (avoid OS-specific shell features in Python utilities).
- Follow a clear, readable Python style: descriptive variable names, early returns, minimal nesting, and only non-obvious comments.
- When adding new COS operations (delete, copy, presign), mirror the ergonomics of `upload_to_cos.py` and `list_cos_objects.py` (shared env vars, dry-run, clear errors).

### Useful References
- Tencent COS Python SDK docs: `https://cloud.tencent.com/document/product/436/12269`
- COS regions: `https://cloud.tencent.com/document/product/436/6224`


