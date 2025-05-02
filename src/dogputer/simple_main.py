#!/usr/bin/env python3
"""
Simplified DogPuter main application module.
This version focuses on performance optimization by removing animations and compositions.
Only the core button->video functionality remains.
"""

import pygame
import os
import sys
import time
from dogputer.core.config import (
    INPUT_MAPPINGS, SCREEN_WIDTH, SCREEN_HEIGHT, BACKGROUND_COLOR
)
from dogputer.core.commands import ExitCommand
from dogputer.core.app_state_simple import AppState, Mode
from dogputer.ui.video_player_simple import VideoPlayer
from dogputer.ui.view_state_simple import ViewStateGenerator
from dogputer.ui.renderer_simple import Renderer

class SimpleDogPuter:
    """Simplified DogPuter application for performance optimization"""
    
    def __init__(self, fullscreen=False):
        """Initialize the DogPuter application"""
        # Initialize pygame
        pygame.init()
        pygame.mixer.init()
        
        # Set up display
        self.screen_width = SCREEN_WIDTH
        self.screen_height = SCREEN_HEIGHT
        
        # Set fullscreen mode if requested
        display_flags = pygame.FULLSCREEN if fullscreen else 0
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height), display_flags)
        pygame.display.set_caption("DogPuter Simplified")
        
        # Set up directories
        self.sounds_dir = "media/sounds"
        self.videos_dir = "media/videos"
        
        # Create directories if they don't exist
        os.makedirs(self.sounds_dir, exist_ok=True)
        os.makedirs(self.videos_dir, exist_ok=True)
        
        # Initialize input handler
        self.input_config = {'input_mappings': INPUT_MAPPINGS}
        
        from dogputer.io.input_handler import create_input_handler
        self.input_handler = create_input_handler(self.input_config)
        
        # Initialize video player
        self.video_player = VideoPlayer(self.screen, self.videos_dir)
        
        # Create font
        self.font = pygame.font.SysFont(None, 48)
        
        # Initialize application state
        self.app_state = AppState(
            self.video_player,
            None,  # No TTS handler
            BACKGROUND_COLOR,
            self.font,
            self.font,  # Same font for feedback
            self.screen_width,
            self.screen_height
        )
        
        # Initialize view state generator
        self.view_state_generator = ViewStateGenerator(
            self.screen_width,
            self.screen_height
        )
        
        # Initialize renderer
        self.renderer = Renderer(self.screen)
        
        # Override methods in app_state to use our implementations
        self.app_state.play_sound = self.play_sound
    
    def play_sound(self, sound_name):
        """Play a sound from the sounds directory"""
        try:
            sound_path = os.path.join(self.sounds_dir, sound_name)
            sound = pygame.mixer.Sound(sound_path)
            sound.play()
        except pygame.error:
            print(f"Could not play sound: {sound_name}")
    
    def run(self):
        """Main game loop"""
        running = True
        clock = pygame.time.Clock()
        
        while running:
            # Calculate delta time
            delta_time = clock.tick(60) / 1000.0  # Convert to seconds
            
            # Handle quit events directly from pygame
            for event in pygame.event.get([pygame.QUIT]):
                if event.type == pygame.QUIT:
                    running = False
            
            # Update input handler
            self.input_handler.update()
            
            # Get and process commands from our input handler
            commands = self.input_handler.get_commands()
            for command in commands:
                # Process the command
                print(f"Processing command: {command}")
                # Handle exit command specially
                if isinstance(command, ExitCommand):
                    running = False
                else:
                    # Pass other commands to app state
                    self.app_state.handle_command(command)
            
            # Also process raw events for backward compatibility
            events = self.input_handler.get_events()
            for event in events:
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    # Exit on ESC key
                    running = False
            
            # Update state
            self.app_state.update(delta_time)
            
            # Generate view state
            view_state = self.view_state_generator.generate_view_state(self.app_state)
            
            # Render view state
            self.renderer.render(view_state)
            
            # Update display
            pygame.display.flip()
        
        # Clean up
        self.app_state.cleanup()
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    app = SimpleDogPuter(fullscreen=False)
    app.run()
