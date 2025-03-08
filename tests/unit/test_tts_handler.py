#!/usr/bin/env python3
"""
Unit tests for the TTSHandler class
"""

import unittest
from unittest.mock import patch, MagicMock
import threading
import time
from tts_handler import TTSHandler

def raise_import_error(name, *args):
    """Helper function to raise ImportError for specific modules"""
    raise ImportError(f"Mock ImportError for {name}")

class TestTTSHandler(unittest.TestCase):
    """Test cases for the TTSHandler class"""

    @patch('pyttsx3.init')
    def test_init_with_pyttsx3(self, mock_pyttsx3):
        """Test initialization with pyttsx3"""
        # Setup mock
        mock_engine = MagicMock()
        mock_pyttsx3.init.return_value = mock_engine

        # Create instance
        tts = TTSHandler(use_pyttsx3=True)

        # Verify
        mock_pyttsx3.init.assert_called_once()
        mock_engine.setProperty.assert_any_call('rate', 150)
        mock_engine.setProperty.assert_any_call('volume', 1.0)
        self.assertEqual(tts.use_pyttsx3, True)
        self.assertEqual(tts.speaking, False)
        self.assertEqual(tts.engine, mock_engine)

    def test_init_pyttsx3_import_error(self):
        """Test initialization when pyttsx3 raises ImportError"""
        # Setup mock to raise ImportError
        with patch('builtins.__import__', side_effect=lambda name, *args: 
                   raise_import_error(name, *args) if name == 'pyttsx3' else __import__(name, *args)):
            # Create instance with print mock
            with patch('builtins.print') as mock_print:
                tts = TTSHandler(use_pyttsx3=True)
                
                # Verify fallback behavior
                self.assertEqual(tts.use_pyttsx3, False)
                mock_print.assert_any_call("pyttsx3 not found. Falling back to built-in TTS.")


    @patch('pygame.freetype')
    def test_init_with_pygame_fallback(self, mock_pygame):
        """Test initialization with pygame fallback"""
        # Create instance with pyttsx3 disabled
        with patch('builtins.print') as mock_print:
            tts = TTSHandler(use_pyttsx3=False)

        # Verify
        self.assertEqual(tts.use_pyttsx3, False)
        self.assertEqual(tts.use_pygame, True)
        mock_print.assert_called_with("TTS engine initialized using pygame")

    def test_init_pygame_import_error(self):
        """Test initialization when both pyttsx3 and pygame are unavailable"""
        # Setup mock to raise ImportError
        with patch('builtins.__import__', side_effect=lambda name, *args: 
                   raise_import_error(name, *args) if name == 'pygame' else __import__(name, *args)):
            # Create instance with pyttsx3 disabled and print mock
            with patch('builtins.print') as mock_print:
                tts = TTSHandler(use_pyttsx3=False)
                
                # Verify fallback behavior
                self.assertEqual(tts.use_pyttsx3, False)
                self.assertEqual(hasattr(tts, 'use_pygame'), True)
                self.assertEqual(tts.use_pygame, False)
                mock_print.assert_called_with("No TTS engine available. Speech functionality disabled.")


    @patch('pyttsx3.init')
    def test_speak_empty_text(self, mock_pyttsx3):
        """Test speak with empty text"""
        # Setup
        mock_engine = MagicMock()
        mock_pyttsx3.init.return_value = mock_engine
        tts = TTSHandler()

        # Call with empty text
        tts.speak("")

        # Verify no thread started
        mock_engine.say.assert_not_called()
        self.assertEqual(tts.speaking, False)

    @patch('pyttsx3.init')
    def test_speak_already_speaking(self, mock_pyttsx3):
        """Test speak when already speaking"""
        # Setup
        mock_engine = MagicMock()
        mock_pyttsx3.init.return_value = mock_engine
        tts = TTSHandler()
        tts.speaking = True  # Set as already speaking

        # Call
        tts.speak("Hello")

        # Verify no new speech started
        mock_engine.say.assert_not_called()

    @patch('pyttsx3.init')
    def test_speak_with_pyttsx3(self, mock_pyttsx3):
        """Test speak with pyttsx3"""
        # Setup
        mock_engine = MagicMock()
        mock_pyttsx3.init.return_value = mock_engine
        tts = TTSHandler()

        # Mock threading.Thread to capture the target function and args
        with patch('threading.Thread', autospec=True) as mock_thread:
            mock_thread_instance = MagicMock()
            mock_thread.return_value = mock_thread_instance
            
            # Call
            tts.speak("Hello")
            
            # Verify thread created and started
            mock_thread.assert_called_once()
            args, kwargs = mock_thread.call_args
            self.assertEqual(kwargs['target'], tts._speak_thread)
            self.assertEqual(kwargs['args'], ("Hello",))
            self.assertEqual(kwargs['daemon'], True)
            mock_thread_instance.start.assert_called_once()

    @patch('pyttsx3.init')
    def test_speak_thread_with_pyttsx3(self, mock_pyttsx3):
        """Test _speak_thread with pyttsx3"""
        # Setup
        mock_engine = MagicMock()
        mock_pyttsx3.init.return_value = mock_engine
        tts = TTSHandler()

        # Call
        tts._speak_thread("Hello")

        # Verify
        mock_engine.say.assert_called_once_with("Hello")
        mock_engine.runAndWait.assert_called_once()
        self.assertEqual(tts.speaking, False)  # Should reset to False after speaking

    @patch('pygame.freetype')
    def test_speak_thread_with_pygame(self, mock_pygame):
        """Test _speak_thread with pygame fallback"""
        # Setup
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
        tts = TTSHandler(use_pyttsx3=False)
        tts.use_pygame = False

        # Call
        with patch('builtins.print') as mock_print:
            tts._speak_thread("Hello")

        # Verify
        mock_print.assert_called_with("Would speak: Hello")
        self.assertEqual(tts.speaking, False)  # Should reset to False after speaking

    @patch('pyttsx3.init')
    def test_speak_thread_exception(self, mock_pyttsx3):
        """Test _speak_thread handling exceptions"""
        # Setup
        mock_engine = MagicMock()
        mock_engine.say.side_effect = Exception("Test exception")
        mock_pyttsx3.init.return_value = mock_engine
        tts = TTSHandler()

        # Call
        with patch('builtins.print') as mock_print:
            tts._speak_thread("Hello")

        # Verify
        mock_print.assert_called_with("Error in TTS: Test exception")
        self.assertEqual(tts.speaking, False)  # Should reset to False after exception

    @patch('pyttsx3.init')
    def test_stop(self, mock_pyttsx3):
        """Test stop method"""
        # Setup
        mock_engine = MagicMock()
        mock_pyttsx3.init.return_value = mock_engine
        tts = TTSHandler()
        tts.speaking = True

        # Call
        tts.stop()

        # Verify
        mock_engine.stop.assert_called_once()
        self.assertEqual(tts.speaking, False)

if __name__ == '__main__':
    unittest.main()
