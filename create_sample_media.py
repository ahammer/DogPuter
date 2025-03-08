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
    # Base template for photo-realistic images from a dog's perspective
    base_template = "Create a photo-realistic image from a dog's perspective. The image should be taken from a low angle, as if seen through the eyes of a dog, with a slight wide-angle distortion. Colors should be slightly muted in the red-green spectrum to simulate dog vision, with blues and yellows more prominent."
    
    prompts = {
        "Play": f"{base_template} Photo of a play area from a dog's perspective, looking up at a human holding a toy, ready to play. The scene should be bright and exciting, capturing the anticipation of playtime.",
        "Rope": f"{base_template} Photo of a rope toy from a dog's perspective, lying on the ground just in front of the dog's paws. The rope should be colorful and appear slightly larger than life, as if the dog is focusing intently on it.",
        "Ball": f"{base_template} Photo of a tennis ball from a dog's perspective, sitting on grass with the dog's paw partially visible in the frame. The ball should be the main focus, appearing slightly larger as the dog fixates on it.",
        "Hugs": f"{base_template} Photo of a human hugging a dog from the dog's perspective, showing the human's arms wrapped around and the human's face close by, conveying warmth and affection. The image should capture the intimate, comforting feeling of being hugged.",
        "Outside": f"{base_template} Photo of a backyard or garden from a dog's perspective, with the door just opening and bright daylight streaming in. The outdoor scene should look vast and exciting from the low angle of a dog.",
        "Walk": f"{base_template} Photo of a walking path from a dog's perspective, with a leash visible extending from the frame to a human hand. The path should stretch ahead invitingly, with interesting elements like trees or other dogs visible in the distance.",
        "Water": f"{base_template} Photo of a water bowl from a dog's perspective, with the water surface reflecting light and appearing refreshing. The bowl should be positioned as if the dog is about to drink from it.",
        "Park": f"{base_template} Photo of a dog park from a dog's perspective, showing other dogs playing in the distance and open space to run. The image should capture the excitement and freedom of being at the park.",
        "Toy": f"{base_template} Photo of a collection of dog toys from a dog's perspective, scattered on the floor with one toy prominently in focus in the foreground. The toys should appear enticing and ready to be played with.",
        "Bed": f"{base_template} Photo of a cozy dog bed from a dog's perspective, looking at it from a slight distance as if considering whether to go lie down. The bed should look soft, warm and inviting."
    }
    
    # Get the prompt for the key name, or use a generic one if not found
    return prompts.get(key_name, f"{base_template} Photo of the concept of '{key_name}' from a dog's perspective, showing what a dog would see when encountering this object or situation.")

if __name__ == "__main__":
    main()
