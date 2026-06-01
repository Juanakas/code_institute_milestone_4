#!/usr/bin/env python3
"""Upload local MP4 videos to S3 or an S3-compatible endpoint (Cloudflare R2).

Usage examples:
  # AWS S3 (using env AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY)
  python scripts/upload_videos.py \
    --local-dir "videos2" \
    --bucket my-bucket-name \
    --provider s3 \
    --public-base-url "https://my-bucket-name.s3.amazonaws.com"

  # Cloudflare R2 (S3-compatible) with custom endpoint and public base URL
  python scripts/upload_videos.py \
    --local-dir "C:\\...\\videos2" \
    --bucket my-r2-bucket \
    --provider r2 \
    --endpoint-url https://<account_id>.r2.cloudflarestorage.com \
    --public-base-url https://<your-cf-worker-or-hosted-cdn>/videos

The script uploads all .mp4 files found directly under --local-dir to the target
bucket under the given prefix (default: "videos"). It prints a mapping of local
filename -> uploaded object key and public URL (if --public-base-url is set).
"""

from __future__ import annotations

import argparse
import logging
from pathlib import Path
import sys
from typing import Optional

try:
    import boto3
    from botocore.exceptions import ClientError
except Exception as exc:  # pragma: no cover - runtime dependency
    print("Missing dependency: boto3. Install with `pip install boto3`.")
    raise


logger = logging.getLogger("upload_videos")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Upload local MP4s to S3 or S3-compatible storage")
    p.add_argument("--local-dir", required=True, help="Path to local folder containing MP4 files")
    p.add_argument("--bucket", required=True, help="Target bucket name")
    p.add_argument("--provider", choices=("s3", "r2"), default="s3", help="Provider type (s3 or r2)")
    p.add_argument("--endpoint-url", default=None, help="Custom S3 endpoint URL (for R2)")
    p.add_argument("--prefix", default="videos", help="Object key prefix in bucket (default: videos)")
    p.add_argument("--acl", default=None, help="ACL to apply (e.g. public-read). Optional")
    p.add_argument("--public-base-url", default=None, help="Public base url to construct object URLs (optional)")
    p.add_argument("--dry-run", action="store_true", help="Show actions without performing uploads")
    p.add_argument("--verbose", action="store_true")
    return p.parse_args()


def make_s3_client(endpoint_url: Optional[str] = None):
    session = boto3.session.Session()
    client = session.client("s3", endpoint_url=endpoint_url)
    return client


def upload_file(client, bucket: str, key: str, path: Path, acl: Optional[str] = None, dry_run: bool = False):
    extra = {"ContentType": "video/mp4"}
    if acl:
        extra["ACL"] = acl

    if dry_run:
        logger.info("DRY RUN: upload %s -> s3://%s/%s (ExtraArgs=%s)", path, bucket, key, extra)
        return True

    try:
        client.upload_file(str(path), bucket, key, ExtraArgs=extra)
        return True
    except ClientError as e:
        logger.error("Upload failed for %s: %s", path, e)
        return False


def build_public_url(public_base: Optional[str], prefix: str, filename: str, bucket: str, provider: str) -> str:
    if public_base:
        return f"{public_base.rstrip('/')}/{prefix}/{filename}"
    if provider == "s3":
        return f"https://{bucket}.s3.amazonaws.com/{prefix}/{filename}"
    # Fallback generic
    return f"s3://{bucket}/{prefix}/{filename}"


def main():
    args = parse_args()
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO, format="%(levelname)s: %(message)s")

    local_dir = Path(args.local_dir).expanduser().resolve()
    if not local_dir.exists() or not local_dir.is_dir():
        logger.error("Local dir not found: %s", local_dir)
        sys.exit(2)

    client = make_s3_client(endpoint_url=args.endpoint_url)

    mp4_files = sorted([p for p in local_dir.iterdir() if p.is_file() and p.suffix.lower() == ".mp4"])
    if not mp4_files:
        logger.warning("No .mp4 files found in %s", local_dir)
        return

    success = []
    failed = []

    for p in mp4_files:
        filename = p.name
        key = f"{args.prefix.rstrip('/')}/{filename}"
        ok = upload_file(client, args.bucket, key, p, acl=args.acl, dry_run=args.dry_run)
        if ok:
            url = build_public_url(args.public_base_url, args.prefix, filename, args.bucket, args.provider)
            logger.info("Uploaded: %s -> %s", p, url)
            success.append((p, key, url))
        else:
            failed.append(p)

    logger.info("Uploaded %d files, failed %d", len(success), len(failed))
    if failed:
        for p in failed:
            logger.error("Failed: %s", p)


if __name__ == "__main__":
    main()
