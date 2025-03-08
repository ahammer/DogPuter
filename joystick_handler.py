#!/usr/bin/env python3
"""
Joystick handler for DogPuter
This script maps a GPIO-based joystick to events that the main DogPuter application can process.
It's useful for DIY joysticks or when using analog joysticks connected via ADC.
Includes input cooldown to prevent rapid joystick movements.
"""

from gpiozero import MCP3008
from signal import pause
import pygame
import os
import time
import sys

# Define ADC channels for joystick axes
# This assumes you're using an MCP3008 ADC connected via SPI
# Adjust channel numbers based on your wiring
JOYSTICK_X_CHANNEL = 0  # ADC channel for X axis
JOYSTICK_Y_CHANNEL = 1  # ADC channel for Y axis

# Define GPIO pin for joystick button (if present)
JOYSTICK_BUTTON_PIN = 25

# Joystick settings
JOYSTICK_DEADZONE = 0.1  # Ignore small movements
JOYSTICK_THRESHOLD = 0.5  # Threshold for registering a direction change

# Input cooldown settings
INPUT_COOLDOWN = 0.5  # seconds between allowed joystick movements
BUTTON_COOLDOWN = 0.5  # seconds between allowed button presses

def main():
    """Main function to run the joystick handler"""
    # Initialize pygame
    pygame.init()
    
    # Create a dummy window (required for pygame.event to work)
    os.environ["SDL_VIDEODRIVER"] = "dummy"
    pygame.display.set_mode((1, 1))
    
    try:
        # Initialize ADC for joystick axes
        # The MCP3008 is a 10-bit ADC, so values range from 0 to 1023
        x_axis = MCP3008(channel=JOYSTICK_X_CHANNEL)
        y_axis = MCP3008(channel=JOYSTICK_Y_CHANNEL)
        
        # Initialize button (if present)
        try:
            from gpiozero import Button
            joystick_button = Button(JOYSTICK_BUTTON_PIN, pull_up=True)
            
            # Track last button press time for cooldown
            last_button_time = 0
            
            def button_pressed():
                nonlocal last_button_time
                current_time = time.time()
                
                # Check for button cooldown
                if current_time - last_button_time < BUTTON_COOLDOWN:
                    print("Joystick button press ignored (cooldown active)")
                    return
                    
                # Update last button press time
                last_button_time = current_time
                
                # Send key event
                event = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_SPACE})
                pygame.event.post(event)
                print("Joystick button pressed")
            
            joystick_button.when_pressed = button_pressed
            print(f"Initialized joystick button on GPIO pin {JOYSTICK_BUTTON_PIN}")
        except Exception as e:
            print(f"Error initializing joystick button: {e}")
            joystick_button = None
        
        print(f"Joystick handler running with {INPUT_COOLDOWN}s cooldown. Press Ctrl+C to exit.")
        
        # Track joystick state to detect changes
        last_x_direction = 0  # -1: left, 0: center, 1: right
        last_y_direction = 0  # -1: up, 0: center, 1: down
        
        # Track last direction change time for cooldown
        last_direction_time = 0
        
        # Main loop
        while True:
            # Read joystick values and convert to -1 to 1 range
            # Center is around 0.5 for MCP3008
            x_value = (x_axis.value * 2) - 1
            y_value = (y_axis.value * 2) - 1
            
            # Apply deadzone
            if abs(x_value) < JOYSTICK_DEADZONE:
                x_value = 0
            if abs(y_value) < JOYSTICK_DEADZONE:
                y_value = 0
            
            # Determine current directions
            x_direction = 0
            if x_value > JOYSTICK_THRESHOLD:
                x_direction = 1  # right
            elif x_value < -JOYSTICK_THRESHOLD:
                x_direction = -1  # left
                
            y_direction = 0
            if y_value > JOYSTICK_THRESHOLD:
                y_direction = 1  # down (y-axis is inverted)
            elif y_value < -JOYSTICK_THRESHOLD:
                y_direction = -1  # up (y-axis is inverted)
            
            # Get current time for cooldown check
            current_time = time.time()
            
            # Check for direction changes with cooldown
            direction_changed = False
            
            if x_direction != last_x_direction or y_direction != last_y_direction:
                # Check cooldown before processing direction change
                if current_time - last_direction_time < INPUT_COOLDOWN:
                    # Skip this update if cooldown is active
                    pass
                else:
                    direction_changed = True
                    last_direction_time = current_time
                    
                    # Process X direction change
                    if x_direction != last_x_direction:
                        if x_direction == 1:
                            # Right movement
                            event = pygame.event.Event(pygame.JOYAXISMOTION, {"joy": 0, "axis": 0, "value": 1.0})
                            pygame.event.post(event)
                            print("Joystick moved right")
                        elif x_direction == -1:
                            # Left movement
                            event = pygame.event.Event(pygame.JOYAXISMOTION, {"joy": 0, "axis": 0, "value": -1.0})
                            pygame.event.post(event)
                            print("Joystick moved left")
                        last_x_direction = x_direction
                    
                    # Process Y direction change
                    if y_direction != last_y_direction:
                        if y_direction == 1:
                            # Down movement
                            event = pygame.event.Event(pygame.JOYAXISMOTION, {"joy": 0, "axis": 1, "value": 1.0})
                            pygame.event.post(event)
                            print("Joystick moved down")
                        elif y_direction == -1:
                            # Up movement
                            event = pygame.event.Event(pygame.JOYAXISMOTION, {"joy": 0, "axis": 1, "value": -1.0})
                            pygame.event.post(event)
                            print("Joystick moved up")
                        last_y_direction = y_direction
            
            # Sleep to avoid using too much CPU
            # Shorter sleep time for more responsive input
            time.sleep(0.05)
            
    except KeyboardInterrupt:
        print("Joystick handler stopped.")
        sys.exit(0)
    except Exception as e:
        print(f"Error in joystick handler: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
