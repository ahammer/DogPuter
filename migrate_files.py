#!/usr/bin/env python3
"""
Script to migrate files to the new project structure
"""

import os
import shutil
import sys

# Source files to migrate
SOURCE_FILES = [
    # Core functionality
    ('tts_handler.py', 'src/dogputer/core/tts_handler.py'),
    ('app_state.py', 'src/dogputer/core/app_state.py'),
    ('config.py', 'src/dogputer/core/config.py'),
    
    # UI components
    ('renderer.py', 'src/dogputer/ui/renderer.py'),
    ('video_player.py', 'src/dogputer/ui/video_player.py'),
    ('view_state.py', 'src/dogputer/ui/view_state.py'),
    ('animation.py', 'src/dogputer/ui/animation.py'),
    
    # Input/Output handling
    ('button_handler.py', 'src/dogputer/io/button_handler.py'),
    ('joystick_handler.py', 'src/dogputer/io/joystick_handler.py'),
    
    # Utilities
    ('create_videos_from_images.py', 'src/dogputer/utils/create_videos_from_images.py'),
    ('create_sample_media.py', 'src/dogputer/utils/create_sample_media.py'),
    
    # Main application
    ('main.py', 'src/dogputer/main.py'),
]

# Media files directories to copy
MEDIA_DIRS = [
    ('images', 'media/images'),
    ('sounds', 'media/sounds'),
    ('videos', 'media/videos'),
]

# Documentation files
DOC_FILES = [
    ('raspberry_pi_setup.md', 'docs/raspberry_pi_setup.md'),
]

def copy_file(src, dest):
    """Copy a file, creating any necessary parent directories"""
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    
    if os.path.exists(src):
        print(f"Copying {src} -> {dest}")
        shutil.copy2(src, dest)
    else:
        print(f"Warning: Source file not found: {src}")

def copy_directory(src, dest):
    """Copy a directory recursively, creating parent directories if needed"""
    if not os.path.exists(src):
        print(f"Warning: Source directory not found: {src}")
        return
        
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    
    if os.path.exists(dest):
        print(f"Merging directory {src} -> {dest}")
        for item in os.listdir(src):
            s = os.path.join(src, item)
            d = os.path.join(dest, item)
            if os.path.isdir(s):
                copy_directory(s, d)
            else:
                copy_file(s, d)
    else:
        print(f"Copying directory {src} -> {dest}")
        shutil.copytree(src, dest)

def create_init_file(directory):
    """Create an __init__.py file in the specified directory"""
    init_file = os.path.join(directory, '__init__.py')
    if not os.path.exists(init_file):
        print(f"Creating {init_file}")
        with open(init_file, 'w') as f:
            f.write(f"# {os.path.basename(directory)} package\n")

def create_init_files(root_dir):
    """Recursively create __init__.py files in all subdirectories"""
    for dirpath, dirnames, filenames in os.walk(root_dir):
        if os.path.basename(dirpath) != '__pycache__':
            create_init_file(dirpath)

def main():
    """Main function to run the migration process"""
    # Get the root directory
    if len(sys.argv) > 1:
        root_dir = sys.argv[1]
    else:
        root_dir = os.getcwd()
        
    # Change to the root directory
    os.chdir(root_dir)
    
    # Copy source files
    for src, dest in SOURCE_FILES:
        copy_file(src, dest)
    
    # Copy media directories
    for src, dest in MEDIA_DIRS:
        copy_directory(src, dest)
    
    # Copy documentation files
    for src, dest in DOC_FILES:
        copy_file(src, dest)
    
    # Create __init__.py files
    create_init_files('src/dogputer')
    
    print("\nMigration complete!")
    print("\nNOTE: This script only copies files to the new structure.")
    print("You will need to update imports in the migrated files to use the new package structure.")
    print("For example, change 'from video_player import VideoPlayer' to 'from dogputer.ui.video_player import VideoPlayer'")

if __name__ == "__main__":
    main()
