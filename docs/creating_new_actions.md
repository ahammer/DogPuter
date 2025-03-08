# Creating New Actions in DogPuter

This guide walks you through the process of creating completely new actions for DogPuter, building on the information in the [Customization Guide](customization_guide.md).

## Table of Contents

1. [Introduction](#introduction)
2. [Action Components](#action-components) 
3. [Step by Step: Creating a New Action](#step-by-step-creating-a-new-action)
   - [Prepare Media Files](#prepare-media-files)
   - [Update Configuration Files](#update-configuration-files)
   - [Test Your New Action](#test-your-new-action)
4. [Advanced: Creating Video Channels](#advanced-creating-video-channels)
5. [Advanced: Creating Custom Action Categories](#advanced-creating-custom-action-categories)
6. [Troubleshooting](#troubleshooting)

## Introduction

Actions in DogPuter represent interactive options that can be triggered by buttons, keys, or joystick movements. Each action typically consists of:

- A key binding or input mapping
- An image to display
- A sound to play
- Optionally, a video to play
- Text-to-speech output of the action name

## Action Components

A complete action in DogPuter requires the following components:

1. **Action Name**: A unique identifier used throughout the system (e.g., `treat`, `fetch`)
2. **Media Files**:
   - An image file named `[action_name].jpg` in the `images/` directory
   - A sound file named `[action_name].wav` in the `sounds/` directory
   - Optionally, a video file named `[action_name].mp4` in the `videos/` directory
3. **Key Binding**: A mapping in a configuration file that associates a key press with the action

## Step by Step: Creating a New Action

Let's create a new action called `treat` as an example.

### Prepare Media Files

1. **Create or acquire the necessary media files**:
   - `treat.jpg`: An image of a dog treat (place in `images/` directory)
   - `treat.wav`: A sound effect related to treats (place in `sounds/` directory)
   - (Optional) `treat.mp4`: A video related to treats (place in `videos/` directory)

2. **Ensure proper format and dimensions**:
   - Images: JPG format, matching your display resolution
   - Sounds: WAV format, short duration (1-3 seconds)
   - Videos: MP4 format, matching your display resolution

### Update Configuration Files

1. **Edit the key mapping configuration**:

   Open the appropriate configuration file (e.g., `configs/keymappings/development.json`) and add a new key binding:

   ```json
   {
     "K_0": "play",
     "K_1": "rope",
     // ... existing bindings ...
     "K_t": "treat"  // Add our new action
   }
   ```

   For X-Arcade controllers, you might add:

   ```json
   {
     "p1_button7": "treat"
   }
   ```

2. **Copy files to the correct locations**:

   Make sure your media files are in the correct directories:
   ```
   images/treat.jpg
   sounds/treat.wav
   videos/treat.mp4 (optional)
   ```

### Test Your New Action

1. **Launch DogPuter**:
   ```
   python -m dogputer
   ```

2. **Press the assigned key** ('t' in our example)

3. **Verify that**:
   - The correct sound plays
   - The image or video displays
   - The text-to-speech says "treat"

## Advanced: Creating Video Channels

Video channels are special actions that play continuous video streams. To create a new video channel:

1. **Add the video file** to the `videos/` directory (e.g., `cats.mp4`)

2. **Edit `configs/content/videos.json`** to add your new channel:

   ```json
   {
     "video_channels": [
       {"name": "Squirrels", "video": "squirrels.mp4"},
       {"name": "Birds", "video": "birds.mp4"},
       // Add your new channel
       {"name": "Fishbowl", "video": "fish.mp4"}
     ]
   }
   ```

3. **Edit your key mapping configuration** to add a binding for the new channel:

   ```json
   {
     "K_UP": "video_squirrels",
     "K_RIGHT": "video_birds",
     // Add your new channel
     "K_f": "video_fish"
   }
   ```

   Note that video channel actions are prefixed with `video_`.

## Advanced: Creating Custom Action Categories

You can organize actions into custom categories for more complex interfaces:

1. **Create a naming convention** for your category
   - For example, `food_treat`, `food_kibble`, `toy_ball`, `toy_rope`

2. **Prepare all media files** following this naming convention

3. **Update key mappings** to use these categorized actions

4. **For specialized behavior**, you may need to modify the code in `src/dogputer/core/app_state.py` to handle your custom categories differently

## Troubleshooting

If your new action doesn't work as expected, check the following:

1. **File naming**: Ensure all files use exactly the same base name as your action
2. **File locations**: Verify files are in the correct directories
3. **Configuration syntax**: Check for JSON syntax errors in your configuration files
4. **Key mappings**: Verify the key constant is correct (e.g., `K_t` for the 't' key)
5. **Console output**: Check the terminal output for error messages
6. **File formats**: Ensure media files are in the correct formats

Common issues:
- JSON syntax errors (missing commas, extra commas, unquoted strings)
- Incorrect file paths or names
- Unsupported media formats
- Pygame key constants not matching actual keys
- Mismatched action names between configuration and media files

If you continue to experience issues, you can check the application logs for more detailed error information.
