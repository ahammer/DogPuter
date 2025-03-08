#!/usr/bin/env python3
"""
Main entry point for the DogPuter application.
This allows running the application using 'python -m dogputer'
"""

import argparse
from dogputer.main import DogPuter
from dogputer.core.config import load_config

def main():
    """Main function to run the DogPuter application"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='DogPuter - Interactive interface for dogs')
    parser.add_argument('--config', '-c', type=str, default=None,
                        help='Configuration to use (e.g., "development" or "x-arcade")')
    parser.add_argument('--list-configs', '-l', action='store_true',
                        help='List available configurations and exit')
    args = parser.parse_args()
    
    # If list-configs is specified, list available configurations and exit
    if args.list_configs:
        print("Available configurations:")
        print("  - development (default): Number keys 0-9 and arrow keys")
        print("  - x-arcade: X-Arcade joystick and buttons")
        return
    
    # Load the specified configuration
    config = load_config(args.config)
    
    # Initialize and run the application
    app = DogPuter(config=config)
    app.run()

if __name__ == "__main__":
    main()
