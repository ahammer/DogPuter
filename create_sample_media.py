#!/usr/bin/env python3
"""
Utility script to create sample media files for testing the DogPuter application.
This script generates images using DALL-E and sound files based on the configuration.
"""

import os
import pygame
import sys
import requests
import io
from PIL import Image
from openai import OpenAI
from config import KEY_MAPPINGS, VIDEO_CHANNELS

def create_dalle_image(prompt, filename, size=(1024, 1024)):
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
            model="dall-e-3",
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
        return True
    except Exception as e:
        print(f"Error generating DALL-E image: {e}")
        # Fall back to creating a basic image with text
        create_basic_image(filename, prompt.split(":")[-1].strip())
        return False

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

def create_sample_sound(filename, duration=1.0, freq=440):
    """Create a sample sound file"""
    import wave
    import struct
    import numpy as np
    
    # Parameters for the WAV file
    sample_rate = 44100
    num_samples = int(sample_rate * duration)
    
    # Generate a simple sine wave
    samples = []
    for i in range(num_samples):
        sample = 32767 * 0.5 * np.sin(2 * np.pi * freq * i / sample_rate)
        samples.append(int(sample))
    
    # Create a WAV file
    with wave.open(filename, 'w') as wav_file:
        # Set parameters
        wav_file.setparams((1, 2, sample_rate, num_samples, 'NONE', 'not compressed'))
        
        # Write the samples
        for sample in samples:
            packed_sample = struct.pack('h', sample)
            wav_file.writeframes(packed_sample)
    
    print(f"Created sound: {filename}")

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
    
    # Create sample images and sounds for key mappings
    for key, mapping in KEY_MAPPINGS.items():
        if "image" in mapping:
            image_path = os.path.join("images", mapping["image"])
            # Extract the name without extension
            name = os.path.splitext(mapping["image"])[0].capitalize()
            
            if use_dalle:
                # Create a detailed prompt for DALL-E based on the key name
                prompt = generate_prompt_for_key(name)
                create_dalle_image(prompt, image_path)
            else:
                create_basic_image(image_path, name)
        
        if "sound" in mapping:
            sound_path = os.path.join("sounds", mapping["sound"])
            create_sample_sound(sound_path)
    
    # Create placeholder text files for videos
    # (We can't easily generate video files, so we'll just create placeholder text files)
    for channel in VIDEO_CHANNELS:
        video_path = os.path.join("videos", channel["video"])
        with open(video_path + ".txt", "w") as f:
            f.write(f"Placeholder for {channel['name']} video\n")
            f.write("In a real setup, you would place an actual video file here.")
        print(f"Created video placeholder: {video_path}.txt")
    
    print("\nSample media files created successfully!")
    print("Note: Video files are represented as placeholder .txt files.")
    print("In a real setup, you would need to provide actual video files.")

def generate_prompt_for_key(key_name):
    """Generate a detailed prompt for DALL-E based on the key name"""
    prompts = {
        "Play": "A high-quality, cheerful image of a dog toy, specifically a colorful ball or frisbee on grass, perfect for play time. The image should be bright, inviting, and clearly show the toy ready for a dog to play with.",
        "Rope": "A high-quality image of a dog rope toy, with colorful twisted fabric, laid out on a clean surface. The rope should have knots on both ends and look durable and fun for a dog to chew and play with.",
        "Ball": "A high-quality image of a tennis ball or rubber ball specifically designed for dogs, sitting on grass or a clean surface. The ball should be vibrant and appealing, clearly meant for a dog to fetch and play with.",
        "Treat": "A high-quality image of dog treats arranged neatly on a clean plate or surface. The treats should look appetizing, perhaps bone-shaped or in various fun shapes that would appeal to a dog owner.",
        "Outside": "A high-quality, sunny image of a beautiful backyard, park, or outdoor space that would be perfect for a dog to play in. The image should show green grass, perhaps some trees, and convey a sense of freedom and outdoor fun.",
        "Walk": "A high-quality image of a dog leash and collar, or perhaps a path in a park that suggests it's time for a walk. The image should be inviting and clearly communicate the concept of taking a dog for a walk."
    }
    
    # Get the prompt for the key name, or use a generic one if not found
    return prompts.get(key_name, f"A high-quality, clear image representing the concept of '{key_name}' for a dog, in a style appropriate for a dog-focused application.")

if __name__ == "__main__":
    main()
