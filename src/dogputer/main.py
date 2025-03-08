import pygame
import os
import sys
import time
import math
from dogputer.core.config import (
    KEY_MAPPINGS, VIDEO_CHANNELS, ARROW_KEY_MAPPINGS,
    SCREEN_WIDTH, SCREEN_HEIGHT, BACKGROUND_COLOR, DEFAULT_DISPLAY_TIME
)
from dogputer.ui.video_player import VideoPlayer
from dogputer.core.tts_handler import TTSHandler
from dogputer.core.app_state import AppState
from dogputer.ui.view_state import ViewStateGenerator
from dogputer.ui.renderer import Renderer
from dogputer.ui.animation import AnimationSystem, EasingFunctions

class DogPuter:
    def __init__(self):
        # Initialize pygame
        pygame.init()
        pygame.mixer.init()
        
        # Set up display
        self.screen_width = SCREEN_WIDTH
        self.screen_height = SCREEN_HEIGHT
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("DogPuter")
        
        # Set up directories
        self.sounds_dir = "sounds"
        self.images_dir = "images"
        self.videos_dir = "videos"
        
        # Create directories if they don't exist
        os.makedirs(self.sounds_dir, exist_ok=True)
        os.makedirs(self.images_dir, exist_ok=True)
        os.makedirs(self.videos_dir, exist_ok=True)
        
        # Initialize joystick
        self.joystick = None
        if pygame.joystick.get_count() > 0:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
            print(f"Joystick detected: {self.joystick.get_name()}")
        
        # Initialize video player
        self.video_player = VideoPlayer(self.screen, self.videos_dir)
        
        # Initialize text-to-speech handler
        self.tts_handler = TTSHandler()
        
        # Create fonts
        self.font = pygame.font.SysFont(None, 48)
        self.feedback_font = pygame.font.SysFont(None, 36)
        
        # Create paw cursor image
        self.paw_cursor = self.create_paw_cursor()
        
        # Initialize application state
        self.app_state = AppState(
            self.video_player,
            self.tts_handler,
            BACKGROUND_COLOR,
            self.font,
            self.feedback_font,
            self.screen_width,
            self.screen_height
        )
        self.app_state.paw_cursor = self.paw_cursor
        
        # Initialize view state generator
        self.view_state_generator = ViewStateGenerator(
            self.screen_width,
            self.screen_height
        )
        
        # Initialize renderer
        self.renderer = Renderer(self.screen)
        
        # Initialize animation system
        self.animation_system = AnimationSystem()
        
        # Override methods in app_state to use our implementations
        self.app_state.load_image = self.load_image
        self.app_state.play_sound = self.play_sound

    def create_paw_cursor(self):
        """Create a simple paw cursor for the waiting screen"""
        size = 80
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        
        # Draw paw pad (main circle)
        pygame.draw.circle(surface, (200, 200, 200), (size//2, size//2), size//3)
        
        # Draw toe pads (smaller circles)
        pad_positions = [
            (size//2, size//4),  # Top
            (size//4, size//2),  # Left
            (3*size//4, size//2),  # Right
            (size//2, 3*size//4)  # Bottom
        ]
        
        for pos in pad_positions:
            pygame.draw.circle(surface, (200, 200, 200), pos, size//6)
            
        return surface
        
    def load_image(self, image_name):
        """Load an image from the images directory"""
        try:
            image_path = os.path.join(self.images_dir, image_name)
            image = pygame.image.load(image_path)
            return pygame.transform.scale(image, (self.screen_width, self.screen_height))
        except pygame.error:
            print(f"Could not load image: {image_name}")
            return None

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
            
            # Process input events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    # Exit on ESC key
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    else:
                        self.app_state.handle_key_press(event.key)
                elif event.type == pygame.JOYBUTTONDOWN:
                    # Handle joystick button press as input
                    self.app_state.handle_key_press(pygame.K_SPACE)  # Treat as space key
            
            # Handle continuous joystick input
            if self.joystick:
                self.app_state.handle_joystick(self.joystick)
            
            # Update state
            self.app_state.update(delta_time)
            
            # Update animations
            self.animation_system.update_animations(delta_time)
            
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
    app = DogPuter()
    app.run()
