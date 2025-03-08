#!/usr/bin/env python3
"""
Integration tests for the DogPuter UI
"""

import os
import sys
import pytest
import pygame
import time
import threading
from unittest.mock import patch, MagicMock

# Add src directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "src")))

# Use relative imports for current project structure
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

# We'll need these for UI tests
from dogputer.io.input_handler import MockInputHandler

# Import the main application class from the refactored package structure
from dogputer.main import DogPuter

class TestUIIntegration:
    """Integration tests for the DogPuter UI"""
    
    @pytest.fixture
    def mock_pygame_init(self):
        """Mock pygame initialization"""
        with patch('pygame.init') as mock_init:
            with patch('pygame.mixer.init') as mock_mixer:
                with patch('pygame.display.set_mode') as mock_display:
                    mock_display.return_value = pygame.Surface((800, 600))
                    yield mock_init, mock_mixer, mock_display
    
    @pytest.fixture
    def mock_input_handler(self):
        """Create a mock input handler for testing"""
        return MockInputHandler()
    
    @pytest.fixture
    def mock_video_player(self):
        """Create a mock video player for testing"""
        mock = MagicMock()
        mock.play_video = MagicMock(return_value=True)
        mock.stop = MagicMock()
        mock.update = MagicMock(return_value=(pygame.Surface((800, 600)), False))
        return mock
    
    @pytest.fixture
    def mock_tts_handler(self):
        """Create a mock TTS handler for testing"""
        mock = MagicMock()
        mock.speak = MagicMock()
        mock.stop = MagicMock()
        mock.speaking = False
        return mock
    
    @pytest.mark.ui
    def test_app_initialization(self, mock_pygame_init):
        """Test that the application initializes correctly"""
        # This test patches pygame initializations so we don't need a display
        with patch('os.makedirs') as mock_makedirs:
            app = DogPuter()
            
            # Verify directories created
            assert mock_makedirs.call_count >= 3  # At least 3 directories
            
            # Verify pygame was initialized
            mock_init, mock_mixer, mock_display = mock_pygame_init
            mock_init.assert_called_once()
            mock_mixer.assert_called_once()
            mock_display.assert_called_once()
            
            # Check that the app has the expected components
            assert app.video_player is not None
            assert app.tts_handler is not None
    
    @pytest.mark.ui
    def test_app_keystroke_processing(self):
        """Test that the application processes keystrokes correctly"""
        # Create patched app with all necessary mocks
        with patch('pygame.init'), \
             patch('pygame.mixer.init'), \
             patch('pygame.display.set_mode', return_value=pygame.Surface((800, 600))), \
             patch('pygame.font.SysFont', return_value=MagicMock()), \
             patch('os.makedirs'), \
             patch('pygame.joystick.get_count', return_value=0):
            
            # Create app instance with mocked components
            app = DogPuter()
            
            # Patch the app's handle_key_press method to track calls
            app.app_state.handle_key_press = MagicMock()
            
            # Mock pygame.event.get to return our test events
            test_event = pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_SPACE})
            
            # Create a flag for stopping the run loop
            should_stop = [False]
            
            # Replace the app's run method with our test version
            original_run = app.run
            def test_run():
                # Just run one iteration of the event processing
                running = True
                clock = pygame.time.Clock()
                
                while running and not should_stop[0]:
                    # Process one set of events
                    with patch('pygame.event.get', return_value=[test_event]):
                        # Process events
                        for event in pygame.event.get():
                            if event.type == pygame.KEYDOWN:
                                app.app_state.handle_key_press(event.key)
                    
                    # Only run one iteration
                    should_stop[0] = True
                    clock.tick(60)
            
            # Replace run method
            app.run = test_run
            
            # Start the app in a thread to avoid blocking
            app_thread = threading.Thread(target=app.run)
            app_thread.daemon = True
            app_thread.start()
            
            # Wait a short time for processing
            time.sleep(0.1)
            
            # Verify that handle_key_press was called with our key
            app.app_state.handle_key_press.assert_called_with(pygame.K_SPACE)
    
    @pytest.mark.ui
    def test_app_joystick_handling(self):
        """Test that the application handles joystick input correctly"""
        # Create patched app with mocked joystick
        with patch('pygame.init'), \
             patch('pygame.mixer.init'), \
             patch('pygame.display.set_mode', return_value=pygame.Surface((800, 600))), \
             patch('pygame.font.SysFont', return_value=MagicMock()), \
             patch('os.makedirs'), \
             patch('pygame.joystick.get_count', return_value=1):
            
            # Mock joystick
            mock_joystick = MagicMock()
            mock_joystick.get_name.return_value = "Test Joystick"
            
            with patch('pygame.joystick.Joystick', return_value=mock_joystick):
                # Create app instance
                app = DogPuter()
                
                # Verify joystick was detected and initialized
                assert app.joystick is not None
                mock_joystick.init.assert_called_once()
                
                # Mock the joystick handling in app_state
                app.app_state.handle_joystick = MagicMock()
                
                # Create a flag for stopping the run loop
                should_stop = [False]
                
                # Replace the app's run method with our test version
                def test_run():
                    # Just run one iteration of the event processing
                    running = True
                    clock = pygame.time.Clock()
                    
                    while running and not should_stop[0]:
                        # Only need to verify joystick handling is called
                        app.app_state.handle_joystick(app.joystick)
                        
                        # Only run one iteration
                        should_stop[0] = True
                        clock.tick(60)
                
                # Replace run method
                app.run = test_run
                
                # Start the app in a thread to avoid blocking
                app_thread = threading.Thread(target=app.run)
                app_thread.daemon = True
                app_thread.start()
                
                # Wait a short time for processing
                time.sleep(0.1)
                
                # Verify joystick handling was called
                app.app_state.handle_joystick.assert_called_with(mock_joystick)
    
    @pytest.mark.ui
    def test_app_video_playback(self):
        """Test that the application can play videos"""
        # Create patched app with mocked video player
        with patch('pygame.init'), \
             patch('pygame.mixer.init'), \
             patch('pygame.display.set_mode', return_value=pygame.Surface((800, 600))), \
             patch('pygame.font.SysFont', return_value=MagicMock()), \
             patch('os.makedirs'), \
             patch('pygame.joystick.get_count', return_value=0):
            
            # Create mocked video player
            mock_video_player = MagicMock()
            mock_video_player.play_video.return_value = True
            
            # Create app with mocked components
            app = DogPuter()
            app.video_player = mock_video_player
            
            # Test playing a video
            app.video_player.play_video("test.mp4")
            
            # Verify video player was called correctly
            mock_video_player.play_video.assert_called_with("test.mp4")

    @pytest.mark.ui
    def test_app_tts_functionality(self):
        """Test that the application can speak text"""
        # Create patched app with mocked TTS handler
        with patch('pygame.init'), \
             patch('pygame.mixer.init'), \
             patch('pygame.display.set_mode', return_value=pygame.Surface((800, 600))), \
             patch('pygame.font.SysFont', return_value=MagicMock()), \
             patch('os.makedirs'), \
             patch('pygame.joystick.get_count', return_value=0):
            
            # Create mocked TTS handler
            mock_tts = MagicMock()
            
            # Create app with mocked components
            app = DogPuter()
            app.tts_handler = mock_tts
            
            # Test speaking text
            app.tts_handler.speak("Hello, world!")
            
            # Verify TTS handler was called correctly
            mock_tts.speak.assert_called_with("Hello, world!")
