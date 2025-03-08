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
DEFAULT_KEYMAPPING = 'development'
DEFAULT_UI_CONFIG = 'display'
DEFAULT_CONTENT_CONFIG = 'videos'

def get_pygame_key_constant(key_name):
    """Convert a key name string (e.g., 'K_a') to a pygame key constant."""
    if not key_name.startswith('K_'):
        return None
        
    try:
        return getattr(pygame, key_name)
    except AttributeError:
        print(f"Warning: Unknown pygame key constant: {key_name}")
        return None

def get_gamepad_constant(button_name):
    """Convert a gamepad button name to a constant value."""
    # Parse gamepad button names like GAMEPAD1_BUTTON1, GAMEPAD2_UP, etc.
    if not button_name.startswith('GAMEPAD'):
        return None
        
    try:
        parts = button_name.split('_')
        if len(parts) < 2:
            return None
            
        gamepad_num = int(parts[0][7:]) - 1  # GAMEPAD1 -> 0, GAMEPAD2 -> 1
        button_type = parts[1]
        
        if button_type == 'BUTTON':
            button_num = int(parts[2]) - 1  # BUTTON1 -> 0, BUTTON2 -> 1
            return ('button', gamepad_num, button_num)
        elif button_type in ('UP', 'DOWN', 'LEFT', 'RIGHT'):
            return ('hat', gamepad_num, button_type.lower())
        elif button_type == 'START':
            return ('button', gamepad_num, 9)  # Typically button 9 or 10 is START
            
        return None
    except (ValueError, IndexError):
        print(f"Warning: Invalid gamepad button name: {button_name}")
        return None

def find_config_file(config_name, subdirectory=None):
    """Find a config file in the search paths."""
    config_filename = f"{config_name}.json"
    
    # Check subdirectory first if provided
    if subdirectory:
        for config_dir in CONFIG_DIRS:
            sub_dir = config_dir / subdirectory
            potential_path = sub_dir / config_filename
            
            if potential_path.exists():
                return potential_path
    
    # If not found in subdirectory, check main dirs
    for config_dir in CONFIG_DIRS:
        potential_path = config_dir / config_filename
        
        if potential_path.exists():
            return potential_path
    
    return None

def load_ui_config(config_name=None):
    """Load UI configuration (colors, display, animations)."""
    config_name = config_name or DEFAULT_UI_CONFIG
    config_path = find_config_file(config_name, 'ui')
    
    if config_path is None:
        print(f"Warning: UI config file '{config_name}.json' not found, using builtin defaults")
        return create_default_ui_config()
    
    try:
        with open(config_path, 'r') as f:
            ui_config = json.load(f)
            print(f"Loaded UI config from {config_path}")
            return ui_config
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error loading UI config file {config_path}: {e}")
        return create_default_ui_config()

def load_keymapping(config_name=None):
    """Load key mapping configuration."""
    config_name = config_name or DEFAULT_KEYMAPPING
    config_path = find_config_file(config_name, 'keymappings')
    
    if config_path is None:
        print(f"Warning: Keymapping file '{config_name}.json' not found, using builtin defaults")
        return create_default_keymapping()
    
    try:
        with open(config_path, 'r') as f:
            raw_mappings = json.load(f)
            print(f"Loaded keymapping from {config_path}")
            
            # Process the flat mapping format
            input_mappings = {}
            for key_name, command in raw_mappings.items():
                # Check if it's a gamepad mapping
                if key_name.startswith('GAMEPAD'):
                    gamepad_const = get_gamepad_constant(key_name)
                    if gamepad_const:
                        input_mappings[gamepad_const] = command
                # Otherwise treat it as a keyboard key
                else:
                    key_constant = get_pygame_key_constant(key_name)
                    if key_constant is not None:
                        input_mappings[key_constant] = command
            
            return input_mappings
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error loading keymapping file {config_path}: {e}")
        return create_default_keymapping()

def load_content_config(config_name=None):
    """Load content configuration (videos, channels, etc.)."""
    config_name = config_name or DEFAULT_CONTENT_CONFIG
    config_path = find_config_file(config_name, 'content')
    
    if config_path is None:
        print(f"Warning: Content config file '{config_name}.json' not found, using builtin defaults")
        return create_default_content_config()
    
    try:
        with open(config_path, 'r') as f:
            content_config = json.load(f)
            print(f"Loaded content config from {config_path}")
            return content_config
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error loading content config file {config_path}: {e}")
        return create_default_content_config()

def create_default_ui_config():
    """Create default UI configuration."""
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
        }
    }

def create_default_keymapping():
    """Create default key mapping."""
    return {
        pygame.K_0: "play",
        pygame.K_1: "rope",
        pygame.K_2: "ball",
        pygame.K_3: "hugs",
        pygame.K_4: "outside",
        pygame.K_5: "walk",
        pygame.K_6: "water",
        pygame.K_7: "park",
        pygame.K_8: "toy",
        pygame.K_9: "bed"
    }

def create_default_content_config():
    """Create default content configuration."""
    return {
        "video_channels": [
            {"name": "Squirrels", "video": "squirrels.mp4"},
            {"name": "Birds", "video": "birds.mp4"},
            {"name": "Dogs", "video": "dogs.mp4"},
            {"name": "Cats", "video": "cats.mp4"},
            {"name": "Water", "video": "water.mp4"}
        ]
    }

def extract_to_globals(ui_config):
    """Extract UI configuration values to global variables for backward compatibility."""
    # Extract colors
    if 'colors' in ui_config:
        globals().update({k: tuple(v) for k, v in ui_config['colors'].items()})
    
    # Extract display settings
    if 'display' in ui_config:
        globals().update({k: tuple(v) if isinstance(v, list) else v for k, v in ui_config['display'].items()})
    
    # Extract animation settings
    if 'animations' in ui_config:
        for k, v in ui_config['animations'].items():
            if isinstance(v, list) and len(v) == 2:
                globals()[k] = tuple(v)
            else:
                globals()[k] = v

def load_config(keymapping_name=None):
    """
    Load all configuration components.
    
    Args:
        keymapping_name (str): Name of the keymapping to load (without extension)
    
    Returns:
        dict: Combined configuration
    """
    # Load UI configuration
    ui_config = load_ui_config()
    
    # Load key mappings
    input_mappings = load_keymapping(keymapping_name)
    
    # Load content configuration
    content_config = load_content_config()
    
    # Combine everything
    config = {
        **ui_config,
        "input_mappings": input_mappings,
        **content_config
    }
    
    # For backward compatibility
    config["key_mappings"] = input_mappings
    
    # Extract UI settings to globals for backward compatibility
    extract_to_globals(ui_config)
    
    return config

# Load the default configuration on module import
config = load_config()

# Make configuration available via module variables for backward compatibility
INPUT_MAPPINGS = config.get('input_mappings', {})
KEY_MAPPINGS = INPUT_MAPPINGS  # For backward compatibility
VIDEO_CHANNELS = config.get('video_channels', [])
