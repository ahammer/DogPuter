#!/usr/bin/env python3
"""
Video player module wrapper for Raspberry Pi
This module provides a compatible interface between the simplified VideoPlayer
and the optimized RPiVideoPlayer, allowing them to be used interchangeably.
This version is optimized for performance.
"""

import os
import platform

# Check if we're on a Raspberry Pi
def is_raspberry_pi():
    """Check if we're running on a Raspberry Pi"""
    try:
        with open('/sys/firmware/devicetree/base/model', 'r') as f:
            model = f.read()
            return 'raspberry pi' in model.lower()
    except:
        # Check platform info as fallback
        return platform.machine().startswith('arm') or platform.machine().startswith('aarch')

# Import the appropriate video player based on platform
if is_raspberry_pi():
    from dogputer.ui.rpi_video_player import RPiVideoPlayer as VideoPlayer
    print("Using RPi-optimized video player")
else:
    from dogputer.ui.video_player_simple import VideoPlayer
    print("Using simplified video player for better performance")

# Re-export VideoPlayer
__all__ = ['VideoPlayer']
