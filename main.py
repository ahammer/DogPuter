import pygame
import os
import sys
import time
from config import KEY_MAPPINGS, VIDEO_CHANNELS, SCREEN_WIDTH, SCREEN_HEIGHT, BACKGROUND_COLOR, DEFAULT_DISPLAY_TIME
from video_player import VideoPlayer

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
        
        # Current state
        self.current_image = None
        self.image_end_time = 0
        self.current_channel = 0
        self.playing_video = False
        
        # Background color
        self.bg_color = BACKGROUND_COLOR
        
        # Font for text
        self.font = pygame.font.SysFont(None, 48)

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
        if key in self.key_mappings:
            mapping = self.key_mappings[key]
            
            # Play sound
            if "sound" in mapping:
                self.play_sound(mapping["sound"])
            
            # Display image
            if "image" in mapping:
                self.current_image = self.load_image(mapping["image"])
                display_time = mapping.get("display_time", self.default_display_time)
                self.image_end_time = time.time() + display_time
                
                # Stop any playing video
                if self.playing_video:
                    self.video_player.stop()
                    self.playing_video = False

    def handle_joystick(self):
        """Handle joystick input for video channel selection"""
        if not self.joystick:
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
            return
            
        self.last_channel_change = current_time
        
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

    def display_text(self, text):
        """Display text on the screen"""
        self.current_image = pygame.Surface((self.screen_width, self.screen_height))
        self.current_image.fill(self.bg_color)
        text_surface = self.font.render(text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(self.screen_width/2, self.screen_height/2))
        self.current_image.blit(text_surface, text_rect)
        self.image_end_time = time.time() + 3  # Display for 3 seconds

    def run(self):
        """Main game loop"""
        running = True
        clock = pygame.time.Clock()
        
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
            
            # Handle joystick input
            if self.joystick:
                self.handle_joystick()
            
            # Clear the screen
            self.screen.fill(self.bg_color)
            
            # Update and display content based on current state
            if self.playing_video:
                # Update and display video frame
                frame = self.video_player.update()
                if frame:
                    self.screen.blit(frame, (0, 0))
            elif self.current_image and time.time() < self.image_end_time:
                # Display current image
                self.screen.blit(self.current_image, (0, 0))
            
            # Update the display
            pygame.display.flip()
            
            # Cap the frame rate
            clock.tick(30)
        
        # Clean up
        if self.playing_video:
            self.video_player.stop()
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    app = DogPuter()
    app.run()
