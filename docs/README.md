# DogPuter Documentation

Welcome to the DogPuter documentation. This collection of guides will help you understand, customize, and extend your DogPuter system.

## Available Guides

### Core Documentation

- [Customization Guide](customization_guide.md) - Learn how to customize DogPuter by updating actions, key bindings, videos, and sounds
- [Creating New Actions](creating_new_actions.md) - Step-by-step instructions for adding entirely new actions to DogPuter
- [Input Devices Guide](input_devices.md) - Details on setting up and configuring keyboards, joysticks, and X-Arcade controllers

### Hardware Setup

- [Raspberry Pi Setup](../raspberry_pi_setup.md) - Instructions for setting up DogPuter on a Raspberry Pi

## Quick Start Guide

To modify DogPuter for your needs, follow these steps:

1. First, read the [Customization Guide](customization_guide.md) to understand how actions, key bindings, videos, and sounds work together in DogPuter.

2. To add new inputs (buttons/keys) for existing actions:
   - Edit the appropriate configuration file in `configs/keymappings/`
   - Follow the examples in the [Customization Guide](customization_guide.md#modifying-key-bindings)

3. To create entirely new actions:
   - Follow the step-by-step instructions in [Creating New Actions](creating_new_actions.md)
   - Prepare the necessary media files (images, sounds, videos)
   - Update your configuration files

4. To set up different input devices:
   - Refer to the [Input Devices Guide](input_devices.md)
   - Configure the appropriate key mappings for your device
   - Test the setup using the provided tools

## Common Tasks

### Adding a New Button Action

1. Create image file: `images/new_action.jpg`
2. Create sound file: `sounds/new_action.wav`
3. Optionally create video file: `videos/new_action.mp4`
4. Edit `configs/keymappings/development.json` (or your preferred config) to add:
   ```json
   "K_n": "new_action"
   ```
5. Restart DogPuter

### Adding a New Video Channel

1. Add your video file to `videos/` (e.g., `new_channel.mp4`)
2. Edit `configs/content/videos.json` to add:
   ```json
   {"name": "New Channel", "video": "new_channel.mp4"}
   ```
3. Edit your key mapping configuration to add:
   ```json
   "K_n": "video_newchannel"
   ```
4. Restart DogPuter

### Changing an Existing Key Binding

1. Edit the appropriate configuration file in `configs/keymappings/`
2. Change the action assigned to a key, for example:
   ```json
   "K_1": "ball"  // Change from "rope" to "ball"
   ```
3. Restart DogPuter

## Contribution and Development

If you'd like to contribute to DogPuter development, please:

1. Fork the repository
2. Create a feature branch
3. Submit a pull request with your changes

For bug reports and feature requests, please use the GitHub issue tracker.
