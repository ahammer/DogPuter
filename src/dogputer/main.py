import pygame
import os
import sys
import time
import math
import random
import threading
from dogputer.core.config import (
    INPUT_MAPPINGS, VIDEO_CHANNELS,
    SCREEN_WIDTH, SCREEN_HEIGHT, BACKGROUND_COLOR, DEFAULT_DISPLAY_TIME,
    BLUE_PRIMARY, YELLOW_PRIMARY, WHITE, LIGHT_BLUE, CREAM,
    SUCCESS_COLOR, ALERT_COLOR, ERROR_COLOR, PAW_CURSOR_SIZE
)
from dogputer.core.commands import ExitCommand
from dogputer.ui.video_player import VideoPlayer
from dogputer.core.tts_handler import TTSHandler
from dogputer.core.app_state import AppState, Mode
from dogputer.ui.view_state import ViewStateGenerator
from dogputer.ui.renderer import Renderer
from dogputer.ui.animation import AnimationSystem, EasingFunctions
from dogputer.ui.particle_system import ParticleSystem

# Try to import web interface components, but don't fail if they're not available
WEB_INTERFACE_AVAILABLE = False
try:
    from dogputer.web.app import start_web_server_thread, has_config_changed, get_current_mappings
    from dogputer.web.qr_code import get_local_ip, generate_qr_code
    WEB_INTERFACE_AVAILABLE = True
except ImportError:
    print("Web interface dependencies not available. Web interface will be disabled.")

class DogPuter:
    def __init__(self, config=None):
        # Store the configuration
        self.config = config or {}
        
        # Initialize pygame
        pygame.init()
        pygame.mixer.init()
        
        # Initialize web interface if available
        self.web_interface_enabled = WEB_INTERFACE_AVAILABLE
        if self.web_interface_enabled:
            try:
                self.web_server_port = 5000
                self.ip_address = get_local_ip()
                self.web_url = f"http://{self.ip_address}:{self.web_server_port}"
                print(f"Starting web interface at {self.web_url}")
                self.web_server_thread = start_web_server_thread(port=self.web_server_port)
            except Exception as e:
                print(f"Failed to start web interface: {e}")
                self.web_interface_enabled = False
        
        # Set up display
        self.screen_width = SCREEN_WIDTH
        self.screen_height = SCREEN_HEIGHT
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))

        pygame.display.set_caption("DogPuter")
        
        # Set up directories
        self.sounds_dir = "media/sounds"
        self.images_dir = "media/images"
        self.videos_dir = "media/videos"
        
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
            
        # Store keymapping name for later config checks
        print(f"Config keymapping_name: {self.config.get('keymapping_name')}")
        self.keymapping_name = 'development.json'  # Always set a default
        
        if self.config.get('keymapping_name'):
            km_name = self.config.get('keymapping_name')
            if isinstance(km_name, str):
                self.keymapping_name = km_name if km_name.endswith('.json') else f"{km_name}.json"
                print(f"Using keymapping file: {self.keymapping_name}")
        
        # Track last config check time
        self.last_config_check = time.time()
        self.config_check_interval = 2.0  # Check every 2 seconds
        
        from dogputer.io.input_handler import create_input_handler
        self.input_handler = create_input_handler(self.input_config)
        
        # Initialize video player
        self.video_player = VideoPlayer(self.screen, self.videos_dir)
        
        # Initialize text-to-speech handler
        self.tts_handler = TTSHandler()
        
        # Create fonts
        self.font = pygame.font.SysFont(None, 48)
        self.feedback_font = pygame.font.SysFont(None, 36)
        self.small_font = pygame.font.SysFont(None, 24)
        
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
        
        # Generate QR code for web interface if available
        self.qr_code = None
        self.qr_available = False
        self.show_qr_code = False
        self.last_qr_toggle_time = 0
        
        if self.web_interface_enabled:
            try:
                self.qr_code = generate_qr_code(self.web_url, size=120)
                self.qr_available = True
            except Exception as e:
                print(f"QR code generation failed: {e}")
        
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
            
    def render_web_interface_info(self):
        """Render the web interface IP and QR code in the corner of the screen"""
        if not self.web_interface_enabled:
            return
        
        # Only show the QR code in waiting mode
        show_qr = self.app_state.mode == Mode.WAITING
        
        # Create a semi-transparent background for better readability
        margin = 10
        
        # Render IP text
        ip_text = self.small_font.render(f"Web: {self.web_url}", True, WHITE)
        text_pos = (self.screen_width - ip_text.get_width() - margin, 
                    self.screen_height - ip_text.get_height() - margin)
        
        # Create background rect
        bg_rect = pygame.Rect(
            text_pos[0] - 5, 
            text_pos[1] - 5,
            ip_text.get_width() + 10,
            ip_text.get_height() + 10
        )
        
        # Draw background
        bg_surface = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
        bg_surface.fill((0, 0, 0, 180))  # Semi-transparent black
        self.screen.blit(bg_surface, (bg_rect.x, bg_rect.y))
        
        # Draw text
        self.screen.blit(ip_text, text_pos)
        
        # Show QR code if in waiting mode and available
        if show_qr and self.qr_code and self.qr_available:
            qr_size = self.qr_code.get_size()
            qr_pos = (
                self.screen_width - qr_size[0] - margin,
                self.screen_height - qr_size[1] - ip_text.get_height() - margin*2
            )
            
            # Draw QR code directly without additional background
            # Just draw it to the screen since it already has the margins
            self.screen.blit(self.qr_code, qr_pos)

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
            
            # Handle quit events directly from pygame to ensure they always work
            for event in pygame.event.get([pygame.QUIT]):
                if event.type == pygame.QUIT:
                    running = False
            
            # Update input handler
            self.input_handler.update()
            
            # Get and process commands from our input handler
            commands = self.input_handler.get_commands()
            for command in commands:
                # Create particles for visual feedback when a command is received
                x = random.randint(self.screen_width//3, 2*self.screen_width//3)
                y = random.randint(self.screen_height//3, 2*self.screen_height//3)
                self.particle_system.create_burst(x, y, count=15, color=YELLOW_PRIMARY)
                
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
            
            # Check for configuration changes if web interface is enabled
            current_time = time.time()
            if self.web_interface_enabled and current_time - self.last_config_check > self.config_check_interval:
                self.last_config_check = current_time
                if has_config_changed():
                    print("Configuration changed, reloading input mappings...")
                    new_mappings = get_current_mappings(self.keymapping_name)
                    if new_mappings:
                        # Update the input handler with new mappings
                        self.input_config['input_mappings'] = new_mappings
                        self.input_handler.update_mappings(new_mappings)
                        print("Input mappings reloaded successfully")
            
            # Update state
            self.app_state.update(delta_time)
            
            # Update animations
            self.animation_system.update_animations(delta_time)
            
            # Update particle system
            self.particle_system.update(delta_time)
            
            # Create ambient particles in waiting mode with a more soothing pattern
            if self.app_state.mode == Mode.WAITING:
                # Lower the frequency for a more subtle effect
                if random.random() < 0.02:  # 2% chance each frame instead of 5%
                    # Use current time to create slowly flowing particle patterns
                    current_time = time.time()
                    
                    # Determine which region of the screen to create particles in
                    # Shift this gradually over time for a floating, gentle effect
                    region_shift_x = math.sin(current_time * 0.1) * 0.3
                    region_shift_y = math.cos(current_time * 0.08) * 0.2
                    
                    region_x = self.screen_width * (0.5 + region_shift_x)
                    region_y = self.screen_height * (0.5 + region_shift_y)
                    region_width = self.screen_width * 0.4
                    region_height = self.screen_height * 0.4
                    
                    region = pygame.Rect(
                        region_x - region_width/2,
                        region_y - region_height/2,
                        region_width,
                        region_height
                    )
                    
                    # Create more subtle particles with a softer appearance
                    # Use primarily white/blue-tinted colors for a calming effect
                    # Choose color based on the current time for a gentle shifting effect
                    color_shift = (math.sin(current_time * 0.2) + 1) / 2  # 0 to 1
                    
                    if color_shift > 0.7:  # Occasionally use yellow for visual interest
                        particle_color = YELLOW_PRIMARY
                    else:  # Mostly use soft blue-white
                        r = int(220 + color_shift * 35)
                        g = int(220 + color_shift * 35)
                        b = int(240 + color_shift * 15)
                        particle_color = (r, g, b)
                    
                    # Create particles with longer minimum lifetime for more soothing flow
                    self.particle_system.create_ambient(
                        region_rect=region,
                        count=3,  # Slightly more particles per batch
                        color=particle_color,
                        gravity=-0.1,  # Slight upward drift
                        min_lifetime=1.5,  # Longer lifetime
                        max_lifetime=3.0  # Longer max lifetime
                    )
            
            # Generate view state
            view_state = self.view_state_generator.generate_view_state(self.app_state)
            
            # Render view state
            self.renderer.render(view_state)
            
            # Draw particles on top
            self.particle_system.draw(self.screen)
            
            # Render web interface info if enabled
            if self.web_interface_enabled:
                self.render_web_interface_info()
            
            # Update display
            pygame.display.flip()
        
        # Clean up
        self.app_state.cleanup()
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    app = DogPuter()
    app.run()
