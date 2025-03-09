#!/usr/bin/env python3
"""
Input handler module for DogPuter
Provides a consistent interface for different input methods (keyboard, joystick).
"""

import pygame
from abc import ABC, abstractmethod
from dogputer.io.input_mapper import InputMapper

class InputHandler(ABC):
    """Abstract base class for input handlers"""
    
    def __init__(self):
        """Initialize the input handler"""
        self.mapper = None
    
    def set_mapper(self, mapper):
        """Set the input mapper for this handler"""
        self.mapper = mapper
        return self
    
    @abstractmethod
    def get_events(self):
        """Get all pending input events"""
        pass
    
    def get_commands(self):
        """Get commands from input events using the mapper"""
        if not self.mapper:
            return []
            
        commands = []
        for event in self.get_events():
            command = self.mapper.map_event(event)
            if command:
                commands.append(command)
                
        return commands
    
    @abstractmethod
    def is_key_pressed(self, key):
        """Check if a key is currently pressed"""
        pass
    
    @abstractmethod
    def get_axis_value(self, axis):
        """Get the current value of an axis (joystick)"""
        pass
    
    def get_axis_commands(self):
        """Get commands from axis values"""
        return []
    
    @abstractmethod
    def update(self):
        """Update the input state"""
        pass

class KeyboardInputHandler(InputHandler):
    """Keyboard input handler for DogPuter"""
    
    def __init__(self, input_mappings=None):
        """Initialize the keyboard input handler"""
        super().__init__()
        self.input_mappings = input_mappings or {}
        # For backward compatibility
        self.key_mappings = self.input_mappings
        # Initialize with empty events list
        self.events = []
        # Create input mapper
        self.mapper = InputMapper(self.input_mappings)
        
        print(f"KeyboardInputHandler initialized with {len(self.input_mappings)} input mappings")
        # Log all key mappings for debugging
        for key, command in self.input_mappings.items():
            if not isinstance(key, tuple):  # Only process keyboard keys, not gamepad inputs
                try:
                    key_name = pygame.key.name(key)
                    print(f"  Key mapping: {key_name} (code: {key}) -> {command}")
                except:
                    print(f"  Key mapping: Unknown key {key} -> {command}")
    
    def get_events(self):
        """Get all pending pygame events"""
        # Store all events except QUIT, which is handled directly in the main loop
        all_events = pygame.event.get(exclude=[pygame.QUIT])
        
        # Filter and log keyboard events for debugging
        self.events = []
        for event in all_events:
            if event.type == pygame.KEYDOWN:
                try:
                    key_name = pygame.key.name(event.key)
                    print(f"KeyboardHandler detected key: {key_name} (code: {event.key})")
                    if event.key in self.input_mappings:
                        print(f"  Found mapping: {self.input_mappings[event.key]}")
                    self.events.append(event)
                except:
                    print(f"KeyboardHandler detected unknown key: {event.key}")
                    self.events.append(event)
            elif event.type == pygame.KEYUP:
                self.events.append(event)
            else:
                # Pass through non-keyboard events
                self.events.append(event)
                
        return self.events
    
    def is_key_pressed(self, key):
        """Check if a key is currently pressed"""
        keys = pygame.key.get_pressed()
        
        # If key is a string, it's a command we need to check if any mapped keys for this command are pressed
        if isinstance(key, str):
            # Look for any key that maps to this command
            for k, command in self.input_mappings.items():
                if not isinstance(k, tuple) and command == key and keys[k]:
                    return True
            return False
        
        # For backward compatibility: check if this key is mapped to another key
        if key in self.input_mappings:
            mapped_value = self.input_mappings[key]
            # If the mapped value is a pygame key constant (int), use that key instead
            if isinstance(mapped_value, int):
                return keys[mapped_value]
            
        # Otherwise, check if the specific key is pressed
        is_pressed = keys[key]
        if is_pressed:
            try:
                key_name = pygame.key.name(key)
                print(f"Key is pressed: {key_name} (code: {key})")
            except:
                print(f"Unknown key is pressed: {key}")
        return is_pressed
    
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
    
    def __init__(self, joystick_id=0, input_mappings=None):
        """Initialize the joystick input handler"""
        super().__init__()
        self.input_mappings = input_mappings or {}
        self.joystick_id = joystick_id
        self.events = []
        
        # Create input mapper
        self.mapper = InputMapper(self.input_mappings)
        
        # Initialize joystick if available
        if pygame.joystick.get_count() > joystick_id:
            self.joystick = pygame.joystick.Joystick(joystick_id)
            self.joystick.init()
            print(f"Joystick initialized: {self.joystick.get_name()}")
            self.active = True
        else:
            print(f"No joystick found with ID {joystick_id}")
            self.joystick = None
            self.active = False
    
    def get_events(self):
        """Get all pending pygame events, filtering for joystick events"""
        # Get all events except QUIT, which is handled directly in the main loop
        all_events = pygame.event.get(exclude=[pygame.QUIT])
        
        # Filter for joystick events
        self.events = []
        for event in all_events:
            if event.type in (pygame.JOYBUTTONDOWN, pygame.JOYBUTTONUP, 
                             pygame.JOYAXISMOTION, pygame.JOYHATMOTION):
                if hasattr(event, 'joy') and event.joy == self.joystick_id:
                    self.events.append(event)
                    
                    # Debug info
                    if event.type == pygame.JOYBUTTONDOWN:
                        button_key = ('button', self.joystick_id, event.button)
                        if button_key in self.input_mappings:
                            print(f"Joystick button {event.button} maps to {self.input_mappings[button_key]}")
                    elif event.type == pygame.JOYHATMOTION:
                        if event.value[0] > 0:  # Right
                            hat_key = ('hat', self.joystick_id, 'right')
                            if hat_key in self.input_mappings:
                                print(f"Joystick hat right maps to {self.input_mappings[hat_key]}")
                        elif event.value[0] < 0:  # Left
                            hat_key = ('hat', self.joystick_id, 'left')
                            if hat_key in self.input_mappings:
                                print(f"Joystick hat left maps to {self.input_mappings[hat_key]}")
                        if event.value[1] > 0:  # Up
                            hat_key = ('hat', self.joystick_id, 'up')
                            if hat_key in self.input_mappings:
                                print(f"Joystick hat up maps to {self.input_mappings[hat_key]}")
                        elif event.value[1] < 0:  # Down
                            hat_key = ('hat', self.joystick_id, 'down')
                            if hat_key in self.input_mappings:
                                print(f"Joystick hat down maps to {self.input_mappings[hat_key]}")
                                
        return self.events
    
    def get_axis_commands(self):
        """Get commands from joystick axis values"""
        if not self.active or not self.joystick or not self.mapper:
            return []
            
        commands = []
        for axis in range(self.joystick.get_numaxes()):
            value = self.joystick.get_axis(axis)
            command = self.mapper.map_axis_to_command(self.joystick_id, axis, value)
            if command:
                commands.append(command)
                
        return commands
    
    def is_key_pressed(self, key):
        """Check if a joystick button/direction is pressed"""
        if not self.active or not self.joystick:
            return False
            
        # If key is a string, it's a command we need to check if any mapped inputs for this command are pressed
        if isinstance(key, str):
            # Look for any joystick input that maps to this command
            for input_key, command in self.input_mappings.items():
                if isinstance(input_key, tuple) and command == key:
                    input_type = input_key[0]
                    joy_id = input_key[1]
                    
                    if joy_id != self.joystick_id:
                        continue
                        
                    if input_type == 'button':
                        button_num = input_key[2]
                        if button_num < self.joystick.get_numbuttons() and self.joystick.get_button(button_num):
                            return True
                    elif input_type == 'hat':
                        direction = input_key[2]
                        if self.joystick.get_numhats() > 0:
                            hat_value = self.joystick.get_hat(0)  # Use first hat
                            if direction == 'up' and hat_value[1] > 0:
                                return True
                            elif direction == 'down' and hat_value[1] < 0:
                                return True
                            elif direction == 'right' and hat_value[0] > 0:
                                return True
                            elif direction == 'left' and hat_value[0] < 0:
                                return True
            return False
            
        # For backward compatibility: if key is a tuple, check that specific input
        if isinstance(key, tuple) and len(key) == 3:
            input_type = key[0]
            joy_id = key[1]
            
            if joy_id != self.joystick_id:
                return False
                
            if input_type == 'button':
                button_num = key[2]
                if button_num < self.joystick.get_numbuttons():
                    return self.joystick.get_button(button_num)
            elif input_type == 'hat':
                direction = key[2]
                if self.joystick.get_numhats() > 0:
                    hat_value = self.joystick.get_hat(0)  # Use first hat
                    if direction == 'up':
                        return hat_value[1] > 0
                    elif direction == 'down':
                        return hat_value[1] < 0
                    elif direction == 'right':
                        return hat_value[0] > 0
                    elif direction == 'left':
                        return hat_value[0] < 0
        
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
        # Check if joystick is still connected
        if self.active and (pygame.joystick.get_count() <= self.joystick_id):
            print(f"Joystick {self.joystick_id} disconnected")
            self.active = False
            self.joystick = None

class XArcadeInputHandler(KeyboardInputHandler):
    """X-Arcade input handler for DogPuter - specialized keyboard handler"""
    
    # Default X-Arcade mappings for keyboard mode
    DEFAULT_MAPPINGS = {
        'p1_up': pygame.K_UP,
        'p1_down': pygame.K_DOWN,
        'p1_left': pygame.K_LEFT, 
        'p1_right': pygame.K_RIGHT,
        'p1_button1': pygame.K_z,
        'p1_button2': pygame.K_x,
        'p1_button3': pygame.K_c,
        'p1_button4': pygame.K_v,
        'p1_button5': pygame.K_b,
        'p1_button6': pygame.K_n,
        'p1_start': pygame.K_RETURN,
        'p2_up': pygame.K_w,
        'p2_down': pygame.K_s,
        'p2_left': pygame.K_a,
        'p2_right': pygame.K_d,
        'p2_button1': pygame.K_i,
        'p2_button2': pygame.K_o,
        'p2_button3': pygame.K_p,
        'p2_button4': pygame.K_LEFTBRACKET,
        'p2_button5': pygame.K_SEMICOLON,
        'p2_button6': pygame.K_QUOTE,
        'p2_start': pygame.K_RSHIFT
    }
    
    def __init__(self, xarcade_mappings=None):
        """Initialize the X-Arcade input handler"""
        # Initialize with the X-Arcade default mappings if none provided
        xarcade_mappings = xarcade_mappings or self.DEFAULT_MAPPINGS
        
        # Create mappings from key names to commands
        input_mappings = {}
        
        # Add the global INPUT_MAPPINGS
        from dogputer.core.config import INPUT_MAPPINGS
        input_mappings.update(INPUT_MAPPINGS)
        
        # Initialize parent class with the full input_mappings
        super().__init__(input_mappings=input_mappings)
        
        # Set key_mappings for X-Arcade logical names to pygame keys
        self.key_mappings = xarcade_mappings
        
        # Map X-Arcade logical names to pygame keys through DEFAULT_MAPPINGS
        self.events = []
        
        # Log the X-Arcade key mappings for debugging
        print(f"X-Arcade input handler initialized with {len(self.key_mappings)} logical button mappings")
        for logical_name, pygame_key in self.key_mappings.items():
            try:
                key_name = pygame.key.name(pygame_key)
                print(f"  X-Arcade mapping: {logical_name} -> {key_name} (code: {pygame_key})")
            except:
                print(f"  X-Arcade mapping: {logical_name} -> Unknown key {pygame_key}")
        
    def get_events(self):
        """Get all pending pygame events, filtering for X-Arcade keys"""
        # Get all events except QUIT, which is handled directly in the main loop
        all_events = pygame.event.get(exclude=[pygame.QUIT])
        
        # Filter for X-Arcade keys and mapped command keys
        self.events = []
        x_arcade_keys = set(self.key_mappings.values())
        
        for event in all_events:
            if event.type in (pygame.KEYDOWN, pygame.KEYUP):
                # Include X-Arcade keys and keys in INPUT_MAPPINGS
                if event.key in x_arcade_keys or event.key in self.input_mappings:
                    # If it's a key we care about, add extra debugging
                    if event.type == pygame.KEYDOWN:
                        try:
                            key_name = pygame.key.name(event.key)
                            print(f"X-Arcade handler detected key: {key_name} (code: {event.key})")
                            # Check if it's a mapped key
                            if event.key in self.input_mappings:
                                print(f"  Found INPUT_MAPPING: {self.input_mappings[event.key]}")
                            # Check if it's an X-Arcade key
                            for logical_name, key_code in self.key_mappings.items():
                                if key_code == event.key:
                                    print(f"  Found X-Arcade mapping: {logical_name}")
                        except:
                            print(f"X-Arcade handler detected unknown key: {event.key}")
                            
                    self.events.append(event)
            else:
                # Other events like quit need to be passed through
                if event.type == pygame.QUIT:
                    self.events.append(event)
                    
        return self.events
    
    def is_key_pressed(self, key):
        """Check if a key or X-Arcade logical button is pressed"""
        keys = pygame.key.get_pressed()
        
        # If key is a string, treat it as a logical X-Arcade name (e.g., 'p1_button1')
        if isinstance(key, str):
            if key in self.key_mappings:
                mapped_key = self.key_mappings[key]
                is_pressed = keys[mapped_key]
                if is_pressed:
                    print(f"X-Arcade button {key} is pressed")
                return is_pressed
                
            # Also check if it's a command we need to find in input_mappings
            for k, command in self.input_mappings.items():
                if not isinstance(k, tuple) and command == key:
                    # Check if this key is in our X-Arcade keys
                    if k in set(self.key_mappings.values()) and keys[k]:
                        return True
            return False
            
        # Otherwise, check the specific key
        return super().is_key_pressed(key)
    
    def get_axis_value(self, axis):
        """Simulate axis input using X-Arcade directional buttons"""
        keys = pygame.key.get_pressed()
        
        if axis == 0:  # Horizontal axis
            right = keys[self.key_mappings['p1_right']]
            left = keys[self.key_mappings['p1_left']]
            return (1.0 if right else 0.0) + (-1.0 if left else 0.0)
            
        if axis == 1:  # Vertical axis
            down = keys[self.key_mappings['p1_down']]
            up = keys[self.key_mappings['p1_up']]
            return (1.0 if down else 0.0) + (-1.0 if up else 0.0)
            
        return 0.0
    
    def get_commands_from_logical_buttons(self):
        """Get commands from X-Arcade logical button names"""
        if not self.mapper:
            return []
            
        commands = []
        keys = pygame.key.get_pressed()
        
        # Check each logical button
        for logical_name in self.key_mappings:
            mapped_key = self.key_mappings[logical_name]
            if keys[mapped_key]:
                # If pressed, try to map to command
                command = self.mapper.map_logical_name(logical_name)
                if command:
                    commands.append(command)
                    
        return commands

class CompositeInputHandler(InputHandler):
    """Composite input handler that manages multiple input handlers"""
    
    def __init__(self):
        """Initialize the composite input handler with empty handlers list"""
        super().__init__()
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
    
    def get_commands(self):
        """Get commands from all handlers"""
        commands = []
        
        for handler in self.handlers:
            # Get commands from events
            commands.extend(handler.get_commands())
            
            # Get commands from axis values for joysticks
            if hasattr(handler, 'get_axis_commands'):
                commands.extend(handler.get_axis_commands())
                
            # Get commands from logical buttons for X-Arcade
            if hasattr(handler, 'get_commands_from_logical_buttons'):
                commands.extend(handler.get_commands_from_logical_buttons())
                
        return commands
    
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
        super().__init__()
        self.pressed_keys = set()
        self.events = []
        self.axis_values = {}
        self.mapper = InputMapper({})
    
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
    
    # For backward compatibility: support both input_mappings and key_mappings
    input_mappings = config.get('input_mappings')
    if input_mappings is None:
        input_mappings = config.get('key_mappings')
    
    if input_type == 'mock':
        return MockInputHandler()
    
    if input_type == 'composite':
        composite = CompositeInputHandler()
        
        # Add keyboard handler by default
        composite.add_handler(KeyboardInputHandler(input_mappings))
        
        # Add X-Arcade handler if enabled
        if config.get('use_xarcade', False):
            composite.add_handler(XArcadeInputHandler(config.get('xarcade_mappings')))
        
        # Add joystick handlers if enabled
        if config.get('use_joystick', False):
            # Support multiple joysticks
            joystick_count = pygame.joystick.get_count()
            for i in range(min(joystick_count, 2)):  # Support up to 2 joysticks
                composite.add_handler(JoystickInputHandler(i, input_mappings))
        
        return composite
    
    if input_type == 'keyboard':
        return KeyboardInputHandler(input_mappings)
    
    if input_type == 'joystick':
        return JoystickInputHandler(config.get('joystick_id', 0),
                                   input_mappings)
    
    if input_type == 'xarcade':
        return XArcadeInputHandler(config.get('xarcade_mappings'))
    
    # Default to keyboard if input_type is not recognized
    return KeyboardInputHandler()
