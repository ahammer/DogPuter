# DogPuter

An interactive interface for dogs, designed to run on Raspberry Pi with support for keyboard, joystick, and X-Arcade inputs.

## Overview

DogPuter provides an engaging interface for dogs, allowing them to interact with various media including videos, images, and sounds through simple button presses. The application is designed to run on Raspberry Pi but can be developed and tested on desktop systems.

## Features

- Video playback with smooth transitions
- Text-to-speech functionality
- Support for multiple input methods (keyboard, joystick, X-Arcade)
- Customizable UI with animated elements
- Channel-based content organization
- Configurable key mappings via JSON files
- Web interface for easy command mapping and video upload

## Repository Structure

```
dogputer/
├── configs/               # Configuration files
│   └── keymappings/       # Input key mapping configs
├── src/                   # Source code
│   └── dogputer/          
│       ├── core/          # Core application functionality
│       ├── ui/            # User interface components
│       ├── io/            # Input/output handling
│       ├── web/           # Web interface components
│       └── utils/         # Utility functions and helpers
├── tests/                 # Test suite
│   ├── unit/              # Unit tests
│   ├── integration/       # Integration tests
│   └── fixtures/          # Test fixtures and helpers
├── media/                 # Media files
│   ├── images/            # Image files
│   ├── sounds/            # Sound files
│   └── videos/            # Video files
├── docs/                  # Documentation
└── .github/               # GitHub configuration
    └── workflows/         # CI/CD workflows
```

## Setup

### Requirements

- Python 3.7+
- Pygame
- MoviePy
- pyttsx3 (for TTS functionality)
- Flask (for web interface)
- QR Code (for web interface access)

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/dogputer.git
cd dogputer

# Create and activate a virtual environment
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate

# Install the package and dependencies
pip install -e .

# Install development dependencies
pip install -e ".[dev]"
```

### Running the Application

The application can be run with different key mapping configurations:

```bash
# Run with default (development) configuration
python -m dogputer

# Run with specific configuration
python -m dogputer --config x-arcade

# List available configurations
python -m dogputer --list-configs
```

### Web Interface

DogPuter now includes a web interface that runs alongside the main application, allowing you to:

1. View and edit command mappings from any device on your network
2. Upload new videos in the command_name.mp4 format
3. Manage all registered actions (commands with associated videos)

The web interface is automatically started when you run the application, and:
- Shows the URL and QR code on the main DogPuter screen
- Runs on port 5000 by default
- Can be accessed from any device on the same network

For more details, see the [Web Interface Documentation](docs/web_interface.md).

### Configuration Files

Configuration files are JSON files that define key mappings, display settings, and other options. Default configs are stored in `configs/keymappings/` directory.

DogPuter looks for configuration files in the following locations (in order of priority):
1. Current directory (`.`)
2. User's home config directory (`~/.config/dogputer/`)
3. Application directory (`configs/keymappings/`)

You can create custom configuration files by copying and modifying the default ones.

#### Default Configurations

- **development.json**: Uses number keys (0-9) and arrow keys, suitable for development and testing
- **x-arcade.json**: Configured for X-Arcade controllers with extensive button mappings

#### Creating Custom Configurations

To create a custom configuration:

1. Copy one of the existing config files as a template
2. Modify the key mappings and other settings as needed
3. Save it in `~/.config/dogputer/` or in the application's `configs/keymappings/` directory
4. Run the application with your custom config: `python -m dogputer --config your_config_name`

## Development

### Testing

The project uses pytest for testing. Tests are organized into unit tests and integration tests.

```bash
# Run all tests
pytest

# Run specific test categories
pytest tests/unit
pytest tests/integration

# Run tests with coverage report
pytest --cov=src/dogputer
```

### Building Binaries

The project can be packaged into standalone executables using PyInstaller:

```bash
# Install PyInstaller
pip install pyinstaller

# Build a single-file executable
pyinstaller --onefile --name dogputer src/dogputer/__main__.py

# The executable will be in the dist/ directory
```

For Raspberry Pi deployment, it's recommended to use the Python package:

```bash
# Build the distribution package
pip install build
python -m build

# Install on the target system
pip install dist/dogputer-0.1.0.tar.gz
```

### X-Arcade Support

DogPuter includes built-in support for X-Arcade controllers, which are typically recognized as keyboard devices with specific key mappings. The input handling system abstracts away the differences between input methods, allowing the application to work with X-Arcade, standard keyboards, or joysticks transparently.

To use an X-Arcade controller:

1. Connect the X-Arcade to your Raspberry Pi via USB
2. The controller will be automatically detected as a keyboard
3. Run the application with the x-arcade configuration: `python -m dogputer --config x-arcade`

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
