#!/usr/bin/env python3
"""
Unit tests for the InputHandler classes
"""

import os
import sys
import pygame
import pytest
from unittest.mock import patch, MagicMock

# Add src directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "src")))

# Import the classes to test from the package structure
from dogputer.io.input_handler import (InputHandler, KeyboardInputHandler, 
                                      JoystickInputHandler, XArcadeInputHandler,
                                      CompositeInputHandler, MockInputHandler,
                                      create_input_handler)

class TestKeyboardInputHandler:
    """Test cases for the KeyboardInputHandler class"""
    
    def test_init(self):
        """Test initialization"""
        # Test with default key mappings
        handler = KeyboardInputHandler()
        assert handler.key_mappings == {}
        
        # Test with custom key mappings
        custom_mappings = {pygame.K_a: pygame.K_b}
        handler = KeyboardInputHandler(custom_mappings)
        assert handler.key_mappings == custom_mappings
    
    @patch('pygame.event.get')
    def test_get_events(self, mock_event_get):
        """Test get_events method"""
        # Setup
        mock_events = [
            pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_SPACE}),
            pygame.event.Event(pygame.KEYUP, {'key': pygame.K_SPACE})
        ]
        mock_event_get.return_value = mock_events
        
        # Execute
        handler = KeyboardInputHandler()
        events = handler.get_events()
        
        # Verify
        assert events == mock_events
        mock_event_get.assert_called_once()
    
    @patch('pygame.key.get_pressed')
    def test_is_key_pressed(self, mock_get_pressed):
        """Test is_key_pressed method"""
        # Setup
        mock_key_state = {k: False for k in range(323)}  # Maximum pygame key constant
        mock_key_state[pygame.K_SPACE] = True
        mock_key_state[pygame.K_b] = True
        
        # Create a list-like object that works with subscription
        class MockKeyState:
            def __getitem__(self, key):
                return mock_key_state.get(key, False)
        
        mock_get_pressed.return_value = MockKeyState()
        
        # Execute and verify with no mapping
        handler = KeyboardInputHandler()
        assert handler.is_key_pressed(pygame.K_SPACE) is True
        assert handler.is_key_pressed(pygame.K_a) is False
        
        # Execute and verify with key mapping
        handler = KeyboardInputHandler({pygame.K_a: pygame.K_b})
        assert handler.is_key_pressed(pygame.K_a) is True  # maps to K_b which is True
        
        mock_get_pressed.assert_called()

class TestMockInputHandler:
    """Test cases for the MockInputHandler class"""
    
    def test_init(self):
        """Test initialization"""
        handler = MockInputHandler()
        assert handler.pressed_keys == set()
        assert handler.events == []
        assert handler.axis_values == {}
    
    def test_simulate_key_press(self):
        """Test simulate_key_press method"""
        handler = MockInputHandler()
        
        # Simulate a key press
        handler.simulate_key_press(pygame.K_SPACE)
        
        # Verify
        assert pygame.K_SPACE in handler.pressed_keys
        assert len(handler.events) == 1
        assert handler.events[0].type == pygame.KEYDOWN
        assert handler.events[0].key == pygame.K_SPACE
    
    def test_simulate_key_release(self):
        """Test simulate_key_release method"""
        handler = MockInputHandler()
        
        # Setup by pressing a key first
        handler.simulate_key_press(pygame.K_SPACE)
        handler.events.clear()  # Clear events from press
        
        # Simulate a key release
        handler.simulate_key_release(pygame.K_SPACE)
        
        # Verify
        assert pygame.K_SPACE not in handler.pressed_keys
        assert len(handler.events) == 1
        assert handler.events[0].type == pygame.KEYUP
        assert handler.events[0].key == pygame.K_SPACE
    
    def test_set_axis_value(self):
        """Test set_axis_value method"""
        handler = MockInputHandler()
        
        # Set an axis value
        handler.set_axis_value(0, 0.5)
        
        # Verify
        assert handler.axis_values[0] == 0.5
        assert len(handler.events) == 1
        assert handler.events[0].type == pygame.JOYAXISMOTION
        assert handler.events[0].axis == 0
        assert handler.events[0].value == 0.5
    
    def test_get_events(self):
        """Test get_events method"""
        handler = MockInputHandler()
        
        # Add some events
        handler.simulate_key_press(pygame.K_SPACE)
        handler.simulate_key_press(pygame.K_a)
        
        # Execute
        events = handler.get_events()
        
        # Verify
        assert len(events) == 2
        assert events[0].type == pygame.KEYDOWN
        assert events[0].key == pygame.K_SPACE
        assert events[1].type == pygame.KEYDOWN
        assert events[1].key == pygame.K_a
        
        # Events should be cleared after getting
        assert len(handler.events) == 0
    
    def test_is_key_pressed(self):
        """Test is_key_pressed method"""
        handler = MockInputHandler()
        
        # Key should not be pressed initially
        assert handler.is_key_pressed(pygame.K_SPACE) is False
        
        # Press a key
        handler.simulate_key_press(pygame.K_SPACE)
        
        # Key should now be pressed
        assert handler.is_key_pressed(pygame.K_SPACE) is True
        
        # Other keys should still not be pressed
        assert handler.is_key_pressed(pygame.K_a) is False
    
    def test_get_axis_value(self):
        """Test get_axis_value method"""
        handler = MockInputHandler()
        
        # Axis should be neutral initially
        assert handler.get_axis_value(0) == 0.0
        
        # Set an axis value
        handler.set_axis_value(0, 0.7)
        
        # Axis should now have the set value
        assert handler.get_axis_value(0) == 0.7
        
        # Other axes should still be neutral
        assert handler.get_axis_value(1) == 0.0

class TestXArcadeInputHandler:
    """Test cases for the XArcadeInputHandler class"""
    
    def test_init(self):
        """Test initialization"""
        # Test with default mappings
        handler = XArcadeInputHandler()
        assert handler.key_mappings == XArcadeInputHandler.DEFAULT_MAPPINGS
        
        # Test with custom mappings
        custom_mappings = {'p1_up': pygame.K_w}
        handler = XArcadeInputHandler(custom_mappings)
        assert handler.key_mappings == custom_mappings
    
    @patch('pygame.event.get')
    def test_get_events(self, mock_event_get):
        """Test get_events method with filtering"""
        # Setup
        handler = XArcadeInputHandler()
        
        # Create a mix of events, some matching X-Arcade keys, some not
        x_arcade_key = handler.key_mappings['p1_up']  # Should be in our mappings
        non_x_arcade_key = pygame.K_F12  # Not in our mappings
        
        mock_events = [
            pygame.event.Event(pygame.KEYDOWN, {'key': x_arcade_key}),
            pygame.event.Event(pygame.KEYDOWN, {'key': non_x_arcade_key}),
            pygame.event.Event(pygame.KEYUP, {'key': x_arcade_key}),
            pygame.event.Event(pygame.MOUSEMOTION, {'pos': (100, 100)}),
        ]
        mock_event_get.return_value = mock_events
        
        # Execute
        events = handler.get_events()
        
        # Verify - should only include events with X-Arcade keys
        assert len(events) == 2
        assert events[0].type == pygame.KEYDOWN
        assert events[0].key == x_arcade_key
        assert events[1].type == pygame.KEYUP
        assert events[1].key == x_arcade_key
    
    @patch('pygame.key.get_pressed')
    def test_is_key_pressed_with_logical_name(self, mock_get_pressed):
        """Test is_key_pressed method with logical button names"""
        # Setup
        mock_key_state = {k: False for k in range(323)}
        mock_key_state[pygame.K_UP] = True  # 'p1_up' in DEFAULT_MAPPINGS
        
        class MockKeyState:
            def __getitem__(self, key):
                return mock_key_state.get(key, False)
        
        mock_get_pressed.return_value = MockKeyState()
        
        # Execute and verify with logical name
        handler = XArcadeInputHandler()
        assert handler.is_key_pressed('p1_up') is True
        assert handler.is_key_pressed('p1_down') is False
    
    @patch('pygame.key.get_pressed')
    def test_get_axis_value_simulation(self, mock_get_pressed):
        """Test axis simulation from directional buttons"""
        # Setup
        handler = XArcadeInputHandler()
        
        # Create different key states to test axis simulation
        test_cases = [
            # No buttons pressed - neutral position
            ({}, 0, 0.0),
            # Right pressed - positive X
            ({pygame.K_RIGHT: True}, 0, 1.0),
            # Left pressed - negative X
            ({pygame.K_LEFT: True}, 0, -1.0),
            # Both left and right pressed - neutral X
            ({pygame.K_LEFT: True, pygame.K_RIGHT: True}, 0, 0.0),
            # Down pressed - positive Y
            ({pygame.K_DOWN: True}, 1, 1.0),
            # Up pressed - negative Y
            ({pygame.K_UP: True}, 1, -1.0),
            # Both up and down pressed - neutral Y
            ({pygame.K_UP: True, pygame.K_DOWN: True}, 1, 0.0),
        ]
        
        for key_state, axis, expected_value in test_cases:
            # Create a key state with specific keys pressed
            mock_keys = {k: False for k in range(323)}
            for key in key_state:
                mock_keys[key] = True
                
            class MockKeyState:
                def __getitem__(self, key):
                    return mock_keys.get(key, False)
            
            mock_get_pressed.return_value = MockKeyState()
            
            # Test the axis value
            actual_value = handler.get_axis_value(axis)
            assert actual_value == expected_value, f"Failed for key_state={key_state}, axis={axis}"

class TestCompositeInputHandler:
    """Test cases for the CompositeInputHandler class"""
    
    def test_init(self):
        """Test initialization"""
        handler = CompositeInputHandler()
        assert handler.handlers == []
        assert handler.events == []
    
    def test_add_handler(self):
        """Test add_handler method"""
        composite = CompositeInputHandler()
        
        # Add a mock handler
        mock = MockInputHandler()
        composite.add_handler(mock)
        
        # Verify
        assert len(composite.handlers) == 1
        assert composite.handlers[0] == mock
        
        # Test method chaining
        keyboard = KeyboardInputHandler()
        result = composite.add_handler(keyboard)
        
        assert result == composite
        assert len(composite.handlers) == 2
        assert composite.handlers[1] == keyboard
    
    def test_get_events_combines_from_all_handlers(self):
        """Test that get_events combines events from all handlers"""
        composite = CompositeInputHandler()
        
        # Create mock handlers with different events
        mock1 = MockInputHandler()
        mock1.simulate_key_press(pygame.K_a)
        
        mock2 = MockInputHandler()
        mock2.simulate_key_press(pygame.K_b)
        
        # Add both handlers
        composite.add_handler(mock1)
        composite.add_handler(mock2)
        
        # Get events and verify they're combined
        events = composite.get_events()
        
        assert len(events) == 2
        assert events[0].key == pygame.K_a
        assert events[1].key == pygame.K_b
    
    def test_is_key_pressed_checks_all_handlers(self):
        """Test is_key_pressed checks all handlers and returns True if any is True"""
        composite = CompositeInputHandler()
        
        # Create mock handlers with different keys pressed
        mock1 = MockInputHandler()
        mock1.simulate_key_press(pygame.K_a)
        
        mock2 = MockInputHandler()
        mock2.simulate_key_press(pygame.K_b)
        
        # Add both handlers
        composite.add_handler(mock1)
        composite.add_handler(mock2)
        
        # Check if keys are pressed
        assert composite.is_key_pressed(pygame.K_a) is True
        assert composite.is_key_pressed(pygame.K_b) is True
        assert composite.is_key_pressed(pygame.K_c) is False
    
    def test_get_axis_value_returns_first_non_zero(self):
        """Test get_axis_value returns the first non-zero value from handlers"""
        composite = CompositeInputHandler()
        
        # Create mock handlers with different axis values
        mock1 = MockInputHandler()
        mock1.set_axis_value(0, 0.0)  # Neutral
        mock1.set_axis_value(1, -0.7) # Negative Y
        
        mock2 = MockInputHandler()
        mock2.set_axis_value(0, 0.5)  # Positive X
        mock2.set_axis_value(1, 0.0)  # Neutral
        
        # Add handlers in specific order
        composite.add_handler(mock1)
        composite.add_handler(mock2)
        
        # Check axis values
        assert composite.get_axis_value(0) == 0.5  # From mock2
        assert composite.get_axis_value(1) == -0.7 # From mock1
        assert composite.get_axis_value(2) == 0.0  # Default
    
    def test_update_calls_update_on_all_handlers(self):
        """Test update calls update on all handlers"""
        composite = CompositeInputHandler()
        
        # Create mock handlers
        mock1 = MagicMock(spec=InputHandler)
        mock2 = MagicMock(spec=InputHandler)
        
        # Add handlers
        composite.add_handler(mock1)
        composite.add_handler(mock2)
        
        # Call update
        composite.update()
        
        # Verify
        mock1.update.assert_called_once()
        mock2.update.assert_called_once()

class TestCreateInputHandler:
    """Test cases for the create_input_handler factory function"""
    
    def test_default_creates_keyboard_handler(self):
        """Test default configuration creates a KeyboardInputHandler"""
        handler = create_input_handler()
        assert isinstance(handler, KeyboardInputHandler)
    
    def test_create_mock_handler(self):
        """Test creating a MockInputHandler"""
        handler = create_input_handler({'input_type': 'mock'})
        assert isinstance(handler, MockInputHandler)
    
    def test_create_keyboard_handler_with_mappings(self):
        """Test creating a KeyboardInputHandler with mappings"""
        mappings = {pygame.K_a: pygame.K_b}
        handler = create_input_handler({
            'input_type': 'keyboard',
            'key_mappings': mappings
        })
        assert isinstance(handler, KeyboardInputHandler)
        assert handler.key_mappings == mappings
    
    @patch('pygame.joystick.get_count', return_value=1)
    @patch('pygame.joystick.Joystick')
    def test_create_joystick_handler(self, mock_joystick_class, mock_get_count):
        """Test creating a JoystickInputHandler"""
        # Mock joystick instance
        mock_joystick = MagicMock()
        mock_joystick_class.return_value = mock_joystick
        
        # Create handler
        handler = create_input_handler({'input_type': 'joystick'})
        
        # Verify
        assert isinstance(handler, JoystickInputHandler)
        mock_joystick_class.assert_called_once_with(0)
    
    def test_create_xarcade_handler(self):
        """Test creating an XArcadeInputHandler"""
        mappings = {'p1_up': pygame.K_w}
        handler = create_input_handler({
            'input_type': 'xarcade',
            'xarcade_mappings': mappings
        })
        assert isinstance(handler, XArcadeInputHandler)
        assert handler.key_mappings == mappings
    
    def test_create_composite_handler(self):
        """Test creating a CompositeInputHandler"""
        # Configure a composite with keyboard and x-arcade
        handler = create_input_handler({
            'input_type': 'composite',
            'use_joystick': False,  # Disable joystick to avoid needing mocks
            'use_xarcade': True,
            'key_mappings': {pygame.K_a: pygame.K_b},
            'xarcade_mappings': {'p1_up': pygame.K_w}
        })
        
        # Verify
        assert isinstance(handler, CompositeInputHandler)
        assert len(handler.handlers) == 2
        assert isinstance(handler.handlers[0], KeyboardInputHandler)
        assert isinstance(handler.handlers[1], XArcadeInputHandler)
        assert handler.handlers[0].key_mappings == {pygame.K_a: pygame.K_b}
        assert handler.handlers[1].key_mappings == {'p1_up': pygame.K_w}
