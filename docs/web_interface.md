# DogPuter Web Interface

The DogPuter web interface provides a convenient way to manage command mappings and upload new video content for your DogPuter system. It runs alongside the main application and can be accessed from any device on the same network.

## Overview

The web interface allows you to:

1. View and edit key mappings for commands with a drag-and-drop interface
2. Upload new videos using the command_name.mp4 format
3. Manage all registered actions (commands with associated videos)
4. Make configuration changes without restarting the application
5. See real-time feedback on your changes

## Accessing the Web Interface

When you run the DogPuter application, it automatically starts a web server. The main DogPuter display shows:

1. The web interface URL in the bottom right corner (e.g., http://192.168.1.10:5000)
2. A QR code that toggles visibility every 10 seconds

You can access the web interface by:
- Opening the URL in any web browser on a device connected to the same network
- Scanning the QR code with a mobile device (particularly convenient for mobile phones and tablets)

The system detects your local IP address automatically, making it easy to connect from other devices on your home network.

## Using the Web Interface

### Command Mapping Editor

The Command Mapping editor provides an intuitive drag-and-drop interface that displays:

- All available actions (commands with associated videos)
- The current keyboard mapping configuration
- Visual indicators showing which commands are mapped and which are unmapped
- Color-coded feedback on mapping status

To edit mappings:
1. Drag an action card from the left panel
2. Drop it onto a key in the keyboard layout
3. The key will highlight to show it has a command assigned
4. Click the "Save Mappings" button to save your changes

To remove a mapping:
1. Hover over a mapped key
2. Click the "×" button that appears on the command

Changes to mappings are applied immediately and do not require restarting the DogPuter application.

### Video Upload

The Video Upload tab allows you to add new command videos to the system:

1. Drag and drop MP4 files onto the upload area (or click to select files)
2. Files must be named in the format `command_name.mp4`
3. The filename becomes the command that can be mapped to keys
4. Progress bars show upload status for each file
5. Uploaded videos are automatically added to the available actions list

Newly uploaded videos are immediately available for mapping to keys without restarting the application.

### Configuration Management

The Configuration tab allows you to:

1. View all available configuration files
2. Switch between different key mapping configurations
3. Create new configurations based on existing ones
4. Export and import configuration files

This makes it easy to maintain different setups for different users or devices.

## Technical Details

The web interface includes:

- A Flask web server running on port 5000
- RESTful API endpoints for managing mappings and uploading videos
- Configuration change notification system for real-time updates
- Drag-and-drop interface built with modern web technologies
- Mobile-responsive design that works on phones and tablets
- Automatic QR code generation for easy access

### API Endpoints

The web interface provides the following API endpoints:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/actions` | GET | Get all available actions (commands with videos) |
| `/api/configs` | GET | Get all available configuration files |
| `/api/mappings` | GET | Get current key mappings for a specific config |
| `/api/mappings` | POST | Update key mappings for a specific config |
| `/api/upload` | POST | Upload a new video file |

These endpoints can also be used programmatically if you want to develop additional tools that interact with DogPuter.

## Requirements

The web interface requires the following additional Python packages:
- Flask 2.0.0 or higher
- qrcode 7.0 or higher
- Pillow 8.0.0 or higher (already required by DogPuter)

These dependencies are included in the updated requirements.txt file.

## Troubleshooting

If you cannot connect to the web interface:

1. Check that your device is on the same network as the DogPuter
2. Verify the URL shown on the DogPuter screen matches what you're typing
3. Ensure no firewall is blocking port 5000
4. Try using the IP address directly instead of any hostname
