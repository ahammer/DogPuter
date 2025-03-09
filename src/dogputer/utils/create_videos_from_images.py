#!/usr/bin/env python3
"""
Script to create videos from existing images for the DogPuter application.
This script takes the images in the 'media/images' directory and creates MP4 videos with zoom/pan effects.
"""

import os
import sys
import numpy as np
from PIL import Image
from moviepy.video.VideoClip import ImageClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from dogputer.core.config import KEY_MAPPINGS, VIDEO_CHANNELS

def create_video_from_image(image_path, output_filename, duration=5.0, effect="zoom"):
    """Create a video from an image with zoom or pan effects"""
    try:
        # Check if the image exists
        if not os.path.exists(image_path):
            print(f"Image not found: {image_path}")
            return False
        
        # Create a clip from the image with duration
        clip = ImageClip(image_path).with_duration(duration)
        
        # Apply effects based on the specified effect type
        if effect == "zoom":
            # Zoom effect (start at 1.0, end at 1.2 over the duration)
            def zoom(t):
                # Calculate zoom factor (1.0 to 1.2 over the duration)
                zoom_factor = 1.0 + (0.2 * t / duration)
                return zoom_factor
            
            clip = clip.resized(lambda t: zoom(t))
        elif effect == "pan_right":
            # Pan right effect
            w, h = clip.size
            
            # Create the movement using clip position
            clip = clip.with_position(lambda t: (int(-w*0.1 + (w*0.2*t/duration)), 'center'))
        elif effect == "pan_left":
            # Pan left effect
            w, h = clip.size
            # Create the movement using clip position
            clip = clip.with_position(lambda t: (int(w*0.1 - (w*0.2*t/duration)), 'center'))
        elif effect == "pan_up":
            # Pan up effect
            w, h = clip.size
            # Create the movement using clip position
            clip = clip.with_position(lambda t: ('center', int(h*0.1 - (h*0.2*t/duration))))
        elif effect == "pan_down":
            # Pan down effect
            w, h = clip.size
            # Create the movement using clip position
            clip = clip.with_position(lambda t: ('center', int(-h*0.1 + (h*0.2*t/duration))))
        
        # Create the final video with a black background
        final_clip = CompositeVideoClip([clip], size=(800, 600))
        
        # Write the video file
        final_clip.write_videofile(
            output_filename,
            fps=24,
            codec='libx264',
            audio=False,
            preset='ultrafast'  # Use a fast preset for quicker encoding
        )
        
        print(f"Created video: {output_filename}")
        return True
    except Exception as e:
        print(f"Error creating video: {e}")
        return False

def main():
    """Main function to create videos from existing images"""
    # Create videos directory if it doesn't exist
    os.makedirs("media/videos", exist_ok=True)
    
    # List of effects to cycle through
    effects = ["zoom", "pan_right", "pan_left", "pan_up", "pan_down"]
    effect_index = 0
    
    # Create videos for key mappings
    for key, mapping in KEY_MAPPINGS.items():
        if "image" in mapping:
            # Extract the name without extension
            name = os.path.splitext(mapping["image"])[0].capitalize()
            image_path = os.path.join("media/images", mapping["image"])
            video_path = os.path.join("media/videos", name.lower() + ".mp4")
            
            # Check if the image exists
            if os.path.exists(image_path):
                # Choose an effect
                effect = effects[effect_index % len(effects)]
                effect_index += 1
                
                # Create a video from the image
                create_video_from_image(image_path, video_path, duration=5.0, effect=effect)
            else:
                print(f"Image not found: {image_path}")
    
    # Create videos for video channels
    for channel in VIDEO_CHANNELS:
        video_path = os.path.join("media/videos", channel["video"])
        
        # Check if we already created this video (might be a duplicate of a key mapping)
        if os.path.exists(video_path):
            continue
        
        # Check if there's a channel-specific image
        channel_image_path = os.path.join("media/images", f"{channel['name'].lower()}_channel.jpg")
        
        # If not, try to find a matching image from the key mappings
        if not os.path.exists(channel_image_path):
            # Try to find a matching image
            found = False
            for key, mapping in KEY_MAPPINGS.items():
                if "image" in mapping and mapping["image"].lower().startswith(channel["name"].lower()):
                    channel_image_path = os.path.join("media/images", mapping["image"])
                    found = True
                    break
            
            if not found:
                print(f"No image found for channel: {channel['name']}")
                continue
        
        # Choose an effect
        effect = effects[effect_index % len(effects)]
        effect_index += 1
        
        # Create a video from the image
        create_video_from_image(channel_image_path, video_path, duration=5.0, effect=effect)
    
    # Clean up any .txt placeholder files
    for filename in os.listdir("media/videos"):
        if filename.endswith(".mp4.txt"):
            try:
                os.remove(os.path.join("media/videos", filename))
                print(f"Removed placeholder file: {filename}")
            except Exception as e:
                print(f"Error removing placeholder file: {e}")
    
    print("\nVideos created successfully!")

if __name__ == "__main__":
    main()
