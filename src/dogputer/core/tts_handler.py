#!/usr/bin/env python3
"""
Text-to-speech handler module for DogPuter
This module provides text-to-speech functionality using pyttsx3.
"""

import threading
import time

class TTSHandler:
    """Text-to-speech handler class for DogPuter"""
    
    def __init__(self, use_pyttsx3=True):
        """Initialize the TTS handler"""
        self.use_pyttsx3 = use_pyttsx3
        self.engine = None
        self.speaking = False
        
        if self.use_pyttsx3:
            try:
                import pyttsx3
                self.engine = pyttsx3.init()
                # Set properties (optional)
                self.engine.setProperty('rate', 150)  # Speed of speech
                self.engine.setProperty('volume', 1.0)  # Volume (0.0 to 1.0)
                print("TTS engine initialized using pyttsx3")
            except ImportError:
                print("pyttsx3 not found. Falling back to built-in TTS.")
                self.use_pyttsx3 = False
        
        if not self.use_pyttsx3:
            # Fallback to pygame's built-in speech module if available
            try:
                import pygame.freetype
                self.use_pygame = True
                print("TTS engine initialized using pygame")
            except (ImportError, AttributeError):
                print("No TTS engine available. Speech functionality disabled.")
                self.use_pygame = False
    
    def speak(self, text):
        """Speak the given text"""
        if not text:
            return
            
        # Don't start a new speech if already speaking
        if self.speaking:
            return
            
        # Start speech in a separate thread to avoid blocking
        thread = threading.Thread(target=self._speak_thread, args=(text,))
        thread.daemon = True
        thread.start()
    
    def _speak_thread(self, text):
        """Thread function for speaking text"""
        self.speaking = True
        
        try:
            if self.use_pyttsx3 and self.engine:
                self.engine.say(text)
                self.engine.runAndWait()
            elif hasattr(self, 'use_pygame') and self.use_pygame:
                # Simple visual text display as fallback
                print(f"Speaking: {text}")
                # Simulate speech duration
                time.sleep(len(text) * 0.1)
            else:
                # Just print the text if no TTS engine is available
                print(f"Would speak: {text}")
        except Exception as e:
            print(f"Error in TTS: {e}")
        
        self.speaking = False
    
    def stop(self):
        """Stop any ongoing speech"""
        if self.use_pyttsx3 and self.engine:
            self.engine.stop()
        self.speaking = False

# Test function
def main():
    """Test the TTS handler"""
    tts = TTSHandler()
    test_phrases = [
        "play",
        "rope",
        "ball",
        "treat",
        "outside",
        "walk"
    ]
    
    for phrase in test_phrases:
        print(f"Testing TTS with phrase: {phrase}")
        tts.speak(phrase)
        time.sleep(2)  # Wait for speech to complete
    
    print("TTS test complete")

if __name__ == "__main__":
    main()
