#!/usr/bin/env python3
import requests
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse

def download_file(url, folder="downloads"):
    try:
        # Extract filename from URL
        parsed = urlparse(url)
        filename = os.path.basename(parsed.path)
        if not filename:
            filename = "video_file"
        
        # Create downloads folder
        os.makedirs(folder, exist_ok=True)
        filepath = os.path.join(folder, filename)
        
        print(f"🔹 Downloading {filename}...")
        
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        file_size = os.path.getsize(filepath)
        print(f"✅ {filename} ({file_size/1024/1024:.1f} MB)")
        return True
        
    except Exception as e:
        print(f"❌ Failed to download {filename}: {e}")
        return False

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 download_videos.py <urls_file>")
        sys.exit(1)
    
    urls_file = sys.argv[1]
    
    if not os.path.exists(urls_file):
        print(f"❌ File not found: {urls_file}")
        sys.exit(1)
    
    with open(urls_file, 'r') as f:
        urls = [line.strip() for line in f if line.strip()]
    
    if not urls:
        print("❌ No URLs found in file")
        sys.exit(1)
    
    print(f"📥 Starting download of {len(urls)} files (5 concurrent)...")
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        results = list(executor.map(download_file, urls))
    
    successful = sum(results)
    print(f"\n🎯 Downloaded {successful}/{len(urls)} files successfully")

if __name__ == "__main__":
    main()