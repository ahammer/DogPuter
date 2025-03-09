"""
Web server implementation for DogPuter web interface

This module provides a Flask web server that runs alongside the main
DogPuter application, allowing for remote management of command mappings
and video uploads.
"""

import os
import json
import socket
import threading
import time
from flask import Flask, render_template, request, jsonify, send_from_directory
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Flask application
app = Flask(__name__)

# Configuration change notification
config_changed_time = 0
last_config_update = 0

# Constants
CONFIG_DIR = os.path.join(os.getcwd(), "configs")
KEYMAP_DIR = os.path.join(CONFIG_DIR, "keymappings")
VIDEO_DIR = os.path.join(os.getcwd(), "media", "videos")
DEFAULT_CONFIG = "development.json"


def get_local_ip():
    """Get the local IP address of the device"""
    try:
        # Create a socket to determine the local IP address
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Doesn't need to be reachable, just used to determine the interface
        s.connect(('10.255.255.255', 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'  # Fallback to localhost
    finally:
        s.close()
    return ip


def get_all_actions():
    """
    Get all registered actions based on video files
    
    Returns:
        list: A list of dictionaries with action information
    """
    # Ensure video directory exists
    if not os.path.exists(VIDEO_DIR):
        logger.warning(f"Video directory doesn't exist: {VIDEO_DIR}")
        return []
    
    # Get all mp4 files in the videos directory
    action_files = [f for f in os.listdir(VIDEO_DIR) if f.endswith('.mp4')]
    
    # Extract action names from filenames
    actions = [os.path.splitext(f)[0] for f in action_files]
    
    # Get current mappings
    mappings = get_current_mappings()
    
    # Create result with mapping status
    result = []
    for action in actions:
        # If command starts with video_, extract just the name part
        if action.startswith("video_"):
            action_name = action[6:]  # Remove "video_" prefix
        else:
            action_name = action
        
        # Check if action is in current mappings
        mapped_keys = []
        for key, cmd in mappings.items():
            # Check for direct match or video_ prefix match
            if cmd == action or cmd == f"video_{action_name}":
                mapped_keys.append(key)
        
        result.append({
            "name": action_name,
            "filename": f"{action}.mp4",
            "mapped": len(mapped_keys) > 0,
            "mappings": mapped_keys
        })
    
    # Sort by name
    result.sort(key=lambda x: x["name"])
    
    return result


def get_current_mappings(config_name=DEFAULT_CONFIG):
    """
    Get the current key mappings from the specified config file
    
    Args:
        config_name (str): Name of the config file
        
    Returns:
        dict: The key mappings
    """
    config_path = os.path.join(KEYMAP_DIR, config_name)
    try:
        with open(config_path, "r") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error reading mappings from {config_path}: {e}")
        return {}


def save_mappings(mappings, config_name=DEFAULT_CONFIG):
    """
    Save key mappings to the specified config file
    
    Args:
        mappings (dict): The key mappings to save
        config_name (str): Name of the config file
        
    Returns:
        bool: True if successful, False otherwise
    """
    global config_changed_time
    config_path = os.path.join(KEYMAP_DIR, config_name)
    try:
        with open(config_path, "w") as f:
            json.dump(mappings, f, indent=2)
        # Update the config changed timestamp
        config_changed_time = time.time()
        logger.info(f"Configuration updated at {config_changed_time}")
        return True
    except Exception as e:
        logger.error(f"Error saving mappings to {config_path}: {e}")
        return False

def has_config_changed():
    """
    Check if configuration has changed since last check
    
    Returns:
        bool: True if configuration has changed, False otherwise
    """
    global last_config_update
    if config_changed_time > last_config_update:
        last_config_update = config_changed_time
        return True
    return False


def list_config_files():
    """
    List all available configuration files
    
    Returns:
        list: Names of available config files
    """
    if not os.path.exists(KEYMAP_DIR):
        return []
    
    return [f for f in os.listdir(KEYMAP_DIR) if f.endswith('.json')]


@app.route('/')
def index():
    """Main web interface page"""
    return render_template('index.html')


@app.route('/static/<path:path>')
def serve_static(path):
    """Serve static files"""
    return send_from_directory('static', path)


@app.route('/api/actions')
def api_actions():
    """API endpoint to get all available actions"""
    actions = get_all_actions()
    return jsonify({"actions": actions})


@app.route('/api/configs')
def api_configs():
    """API endpoint to get all available configuration files"""
    configs = list_config_files()
    return jsonify({"configs": configs})


@app.route('/api/mappings')
def api_get_mappings():
    """API endpoint to get current key mappings"""
    config = request.args.get('config', DEFAULT_CONFIG)
    mappings = get_current_mappings(config)
    return jsonify({"mappings": mappings, "config": config})


@app.route('/api/mappings', methods=['POST'])
def api_update_mappings():
    """API endpoint to update key mappings"""
    data = request.json
    if not data or 'mappings' not in data:
        return jsonify({"error": "Invalid request data"}), 400
    
    config = data.get('config', DEFAULT_CONFIG)
    mappings = data['mappings']
    
    if save_mappings(mappings, config):
        return jsonify({"success": True, "config": config, "needsRestart": False})
    else:
        return jsonify({"error": "Failed to save mappings"}), 500


@app.route('/api/upload', methods=['POST'])
def api_upload_video():
    """API endpoint to upload a new video file"""
    if 'video' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['video']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    if not file.filename.endswith('.mp4'):
        return jsonify({"error": "File must be an MP4 video"}), 400
    
    # Ensure the file follows the command_name.mp4 format
    filename = file.filename
    command_name = os.path.splitext(filename)[0]
    
    # Save the file
    try:
        if not os.path.exists(VIDEO_DIR):
            os.makedirs(VIDEO_DIR, exist_ok=True)
        
        filepath = os.path.join(VIDEO_DIR, filename)
        file.save(filepath)
        
        return jsonify({
            "success": True,
            "command": command_name,
            "file": filename
        })
    except Exception as e:
        logger.error(f"Error saving file {filename}: {e}")
        return jsonify({"error": f"Error saving file: {str(e)}"}), 500


def run_web_server(host='0.0.0.0', port=5000):
    """
    Run the Flask web server
    
    Args:
        host (str): Host to bind to
        port (int): Port to bind to
    """
    ip_address = get_local_ip()
    url = f"http://{ip_address}:{port}"
    
    logger.info(f"Starting web server at {url}")
    app.run(host=host, port=port, debug=False, threaded=True)


def start_web_server_thread(host='0.0.0.0', port=5000):
    """
    Start the web server in a separate thread
    
    Args:
        host (str): Host to bind to
        port (int): Port to bind to
        
    Returns:
        threading.Thread: The thread running the web server
    """
    thread = threading.Thread(target=run_web_server, args=(host, port))
    thread.daemon = True  # Thread will exit when main program exits
    thread.start()
    return thread


if __name__ == "__main__":
    # When run directly, start the web server
    run_web_server()
