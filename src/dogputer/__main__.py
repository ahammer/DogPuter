#!/usr/bin/env python3
"""
Main entry point for the DogPuter application.
This allows running the application using 'python -m dogputer'
"""

from dogputer.main import DogPuter

def main():
    """Main function to run the DogPuter application"""
    app = DogPuter()
    app.run()

if __name__ == "__main__":
    main()
