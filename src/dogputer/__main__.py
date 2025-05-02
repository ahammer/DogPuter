#!/usr/bin/env python3
"""
Main entry point for the DogPuter application.
This allows running the application using 'python -m dogputer'
"""

import argparse
from dogputer.simple_main import SimpleDogPuter
from dogputer.core.config import load_config

def main():
    """Main function to run the DogPuter application"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='DogPuter - Interactive interface for dogs')
    parser.add_argument('--config', '-c', type=str, default=None,
                        help='Configuration to use (e.g., "development" or "x-arcade")')
    parser.add_argument('--list-configs', '-l', action='store_true',
                        help='List available configurations and exit')
    parser.add_argument('--fullscreen', '-f', action='store_true',
                        help='Run in fullscreen mode')
    args = parser.parse_args()
    
    # If list-configs is specified, list available configurations and exit
    if args.list_configs:
        print("Available configurations:")
        print("  - development (default): Number keys 0-9 and arrow keys")
        print("  - x-arcade-kb: X-Arcade in keyboard mode")
        print("  - x-arcade-gc: X-Arcade in gamepad/controller mode")
        return
    
    # Get the config name
    config_name = args.config
    
    # If the config is x-arcade, autodetect gamepad/keyboard mode
    if config_name == 'x-arcade':
        import pygame
        pygame.init()  # Initialize pygame to check for joysticks
        
        # Check if joysticks are available
        if pygame.joystick.get_count() > 0:
            print("X-Arcade gamepad detected, using gamepad configuration")
            config_name = 'x-arcade-gc'
        else:
            print("No gamepad detected, using X-Arcade keyboard configuration")
            config_name = 'x-arcade-kb'
        
        pygame.quit()  # Clean up pygame resources for now
    
    # Load the specified configuration
    config = load_config(config_name)
    
    # Initialize and run the application
    app = SimpleDogPuter()
    app.run()

if __name__ == "__main__":
    main()
