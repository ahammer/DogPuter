#!/usr/bin/env python3
"""
Button handler for DogPuter
This script maps physical buttons connected to GPIO pins to keyboard events
that the main DogPuter application can process.
Includes input cooldown to prevent rapid button presses.
"""

from gpiozero import Button
from signal import pause
import pygame
import os
import time
import sys

# Define GPIO pins for buttons
button_pins = {
    "play": 17,   # GPIO pin for "play" button
    "rope": 18,   # GPIO pin for "rope" button
    "ball": 27,   # GPIO pin for "ball" button
    "hugs": 22,   # GPIO pin for "hugs" button (replaced treat)
    "outside": 23,# GPIO pin for "outside" button
    "walk": 24,   # GPIO pin for "walk" button
    "water": 25,  # GPIO pin for "water" button
    "park": 26,   # GPIO pin for "park" button (replaced food)
    # Add more buttons as needed
}

# Map button names to pygame key constants
button_to_key = {
    "play": pygame.K_0,  # Updated to match config.py key mappings
    "rope": pygame.K_1,
    "ball": pygame.K_2,
    "hugs": pygame.K_3,
    "outside": pygame.K_4,
    "walk": pygame.K_5,
    "water": pygame.K_6,
    "park": pygame.K_7,
    # Add more mappings as needed
}

# Input cooldown settings
INPUT_COOLDOWN = 0.5  # seconds between allowed button presses

def main():
    """Main function to run the button handler"""
    # Initialize pygame
    pygame.init()
    
    # Create a dummy window (required for pygame.event to work)
    os.environ["SDL_VIDEODRIVER"] = "dummy"
    pygame.display.set_mode((1, 1))
    
    # Create button objects
    buttons = {}
    for name, pin in button_pins.items():
        try:
            buttons[name] = Button(pin, pull_up=True)
            print(f"Initialized button '{name}' on GPIO pin {pin}")
        except Exception as e:
            print(f"Error initializing button '{name}' on GPIO pin {pin}: {e}")
    
    # Track last button press time for cooldown
    last_press_time = 0
    
    # Define button press handlers
    def button_pressed(name):
        nonlocal last_press_time
        current_time = time.time()
        
        # Check for input cooldown
        if current_time - last_press_time < INPUT_COOLDOWN:
            print(f"Button '{name}' press ignored (cooldown active)")
            return
            
        # Update last press time
        last_press_time = current_time
        
        # Send key event
        key = button_to_key[name]
        event = pygame.event.Event(pygame.KEYDOWN, {"key": key})
        pygame.event.post(event)
        print(f"Button '{name}' pressed, sending key {key}")
        
        # Visual feedback could be added here (e.g., LED flash)
    
    # Attach handlers to buttons
    for name, button in buttons.items():
        button.when_pressed = lambda n=name: button_pressed(n)
    
    print(f"Button handler running with {INPUT_COOLDOWN}s cooldown. Press Ctrl+C to exit.")
    
    try:
        # Keep the script running
        pause()
    except KeyboardInterrupt:
        print("Button handler stopped.")
        sys.exit(0)

if __name__ == "__main__":
    main()
