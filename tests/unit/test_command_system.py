"""
Tests for the new command-based input system
"""

import pytest
import pygame
from dogputer.core.commands import ContentCommand, VideoChannelCommand, ExitCommand
from dogputer.io.input_mapper import InputMapper
from dogputer.io.input_handler import MockInputHandler, KeyboardInputHandler

class TestInputMapper:
    """Tests for the InputMapper class"""
    
    def test_map_keyboard_event(self):
        """Test mapping keyboard events to commands"""
        # Create a mapper with some test mappings
        mappings = {
            pygame.K_a: "ball",
            pygame.K_b: "treat",
            pygame.K_RIGHT: "channel_next"
        }
        mapper = InputMapper(mappings)
        
        # Create a test key down event
        ball_event = pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_a})
        command = mapper.map_event(ball_event)
        
        # Verify the command was created correctly
        assert isinstance(command, ContentCommand)
        assert command.content_name == "ball"
        
        # Test channel command
        channel_event = pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_RIGHT})
        command = mapper.map_event(channel_event)
        
        assert isinstance(command, VideoChannelCommand)
        assert command.direction == 1  # Next channel
        
        # Test unmapped key
        unmapped_event = pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_z})
        command = mapper.map_event(unmapped_event)
        
        assert command is None
    
    def test_map_joystick_event(self):
        """Test mapping joystick events to commands"""
        # Create a mapper with some test joystick mappings
        mappings = {
            ('button', 0, 1): "ball",
            ('hat', 0, 'right'): "channel_next"
        }
        mapper = InputMapper(mappings)
        
        # Create a test joystick button event
        button_event = pygame.event.Event(pygame.JOYBUTTONDOWN, {'joy': 0, 'button': 1})
        command = mapper.map_event(button_event)
        
        # Verify the command was created correctly
        assert isinstance(command, ContentCommand)
        assert command.content_name == "ball"
        
        # Test hat event
        hat_event = pygame.event.Event(pygame.JOYHATMOTION, {'joy': 0, 'value': (1, 0)})  # Right direction
        command = mapper.map_event(hat_event)
        
        assert isinstance(command, VideoChannelCommand)
        assert command.direction == 1  # Next channel

class TestInputHandler:
    """Tests for the enhanced InputHandler classes"""
    
    def test_mock_input_handler_commands(self):
        """Test getting commands from a MockInputHandler"""
        # Initialize pygame for event handling
        pygame.init()
        
        # Create a mock input handler
        handler = MockInputHandler()
        
        # Set up a mapper with test mappings
        mappings = {pygame.K_a: "ball", pygame.K_ESCAPE: "exit"}
        handler.mapper = InputMapper(mappings)
        
        # Simulate key press
        handler.simulate_key_press(pygame.K_a)
        
        # Get commands from the handler
        commands = handler.get_commands()
        
        # Verify command was created correctly
        assert len(commands) == 1
        assert isinstance(commands[0], ContentCommand)
        assert commands[0].content_name == "ball"
        
        # Test ESC key for exit command
        handler.simulate_key_press(pygame.K_ESCAPE)
        commands = handler.get_commands()
        
        assert len(commands) == 1
        assert isinstance(commands[0], ExitCommand)
        
        pygame.quit()
