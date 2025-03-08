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

## Repository Structure

```
dogputer/
├── src/                    # Source code
│   └── dogputer/          
│       ├── core/           # Core application functionality
│       ├── ui/             # User interface components
│       ├── io/             # Input/output handling
│       └── utils/          # Utility functions and helpers
├── tests/                  # Test suite
│   ├── unit/               # Unit tests
│   ├── integration/        # Integration tests
│   └── fixtures/           # Test fixtures and helpers
├── media/                  # Media files
│   ├── images/             # Image files
│   ├── sounds/             # Sound files
│   └── videos/             # Video files
├── docs/                   # Documentation
└── .github/                # GitHub configuration
    └── workflows/          # CI/CD workflows
```

## Setup

### Requirements

- Python 3.7+
- Pygame
- MoviePy
- pyttsx3 (for TTS functionality)

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/dogputer.git
cd dogputer

# Install the package and dependencies
pip install -e .

# Install development dependencies
pip install -e ".[dev]"
```

### Running the Application

```bash
# From the repository root
python src/dogputer/main.py
```

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

### X-Arcade Support

DogPuter includes built-in support for X-Arcade controllers, which are typically recognized as keyboard devices with specific key mappings. The input handling system abstracts away the differences between input methods, allowing the application to work with X-Arcade, standard keyboards, or joysticks transparently.

To use an X-Arcade controller:

1. Connect the X-Arcade to your Raspberry Pi via USB
2. The controller will be automatically detected as a keyboard
3. Use the default key mappings or customize them in the configuration

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
