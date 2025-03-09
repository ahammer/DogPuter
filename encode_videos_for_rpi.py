#!/usr/bin/env python3
"""
Script to re-encode videos from videos_raw to videos directory
with resolution and encoding appropriate for Raspberry Pi 3B.
"""

import os
import subprocess
import sys
from pathlib import Path

# Configuration
SOURCE_DIR = "media/videos_raw"
TARGET_DIR = "media/videos"
# Default to 854x480 (16:9 aspect ratio at 480p)
TARGET_WIDTH = 854
TARGET_HEIGHT = 480
# Use h.264 codec which is well supported by Raspberry Pi hardware acceleration
VIDEO_CODEC = "libx264"
# Use a preset that balances quality and encoding speed
PRESET = "medium"
# Target bitrate
BITRATE = "1M"
# CRF (Constant Rate Factor) - lower is better quality, 18-28 is typical range
CRF = "23"


def get_video_info(video_path):
    """Get video dimensions using ffprobe"""
    cmd = [
        "ffprobe",
        "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=width,height",
        "-of", "csv=p=0",
        video_path
    ]
    
    try:
        output = subprocess.check_output(cmd).decode("utf-8").strip().split(",")
        return int(output[0]), int(output[1])
    except subprocess.CalledProcessError as e:
        print(f"Error getting video info for {video_path}: {e}")
        return None, None


def calculate_crop_params(width, height, target_width, target_height):
    """
    Calculate crop parameters to maintain aspect ratio and fill target dimensions.
    This will crop either width or height to match the target aspect ratio.
    """
    source_aspect = width / height
    target_aspect = target_width / target_height
    
    if source_aspect > target_aspect:
        # Video is wider than target, crop width
        new_width = int(height * target_aspect)
        crop_width = new_width
        crop_height = height
        x_offset = int((width - new_width) / 2)
        y_offset = 0
    else:
        # Video is taller than target, crop height
        new_height = int(width / target_aspect)
        crop_width = width
        crop_height = new_height
        x_offset = 0
        y_offset = int((height - new_height) / 2)
    
    return x_offset, y_offset, crop_width, crop_height


def encode_video(source_file, target_file, target_width, target_height):
    """Re-encode a video file to target resolution with appropriate settings for Raspberry Pi"""
    width, height = get_video_info(source_file)
    
    if width is None or height is None:
        print(f"Skipping {source_file} due to error getting video info")
        return False
        
    x_offset, y_offset, crop_width, crop_height = calculate_crop_params(
        width, height, target_width, target_height
    )
    
    # Create filter string for crop and scale
    filter_str = f"crop={crop_width}:{crop_height}:{x_offset}:{y_offset},scale={target_width}:{target_height}"
    
    cmd = [
        "ffmpeg",
        "-i", source_file,
        "-vf", filter_str,
        "-c:v", VIDEO_CODEC,
        "-preset", PRESET,
        "-b:v", BITRATE,
        "-crf", CRF,
        "-movflags", "+faststart",  # Optimize for web streaming
        "-c:a", "aac",  # AAC audio codec for good compatibility
        "-b:a", "128k",  # Audio bitrate
        "-y",  # Overwrite output file without asking
        target_file
    ]
    
    print(f"Encoding {os.path.basename(source_file)} to {os.path.basename(target_file)}...")
    print(f"  Resolution: {width}x{height} -> {target_width}x{target_height}")
    print(f"  Crop params: offset({x_offset},{y_offset}) size({crop_width}x{crop_height})")
    
    try:
        subprocess.run(cmd, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error encoding {source_file}: {e}")
        return False


def main():
    # Create target directory if it doesn't exist
    target_path = Path(TARGET_DIR)
    target_path.mkdir(exist_ok=True, parents=True)
    
    # Get all mp4 files in source directory
    source_path = Path(SOURCE_DIR)
    video_files = list(source_path.glob("*.mp4"))
    
    if not video_files:
        print(f"No MP4 files found in {SOURCE_DIR}")
        return
    
    print(f"Found {len(video_files)} MP4 files to process")
    
    # Process each video
    success_count = 0
    for video_file in video_files:
        target_file = target_path / video_file.name
        
        if encode_video(str(video_file), str(target_file), TARGET_WIDTH, TARGET_HEIGHT):
            success_count += 1
    
    print(f"Encoding complete: {success_count}/{len(video_files)} videos processed successfully")


if __name__ == "__main__":
    # Allow command-line override of target resolution
    if len(sys.argv) > 1:
        try:
            TARGET_HEIGHT = int(sys.argv[1])
            # Maintain 16:9 aspect ratio
            TARGET_WIDTH = (TARGET_HEIGHT * 16) // 9
            print(f"Using target resolution: {TARGET_WIDTH}x{TARGET_HEIGHT}")
        except ValueError:
            print(f"Invalid resolution: {sys.argv[1]}")
            sys.exit(1)
    
    main()
