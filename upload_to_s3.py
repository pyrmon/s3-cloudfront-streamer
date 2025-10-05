#!/usr/bin/env python3
import boto3
import os
import sys
import re

# Configuration
BUCKET_NAME = "pyrmon-streaming-japan-513864ec"
REGION = "ap-northeast-1"

def sanitize_filename(filename):
    """Convert filename to S3/CloudFront safe format"""
    name, ext = os.path.splitext(filename)
    # Replace spaces and special chars with underscores
    name = re.sub(r'[^a-zA-Z0-9._-]', '_', name)
    # Remove multiple underscores
    name = re.sub(r'_+', '_', name)
    # Remove leading/trailing underscores
    name = name.strip('_')
    return f"{name}{ext}"

def upload_videos(folder_path):
    if not os.path.exists(folder_path):
        print(f"❌ Folder not found: {folder_path}")
        return
    
    s3 = boto3.client('s3', region_name=REGION)
    
    video_files = []
    for file in os.listdir(folder_path):
        if file.lower().endswith(('.mkv', '.mp4')):
            video_files.append(file)
    
    if not video_files:
        print(f"No video files found in {folder_path}")
        return
    
    print(f"Found {len(video_files)} video files to upload:")
    
    for original_name in video_files:
        safe_name = sanitize_filename(original_name)
        file_path = os.path.join(folder_path, original_name)
        
        if original_name != safe_name:
            print(f"🔄 {original_name} → {safe_name}")
        else:
            print(f"📁 {original_name}")
        
        try:
            s3.upload_file(file_path, BUCKET_NAME, safe_name)
            print(f"✅ Uploaded successfully")
        except Exception as e:
            print(f"❌ Upload failed: {e}")
        print()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 upload_to_s3.py <folder_path>")
        sys.exit(1)
    
    folder_path = sys.argv[1]
    upload_videos(folder_path)