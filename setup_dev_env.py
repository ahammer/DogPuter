#!/usr/bin/env python3
"""
Script to set up a development environment for DogPuter.
This will create a virtual environment and install all required dependencies.
"""

import os
import sys
import subprocess
import platform
import argparse

def main():
    parser = argparse.ArgumentParser(description="Set up a development environment for DogPuter")
    parser.add_argument("--venv-path", default="venv", help="Path to create the virtual environment")
    parser.add_argument("--dev", action="store_true", help="Install development dependencies")
    parser.add_argument("--test", action="store_true", help="Run tests after installation")
    args = parser.parse_args()

    venv_path = args.venv_path
    
    # Check if Python 3.7+ is available
    if sys.version_info < (3, 7):
        print("Error: Python 3.7 or higher is required")
        sys.exit(1)
    
    print(f"Setting up virtual environment in '{venv_path}'...")
    
    # Create virtual environment
    try:
        subprocess.run([sys.executable, "-m", "venv", venv_path], check=True)
    except subprocess.CalledProcessError:
        print("Error: Failed to create virtual environment")
        sys.exit(1)
    
    # Determine the path to the Python executable in the virtual environment
    if platform.system() == "Windows":
        python_exec = os.path.join(venv_path, "Scripts", "python.exe")
        pip_exec = os.path.join(venv_path, "Scripts", "pip.exe")
    else:
        python_exec = os.path.join(venv_path, "bin", "python")
        pip_exec = os.path.join(venv_path, "bin", "pip")
    
    # Upgrade pip
    print("Upgrading pip...")
    try:
        subprocess.run([python_exec, "-m", "pip", "install", "--upgrade", "pip"], check=True)
    except subprocess.CalledProcessError:
        print("Warning: Failed to upgrade pip")
    
    # Install package in development mode
    print("Installing DogPuter package...")
    if args.dev:
        # Install with development dependencies
        try:
            subprocess.run([pip_exec, "install", "-e", ".[dev]"], check=True)
        except subprocess.CalledProcessError:
            print("Error: Failed to install development dependencies")
            sys.exit(1)
    else:
        # Install without development dependencies
        try:
            subprocess.run([pip_exec, "install", "-e", "."], check=True)
        except subprocess.CalledProcessError:
            print("Error: Failed to install package")
            sys.exit(1)
    
    # Run tests if requested
    if args.test:
        print("Running tests...")
        try:
            subprocess.run([python_exec, "-m", "pytest"], check=True)
        except subprocess.CalledProcessError:
            print("Warning: Some tests failed")
    
    print("\nDogPuter development environment setup complete!")
    print("\nTo activate the virtual environment:")
    if platform.system() == "Windows":
        print(f"    {venv_path}\\Scripts\\activate")
    else:
        print(f"    source {venv_path}/bin/activate")
    
    print("\nTo run DogPuter:")
    print("    python -m dogputer")
    print("    # or with a specific config:")
    print("    python -m dogputer --config x-arcade")

if __name__ == "__main__":
    main()
