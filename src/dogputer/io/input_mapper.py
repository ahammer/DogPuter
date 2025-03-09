"""
Input mapper module for DogPuter

This module provides a mapping system that converts raw input events
from various input handlers into abstract commands that can be executed
by the application state. This decouples the input handling from the
application logic.
"""

import pygame
from dogputer.core.commands import ContentCommand, VideoChannelCommand, TogglePauseCommand, ExitCommand

class InputMapper:
    """
    Maps raw input events and key states to abstract commands
    """
    
    def __init__(self, input_mappings=None):
        """
        Initialize with a mapping of input keys to command names
        
        Args:
            input_mappings: Dictionary mapping key codes or tuples to command names
        """
        self.input_mappings = input_mappings or {}
        
    def update_mappings(self, new_mappings):
        """
        Update the input mappings dictionary
        
        Args:
            new_mappings: New dictionary mapping key codes or tuples to command names
        """
        self.input_mappings = new_mappings
    
    def map_event(self, event):
        """
        Map a pygame event to a command
        
        Args:
            event: A pygame event object
            
        Returns:
            A Command object or None if the event doesn't map to a command
        """
        # Handle different event types
        if event.type == pygame.KEYDOWN:
            return self._map_key_event(event.key)
        elif event.type == pygame.JOYBUTTONDOWN:
            return self._map_joystick_button_event(event.joy, event.button)
        elif event.type == pygame.JOYHATMOTION:
            return self._map_joystick_hat_event(event.joy, event.value)
        
        return None
    
    def _map_key_event(self, key):
        """Map a keyboard key to a command"""
        # Exit on ESC key
        if key == pygame.K_ESCAPE:
            return ExitCommand()
            
        # Check if this key is mapped to a command
        if key in self.input_mappings:
            command_name = self.input_mappings[key]
            return self._create_command_from_name(command_name)
            
        return None
    
    def _map_joystick_button_event(self, joy_id, button):
        """Map a joystick button to a command"""
        # Create tuple key for joystick button
        button_key = ('button', joy_id, button)
        
        # Check if this button is mapped to a command
        if button_key in self.input_mappings:
            command_name = self.input_mappings[button_key]
            return self._create_command_from_name(command_name)
            
        return None
    
    def _map_joystick_hat_event(self, joy_id, hat_value):
        """Map a joystick hat motion to a command"""
        # Map hat directions to command
        direction = None
        if hat_value[0] > 0:  # Right
            direction = 'right'
        elif hat_value[0] < 0:  # Left
            direction = 'left'
        elif hat_value[1] > 0:  # Up
            direction = 'up'
        elif hat_value[1] < 0:  # Down
            direction = 'down'
            
        if direction:
            # Create tuple key for hat direction
            hat_key = ('hat', joy_id, direction)
            
            # Check if this hat direction is mapped to a command
            if hat_key in self.input_mappings:
                command_name = self.input_mappings[hat_key]
                return self._create_command_from_name(command_name)
                
        return None
    
    def map_axis_to_command(self, joy_id, axis, value):
        """
        Map a joystick axis value to a command
        
        Args:
            joy_id: Joystick ID
            axis: Axis index
            value: Axis value (-1.0 to 1.0)
            
        Returns:
            A Command object or None
        """
        # Only process significant axis movement (apply deadzone)
        if abs(value) < 0.5:
            return None
            
        # Create tuple key for axis
        direction = 'positive' if value > 0 else 'negative'
        axis_key = ('axis', joy_id, axis, direction)
        
        # Check if this axis is mapped to a command
        if axis_key in self.input_mappings:
            command_name = self.input_mappings[axis_key]
            return self._create_command_from_name(command_name)
            
        # Special case for video channel navigation
        if axis == 0:  # Horizontal axis
            if value > 0.5:  # Right
                return VideoChannelCommand(1)
            elif value < -0.5:  # Left
                return VideoChannelCommand(-1)
        elif axis == 1:  # Vertical axis
            if value > 0.5:  # Down
                return VideoChannelCommand(1)
            elif value < -0.5:  # Up
                return VideoChannelCommand(-1)
                
        return None
    
    def _create_command_from_name(self, command_name):
        """Create a command object from a command name"""
        # Handle special video channel navigation commands
        if command_name == "channel_next":
            return VideoChannelCommand(1)
        elif command_name == "channel_prev":
            return VideoChannelCommand(-1)
        elif command_name == "pause":
            return TogglePauseCommand()
        elif command_name == "exit":
            return ExitCommand()
        elif command_name.startswith("video_"):
            # Extract content name from video_ prefix
            content_name = command_name[6:]  # Remove "video_" prefix
            return ContentCommand(content_name)
        else:
            # For regular content commands (ball, treat, etc.)
            return ContentCommand(command_name)
    
    def map_logical_name(self, logical_name):
        """
        Map a logical input name (like 'p1_button1') to a command
        
        Args:
            logical_name: Logical name of an input
            
        Returns:
            A Command object or None
        """
        # Check if the logical name is directly mapped to a command
        for key, command_name in self.input_mappings.items():
            if isinstance(key, str) and key == logical_name:
                return self._create_command_from_name(command_name)
                
        return None
