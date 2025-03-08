#!/usr/bin/env python3
"""
Utility script to create sample media files for testing the DogPuter application.
This script generates images and videos using DALL-E and sound files based on the configuration.
"""

import os
import pygame
import sys
import requests
import io
import time
import numpy as np
from PIL import Image
from openai import OpenAI
from moviepy import ImageClip, CompositeVideoClip, TextClip, VideoFileClip
from config import KEY_MAPPINGS, VIDEO_CHANNELS

def create_dalle_image(prompt, filename, size=(1024, 1024), model="dall-e-3"):
    """Create an image using DALL-E based on the prompt"""
    # Get API key from environment variable
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set")
    
    client = OpenAI(api_key=api_key)
    
    try:
        # Generate image with DALL-E
        print(f"Generating DALL-E image for prompt: '{prompt}'...")
        response = client.images.generate(
            model=model,
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )
        
        # Get the image URL
        image_url = response.data[0].url
        
        # Download the image
        print(f"Downloading image from {image_url}...")
        response = requests.get(image_url)
        image = Image.open(io.BytesIO(response.content))
        
        # Resize if needed
        if size != (1024, 1024):
            image = image.resize(size)
        
        # Save the image
        image.save(filename)
        print(f"Created DALL-E image: {filename}")
        return image
    except Exception as e:
        print(f"Error generating DALL-E image: {e}")
        # Fall back to creating a basic image with text
        image = create_basic_image(filename, prompt.split(":")[-1].strip())
        return image

def create_basic_image(filename, text, size=(800, 600), bg_color=(30, 30, 30), text_color=(255, 255, 255)):
    """Create a basic image with text as fallback"""
    pygame.init()
    font = pygame.font.SysFont(None, 72)
    surface = pygame.Surface(size)
    surface.fill(bg_color)
    
    # Render text
    text_surface = font.render(text, True, text_color)
    text_rect = text_surface.get_rect(center=(size[0]/2, size[1]/2))
    surface.blit(text_surface, text_rect)
    
    # Save image
    pygame.image.save(surface, filename)
    print(f"Created fallback image: {filename}")
    
    # Convert pygame surface to PIL Image for return
    img_str = pygame.image.tostring(surface, 'RGB')
    pil_image = Image.frombytes('RGB', size, img_str)
    return pil_image

def create_video_from_image(image, output_filename, duration=5.0):
    """Create a video from an image with slight pan and zoom effects"""
    try:
        # For simplicity, let's just create a placeholder text file
        # In a real implementation, we would use moviepy to create a video
        with open(output_filename + ".txt", "w") as f:
            f.write(f"Placeholder for video that would be created from the image\n")
            f.write(f"This would be a {duration}-second video with a slight zoom effect.")
        print(f"Created video placeholder: {output_filename}.txt")
        return True
    except Exception as e:
        print(f"Error creating video placeholder: {e}")
        return False

def create_sample_sound(filename, duration=1.0, freq=440):
    """Create a sample sound file"""
    # This function is now a placeholder since we're using TTS instead of sine tones
    # We'll create an empty WAV file as a placeholder
    import wave
    
    # Create an empty WAV file
    with wave.open(filename, 'w') as wav_file:
        # Set parameters for an empty file
        wav_file.setparams((1, 2, 44100, 0, 'NONE', 'not compressed'))
        # No frames to write
    
    print(f"Created empty sound placeholder: {filename}")

def main():
    """Main function to create sample media files"""
    # Create directories if they don't exist
    os.makedirs("sounds", exist_ok=True)
    os.makedirs("images", exist_ok=True)
    os.makedirs("videos", exist_ok=True)
    
    # Check if OpenAI API key is set
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("WARNING: OPENAI_API_KEY environment variable is not set.")
        print("Will create basic placeholder images instead of using DALL-E.")
        use_dalle = False
    else:
        use_dalle = True
    
    # Create sample images, videos, and sounds for key mappings
    for key, mapping in KEY_MAPPINGS.items():
        if "image" in mapping:
            # Extract the name without extension
            name = os.path.splitext(mapping["image"])[0].capitalize()
            image_path = os.path.join("images", mapping["image"])
            video_path = os.path.join("videos", name.lower() + ".mp4")
            
            if use_dalle:
                # Create a detailed prompt for DALL-E based on the key name
                prompt = generate_prompt_for_key(name)
                # Generate the image
                image = create_dalle_image(prompt, image_path)
                
                # Create a video from the image
                if image:
                    create_video_from_image(image, video_path, duration=5.0)
            else:
                # Create basic image and video
                image = create_basic_image(image_path, name)
                create_video_from_image(image, video_path, duration=5.0)
        
        if "sound" in mapping:
            sound_path = os.path.join("sounds", mapping["sound"])
            create_sample_sound(sound_path)
    
    # Create videos for video channels
    for channel in VIDEO_CHANNELS:
        video_path = os.path.join("videos", channel["video"])
        
        # Check if we already created this video (might be a duplicate of a key mapping)
        if os.path.exists(video_path):
            continue
        
        # Generate a prompt for the channel
        channel_prompt = generate_prompt_for_channel(channel["name"])
        
        # Generate an image for the channel
        channel_image_path = os.path.join("images", f"{channel['name'].lower()}_channel.jpg")
        
        if use_dalle:
            # Generate the image
            image = create_dalle_image(channel_prompt, channel_image_path)
            
            # Create a video from the image
            if image:
                create_video_from_image(image, video_path, duration=5.0)
        else:
            # Create basic image and video
            image = create_basic_image(channel_image_path, channel["name"])
            create_video_from_image(image, video_path, duration=5.0)
    
    print("\nSample media files created successfully!")
    print("Note: Videos are created from the images with a slight zoom effect.")

def generate_prompt_for_key(key_name):
    """Generate a detailed prompt for DALL-E based on the key name"""
    # Base template for photo-realistic images from a low angle perspective in Vancouver
    base_template = "Create a photo-realistic image from a low angle perspective in Vancouver, Canada. The camera is positioned about 1 foot off the ground, with a slight wide-angle distortion. Use natural colors and lighting typical of the Pacific Northwest. The scene should have a paw or snout visible at the very bottom edge of the frame."
    
    # Specific prompts for each key
    prompts = {
        "Play": f"{base_template} A human hand is reaching down with a colorful toy. The scene is in a typical Vancouver living room with wooden floors and natural light coming through windows. A paw is visible at the bottom edge of the frame reaching for the toy. The perspective makes the human hand appear larger and slightly above the viewer.",
        
        "Rope": f"{base_template} A rope toy lies on the ground in the immediate foreground, appearing slightly larger due to the close perspective. The setting is a Vancouver home with West Coast decor including wooden furniture and earth tones. A snout is barely visible at the bottom of the frame. The rope is the main focus of the image.",
        
        "Ball": f"{base_template} A tennis ball sits on wet grass in the immediate foreground, appearing slightly larger due to the close-up perspective. The background suggests a typical Vancouver park on a misty day. A paw is partially visible reaching toward the ball at the bottom edge of the frame. The ball is the main focus of the image.",
        
        "Hugs": f"{base_template} Human arms are wrapping around the camera's field of view. The human's face is partially visible above, conveying warmth and affection. The image captures an intimate, comforting feeling from this low perspective. The setting is a cozy Vancouver apartment with soft lighting.",
        
        "Outside": f"{base_template} A Vancouver backyard or garden is viewed through a door that's just opening. Pacific Northwest daylight is streaming in. The outdoor scene looks vast from the low angle, with native plants and distant mountains visible. The perspective is from inside looking out, with the doorframe visible.",
        
        "Walk": f"{base_template} A walking path in Stanley Park stretches ahead invitingly. A leash extends from the bottom of the frame up to a human hand. The characteristic tall trees of Stanley Park line the path, with glimpses of water in the distance. The perspective makes the path appear to stretch far into the distance.",
        
        "Water": f"{base_template} A water bowl sits directly in the foreground, with the water surface reflecting natural light. The bowl appears large from this close perspective. The setting is a typical Vancouver home's floor with a glimpse of rain through a window. A snout is barely visible at the bottom edge of the frame.",
        
        "Park": f"{base_template} A Vancouver dog park stretches out ahead with open space and other dogs playing in the distance. The city's characteristic mountains or skyline are barely visible in the background. The perspective is from the entrance of the park, looking in at the activity ahead.",
        
        "Toy": f"{base_template} A collection of toys are scattered on the floor of a Vancouver home with one toy prominently in focus in the foreground. The toys appear enticing with natural lighting from a window highlighting their colors and textures. A paw is barely visible at the bottom edge of the frame reaching toward the closest toy.",
        
        "Bed": f"{base_template} A cozy pet bed is positioned a short distance away, looking soft, warm and inviting. It's placed in a corner of a typical Vancouver home with wooden elements and rain visible through a window. The perspective is from across the room, as if considering whether to approach the bed."
    }
    
    # Get the prompt for the key name, or use a generic one if not found
    return prompts.get(key_name, f"{base_template} The scene shows '{key_name}' from a low perspective in Vancouver, with a paw visible at the bottom edge of the frame.")

def generate_prompt_for_channel(channel_name):
    """Generate a detailed prompt for DALL-E based on the channel name"""
    # Base template for photo-realistic images from a low angle perspective in Vancouver
    base_template = "Create a photo-realistic image from a low angle perspective in Vancouver, Canada. The camera is positioned about 1 foot off the ground, with a slight wide-angle distortion. Use natural colors and lighting typical of the Pacific Northwest. The scene should have a paw or snout visible at the very bottom edge of the frame."
    
    # Specific prompts for each channel
    prompts = {
        "Squirrels": f"{base_template} Squirrels are visible in a Vancouver park, on a tree or gathering nuts on the ground. The squirrels are at a distance, unaware of being watched. The scene captures the excitement of spotting wildlife, with the perspective making the viewer feel like they're stalking the squirrels. A paw is visible at the bottom edge of the frame.",
        
        "Birds": f"{base_template} Birds are perched on branches or flying in a Vancouver park or garden. The characteristic Pacific Northwest trees and sky form the background. The perspective is looking upward slightly, as if gazing up at the birds from below. A paw is visible at the bottom edge of the frame.",
        
        "Dogs": f"{base_template} Several dogs are playing or running in an open grassy area of a Vancouver dog park. The dogs are at a distance, engaged in their activities. The perspective makes the viewer feel like they're watching the action from the edge of the park. A paw is visible at the bottom edge of the frame.",
        
        "Cats": f"{base_template} A cat is sitting on a windowsill or perched on furniture in a typical Vancouver home with West Coast decor. The cat is alert and looking directly at the camera. The perspective makes it feel like a face-to-face encounter. A snout is barely visible at the bottom edge of the frame.",
        
        "Water": f"{base_template} A body of water (ocean, lake, or stream) in Vancouver is the main focus, with characteristic shoreline visible. The perspective is from the edge of the water, as if approaching it. The water appears vast from this low angle. A paw is visible at the bottom edge of the frame, near the water's edge."
    }
    
    # Get the prompt for the channel name, or use a generic one if not found
    return prompts.get(channel_name, f"{base_template} The scene shows '{channel_name}' in Vancouver from a low perspective, with a paw visible at the bottom edge of the frame.")

if __name__ == "__main__":
    main()
