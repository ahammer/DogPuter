import pygame
import os
import json
import sys
from pathlib import Path

# Default config paths
CONFIG_DIRS = [
    # Current directory
    Path('.'),
    # User's home config directory
    Path.home() / '.config' / 'dogputer',
    # Application directory
    Path(__file__).parent.parent.parent.parent / 'configs'
]

# Default key mappings
DEFAULT_CONFIG_NAME = 'development'

def get_pygame_key_constant(key_name):
    """Convert a key name string (e.g., 'K_a') to a pygame key constant."""
    if not key_name.startswith('K_'):
        return None
        
    try:
        return getattr(pygame, key_name)
    except AttributeError:
        print(f"Warning: Unknown pygame key constant: {key_name}")
        return None

def load_config(config_name=None):
    """
    Load configuration from a JSON file.
    
    Args:
        config_name (str): Name of the config file to load (without extension)
    
    Returns:
        dict: Loaded configuration with pygame key constants
    """
    # Use default if no config name provided
    config_name = config_name or DEFAULT_CONFIG_NAME
    
    # Try to find the config file in the search paths
    config_filename = f"{config_name}.json"
    config_path = None
    
    # Check keymappings subdirectory first
    for config_dir in CONFIG_DIRS:
        keymappings_dir = config_dir / 'keymappings'
        potential_path = keymappings_dir / config_filename
        
        if potential_path.exists():
            config_path = potential_path
            break
    
    # If not found in keymappings, check main dirs
    if config_path is None:
        for config_dir in CONFIG_DIRS:
            potential_path = config_dir / config_filename
            
            if potential_path.exists():
                config_path = potential_path
                break
    
    # If config file not found, use builtin default
    if config_path is None:
        print(f"Warning: Config file '{config_filename}' not found, using builtin defaults")
        return create_default_config()
    
    # Load the config
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
            print(f"Loaded config from {config_path}")
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error loading config file {config_path}: {e}")
        return create_default_config()
    
    # Convert keys to pygame constants for key_mappings
    if 'key_mappings' in config:
        key_mappings = {}
        for key_name, value in config['key_mappings'].items():
            key_constant = get_pygame_key_constant(key_name)
            if key_constant is not None:
                key_mappings[key_constant] = value
        config['key_mappings'] = key_mappings
    
    # Convert keys to pygame constants for arrow_key_mappings
    if 'arrow_key_mappings' in config:
        arrow_key_mappings = {}
        for key_name, value in config['arrow_key_mappings'].items():
            key_constant = get_pygame_key_constant(key_name)
            if key_constant is not None:
                arrow_key_mappings[key_constant] = value
        config['arrow_key_mappings'] = arrow_key_mappings
    
    # Convert X-Arcade mappings if present
    if 'xarcade_mappings' in config:
        xarcade_mappings = {}
        for logical_name, key_name in config['xarcade_mappings'].items():
            key_constant = get_pygame_key_constant(key_name)
            if key_constant is not None:
                xarcade_mappings[logical_name] = key_constant
        config['xarcade_mappings'] = xarcade_mappings
    
    # Extract specific sections into global variables
    extract_to_globals(config)
    
    return config

def create_default_config():
    """Create a default configuration dictionary"""
    return {
        "colors": {
            "BLUE_PRIMARY": [0, 102, 170],
            "YELLOW_PRIMARY": [255, 204, 0],
            "WHITE": [255, 255, 255],
            "LIGHT_BLUE": [153, 204, 255],
            "CREAM": [255, 255, 204],
            "SUCCESS_COLOR": [102, 204, 255],
            "ALERT_COLOR": [255, 255, 153],
            "ERROR_COLOR": [255, 153, 0]
        },
        "display": {
            "SCREEN_WIDTH": 800,
            "SCREEN_HEIGHT": 600,
            "BACKGROUND_COLOR": [0, 102, 170],
            "DEFAULT_DISPLAY_TIME": 5,
            "PAW_CURSOR_SIZE": 120,
            "BUTTON_HIGHLIGHT_THICKNESS": 4,
            "FEEDBACK_HEIGHT": 80,
            "WAITING_TEXT_SIZE": 72,
            "FEEDBACK_TEXT_SIZE": 40
        },
        "animations": {
            "FEEDBACK_DURATION": 1.8,
            "PARTICLE_MAX_COUNT": 40,
            "PARTICLE_DEFAULT_LIFETIME": 1.0,
            "PARTICLE_SIZE_RANGE": [3, 10],
            "PARTICLE_SPEED_RANGE": [20, 80],
            "TRANSITION_DURATION": 0.8,
            "WAITING_ANIMATION_SPEED": 1.5
        },
        "key_mappings": {
            pygame.K_0: {"sound": "play.wav", "image": "play.jpg", "display_time": 5, "command": "play"},
            pygame.K_1: {"sound": "rope.wav", "image": "rope.jpg", "display_time": 5, "command": "rope"},
            pygame.K_2: {"sound": "ball.wav", "image": "ball.jpg", "display_time": 5, "command": "ball"},
            pygame.K_3: {"sound": "hugs.wav", "image": "hugs.jpg", "display_time": 5, "command": "hugs"},
            pygame.K_4: {"sound": "outside.wav", "image": "outside.jpg", "display_time": 5, "command": "outside"},
            pygame.K_5: {"sound": "walk.wav", "image": "walk.jpg", "display_time": 5, "command": "walk"},
            pygame.K_6: {"sound": "water.wav", "image": "water.jpg", "display_time": 5, "command": "water"},
            pygame.K_7: {"sound": "park.wav", "image": "park.jpg", "display_time": 5, "command": "park"},
            pygame.K_8: {"sound": "toy.wav", "image": "toy.jpg", "display_time": 5, "command": "toy"},
            pygame.K_9: {"sound": "bed.wav", "image": "bed.jpg", "display_time": 5, "command": "bed"}
        },
        "arrow_key_mappings": {
            pygame.K_UP: 0,
            pygame.K_RIGHT: 1,
            pygame.K_DOWN: 2, 
            pygame.K_LEFT: 3
        },
        "video_channels": [
            {"name": "Squirrels", "video": "squirrels.mp4"},
            {"name": "Birds", "video": "birds.mp4"},
            {"name": "Dogs", "video": "dogs.mp4"},
            {"name": "Cats", "video": "cats.mp4"},
            {"name": "Water", "video": "water.mp4"}
        ]
    }

def extract_to_globals(config):
    """Extract configuration values to global variables for backward compatibility"""
    # Extract colors
    if 'colors' in config:
        globals().update({k: tuple(v) for k, v in config['colors'].items()})
    
    # Extract display settings
    if 'display' in config:
        globals().update({k: tuple(v) if isinstance(v, list) else v for k, v in config['display'].items()})
    
    # Extract animation settings
    if 'animations' in config:
        for k, v in config['animations'].items():
            if isinstance(v, list) and len(v) == 2:
                globals()[k] = tuple(v)
            else:
                globals()[k] = v
    
    # Extract key mappings and other settings
    globals()['KEY_MAPPINGS'] = config.get('key_mappings', {})
    globals()['ARROW_KEY_MAPPINGS'] = config.get('arrow_key_mappings', {})
    globals()['VIDEO_CHANNELS'] = config.get('video_channels', [])
    globals()['XARCADE_MAPPINGS'] = config.get('xarcade_mappings', {})

# Load the default configuration on module import
config = load_config()

# Make configuration available via module variables for backward compatibility
# The global variables will be populated by extract_to_globals during load_config
KEY_MAPPINGS = config.get('key_mappings', {})
ARROW_KEY_MAPPINGS = config.get('arrow_key_mappings', {})
VIDEO_CHANNELS = config.get('video_channels', [])
