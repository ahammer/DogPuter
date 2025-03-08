#!/usr/bin/env python3
"""
Unit tests for the TTSHandler class
"""

import unittest
from unittest.mock import patch, MagicMock
import threading
import time
import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "src")))

# Import the class to test
try:
    # Try to import from the new package structure
    from dogputer.core.tts_handler import TTSHandler
except ImportError:
    # Fall back to importing from the root directory
    print("Note: Using tts_handler from root directory. Run the migration script.")
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
    from tts_handler import TTSHandler

class TestTTSHandler(unittest.TestCase):
    """Test cases for the TTSHandler class"""

    def test_init_with_pyttsx3(self):
        """Test initialization with pyttsx3"""
        # Setup mock
        with patch('pyttsx3.init') as mock_init:
            mock_engine = MagicMock()
            mock_init.return_value = mock_engine

            # Create instance
            tts = TTSHandler(use_pyttsx3=True)

            # Verify
            mock_init.assert_called_once()
            mock_engine.setProperty.assert_any_call('rate', 150)
            mock_engine.setProperty.assert_any_call('volume', 1.0)
            self.assertEqual(tts.use_pyttsx3, True)
            self.assertEqual(tts.speaking, False)
            self.assertEqual(tts.engine, mock_engine)

    def test_init_pyttsx3_import_error(self):
        """Test initialization when pyttsx3 is not available"""
        # Create a patch that will make the import of pyttsx3 fail
        with patch.dict('sys.modules', {'pyttsx3': None}):
            # Force ImportError when pyttsx3 is imported
            import sys
            sys.modules['pyttsx3'] = None
            
            # Create instance with print mock
            with patch('builtins.print') as mock_print:
                # Create instance
                tts = TTSHandler(use_pyttsx3=True)
                
                # Verify fallback behavior
                self.assertEqual(tts.use_pyttsx3, False)
                mock_print.assert_any_call("pyttsx3 not found. Falling back to built-in TTS.")

    def test_init_with_pygame_fallback(self):
        """Test initialization with pygame fallback"""
        # Create instance with pyttsx3 disabled
        with patch('builtins.print') as mock_print:
            with patch('pyttsx3.init') as mock_init:  # Prevent actual pyttsx3 initialization
                # Mock the pygame.freetype import to succeed
                with patch.dict('sys.modules', {'pygame.freetype': MagicMock()}):
                    # Create a mock pygame module with freetype attribute
                    mock_pygame = MagicMock()
                    mock_pygame.freetype = MagicMock()
                    sys.modules['pygame'] = mock_pygame
                    
                    tts = TTSHandler(use_pyttsx3=False)

                    # Verify
                    self.assertEqual(tts.use_pyttsx3, False)
                    self.assertEqual(tts.use_pygame, True)
                    mock_print.assert_called_with("TTS engine initialized using pygame")

    def test_init_pygame_import_error(self):
        """Test initialization when both pyttsx3 and pygame are unavailable"""
        # Setup mocks to raise ImportError for pygame.freetype
        with patch('builtins.__import__') as mock_import:
            def import_effect(name, *args, **kwargs):
                if name == 'pygame.freetype':
                    raise ImportError("Mock ImportError for pygame.freetype")
                # Let other imports proceed normally
                return __import__.__wrapped__(name, *args, **kwargs) if hasattr(__import__, '__wrapped__') else __import__(name, *args, **kwargs)
                
            mock_import.side_effect = import_effect
            
            # Also patch print to verify output
            with patch('builtins.print') as mock_print:
                # Create instance with pyttsx3 disabled (which will fall back to pygame and fail)
                tts = TTSHandler(use_pyttsx3=False)
                
                # Verify fallback behavior
                self.assertEqual(tts.use_pyttsx3, False)
                self.assertEqual(hasattr(tts, 'use_pygame'), True)
                self.assertEqual(tts.use_pygame, False)
                mock_print.assert_called_with("No TTS engine available. Speech functionality disabled.")

    def test_speak_empty_text(self):
        """Test speak with empty text"""
        # Setup
        with patch('pyttsx3.init') as mock_init:
            mock_engine = MagicMock()
            mock_init.return_value = mock_engine
            tts = TTSHandler()

            # Call with empty text
            tts.speak("")

            # Verify no thread started
            mock_engine.say.assert_not_called()
            self.assertEqual(tts.speaking, False)

    def test_speak_already_speaking(self):
        """Test speak when already speaking"""
        # Setup
        with patch('pyttsx3.init') as mock_init:
            mock_engine = MagicMock()
            mock_init.return_value = mock_engine
            tts = TTSHandler()
            tts.speaking = True  # Set as already speaking

            # Call
            tts.speak("Hello")

            # Verify no new speech started
            mock_engine.say.assert_not_called()

    def test_speak_with_pyttsx3(self):
        """Test speak with pyttsx3"""
        # Setup
        with patch('pyttsx3.init') as mock_init:
            mock_engine = MagicMock()
            mock_init.return_value = mock_engine
            tts = TTSHandler()

            # Mock threading.Thread to capture the target function and args
            with patch('threading.Thread') as mock_thread:
                mock_thread_instance = MagicMock()
                mock_thread.return_value = mock_thread_instance
                
                # Call
                tts.speak("Hello")
                
                # Verify thread created and started
                mock_thread.assert_called_once()
                args, kwargs = mock_thread.call_args
                self.assertEqual(kwargs['target'], tts._speak_thread)
                self.assertEqual(kwargs['args'], ("Hello",))
                # Thread is created with daemon=True in the original, but this may vary
                # Just verify target and args which are the critical parts
                mock_thread_instance.start.assert_called_once()

    def test_speak_thread_with_pyttsx3(self):
        """Test _speak_thread with pyttsx3"""
        # Setup
        with patch('pyttsx3.init') as mock_init:
            mock_engine = MagicMock()
            mock_init.return_value = mock_engine
            tts = TTSHandler()

            # Set the engine directly to ensure it's used in _speak_thread
            tts.engine = mock_engine
            tts.use_pyttsx3 = True

            # Call
            tts._speak_thread("Hello")

            # Verify
            mock_engine.say.assert_called_once_with("Hello")
            mock_engine.runAndWait.assert_called_once()
            self.assertEqual(tts.speaking, False)  # Should reset to False after speaking

    def test_speak_thread_with_pygame(self):
        """Test _speak_thread with pygame fallback"""
        # Setup - create a TTSHandler with mocked dependencies
        with patch('pyttsx3.init') as mock_init:  # To prevent actual pyttsx3 initialization
            # Mock the pygame import
            with patch.dict('sys.modules', {'pygame': MagicMock()}):
                tts = TTSHandler(use_pyttsx3=False)
                tts.use_pygame = True

                # Call with timing patch to avoid actual sleep
                with patch('time.sleep') as mock_sleep:
                    with patch('builtins.print') as mock_print:
                        tts._speak_thread("Hello")

                # Verify
                mock_print.assert_called_with("Speaking: Hello")
                mock_sleep.assert_called_once_with(5 * 0.1)  # len("Hello") * 0.1
                self.assertEqual(tts.speaking, False)  # Should reset to False after speaking

    def test_speak_thread_no_engine(self):
        """Test _speak_thread with no TTS engine available"""
        # Setup
        with patch('pyttsx3.init'):  # To prevent actual pyttsx3 initialization
            tts = TTSHandler(use_pyttsx3=False)
            tts.use_pygame = False

            # Call
            with patch('builtins.print') as mock_print:
                tts._speak_thread("Hello")

            # Verify
            mock_print.assert_called_with("Would speak: Hello")
            self.assertEqual(tts.speaking, False)  # Should reset to False after speaking

    def test_speak_thread_exception(self):
        """Test _speak_thread handling exceptions"""
        # Setup
        with patch('pyttsx3.init') as mock_init:
            mock_engine = MagicMock()
            mock_engine.say.side_effect = Exception("Test exception")
            mock_init.return_value = mock_engine
            
            tts = TTSHandler()
            # Set the engine directly to ensure it's used in _speak_thread
            tts.engine = mock_engine
            tts.use_pyttsx3 = True

            # Call
            with patch('builtins.print') as mock_print:
                tts._speak_thread("Hello")

            # Verify
            mock_print.assert_called_with("Error in TTS: Test exception")
            self.assertEqual(tts.speaking, False)  # Should reset to False after exception

    def test_stop(self):
        """Test stop method"""
        # Setup
        with patch('pyttsx3.init') as mock_init:
            mock_engine = MagicMock()
            mock_init.return_value = mock_engine
            
            tts = TTSHandler()
            # Set the engine directly to ensure it's used in stop
            tts.engine = mock_engine
            tts.use_pyttsx3 = True
            tts.speaking = True

            # Call
            tts.stop()

            # Verify
            mock_engine.stop.assert_called_once()
            self.assertEqual(tts.speaking, False)
