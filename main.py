import pygame
import os
import sys
import time
import math
from config import (
    KEY_MAPPINGS, VIDEO_CHANNELS, ARROW_KEY_MAPPINGS,
    SCREEN_WIDTH, SCREEN_HEIGHT, BACKGROUND_COLOR, DEFAULT_DISPLAY_TIME
)
from video_player import VideoPlayer
from tts_handler import TTSHandler

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
        
        # Default display time for images (in seconds)
        self.default_display_time = DEFAULT_DISPLAY_TIME
        
        # Set up key mappings from config
        self.key_mappings = KEY_MAPPINGS
        
        # Set up arrow key mappings for videos from config
        self.arrow_key_mappings = ARROW_KEY_MAPPINGS
        
        # Set up joystick mappings for videos from config
        self.video_channels = VIDEO_CHANNELS
        
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
        
        # Current state
        self.current_image = None
        self.image_end_time = 0
        self.current_channel = 0
        self.playing_video = False
        self.show_waiting_screen = True  # Start with waiting screen
        self.waiting_animation_frame = 0
        self.waiting_animation_time = 0
        
        # Input handling
        self.last_input_time = 0
        self.input_cooldown = 0.5  # seconds between allowed inputs
        self.input_feedback_time = 0
        self.input_feedback_duration = 0.5  # seconds to show input feedback
        self.input_feedback_message = ""
        self.input_feedback_color = (0, 0, 255)  # Blue for accepted, will be yellow for rejected
        self.input_feedback_animation_start = 0
        self.input_feedback_animation_duration = 0.1  # 100ms for the outline animation
        
        # Background color
        self.bg_color = BACKGROUND_COLOR
        
        # Fonts
        self.font = pygame.font.SysFont(None, 48)
        self.feedback_font = pygame.font.SysFont(None, 36)
        
        # Image transition settings
        self.transition_duration = 0.8  # seconds (increased for smoother transitions)
        self.in_transition = False
        self.transition_start_time = 0
        self.previous_image = None
        self.next_image = None
        
        # Create paw cursor image
        self.paw_cursor = self.create_paw_cursor()

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

    def handle_key_press(self, key):
        """Handle a key press event"""
        current_time = time.time()
        
        # Check for input cooldown
        if current_time - self.last_input_time < self.input_cooldown:
            # Reject input if too rapid
            self.show_input_feedback("Too fast! Wait a moment", (255, 255, 0))  # Yellow for rejection
            print(f"Input rejected: too rapid (cooldown: {self.input_cooldown}s)")
            return
            
        # Exit waiting screen on any key press
        if self.show_waiting_screen:
            self.show_waiting_screen = False
            self.show_input_feedback("Input accepted!", (0, 0, 255))  # Blue for acceptance
            self.last_input_time = current_time
            return
            
        # Handle number keys for commands
        if key in self.key_mappings:
            mapping = self.key_mappings[key]
            
            # Update last input time
            self.last_input_time = current_time
            
            # Show feedback
            command_name = mapping.get("command", "Command")
            self.show_input_feedback(f"{command_name.capitalize()} selected!", (0, 0, 255))  # Blue for acceptance
            
            # Play sound - ensure this runs
            if "sound" in mapping:
                try:
                    self.play_sound(mapping["sound"])
                except Exception as e:
                    print(f"Error playing sound: {e}")
            
            # Speak command using TTS - ensure this runs
            if "command" in mapping:
                try:
                    self.tts_handler.speak(mapping["command"])
                except Exception as e:
                    print(f"Error with TTS: {e}")
            
            # Display image with transition
            if "image" in mapping:
                # If an image is already displayed, set up transition
                if self.current_image and not self.in_transition:
                    self.previous_image = self.current_image
                    self.next_image = self.load_image(mapping["image"])
                    self.in_transition = True
                    self.transition_start_time = time.time()
                else:
                    # No current image, just display the new one
                    self.current_image = self.load_image(mapping["image"])
                
                display_time = mapping.get("display_time", self.default_display_time)
                self.image_end_time = time.time() + display_time + (self.transition_duration if self.in_transition else 0)
                
                # Stop any playing video
                if self.playing_video:
                    self.video_player.stop()
                    self.playing_video = False
        
        # Handle arrow keys for video channels
        elif key in self.arrow_key_mappings:
            # Update last input time
            self.last_input_time = current_time
            
            channel_index = self.arrow_key_mappings[key]
            if 0 <= channel_index < len(self.video_channels):
                self.current_channel = channel_index
                channel = self.video_channels[self.current_channel]
                print(f"Switched to channel: {channel['name']}")
                
                # Show feedback
                self.show_input_feedback(f"Channel: {channel['name']}", (0, 0, 255))  # Blue for acceptance
                
                # Speak the channel name
                self.tts_handler.speak(channel['name'])
                
                # Clear any displayed image
                self.current_image = None
                self.image_end_time = 0
                self.in_transition = False
                
                # Try to play the video
                try:
                    video_file = channel["video"]
                    if self.video_player.play_video(video_file):
                        self.playing_video = True
                    else:
                        # If video playback fails, display the channel name
                        self.playing_video = False
                        self.display_text(f"Channel: {channel['name']}")
                except Exception as e:
                    print(f"Error playing video: {e}")
                    self.playing_video = False
                    self.display_text(f"Channel: {channel['name']}")

    def handle_joystick(self):
        """Handle joystick input for video channel selection"""
        if not self.joystick:
            return
            
        # Check for input cooldown
        current_time = time.time()
        if current_time - self.last_input_time < self.input_cooldown:
            return
            
        # Exit waiting screen on any joystick movement
        if self.show_waiting_screen:
            # Check if joystick is moved significantly
            x_axis = self.joystick.get_axis(0)
            y_axis = self.joystick.get_axis(1)
            
            if abs(x_axis) > 0.5 or abs(y_axis) > 0.5:
                self.show_waiting_screen = False
                self.show_input_feedback("Input accepted!", (0, 0, 255))  # Blue for acceptance
                self.last_input_time = current_time
            return
            
        # Check joystick axis for channel changes
        x_axis = self.joystick.get_axis(0)
        y_axis = self.joystick.get_axis(1)
        
        # Simple threshold for joystick movement
        threshold = 0.5
        
        # Change channel based on joystick position
        if x_axis > threshold:  # Right
            self.change_channel(1)
        elif x_axis < -threshold:  # Left
            self.change_channel(-1)
        elif y_axis > threshold:  # Down
            self.change_channel(1)
        elif y_axis < -threshold:  # Up
            self.change_channel(-1)

    def change_channel(self, direction):
        """Change the video channel"""
        # Prevent rapid channel changes by adding a delay
        current_time = time.time()
        if hasattr(self, 'last_channel_change') and current_time - self.last_channel_change < 0.5:
            # Show feedback for rejected input
            self.show_input_feedback("Too fast! Wait a moment", (255, 255, 0))  # Yellow for rejection
            return
            
        self.last_channel_change = current_time
        self.last_input_time = current_time
        
        # Show feedback for accepted input
        self.show_input_feedback("Channel changed!", (0, 0, 255))  # Blue for acceptance
        
        # Update channel index
        self.current_channel = (self.current_channel + direction) % len(self.video_channels)
        
        # Get the channel info
        channel = self.video_channels[self.current_channel]
        print(f"Changed to channel: {channel['name']}")
        
        # Clear any displayed image
        self.current_image = None
        self.image_end_time = 0
        
        # Try to play the video
        try:
            video_file = channel["video"]
            if self.video_player.play_video(video_file):
                self.playing_video = True
            else:
                # If video playback fails, display the channel name
                self.playing_video = False
                self.display_text(f"Channel: {channel['name']}")
        except Exception as e:
            print(f"Error playing video: {e}")
            self.playing_video = False
            self.display_text(f"Channel: {channel['name']}")

    def show_input_feedback(self, message, color):
        """Show feedback for input (accepted or rejected)"""
        self.input_feedback_message = message
        self.input_feedback_color = color
        self.input_feedback_time = time.time()
        self.input_feedback_animation_start = time.time()  # Start the outline animation
        
    def display_text(self, text):
        """Display text on the screen"""
        self.current_image = pygame.Surface((self.screen_width, self.screen_height))
        self.current_image.fill(self.bg_color)
        text_surface = self.font.render(text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(self.screen_width/2, self.screen_height/2))
        self.current_image.blit(text_surface, text_rect)
        self.image_end_time = time.time() + 3  # Display for 3 seconds
        
    def render_waiting_screen(self):
        """Render the waiting screen with animation"""
        # Create surface for waiting screen
        surface = pygame.Surface((self.screen_width, self.screen_height))
        surface.fill(self.bg_color)
        
        # Update animation frame every 0.5 seconds
        current_time = time.time()
        if current_time - self.waiting_animation_time > 0.5:
            self.waiting_animation_frame = (self.waiting_animation_frame + 1) % 4
            self.waiting_animation_time = current_time
        
        # Draw pulsing text
        pulse_scale = 1.0 + 0.1 * abs(math.sin(current_time * 2))
        
        # Main message
        main_font = pygame.font.SysFont(None, int(72 * pulse_scale))
        main_text = main_font.render("Paw a Key", True, (255, 255, 255))
        main_rect = main_text.get_rect(center=(self.screen_width/2, self.screen_height/2 - 50))
        surface.blit(main_text, main_rect)
        
        # Subtitle
        sub_font = pygame.font.SysFont(None, 36)
        sub_text = sub_font.render("to start", True, (200, 200, 200))
        sub_rect = sub_text.get_rect(center=(self.screen_width/2, self.screen_height/2 + 20))
        surface.blit(sub_text, sub_rect)
        
        # Draw animated paw cursor
        # Position based on animation frame
        positions = [
            (self.screen_width/2 - 150, self.screen_height/2 + 100),  # Left
            (self.screen_width/2 - 50, self.screen_height/2 + 120),   # Middle-left
            (self.screen_width/2 + 50, self.screen_height/2 + 120),   # Middle-right
            (self.screen_width/2 + 150, self.screen_height/2 + 100)   # Right
        ]
        
        paw_pos = positions[self.waiting_animation_frame]
        surface.blit(self.paw_cursor, paw_pos)
        
        return surface

    def run(self):
        """Main game loop"""
        running = True
        clock = pygame.time.Clock()
        
        # Import math for animations
        import math
        
        while running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    # Exit on ESC key
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    else:
                        self.handle_key_press(event.key)
                elif event.type == pygame.JOYBUTTONDOWN:
                    # Handle joystick button press as input
                    self.handle_key_press(pygame.K_SPACE)  # Treat as space key
            
            # Handle joystick input
            if self.joystick:
                self.handle_joystick()
            
            # Clear the screen
            self.screen.fill(self.bg_color)
            
            # Update and display content based on current state
            current_time = time.time()
            
            if self.show_waiting_screen:
                # Show waiting screen
                waiting_surface = self.render_waiting_screen()
                self.screen.blit(waiting_surface, (0, 0))
            elif self.playing_video:
                # Update and display video frame
                frame = self.video_player.update()
                if frame:
                    self.screen.blit(frame, (0, 0))
            elif self.in_transition and self.previous_image and self.next_image:
                # Handle image transition
                transition_time = current_time - self.transition_start_time
                
                # If transition is complete, switch to the next image
                if transition_time >= self.transition_duration:
                    self.current_image = self.next_image
                    self.previous_image = None
                    self.next_image = None
                    self.in_transition = False
                else:
                    # Create transition effect (smooth fade with easing)
                    # Use sine easing for smoother transition
                    progress = math.sin((transition_time / self.transition_duration) * math.pi / 2)
                    
                    # Set alpha values for the blend
                    self.previous_image.set_alpha(int(255 * (1 - progress)))
                    self.next_image.set_alpha(int(255 * progress))
                    
                    # Blit both images
                    self.screen.blit(self.previous_image, (0, 0))
                    self.screen.blit(self.next_image, (0, 0))
            elif self.current_image and current_time < self.image_end_time:
                # Display current image
                self.screen.blit(self.current_image, (0, 0))
            else:
                # Return to waiting screen if nothing is displayed
                self.show_waiting_screen = True
            
            # Display input feedback if active
            if current_time - self.input_feedback_time < self.input_feedback_duration:
                # Create semi-transparent overlay for feedback
                feedback_surface = pygame.Surface((self.screen_width, 50), pygame.SRCALPHA)
                feedback_surface.fill((0, 0, 0, 180))  # Semi-transparent black
                
                # Render feedback text
                feedback_text = self.feedback_font.render(self.input_feedback_message, True, self.input_feedback_color)
                feedback_rect = feedback_text.get_rect(center=(self.screen_width/2, 25))
                
                # Blit to feedback surface
                feedback_surface.blit(feedback_text, feedback_rect)
                
                # Blit feedback surface to screen
                self.screen.blit(feedback_surface, (0, self.screen_height - 50))
                
                # Draw animated outline if within animation duration
                if current_time - self.input_feedback_animation_start < self.input_feedback_animation_duration:
                    # Calculate animation progress (0.0 to 1.0)
                    progress = (current_time - self.input_feedback_animation_start) / self.input_feedback_animation_duration
                    
                    # Calculate outline thickness based on animation progress (starts thick, gets thinner)
                    thickness = int(10 * (1 - progress))
                    
                    # Draw rectangle outline around the screen
                    pygame.draw.rect(self.screen, self.input_feedback_color, 
                                    (0, 0, self.screen_width, self.screen_height), 
                                    thickness)
            
            # Update the display
            pygame.display.flip()
            
            # Cap the frame rate
            clock.tick(60)  # Increased for smoother animations
        
        # Clean up
        if self.playing_video:
            self.video_player.stop()
        self.tts_handler.stop()
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    app = DogPuter()
    app.run()
