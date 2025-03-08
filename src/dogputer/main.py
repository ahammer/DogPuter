import pygame
import os
import sys
import time
import math
import random
from dogputer.core.config import (
    INPUT_MAPPINGS, VIDEO_CHANNELS,
    SCREEN_WIDTH, SCREEN_HEIGHT, BACKGROUND_COLOR, DEFAULT_DISPLAY_TIME,
    BLUE_PRIMARY, YELLOW_PRIMARY, WHITE, LIGHT_BLUE, CREAM,
    SUCCESS_COLOR, ALERT_COLOR, ERROR_COLOR, PAW_CURSOR_SIZE
)
from dogputer.ui.video_player import VideoPlayer
from dogputer.core.tts_handler import TTSHandler
from dogputer.core.app_state import AppState, Mode
from dogputer.ui.view_state import ViewStateGenerator
from dogputer.ui.renderer import Renderer
from dogputer.ui.animation import AnimationSystem, EasingFunctions
from dogputer.ui.particle_system import ParticleSystem

class DogPuter:
    def __init__(self, config=None):
        # Store the configuration
        self.config = config or {}
        
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
        
        # Initialize input handler based on configuration
        self.input_config = {
            'input_type': 'composite',
            'use_joystick': True,
            'input_mappings': INPUT_MAPPINGS
        }
        
        # Check if x-arcade keyboard mode is being used
        if self.config.get('keymapping_name') == 'x-arcade-kb':
            self.input_config['use_xarcade'] = True
            
        from dogputer.io.input_handler import create_input_handler
        self.input_handler = create_input_handler(self.input_config)
        
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
        
        # Initialize particle system
        self.particle_system = ParticleSystem(self.screen_width, self.screen_height)
        
        # Override methods in app_state to use our implementations
        self.app_state.load_image = self.load_image
        self.app_state.play_sound = self.play_sound

    def create_paw_cursor(self):
        """Create an enhanced paw cursor for the waiting screen that's more visible to dogs"""
        size = PAW_CURSOR_SIZE  # Larger size from config
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        
        # Draw paw pad (main circle) with dog-friendly color
        pad_color = YELLOW_PRIMARY  # Dog-friendly yellow for high visibility
        outline_color = BLUE_PRIMARY  # Contrasting color for outline
        
        # Add a subtle glow effect
        glow_radius = size//2 + 10
        glow_surface = pygame.Surface((size + 20, size + 20), pygame.SRCALPHA)
        for radius in range(glow_radius, glow_radius - 10, -2):
            alpha = 100 - (glow_radius - radius) * 10
            pygame.draw.circle(
                glow_surface, 
                (*YELLOW_PRIMARY, alpha), 
                (size//2 + 10, size//2 + 10), 
                radius
            )
        
        # Draw main pad with outline
        pad_radius = size//3
        pygame.draw.circle(surface, outline_color, (size//2, size//2), pad_radius + 3)  # Outline
        pygame.draw.circle(surface, pad_color, (size//2, size//2), pad_radius)  # Main pad
        
        # Draw toe pads (smaller circles)
        pad_positions = [
            (size//2, size//4),      # Top
            (size//4, size//2),      # Left
            (3*size//4, size//2),    # Right
            (size//2, 3*size//4)     # Bottom
        ]
        
        toe_radius = size//6
        for pos in pad_positions:
            pygame.draw.circle(surface, outline_color, pos, toe_radius + 2)  # Outline
            pygame.draw.circle(surface, pad_color, pos, toe_radius)  # Toe pad
        
        # Combine the glow and the paw
        final_surface = pygame.Surface((size + 20, size + 20), pygame.SRCALPHA)
        final_surface.blit(glow_surface, (0, 0))
        final_surface.blit(surface, (10, 10))
            
        return final_surface
        
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
            
            # Get accepted keys from config (if available)
            accepted_keys_strings = self.config.get('accepted_keys', [])
            accepted_keys = []
            
            # Convert key strings to pygame key constants
            for key_str in accepted_keys_strings:
                key_constant = getattr(pygame, key_str, None)
                if key_constant is not None:
                    accepted_keys.append(key_constant)
            
            # Process input events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    # Exit on ESC key
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    # Only process keys in our accepted list if we have one
                    elif not accepted_keys or event.key in accepted_keys:
                        # Create particles on key press for visual feedback
                        x = random.randint(self.screen_width//3, 2*self.screen_width//3)
                        y = random.randint(self.screen_height//3, 2*self.screen_height//3)
                        self.particle_system.create_burst(x, y, count=15, color=YELLOW_PRIMARY)
                        self.app_state.handle_key_press(event.key)
                elif event.type == pygame.JOYBUTTONDOWN:
                    # Handle joystick button press as input
                    self.app_state.handle_key_press(pygame.K_SPACE)  # Treat as space key
            
            # Update input handler
            self.input_handler.update()
            
            # Process the events from our input handler
            events = self.input_handler.get_events()
            for event in events:
                if event.type == pygame.KEYDOWN:
                    # Only process keys that are in our accepted list if we have one
                    if not accepted_keys or event.key in accepted_keys:
                        # Create particles on key press for visual feedback
                        x = random.randint(self.screen_width//3, 2*self.screen_width//3)
                        y = random.randint(self.screen_height//3, 2*self.screen_height//3)
                        self.particle_system.create_burst(x, y, count=15, color=YELLOW_PRIMARY)
                        
                        # Handle the keypress once when the key is pressed down
                        key_name = pygame.key.name(event.key)
                        print(f"Key pressed: {key_name} (code: {event.key})")
                        
                        # Process key - handle specially for X-Arcade keys
                        if self.config.get('keymapping_name') == 'x-arcade-kb':
                            # For x-arcade-kb, if key is a mapped X-Arcade button, check the command in the mapping
                            from dogputer.core.config import INPUT_MAPPINGS
                            if event.key in INPUT_MAPPINGS:
                                # Process mapped key
                                command = INPUT_MAPPINGS[event.key]
                                print(f"Found mapping for key {key_name}: {command}")
                                
                                # Handle video commands differently
                                if command.startswith("video_"):
                                    # Extract channel from video_ prefix
                                    video_name = command[6:] # Remove "video_" prefix
                                    print(f"Selecting video: {video_name}")
                            
                            # Create a special mapping for z key to ball if in x-arcade-kb mode
                            if event.key == pygame.K_z:
                                print(f"Special mapping for X-Arcade p1_button1 (z key) -> ball")
                            
                            # Always process key for X-Arcade
                            self.app_state.handle_key_press(event.key)
                        elif event.key in INPUT_MAPPINGS:
                            # Process mapped key
                            command = INPUT_MAPPINGS[event.key]
                            print(f"Found mapping for key {key_name}: {command}")
                            
                            # Handle video commands differently
                            if command.startswith("video_"):
                                # Extract channel from video_ prefix
                                video_name = command[6:] # Remove "video_" prefix
                                print(f"Selecting video: {video_name}")
                            
                            self.app_state.handle_key_press(event.key)
                        else:
                            print(f"No mapping found for key {key_name}")
            
            # Update state
            self.app_state.update(delta_time)
            
            # Update animations
            self.animation_system.update_animations(delta_time)
            
            # Update particle system
            self.particle_system.update(delta_time)
            
            # Create ambient particles in waiting mode
            if self.app_state.mode == Mode.WAITING:
                # Add ambient particles occasionally
                if random.random() < 0.05:  # 5% chance each frame
                    self.particle_system.create_ambient(count=2, color=YELLOW_PRIMARY)
            
            # Generate view state
            view_state = self.view_state_generator.generate_view_state(self.app_state)
            
            # Render view state
            self.renderer.render(view_state)
            
            # Draw particles on top
            self.particle_system.draw(self.screen)
            
            # Update display
            pygame.display.flip()
        
        # Clean up
        self.app_state.cleanup()
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    app = DogPuter()
    app.run()
