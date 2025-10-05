#!/usr/bin/env python3
import boto3
import subprocess
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration from environment variables
S3_BUCKET = os.getenv('S3_BUCKET_NAME')
DISTRIBUTION_ID = os.getenv('CLOUDFRONT_DISTRIBUTION_ID')
DOMAIN_NAME = os.getenv('CLOUDFRONT_DOMAIN_NAME')
KEY_PAIR_ID = os.getenv('CLOUDFRONT_KEY_PAIR_ID')
PRIVATE_KEY_FILE = os.getenv('PRIVATE_KEY_FILE', './private_key.pem')
EXPIRATION_DAYS = int(os.getenv('URL_EXPIRATION_DAYS', '1'))

def check_config():
    """Check if all required environment variables are set"""
    required_vars = {
        'S3_BUCKET_NAME': S3_BUCKET,
        'CLOUDFRONT_DISTRIBUTION_ID': DISTRIBUTION_ID,
        'CLOUDFRONT_DOMAIN_NAME': DOMAIN_NAME,
        'CLOUDFRONT_KEY_PAIR_ID': KEY_PAIR_ID
    }
    
    missing = [var for var, value in required_vars.items() if not value]
    if missing:
        print("❌ Missing required environment variables:")
        for var in missing:
            print(f"   - {var}")
        print("\nPlease copy .env.example to .env and configure your settings")
        return False
    
    if not os.path.exists(PRIVATE_KEY_FILE):
        print(f"❌ Private key file not found: {PRIVATE_KEY_FILE}")
        return False
    
    return True

def main():
    if not check_config():
        return
    
    print(f"🔹 Using S3 bucket: {S3_BUCKET}")
    print(f"🔹 Using CloudFront distribution: {DISTRIBUTION_ID}")
    print(f"🔹 Using domain: {DOMAIN_NAME}")
    print(f"🔹 Using key pair ID: {KEY_PAIR_ID}\n")

    try:
        s3 = boto3.client("s3")
        expires = (datetime.utcnow() + timedelta(days=EXPIRATION_DAYS)).strftime("%Y-%m-%dT%H:%M:%SZ")
    except Exception as e:
        print(f"❌ Failed to create S3 client: {e}")
        return

    try:
        response = s3.list_objects_v2(Bucket=S3_BUCKET)
    except Exception as e:
        print(f"❌ Error accessing S3 bucket: {e}")
        return

    if "Contents" not in response:
        print(f"No files found in bucket {S3_BUCKET}")
        print("Upload some video files first using: python3 upload_to_s3.py /path/to/videos/")
        return

    video_files = [obj["Key"] for obj in response["Contents"] 
                   if obj["Key"].endswith((".mkv", ".mp4", ".avi", ".mov", ".wmv"))]

    if not video_files:
        print(f"No video files found in bucket {S3_BUCKET}")
        print("Upload some video files first using: python3 upload_to_s3.py /path/to/videos/")
        return

    print(f"Found {len(video_files)} video(s) in S3 bucket '{S3_BUCKET}': {video_files}\n")

    choice = input("Output URLs to (1) console or (2) text file? [1/2]: ").strip()
    write_to_file = choice == "2"

    if write_to_file:
        output_file = "signed_urls.txt"
        f = open(output_file, "w")
        print(f"Writing URLs to {output_file}...\n")
    else:
        print(f"Generating signed URLs (valid for {EXPIRATION_DAYS} day(s)):\n")

    for video in video_files:
        cmd = [
            "aws", "cloudfront", "sign",
            "--url", f"https://{DOMAIN_NAME}/{video}",
            "--key-pair-id", KEY_PAIR_ID,
            "--private-key", f"file://{PRIVATE_KEY_FILE}",
            "--date-less-than", expires
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Error for {video}:\n{result.stderr}")
        else:
            signed_url = result.stdout.strip()
            if write_to_file:
                f.write(f"{signed_url}\n")
                print(f"✅ {video}")
            else:
                print(f"✅ {video}:")
                print(f"{signed_url}\n")

    if write_to_file:
        f.close()
        print(f"\n✅ URLs saved to {output_file}")

if __name__ == "__main__":
    main()