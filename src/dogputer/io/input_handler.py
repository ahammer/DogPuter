#!/usr/bin/env python3
"""
Input handler module for DogPuter
Provides a consistent interface for different input methods (keyboard, joystick, x-arcade).
"""

import pygame
from abc import ABC, abstractmethod

class InputHandler(ABC):
    """Abstract base class for input handlers"""
    
    @abstractmethod
    def get_events(self):
        """Get all pending input events"""
        pass
    
    @abstractmethod
    def is_key_pressed(self, key):
        """Check if a key is currently pressed"""
        pass
    
    @abstractmethod
    def get_axis_value(self, axis):
        """Get the current value of an axis (joystick)"""
        pass
    
    @abstractmethod
    def update(self):
        """Update the input state"""
        pass

class KeyboardInputHandler(InputHandler):
    """Keyboard input handler for DogPuter"""
    
    def __init__(self, key_mappings=None):
        """Initialize the keyboard input handler"""
        self.key_mappings = key_mappings or {}
        # Initialize with empty events list
        self.events = []
    
    def get_events(self):
        """Get all pending pygame events"""
        # Get events from pygame event queue
        self.events = pygame.event.get()
        return self.events
    
    def is_key_pressed(self, key):
        """Check if a key is currently pressed"""
        keys = pygame.key.get_pressed()
        mapped_key = self.key_mappings.get(key, key)
        return keys[mapped_key]
    
    def get_axis_value(self, axis):
        """Get the current value of an axis (simulated via keyboard)"""
        # For keyboard, we simulate axes using key pairs
        # For example, left/right arrows could simulate a horizontal axis
        return 0.0  # Default implementation returns neutral position
    
    def update(self):
        """Update the input state"""
        # For keyboard, we don't need additional updates beyond get_events
        pass

class JoystickInputHandler(InputHandler):
    """Joystick input handler for DogPuter"""
    
    def __init__(self, joystick_id=0, button_mappings=None):
        """Initialize the joystick input handler"""
        self.button_mappings = button_mappings or {}
        self.events = []
        
        # Initialize joystick if available
        if pygame.joystick.get_count() > joystick_id:
            self.joystick = pygame.joystick.Joystick(joystick_id)
            self.joystick.init()
            print(f"Joystick initialized: {self.joystick.get_name()}")
            self.active = True
        else:
            print("No joystick found")
            self.joystick = None
            self.active = False
    
    def get_events(self):
        """Get all pending pygame events, filtering for joystick events"""
        # Get all events
        all_events = pygame.event.get()
        
        # Filter for joystick events
        self.events = [event for event in all_events if 
                      event.type in (pygame.JOYBUTTONDOWN, pygame.JOYBUTTONUP, 
                                    pygame.JOYAXISMOTION, pygame.JOYHATMOTION)]
                                    
        return self.events
    
    def is_key_pressed(self, key):
        """Check if a joystick button is pressed, using mapped keys"""
        if not self.active or not self.joystick:
            return False
            
        # Map key to joystick button if mapping exists
        button = self.button_mappings.get(key, None)
        
        if button is not None and 0 <= button < self.joystick.get_numbuttons():
            return self.joystick.get_button(button)
        
        return False
    
    def get_axis_value(self, axis):
        """Get the current value of a joystick axis"""
        if not self.active or not self.joystick:
            return 0.0
            
        if 0 <= axis < self.joystick.get_numaxes():
            return self.joystick.get_axis(axis)
            
        return 0.0
    
    def update(self):
        """Update the joystick state"""
        # Just check if joystick is still connected
        if self.active and not pygame.joystick.get_count() > 0:
            print("Joystick disconnected")
            self.active = False
            self.joystick = None

class XArcadeInputHandler(InputHandler):
    """X-Arcade input handler for DogPuter
    
    The X-Arcade is typically recognized as a keyboard device,
    but with specific key mappings for its buttons.
    """
    
    # Default X-Arcade key mappings based on common configurations
    DEFAULT_MAPPINGS = {
        # Player 1 controls
        'p1_up': pygame.K_UP,
        'p1_down': pygame.K_DOWN,
        'p1_left': pygame.K_LEFT,
        'p1_right': pygame.K_RIGHT,
        'p1_a': pygame.K_LCTRL,
        'p1_b': pygame.K_LALT,
        'p1_c': pygame.K_SPACE,
        'p1_start': pygame.K_1,
        'p1_coin': pygame.K_5,
        
        # Player 2 controls (if needed)
        'p2_up': pygame.K_r,
        'p2_down': pygame.K_f,
        'p2_left': pygame.K_d,
        'p2_right': pygame.K_g,
        'p2_a': pygame.K_a,
        'p2_b': pygame.K_s,
        'p2_c': pygame.K_q,
        'p2_start': pygame.K_2,
        'p2_coin': pygame.K_6,
    }
    
    def __init__(self, key_mappings=None):
        """Initialize the X-Arcade input handler with custom mappings if provided"""
        self.key_mappings = key_mappings or self.DEFAULT_MAPPINGS
        self.events = []
    
    def get_events(self):
        """Get all pending pygame events, filtering for keyboard events used by X-Arcade"""
        # Get all events
        all_events = pygame.event.get()
        
        # Filter for keyboard events that match our mappings
        x_arcade_keys = set(self.key_mappings.values())
        
        self.events = [event for event in all_events if 
                      (event.type in (pygame.KEYDOWN, pygame.KEYUP) and 
                       hasattr(event, 'key') and event.key in x_arcade_keys)]
                      
        return self.events
    
    def is_key_pressed(self, key):
        """Check if an X-Arcade button is pressed, using logical button names"""
        keys = pygame.key.get_pressed()
        
        # Handle case where key is a logical name (like 'p1_up')
        if isinstance(key, str) and key in self.key_mappings:
            mapped_key = self.key_mappings[key]
            return keys[mapped_key]
        
        # Handle case where key is a pygame key constant
        for logical_key, mapped_key in self.key_mappings.items():
            if mapped_key == key:
                return keys[mapped_key]
                
        return False
    
    def get_axis_value(self, axis):
        """Simulate joystick axes using X-Arcade directional buttons"""
        # X-Arcade doesn't have true analog axes, but we can simulate them
        if axis == 0:  # Horizontal axis
            left = self.is_key_pressed('p1_left')
            right = self.is_key_pressed('p1_right')
            return 1.0 if right and not left else -1.0 if left and not right else 0.0
        elif axis == 1:  # Vertical axis
            up = self.is_key_pressed('p1_up')
            down = self.is_key_pressed('p1_down')
            return 1.0 if down and not up else -1.0 if up and not down else 0.0
        
        return 0.0
    
    def update(self):
        """Update the input state"""
        # For X-Arcade, we don't need additional updates beyond get_events
        pass

class CompositeInputHandler(InputHandler):
    """Composite input handler that manages multiple input handlers"""
    
    def __init__(self):
        """Initialize the composite input handler with empty handlers list"""
        self.handlers = []
        self.events = []
    
    def add_handler(self, handler):
        """Add an input handler to the composite"""
        if isinstance(handler, InputHandler):
            self.handlers.append(handler)
        return self
    
    def get_events(self):
        """Get events from all handlers"""
        self.events = []
        
        for handler in self.handlers:
            self.events.extend(handler.get_events())
            
        return self.events
    
    def is_key_pressed(self, key):
        """Check if a key is pressed on any handler"""
        for handler in self.handlers:
            if handler.is_key_pressed(key):
                return True
                
        return False
    
    def get_axis_value(self, axis):
        """Get axis value from the first handler that returns a non-zero value"""
        for handler in self.handlers:
            value = handler.get_axis_value(axis)
            if abs(value) > 0.1:  # Apply a small deadzone
                return value
                
        return 0.0
    
    def update(self):
        """Update all handlers"""
        for handler in self.handlers:
            handler.update()

class MockInputHandler(InputHandler):
    """Mock input handler for testing"""
    
    def __init__(self):
        """Initialize the mock input handler"""
        self.pressed_keys = set()
        self.events = []
        self.axis_values = {}
    
    def simulate_key_press(self, key):
        """Simulate a key press"""
        self.pressed_keys.add(key)
        
        # Create a mock event
        event = pygame.event.Event(pygame.KEYDOWN, {'key': key})
        self.events.append(event)
    
    def simulate_key_release(self, key):
        """Simulate a key release"""
        if key in self.pressed_keys:
            self.pressed_keys.remove(key)
            
        # Create a mock event
        event = pygame.event.Event(pygame.KEYUP, {'key': key})
        self.events.append(event)
    
    def set_axis_value(self, axis, value):
        """Set a mock axis value"""
        self.axis_values[axis] = value
        
        # Create a mock event
        event = pygame.event.Event(pygame.JOYAXISMOTION, {'axis': axis, 'value': value})
        self.events.append(event)
    
    def get_events(self):
        """Get all pending mock events"""
        events = self.events.copy()
        self.events.clear()
        return events
    
    def is_key_pressed(self, key):
        """Check if a key is pressed in our mock state"""
        return key in self.pressed_keys
    
    def get_axis_value(self, axis):
        """Get the current value of a mock axis"""
        return self.axis_values.get(axis, 0.0)
    
    def update(self):
        """Update the mock input state"""
        pass

def create_input_handler(config=None):
    """Factory function to create the appropriate input handler(s) based on configuration"""
    config = config or {}
    input_type = config.get('input_type', 'keyboard')
    
    if input_type == 'mock':
        return MockInputHandler()
    
    if input_type == 'composite':
        composite = CompositeInputHandler()
        
        # Add keyboard handler by default
        composite.add_handler(KeyboardInputHandler(config.get('key_mappings')))
        
        # Add joystick handler if enabled
        if config.get('use_joystick', True):
            composite.add_handler(JoystickInputHandler(config.get('joystick_id', 0),
                                                     config.get('button_mappings')))
        
        # Add X-Arcade handler if enabled
        if config.get('use_xarcade', False):
            composite.add_handler(XArcadeInputHandler(config.get('xarcade_mappings')))
            
        return composite
    
    if input_type == 'keyboard':
        return KeyboardInputHandler(config.get('key_mappings'))
    
    if input_type == 'joystick':
        return JoystickInputHandler(config.get('joystick_id', 0),
                                  config.get('button_mappings'))
    
    if input_type == 'xarcade':
        return XArcadeInputHandler(config.get('xarcade_mappings'))
    
    # Default to keyboard if input_type is not recognized
    return KeyboardInputHandler()
