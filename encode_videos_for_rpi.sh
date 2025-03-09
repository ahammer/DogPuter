#!/bin/bash
# Script to re-encode videos from videos_raw to videos directory
# with resolution and encoding appropriate for Raspberry Pi 3B.

SOURCE_DIR="media/videos_raw"
TARGET_DIR="media/videos"
# Default to 854x480 (16:9 aspect ratio at 480p)
TARGET_HEIGHT=480
TARGET_WIDTH=854

# Create target directory if it doesn't exist
mkdir -p "$TARGET_DIR"

# Process each video
echo "Starting video encoding process..."

for video in "$SOURCE_DIR"/*.mp4; do
    filename=$(basename "$video")
    output="$TARGET_DIR/$filename"
    
    # Get video dimensions
    dimensions=$(ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=p=0 "$video")
    width=$(echo $dimensions | cut -d ',' -f1)
    height=$(echo $dimensions | cut -d ',' -f2)
    
    # Calculate aspect ratios
    source_aspect=$(awk "BEGIN {print $width/$height}")
    target_aspect=$(awk "BEGIN {print $TARGET_WIDTH/$TARGET_HEIGHT}")
    
    # Calculate crop parameters
    if (( $(awk "BEGIN {print ($source_aspect > $target_aspect) ? 1 : 0}") )); then
        # Video is wider than target, crop width
        crop_width=$(awk "BEGIN {print int($height * $target_aspect)}")
        crop_height=$height
        x_offset=$(awk "BEGIN {print int(($width - $crop_width) / 2)}")
        y_offset=0
    else
        # Video is taller than target, crop height
        crop_width=$width
        crop_height=$(awk "BEGIN {print int($width / $target_aspect)}")
        x_offset=0
        y_offset=$(awk "BEGIN {print int(($height - $crop_height) / 2)}")
    fi
    
    echo "Encoding $filename to $TARGET_WIDTH x $TARGET_HEIGHT"
    echo "  Original: $width x $height"
    echo "  Crop: offset($x_offset,$y_offset) size(${crop_width}x${crop_height})"
    
    # Perform the actual encoding
    ffmpeg -i "$video" \
        -vf "crop=$crop_width:$crop_height:$x_offset:$y_offset,scale=$TARGET_WIDTH:$TARGET_HEIGHT" \
        -c:v libx264 -preset medium -b:v 1M -crf 23 \
        -movflags +faststart \
        -c:a aac -b:a 128k \
        -y "$output"
    
    if [ $? -eq 0 ]; then
        echo "Successfully encoded $filename"
    else
        echo "Failed to encode $filename"
    fi
done

echo "Encoding process complete!"
