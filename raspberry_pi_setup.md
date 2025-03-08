# Raspberry Pi Setup Guide for DogPuter

This guide provides instructions for setting up the DogPuter application on a Raspberry Pi, including how to configure it to run on startup and how to set up physical buttons and joysticks.

## Basic Raspberry Pi Setup

1. Start with a fresh installation of Raspberry Pi OS (formerly Raspbian)
2. Connect your Raspberry Pi to a display, keyboard, and mouse
3. Connect to the internet via Wi-Fi or Ethernet
4. Open a terminal and update your system:

```bash
sudo apt update
sudo apt upgrade -y
```

## Install Required Dependencies

Install Python and Pygame:

```bash
sudo apt install -y python3-pip python3-pygame
```

For better audio support:

```bash
sudo apt install -y python3-sdl2 libsdl2-mixer-2.0-0
```

## Clone the DogPuter Repository

```bash
cd ~
git clone https://github.com/yourusername/dogputer.git
cd dogputer
```

Or, if you've downloaded the files directly, copy them to a directory on your Raspberry Pi.

## Setting Up Physical Buttons

You can connect physical buttons to the GPIO pins on your Raspberry Pi and map them to keyboard keys. Here's a simple approach using the `gpiozero` library:

1. Install the required library:

```bash
sudo apt install -y python3-gpiozero
```

2. Create a new file called `button_handler.py`:

```python
from gpiozero import Button
from signal import pause
import pygame
import os
import time

# Define GPIO pins for buttons
button_pins = {
    "play": 17,  # GPIO pin for "play" button
    "rope": 18,  # GPIO pin for "rope" button
    "ball": 27,  # GPIO pin for "ball" button
    # Add more buttons as needed
}

# Map GPIO pins to pygame key constants
button_to_key = {
    "play": pygame.K_a,
    "rope": pygame.K_s,
    "ball": pygame.K_d,
    # Add more mappings as needed
}

# Initialize pygame
pygame.init()

# Create a dummy window (required for pygame.event to work)
os.environ["SDL_VIDEODRIVER"] = "dummy"
pygame.display.set_mode((1, 1))

# Create button objects
buttons = {}
for name, pin in button_pins.items():
    buttons[name] = Button(pin, pull_up=True)

# Define button press handlers
def button_pressed(name):
    key = button_to_key[name]
    event = pygame.event.Event(pygame.KEYDOWN, {"key": key})
    pygame.event.post(event)
    print(f"Button '{name}' pressed, sending key {key}")

# Attach handlers to buttons
for name, button in buttons.items():
    button.when_pressed = lambda n=name: button_pressed(n)

print("Button handler running. Press Ctrl+C to exit.")
pause()  # Keep the script running
```

3. Run this script alongside the main DogPuter application:

```bash
python3 button_handler.py &
python3 main.py
```

## Setting Up a Joystick

For a USB joystick, Pygame should detect it automatically. For a GPIO-based joystick, you can use a similar approach to the button handler above.

## Auto-Starting on Boot

To make the DogPuter application start automatically when the Raspberry Pi boots:

1. Create a systemd service file:

```bash
sudo nano /etc/systemd/system/dogputer.service
```

2. Add the following content:

```
[Unit]
Description=DogPuter Application
After=network.target

[Service]
ExecStart=/usr/bin/python3 /home/pi/dogputer/main.py
WorkingDirectory=/home/pi/dogputer
StandardOutput=inherit
StandardError=inherit
Restart=always
User=pi

[Install]
WantedBy=multi-user.target
```

3. Enable and start the service:

```bash
sudo systemctl enable dogputer.service
sudo systemctl start dogputer.service
```

4. If you're using the button handler, create a separate service for it:

```bash
sudo nano /etc/systemd/system/dogputer-buttons.service
```

```
[Unit]
Description=DogPuter Button Handler
After=network.target

[Service]
ExecStart=/usr/bin/python3 /home/pi/dogputer/button_handler.py
WorkingDirectory=/home/pi/dogputer
StandardOutput=inherit
StandardError=inherit
Restart=always
User=pi

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable dogputer-buttons.service
sudo systemctl start dogputer-buttons.service
```

## Disabling Screen Blanking

To prevent the screen from going blank after a period of inactivity:

1. Edit the autostart file:

```bash
sudo nano /etc/xdg/lxsession/LXDE-pi/autostart
```

2. Add these lines:

```
@xset s off
@xset -dpms
@xset s noblank
```

## Troubleshooting

### Audio Issues

If you encounter audio issues:

1. Make sure your audio output is correctly configured:

```bash
sudo raspi-config
```

Navigate to "System Options" > "Audio" and select your preferred output.

2. Test audio playback:

```bash
aplay /usr/share/sounds/alsa/Front_Center.wav
```

### Display Issues

If the display doesn't work correctly:

1. Check your display settings in `/boot/config.txt`:

```bash
sudo nano /boot/config.txt
```

2. You may need to adjust settings like:

```
hdmi_force_hotplug=1
hdmi_group=1
hdmi_mode=16  # 1080p 60Hz
```

### GPIO Issues

If buttons aren't working:

1. Check your wiring
2. Test the GPIO pins with a simple script:

```python
from gpiozero import Button
from signal import pause

button = Button(17)  # Replace with your GPIO pin
button.when_pressed = lambda: print("Button pressed!")
button.when_released = lambda: print("Button released!")

pause()
```

## Additional Resources

- [Raspberry Pi Documentation](https://www.raspberrypi.org/documentation/)
- [GPIO Zero Documentation](https://gpiozero.readthedocs.io/)
- [Pygame Documentation](https://www.pygame.org/docs/)
