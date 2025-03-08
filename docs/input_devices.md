# DogPuter Input Devices Guide

This guide covers setting up and configuring various input devices for DogPuter, including keyboards, joysticks, and X-Arcade controllers.

## Table of Contents

1. [Overview of Input Handling](#overview-of-input-handling)
2. [Keyboard Setup](#keyboard-setup)
3. [X-Arcade Controller Setup](#x-arcade-controller-setup)
   - [Keyboard Mode Configuration](#keyboard-mode-configuration)
   - [Gamepad Mode Configuration](#gamepad-mode-configuration)
   - [Physical Setup](#physical-setup)
4. [Joystick/Gamepad Setup](#joystickgamepad-setup)
5. [Multiple Input Devices](#multiple-input-devices)
6. [Testing Input Devices](#testing-input-devices)
7. [Troubleshooting](#troubleshooting)

## Overview of Input Handling

DogPuter supports multiple input methods to make interaction accessible:

- **Keyboard**: Standard computer keyboard input
- **X-Arcade Controllers**: Specialized arcade-style controllers
- **Joysticks/Gamepads**: Standard USB gaming controllers

The system translates these different inputs into a common set of actions using configuration files.

## Keyboard Setup

Keyboard input is the simplest to set up and is ideal for testing and development:

1. Ensure your keyboard is connected and recognized by your operating system
2. The default keyboard mappings are defined in `configs/keymappings/development.json`
3. No additional setup is required

To customize keyboard keys, refer to the [Customization Guide](customization_guide.md).

## X-Arcade Controller Setup

X-Arcade controllers are arcade-style controllers that can work in two modes:

- **Keyboard Mode**: The controller emulates keyboard key presses (default)
- **Gamepad Mode**: The controller functions as a joystick/gamepad (requires configuration)

### Keyboard Mode Configuration

1. Connect your X-Arcade controller to the Raspberry Pi via USB
2. The system should automatically detect it as a keyboard input device
3. Run DogPuter with the X-Arcade keyboard configuration:
   ```
   python -m dogputer --config x-arcade-kb
   ```

The X-Arcade keyboard mappings are defined in `configs/keymappings/x-arcade-kb.json`. This configuration maps the physical X-Arcade buttons to logical button names (e.g., `p1_button1`, `p1_up`) and then to DogPuter actions.

### Gamepad Mode Configuration

If your X-Arcade controller is in gamepad mode:

1. Connect the controller via USB
2. Run DogPuter with the X-Arcade gamepad configuration:
   ```
   python -m dogputer --config x-arcade-gc
   ```

The X-Arcade gamepad mappings are defined in `configs/keymappings/x-arcade-gc.json`. This configuration maps joystick buttons and hat directions to DogPuter actions.

### Physical Setup

For optimal usability with dogs:

1. Mount the X-Arcade controller securely at an appropriate height
2. Consider covering unused buttons to reduce confusion
3. Label buttons with images that correspond to their actions
4. Ensure the controller is stable and can withstand enthusiastic use

## Joystick/Gamepad Setup

Standard USB joysticks and gamepads work similarly to X-Arcade controllers in gamepad mode:

1. Connect your joystick/gamepad to the Raspberry Pi via USB
2. The system should automatically detect it
3. Run DogPuter with joystick support enabled:
   ```
   python -m dogputer --joystick
   ```

Joystick mappings use a tuple format in the configuration files, as shown in this example:

```json
{
  ("button", 0, 0): "ball",
  ("button", 0, 1): "rope",
  ("hat", 0, "up"): "video_squirrels",
  ("hat", 0, "down"): "video_dogs"
}
```

Where:
- First element: Input type (`button` or `hat`)
- Second element: Joystick ID (usually 0 for the first joystick)
- Third element: Button number or hat direction

## Multiple Input Devices

DogPuter can accept input from multiple devices simultaneously:

1. Run DogPuter with the composite input option:
   ```
   python -m dogputer --input-type composite
   ```

2. Configure which devices to include in `src/dogputer/core/config.py` or use command-line flags:
   ```
   python -m dogputer --input-type composite --use-keyboard --use-joystick --use-xarcade
   ```

This setup allows for flexibility, such as having an X-Arcade controller for the dog and a keyboard for the handler.

## Testing Input Devices

To test your input devices:

1. Run DogPuter with debug logging enabled:
   ```
   python -m dogputer --debug
   ```

2. Press buttons on your input device and observe the console output
3. The log will show:
   - Detected key/button presses
   - The corresponding action (if mapped)
   - Any errors or issues that occur

You can also use a simple test script to verify input detection:

```python
import pygame

pygame.init()
pygame.display.set_mode((300, 200))
print("Press buttons on your controller (ESC to exit)")

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            print(f"Key: {pygame.key.name(event.key)} (code: {event.key})")
            if event.key == pygame.K_ESCAPE:
                running = False
        elif event.type == pygame.JOYBUTTONDOWN:
            print(f"Joystick {event.joy} button: {event.button}")
        elif event.type == pygame.JOYHATMOTION:
            print(f"Joystick {event.joy} hat: {event.hat} value: {event.value}")
        elif event.type == pygame.QUIT:
            running = False

pygame.quit()
```

Save this as `test_inputs.py` and run it to see raw input data.

## Troubleshooting

### X-Arcade Controller Issues

1. **Controller not detected**:
   - Ensure it's properly connected via USB
   - Check if it appears in `lsusb` output
   - Try a different USB port

2. **Wrong key mappings**:
   - X-Arcade controllers may have different mappings depending on the model and mode
   - Use the test script above to determine actual key codes
   - Update the configuration file accordingly

3. **Buttons triggering unexpected actions**:
   - Check the mapping in your configuration file
   - Ensure you're using the correct configuration (KB vs GC mode)

### Joystick Issues

1. **Joystick not detected**:
   - Run `python -m pygame.examples.joystick` to test if Pygame detects it
   - Check if it appears in `ls /dev/input/js*`
   - Ensure you have the required permissions to access the device

2. **Incorrect button mapping**:
   - Different joysticks use different button numbering schemes
   - Use the test script to determine your specific button numbers
   - Update your configuration accordingly

3. **Hat/D-pad not working**:
   - Some controllers implement the D-pad as a hat, others as buttons
   - Check the event type generated when you press the D-pad

### General Input Issues

1. **No response to input**:
   - Check if the input device is detected by the operating system
   - Verify that Pygame is receiving events (using test script)
   - Ensure the configuration file properly maps inputs to actions

2. **Action triggers multiple times**:
   - Check for duplicate mappings in your configuration
   - Verify that the input cooldown is functioning correctly

3. **Input lag**:
   - Simplify your configuration to reduce processing overhead
   - Check for CPU usage issues on the Raspberry Pi
   - Consider disabling features like TTS if performance is a concern
