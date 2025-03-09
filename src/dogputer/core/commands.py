"""
Command pattern implementation for Dogputer

This module provides a command-based architecture to decouple
input handling from application logic. Commands represent
actions that can be executed on the application state.
"""

from abc import ABC, abstractmethod
import os
import time
import pygame
from dogputer.core.app_state import Mode


class Command(ABC):
    """Abstract base class for all commands"""
    
    @abstractmethod
    def execute(self, app_state):
        """Execute the command on the application state"""
        pass
    
    def __str__(self):
        return self.__class__.__name__


class ContentCommand(Command):
    """Command to select a specific content"""
    
    def __init__(self, content_name):
        """Initialize with content name"""
        self.content_name = content_name
    
    def execute(self, app_state):
        """Execute content selection"""
        # Show feedback
        app_state.show_feedback(f"{self.content_name.capitalize()} selected!", (0, 0, 255))
        
        # Play sound
        sound_file = f"{self.content_name}.wav"
        try:
            app_state.play_sound(sound_file)
        except Exception as e:
            print(f"Error playing sound: {e}")
        
        # Speak command using TTS
        try:
            app_state.tts_handler.speak(self.content_name)
        except Exception as e:
            print(f"Error with TTS: {e}")
        
        # Try to play video first, fall back to image if video doesn't exist
        video_filename = f"{self.content_name}.mp4"
        video_path = os.path.join("videos", video_filename)
        video_placeholder_path = video_path + ".txt"
        
        # If we're already playing this video, ignore the command
        if (app_state.mode.name == "VIDEO" and 
            app_state.content_state.video_content.is_playing and 
            hasattr(app_state.content_state.video_content, 'current_video_filename') and
            app_state.content_state.video_content.current_video_filename == video_filename):
            print(f"Already playing video: {video_filename}, ignoring repeat command")
            return
            
        # Check if video or placeholder exists
        if os.path.exists(video_path):
            # Play the actual video
            print(f"Playing video for command: {self.content_name} (path: {video_path})")
            result = app_state.content_state.set_video_by_filename(video_filename)
            if result:
                print(f"Video playback started successfully, switching to VIDEO mode")
                app_state.mode = Mode.VIDEO
                # Store the current video filename for repeat detection
                app_state.content_state.video_content.current_video_filename = video_filename
            else:
                # Fall back to image if video playback fails
                print(f"Video playback failed, falling back to image")
                self._display_image_fallback(app_state)
        elif os.path.exists(video_placeholder_path):
            # If we have a placeholder, display the image with a message
            print(f"Video placeholder found for command: {self.content_name}, displaying image instead")
            self._display_image_fallback(app_state)
            # Show feedback about placeholder
            app_state.show_feedback("Video placeholder - using image instead", (0, 0, 255))
        else:
            # Fall back to image
            self._display_image_fallback(app_state)
    
    def _display_image_fallback(self, app_state):
        """Display image as fallback when video is not available"""
        from dogputer.core.config import DEFAULT_DISPLAY_TIME
        
        image_name = f"{self.content_name}.jpg"
        print(f"Loading image fallback: {image_name}")
        image = app_state.load_image(image_name)
        if image:
            print(f"Image loaded successfully, displaying for {DEFAULT_DISPLAY_TIME} seconds")
            app_state.content_state.set_image(image, DEFAULT_DISPLAY_TIME)
            app_state.mode = Mode.IMAGE
        else:
            print(f"Failed to load image: {image_name}")
            app_state.show_feedback(f"Failed to load image: {image_name}", (255, 0, 0))


class VideoChannelCommand(Command):
    """Command to change video channel"""
    
    def __init__(self, direction):
        """Initialize with direction (1 for next, -1 for previous)"""
        self.direction = direction
    
    def execute(self, app_state):
        """Execute channel change"""
        # Record channel change
        app_state.input_state.record_channel_change()
        
        # Show feedback
        app_state.show_feedback("Channel changed!", (0, 0, 255))
        
        # Change channel
        result = app_state.content_state.change_video_channel(self.direction)
        if isinstance(result, tuple):
            success, channel_name = result
            if not success and channel_name:
                from dogputer.core.config import VIDEO_CHANNELS
                # Display channel name as text
                channel_index = (app_state.content_state.video_content.current_channel + self.direction) % len(VIDEO_CHANNELS)
                channel = VIDEO_CHANNELS[channel_index]
                print(f"Changed to channel: {channel['name']}")
                
                # Speak the channel name
                app_state.tts_handler.speak(channel['name'])
                
                # Display channel name as text
                app_state.content_state.set_text(f"Channel: {channel_name}", app_state.font, 3.0, 
                                              app_state.screen_width, app_state.screen_height)
                app_state.mode = Mode.TEXT
        elif result:
            app_state.mode = Mode.VIDEO


class TogglePauseCommand(Command):
    """Command to toggle pause state of current content"""
    
    def execute(self, app_state):
        """Execute pause toggle"""
        if app_state.mode.name == "VIDEO" and app_state.content_state.video_content.is_playing:
            app_state.content_state.video_content.video_player.toggle_pause()
            is_paused = app_state.content_state.video_content.video_player.paused
            message = "Paused" if is_paused else "Resumed"
            app_state.show_feedback(message, (0, 0, 255))


class ExitCommand(Command):
    """Command to exit the application"""
    
    def execute(self, app_state):
        """Set the application to exit"""
        # This will be handled by the main loop
        pygame.event.post(pygame.event.Event(pygame.QUIT))
