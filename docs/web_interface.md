# DogPuter Web Interface

The DogPuter web interface provides a convenient way to manage command mappings and upload new video content for your DogPuter system. It runs alongside the main application and can be accessed from any device on the same network.

## Overview

The web interface allows you to:

1. View and edit key mappings for commands
2. Upload new videos using the command_name.mp4 format
3. Manage all registered actions (commands with associated videos)

## Accessing the Web Interface

When you run the DogPuter application, it now automatically starts a web server. The main DogPuter display will show:

1. The web interface URL in the bottom right corner (e.g., http://192.168.1.10:5000)
2. A QR code that toggles visibility every 10 seconds

You can access the web interface by:
- Opening the URL in any web browser on a device connected to the same network
- Scanning the QR code with a mobile device

## Using the Web Interface

### Command Mapping Editor

The Command Mapping editor displays:

- All available actions (commands with associated videos)
- The current keyboard mapping configuration
- Visual indicators showing which commands are mapped and which are unmapped

To edit mappings:
1. Drag an action card from the left panel
2. Drop it onto a key in the keyboard layout
3. The key will highlight to show it has a command assigned
4. Click the "Save Mappings" button to save your changes

To remove a mapping:
1. Hover over a mapped key
2. Click the "×" button that appears on the command

### Video Upload

The Video Upload tab allows you to add new command videos to the system:

1. Drag and drop MP4 files onto the upload area (or click to select files)
2. Files must be named in the format `command_name.mp4`
3. The filename becomes the command that can be mapped to keys
4. Uploaded videos are automatically added to the available actions list

## Technical Details

The web interface includes:

- A Flask web server running on port 5000
- RESTful API endpoints for managing mappings and uploading videos
- Drag-and-drop interface for intuitive mapping creation
- Real-time feedback on upload progress and status

## Requirements

The web interface requires the following additional Python packages:
- Flask 2.0.0 or higher
- qrcode 7.0 or higher
- Pillow 8.0.0 or higher (already required by DogPuter)

These dependencies are included in the updated requirements.txt file.
