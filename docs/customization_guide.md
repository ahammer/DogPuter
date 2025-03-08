# DogPuter Customization Guide

This guide explains how to customize your DogPuter system by updating actions, key bindings, videos, and sounds. These customizations allow you to tailor the interface to your specific needs and preferences.

## Table of Contents

1. [Understanding the System Architecture](#understanding-the-system-architecture)
2. [Input Mappings and Actions](#input-mappings-and-actions)
   - [Available Actions](#available-actions)
   - [Modifying Key Bindings](#modifying-key-bindings)
   - [X-Arcade Controller Mappings](#x-arcade-controller-mappings)
   - [Joystick Mappings](#joystick-mappings)
3. [Adding and Updating Videos](#adding-and-updating-videos)
   - [Video File Requirements](#video-file-requirements)
   - [Adding New Videos](#adding-new-videos)
   - [Configuring Video Channels](#configuring-video-channels)
4. [Adding and Updating Sounds](#adding-and-updating-sounds)
   - [Sound File Requirements](#sound-file-requirements)
   - [Adding New Sounds](#adding-new-sounds)
5. [Testing Your Changes](#testing-your-changes)

## Understanding the System Architecture

DogPuter uses a modular architecture that separates different aspects of the system:

- **Input Handling**: Processes keyboard, joystick, and X-Arcade controller inputs
- **Content Management**: Manages videos, images, and sounds
- **Actions**: Maps inputs to specific behaviors in the application

When an input event occurs (like a button press), the system:
1. Uses the input mapping configuration to determine which action to perform
2. Plays the corresponding sound
3. Displays the associated image or video
4. Uses text-to-speech to vocalize the action

## Input Mappings and Actions

### Available Actions

DogPuter comes with the following built-in actions:

- Basic actions: `play`, `rope`, `ball`, `hugs`, `outside`, `walk`, `water`, `park`, `toy`, `bed`
- Video channel actions: `video_squirrels`, `video_birds`, `video_dogs`, `video_cats`, `video_water`

Each action is associated with:
- A sound file (e.g., `ball.wav`)
- An image file (e.g., `ball.jpg`)
- A video file if available (e.g., `ball.mp4`)

### Modifying Key Bindings

Key bindings are defined in JSON configuration files located in the `configs/keymappings/` directory. The default configurations are:

- `development.json`: Uses number keys and arrow keys, suitable for development and testing
- `x-arcade-kb.json`: Configured for X-Arcade controllers in keyboard mode
- `x-arcade-gc.json`: Configured for X-Arcade controllers in gamepad mode

To modify key bindings:

1. Open the appropriate configuration file in a text editor
2. The configuration uses Pygame key constants as keys and action names as values:

```json
{
  "K_0": "play",
  "K_1": "rope",
  "K_2": "ball",
  "K_UP": "video_squirrels",
  "K_RIGHT": "video_birds"
}
```

3. To add a new binding, add a new key-value pair:
   - The key should be a valid Pygame key constant (e.g., `K_a` for the 'A' key)
   - The value should be the name of an action

Common Pygame key constants:
- `K_0` through `K_9`: Number keys
- `K_a` through `K_z`: Letter keys
- `K_UP`, `K_DOWN`, `K_LEFT`, `K_RIGHT`: Arrow keys
- `K_SPACE`: Space bar
- `K_RETURN`: Enter key

4. Save the file and restart the application for changes to take effect

### X-Arcade Controller Mappings

X-Arcade controllers can be used in two modes:

1. **Keyboard Mode**: The controller emulates keyboard presses
2. **Gamepad Mode**: The controller functions as a joystick/gamepad

To modify X-Arcade mappings:

1. For keyboard mode, edit `configs/keymappings/x-arcade-kb.json`
2. For gamepad mode, edit `configs/keymappings/x-arcade-gc.json`
3. The X-Arcade configuration uses logical button names that map to physical buttons:

```json
{
  "p1_up": "video_squirrels",
  "p1_down": "video_dogs",
  "p1_left": "video_cats", 
  "p1_right": "video_birds",
  "p1_button1": "ball",
  "p1_button2": "rope"
}
```

4. Save the file and restart the application for changes to take effect

### Joystick Mappings

Joystick mappings use a tuple format to identify joystick inputs:

```json
{
  ("button", 0, 0): "ball",
  ("button", 0, 1): "rope",
  ("hat", 0, "up"): "video_squirrels",
  ("hat", 0, "down"): "video_dogs"
}
```

Where:
- First element is the input type (`button` or `hat`)
- Second element is the joystick ID (usually 0 for the first joystick)
- Third element is the button number or hat direction

To customize joystick mappings:

1. Edit the appropriate configuration file for your setup
2. Add or modify the joystick tuples with the desired actions
3. Save the file and restart the application

## Adding and Updating Videos

### Video File Requirements

- Format: MP4 (recommended) or any format supported by MoviePy
- Resolution: Match your display resolution (e.g., 1280×720)
- Name: Must match an action name (e.g., `ball.mp4` for the `ball` action)

### Adding New Videos

1. Create a video file with the appropriate name (matching an action)
2. Place the video file in the `videos/` directory
3. Ensure there is a corresponding image file in the `images/` directory with the same base name
4. Ensure there is a corresponding sound file in the `sounds/` directory with the same base name
5. Restart the application

### Configuring Video Channels

Video channels are configured in `configs/content/videos.json`:

```json
{
  "video_channels": [
    {"name": "Squirrels", "video": "squirrels.mp4"},
    {"name": "Birds", "video": "birds.mp4"},
    {"name": "Dogs", "video": "dogs.mp4"},
    {"name": "Cats", "video": "cats.mp4"}
  ]
}
```

To add or modify video channels:

1. Open `configs/content/videos.json` in a text editor
2. Each channel requires:
   - `name`: The display name of the channel
   - `video`: The video file to play (must be in the `videos/` directory)
3. Add, remove, or modify the channel entries as needed
4. Save the file and restart the application
5. Update your key bindings to include actions for the new channels (e.g., `video_newchannel`)

## Adding and Updating Sounds

### Sound File Requirements

- Format: WAV (recommended)
- Name: Must match an action name (e.g., `ball.wav` for the `ball` action)

### Adding New Sounds

1. Create a sound file with the appropriate name (matching an action)
2. Place the sound file in the `sounds/` directory
3. Ensure there is a corresponding image in the `images/` directory
4. Optionally add a corresponding video in the `videos/` directory
5. Update your key bindings to include the new action
6. Restart the application

## Testing Your Changes

After making changes to configurations, it's recommended to:

1. Run DogPuter with the default configuration: `python -m dogputer`
2. Test all modified actions to ensure they work as expected
3. If using a custom configuration, run with that config: `python -m dogputer --config your_config_name`
4. Check that all key bindings, videos, and sounds are working correctly

If you encounter issues:
- Check the console output for errors
- Verify that all file paths and names are correct
- Ensure all configuration files are valid JSON
- Confirm that the action names in your key bindings match the names of your media files
