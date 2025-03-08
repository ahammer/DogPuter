#!/usr/bin/env python3
"""
Test fixtures for DogPuter tests
"""

import os
import sys
import pytest
import pygame
import threading
import time
from unittest.mock import MagicMock, patch

# Add src directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

# Pygame initialization for tests
@pytest.fixture(scope="session", autouse=True)
def pygame_init():
    """Initialize pygame for tests"""
    pygame.init()
    pygame.mixer.init()
    yield
    pygame.quit()

# Mock display for UI tests
@pytest.fixture
def mock_display():
    """Create a mock display surface for testing"""
    original_set_mode = pygame.display.set_mode
    
    # Create a mock surface
    mock_surface = pygame.Surface((800, 600))
    
    # Mock the set_mode function
    def mock_set_mode(size, flags=0, depth=0, display=0):
        return mock_surface
    
    # Apply patch
    with patch('pygame.display.set_mode', side_effect=mock_set_mode):
        yield mock_surface

# Mock input handler
@pytest.fixture
def mock_input():
    """Create a mock input handler for testing"""
    class MockInput:
        def __init__(self):
            self.events = []
            self.key_state = {}
        
        def add_event(self, event):
            """Add an event to the queue"""
            self.events.append(event)
        
        def simulate_key_press(self, key):
            """Simulate a key press event"""
            event = MagicMock()
            event.type = pygame.KEYDOWN
            event.key = key
            self.events.append(event)
            self.key_state[key] = True
        
        def simulate_key_release(self, key):
            """Simulate a key release event"""
            event = MagicMock()
            event.type = pygame.KEYUP
            event.key = key
            self.events.append(event)
            self.key_state[key] = False
        
        def is_key_pressed(self, key):
            """Check if a key is pressed"""
            return self.key_state.get(key, False)
        
        def get_events(self):
            """Get all pending events and clear the queue"""
            events = self.events.copy()
            self.events.clear()
            return events
    
    return MockInput()

# TTS Handler mock
@pytest.fixture
def mock_tts():
    """Create a mock TTS handler for testing"""
    mock = MagicMock()
    mock.speak = MagicMock()
    mock.stop = MagicMock()
    mock.speaking = False
    return mock

# Video Player mock
@pytest.fixture
def mock_video_player():
    """Create a mock video player for testing"""
    mock = MagicMock()
    mock.play_video = MagicMock(return_value=True)
    mock.stop = MagicMock()
    mock.pause = MagicMock()
    mock.resume = MagicMock()
    mock.toggle_pause = MagicMock()
    mock.update = MagicMock(return_value=(pygame.Surface((800, 600)), False))
    return mock

# Helper utilities for UI testing
@pytest.fixture
def ui_test_helpers():
    """Helper functions for UI testing"""
    class UITestHelpers:
        @staticmethod
        def capture_surface(surface):
            """Capture surface for comparison"""
            return pygame.surfarray.array3d(surface).copy()
        
        @staticmethod
        def surfaces_differ(surface1, surface2, threshold=0.05):
            """Compare two surfaces and return True if they differ significantly"""
            if surface1.get_size() != surface2.get_size():
                return True
                
            array1 = pygame.surfarray.array3d(surface1)
            array2 = pygame.surfarray.array3d(surface2)
            
            diff = abs(array1.astype(float) - array2.astype(float))
            total_pixels = array1.size / 3
            changed_pixels = (diff > 10).sum() / 3
            
            return changed_pixels / total_pixels > threshold
        
        @staticmethod
        def wait_for_render(app, timeout=1.0):
            """Wait for a render cycle to complete"""
            start_time = time.time()
            while time.time() - start_time < timeout:
                # Allow a short delay for rendering
                time.sleep(0.05)
                
                # Check if we've reached the timeout
                if time.time() - start_time >= timeout:
                    raise TimeoutError("Timed out waiting for render")
    
    return UITestHelpers()
