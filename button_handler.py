#!/usr/bin/env python3
"""
Button handler for DogPuter
This script maps physical buttons connected to GPIO pins to keyboard events
that the main DogPuter application can process.
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
    "treat": 22,  # GPIO pin for "treat" button
    "outside": 23,# GPIO pin for "outside" button
    "walk": 24,   # GPIO pin for "walk" button
    # Add more buttons as needed
}

# Map button names to pygame key constants
button_to_key = {
    "play": pygame.K_a,
    "rope": pygame.K_s,
    "ball": pygame.K_d,
    "treat": pygame.K_f,
    "outside": pygame.K_g,
    "walk": pygame.K_h,
    # Add more mappings as needed
}

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
    
    # Define button press handlers
    def button_pressed(name):
        key = button_to_key[name]
        event = pygame.event.Event(pygame.KEYDOWN, {"key": key})
        pygame.event.post(event)
        print(f"Button '{name}' pressed, sending key {key}")
    
    # Attach handlers to buttons
    for name, button in buttons.items():
        button.when_pressed = lambda n=name: button_pressed(n)
    
    print("Button handler running. Press Ctrl+C to exit.")
    
    try:
        # Keep the script running
        pause()
    except KeyboardInterrupt:
        print("Button handler stopped.")
        sys.exit(0)

if __name__ == "__main__":
    main()
