#!/usr/bin/env python3
import boto3
import subprocess
from datetime import datetime, timedelta

# Configuration from your deployed infrastructure
S3_BUCKET = "pyrmon-streaming-japan-513864ec"
DISTRIBUTION_ID = "E3KKFPRD3K173R"
DOMAIN_NAME = "d585s897ti1me.cloudfront.net"
KEY_PAIR_ID = "K34BWQLMYSKP6K"
PRIVATE_KEY_FILE = "./private_key.pem"
EXPIRATION_DAYS = 1

print(f"🔹 Using S3 bucket: {S3_BUCKET}")
print(f"🔹 Using CloudFront distribution: {DISTRIBUTION_ID}")
print(f"🔹 Using domain: {DOMAIN_NAME}")
print(f"🔹 Using key pair ID: {KEY_PAIR_ID}\n")

s3 = boto3.client("s3")
expires = (datetime.utcnow() + timedelta(days=EXPIRATION_DAYS)).strftime("%Y-%m-%dT%H:%M:%SZ")

try:
    response = s3.list_objects_v2(Bucket=S3_BUCKET)
except Exception as e:
    print(f"❌ Error accessing S3 bucket: {e}")
    exit(1)

if "Contents" not in response:
    print(f"No files found in bucket {S3_BUCKET}")
    print("Upload some .mkv files first using: python3 upload_to_s3.py /path/to/video.mkv")
    exit(0)

video_files = [obj["Key"] for obj in response["Contents"] if obj["Key"].endswith((".mkv", ".mp4"))]

if not video_files:
    print(f"No video files found in bucket {S3_BUCKET}")
    print("Upload some video files first using: python3 upload_to_s3.py /path/to/video.mp4")
    exit(0)

print(f"Found {len(video_files)} video(s) in S3 bucket '{S3_BUCKET}': {video_files}\n")

choice = input("Output URLs to (1) console or (2) text file? [1/2]: ").strip()
write_to_file = choice == "2"

if write_to_file:
    output_file = "signed_urls.txt"
    f = open(output_file, "w")
    print(f"Writing URLs to {output_file}...\n")
else:
    print("Generating signed URLs (valid for 1 day):\n")

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
