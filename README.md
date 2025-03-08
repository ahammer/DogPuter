# DogPuter

A simple Pygame-based application designed to run on a Raspberry Pi that allows dogs to interact with buttons and joysticks to trigger sounds, images, and videos. Features text-to-speech commands and smooth transitions between media.

## Overview

DogPuter maps keystrokes to sounds and images, and joystick movements to videos. When a button is pressed, it plays a corresponding sound (like "play", "rope", or "ball") and displays an image. When joysticks are used, it changes "channels" to play videos that might entertain a dog (like videos of squirrels).

## Requirements

- Python 3.6+
- Pygame
- Raspberry Pi (recommended, but can run on any computer with Python)
- Input devices (keyboard, buttons, joystick)
- pyttsx3 (for text-to-speech functionality)

## Setup

1. Clone or download this repository to your Raspberry Pi
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

3. Set up your OpenAI API key for DALL-E image generation:

```bash
# On Linux/macOS
export OPENAI_API_KEY=your_api_key_here

# On Windows (Command Prompt)
set OPENAI_API_KEY=your_api_key_here

# On Windows (PowerShell)
$env:OPENAI_API_KEY="your_api_key_here"
```

4. Generate sample media files using DALL-E:

```bash
python create_sample_media.py
```

This will:
- Create the necessary directories (`sounds`, `images`, `videos`)
- Generate images using DALL-E based on the key mappings in `config.py`
- Create sample sound files
- Create placeholder text files for videos

5. Alternatively, you can manually add your own media files:
   - Add sound files to the `sounds` directory (WAV format recommended)
   - Add image files to the `images` directory (JPG or PNG format)
   - Add video files to the `videos` directory (MP4 format)

## Customization

### Key Mappings

You can customize the key mappings in the `config.py` file. Each key mapping associates a pygame key constant with a sound file, an image file, a display time, and a command to speak.

```python
KEY_MAPPINGS = {
    pygame.K_0: {"sound": "play.wav", "image": "play.jpg", "display_time": 5, "command": "play"},
    pygame.K_1: {"sound": "rope.wav", "image": "rope.jpg", "display_time": 5, "command": "rope"},
    # Add more key mappings as needed (keys 0-9 available)
}
```

For a list of pygame key constants, see the [pygame documentation](https://www.pygame.org/docs/ref/key.html).

### Video Channels and Arrow Key Mappings

You can customize the video channels and arrow key mappings in the `config.py` file:

```python
VIDEO_CHANNELS = [
    {"name": "Squirrels", "video": "squirrels.mp4"},
    {"name": "Birds", "video": "birds.mp4"},
    # Add more video channels as needed
]

ARROW_KEY_MAPPINGS = {
    pygame.K_UP: 0,     # Birds
    pygame.K_RIGHT: 1,  # Dogs
    pygame.K_DOWN: 2,   # Cats
    pygame.K_LEFT: 3,   # Squirrels
}
```

### Display Settings

You can also customize the display settings in the `config.py` file:

```python
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BACKGROUND_COLOR = (30, 30, 30)  # Dark gray
DEFAULT_DISPLAY_TIME = 5  # seconds
```

## Running the Application

To run the DogPuter application:

```bash
python main.py
```

## Features

### Text-to-Speech

The application now includes text-to-speech functionality using the pyttsx3 library. When a command button is pressed, the application will:

1. Play the associated sound file
2. Speak the command name using text-to-speech
3. Display the associated image

This provides auditory feedback for the user, making it easier to understand what command was triggered.

### Transitions

The application now includes smooth transitions between images and videos:

1. Image transitions: When switching between images, a fade transition is applied
2. Video transitions: When switching between videos, a fade transition is applied

These transitions make the application more visually appealing and provide a smoother user experience.

### Keyboard Controls

- Number keys (0-9): Trigger commands (play, rope, ball, etc.)
- Arrow keys: Directly select video channels
- ESC key: Exit the application

### Joystick Controls

- Move joystick: Cycle through video channels

## DALL-E Image Generation

The DogPuter application includes integration with OpenAI's DALL-E to generate appropriate images for each keypress. This feature:

1. Uses the OpenAI API to generate high-quality, contextually appropriate images
2. Creates custom images for each button/key based on its function (play, rope, ball, etc.)
3. Falls back to basic text images if the API key is not set or if there's an error

To use this feature:

1. Sign up for an OpenAI API key at [https://platform.openai.com](https://platform.openai.com)
2. Set the `OPENAI_API_KEY` environment variable as shown in the Setup section
3. Run the `create_sample_media.py` script to generate images

The script uses carefully crafted prompts for each key to generate images that are appropriate for dogs and clearly communicate the purpose of each button.

## Hardware Setup for Raspberry Pi

For a complete DogPuter setup on a Raspberry Pi, you might want to:

1. Connect physical buttons to GPIO pins and map them to keyboard keys
2. Connect a joystick via USB or GPIO
3. Connect a display via HDMI
4. Connect speakers or headphones for audio output

## License

This project is open source and available under the MIT License.
