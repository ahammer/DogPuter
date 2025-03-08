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
    # Base template for cartoon-style images with dog-friendly colors
    base_template = "Create a friendly, cartoon-style illustration for children that is also optimized for dog vision. Use a simple, clear design with bold outlines and predominantly blue and yellow for important elements, though some red and green can be included. The image should be cute and appealing, not abstract or overly stylized."
    
    prompts = {
        "Play": f"{base_template} Draw a happy cartoon dog playing with a toy, with blue and yellow highlights. The scene should clearly communicate 'play time' in a way that's easy for both children and dogs to understand.",
        "Rope": f"{base_template} Draw a cartoon-style dog rope toy with blue and yellow colors and clear knots on both ends. Make it look fun and appealing for a children's app, while being recognizable to dogs.",
        "Ball": f"{base_template} Draw a cartoon-style ball for dogs, with blue and yellow patterns. Make it look bouncy and fun in a children's illustration style, while being instantly recognizable to dogs.",
        "Treat": f"{base_template} Draw a cartoon-style dog bone or treat with blue and yellow highlights. Make it look appetizing and fun in a children's illustration style, while being instantly recognizable to dogs.",
        "Outside": f"{base_template} Draw a simple, cartoon-style outdoor scene with a tree, sun, and grass. Use blue for the sky and yellow for the sun to make these elements pop for dogs, while keeping the overall style appropriate for children.",
        "Walk": f"{base_template} Draw a cartoon-style dog leash or a simple path in a park that suggests it's time for a walk. Use blue and yellow for important elements to make them stand out for dogs, while keeping the style fun for children.",
        "Water": f"{base_template} Draw a cartoon-style water bowl or water dish for dogs with blue water. Make it look refreshing and appealing in a children's illustration style, while being instantly recognizable to dogs.",
        "Food": f"{base_template} Draw a cartoon-style dog food bowl filled with kibble. Use blue for the bowl and yellow/brown for the food to make it stand out for dogs, while keeping the style appropriate for children.",
        "Toy": f"{base_template} Draw a cartoon-style collection of dog toys (like a stuffed animal or squeaky toy) with blue and yellow elements. Make them look fun and appealing in a children's illustration style.",
        "Bed": f"{base_template} Draw a cartoon-style cozy dog bed or sleeping area. Use blue and yellow for the bed to make it stand out for dogs, while keeping the overall style cute and appropriate for children."
    }
    
    # Get the prompt for the key name, or use a generic one if not found
    return prompts.get(key_name, f"{base_template} Draw a simple, cartoon-style illustration representing the concept of '{key_name}' that would appeal to both children and dogs, with blue and yellow highlights for dog visibility.")

if __name__ == "__main__":
    main()
