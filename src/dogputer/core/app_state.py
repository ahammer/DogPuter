import os
import time
import enum
import pygame
from dogputer.core.config import (
    KEY_MAPPINGS, VIDEO_CHANNELS, ARROW_KEY_MAPPINGS,
    DEFAULT_DISPLAY_TIME
)

class Mode(enum.Enum):
    """Application modes"""
    WAITING = 0
    IMAGE = 1
    VIDEO = 2
    TEXT = 3

class ContentType(enum.Enum):
    """Content types"""
    NONE = 0
    IMAGE = 1
    VIDEO = 2
    TEXT = 3
    WAITING = 4

class InputState:
    """Manages input state and cooldown"""
    
    def __init__(self, cooldown=1.5):  # Increased cooldown to 1.5 seconds
        self.last_input_time = 0
        self.input_cooldown = cooldown
        self.last_channel_change = 0
    
    def is_input_allowed(self):
        """Check if input is allowed based on cooldown"""
        return time.time() - self.last_input_time >= self.input_cooldown
    
    def record_input(self):
        """Record that input was received"""
        self.last_input_time = time.time()
        
    def is_channel_change_allowed(self):
        """Check if channel change is allowed"""
        return not hasattr(self, 'last_channel_change') or time.time() - self.last_channel_change >= 1.5  # Increased cooldown to 1.5 seconds
    
    def record_channel_change(self):
        """Record that a channel change occurred"""
        self.last_channel_change = time.time()
        self.last_input_time = time.time()

class ImageContent:
    """Manages image content state"""
    
    def __init__(self):
        self.current_image = None
        self.previous_image = None
        self.next_image = None
        self.in_transition = False
        self.transition_start_time = 0
        self.transition_duration = 0.8
        self.display_end_time = 0
    
    def set_image(self, image, display_time=DEFAULT_DISPLAY_TIME):
        """Set the current image"""
        if self.current_image and not self.in_transition:
            # Start transition
            self.previous_image = self.current_image
            self.next_image = image
            self.in_transition = True
            self.transition_start_time = time.time()
            self.display_end_time = time.time() + display_time + self.transition_duration
        else:
            # Just set the image directly
            self.current_image = image
            self.display_end_time = time.time() + display_time
    
    def update(self, delta_time):
        """Update image state"""
        current_time = time.time()
        
        # Handle transition completion
        if self.in_transition:
            transition_time = current_time - self.transition_start_time
            if transition_time >= self.transition_duration:
                self.current_image = self.next_image
                self.previous_image = None
                self.next_image = None
                self.in_transition = False
        
        # Check if display time has ended
        return current_time < self.display_end_time
    
    def get_transition_progress(self):
        """Get the current transition progress (0.0 to 1.0)"""
        if not self.in_transition:
            return 0.0
        
        transition_time = time.time() - self.transition_start_time
        return min(transition_time / self.transition_duration, 1.0)

class VideoContent:
    """Manages video content state"""
    
    def __init__(self, video_player):
        self.video_player = video_player
        self.current_channel = 0
        self.is_playing = False
    
    def play_channel(self, channel_index):
        """Play a video channel"""
        if 0 <= channel_index < len(VIDEO_CHANNELS):
            self.current_channel = channel_index
            channel = VIDEO_CHANNELS[self.current_channel]
            video_file = channel["video"]
            
            if self.video_player.play_video(video_file):
                self.is_playing = True
                return True, None
            else:
                self.is_playing = False
                return False, channel["name"]
        
        return False, None
    
    def change_channel(self, direction):
        """Change the current channel by a relative amount"""
        new_channel = (self.current_channel + direction) % len(VIDEO_CHANNELS)
        return self.play_channel(new_channel)
    
    def stop(self):
        """Stop video playback"""
        if self.is_playing:
            self.video_player.stop()
            self.is_playing = False

class TextContent:
    """Manages text content state"""
    
    def __init__(self, bg_color):
        self.text = ""
        self.surface = None
        self.display_end_time = 0
        self.bg_color = bg_color
    
    def set_text(self, text, font, display_time=3.0, screen_width=800, screen_height=600):
        """Set the text to display"""
        self.text = text
        
        # Create a surface for the text
        self.surface = pygame.Surface((screen_width, screen_height))
        self.surface.fill(self.bg_color)
        
        # Render the text
        text_surface = font.render(text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(screen_width/2, screen_height/2))
        self.surface.blit(text_surface, text_rect)
        
        # Set display time
        self.display_end_time = time.time() + display_time
    
    def update(self, delta_time):
        """Update text state"""
        return time.time() < self.display_end_time

class WaitingScreenContent:
    """Manages waiting screen content state"""
    
    def __init__(self, bg_color):
        self.animation_frame = 0
        self.animation_time = 0
        self.bg_color = bg_color
        self.paw_cursor = None
    
    def update(self, delta_time):
        """Update waiting screen state"""
        current_time = time.time()
        
        # Update animation frame every 0.5 seconds
        if current_time - self.animation_time > 0.5:
            self.animation_frame = (self.animation_frame + 1) % 4
            self.animation_time = current_time
        
        return True

class FeedbackState:
    """Manages feedback state"""
    
    def __init__(self, duration=0.5, animation_duration=0.1):
        self.message = ""
        self.color = (0, 0, 255)  # Blue by default
        self.start_time = 0
        self.duration = duration
        self.animation_start_time = 0
        self.animation_duration = animation_duration
        self.is_active = False
    
    def show_feedback(self, message, color):
        """Show feedback with the given message and color"""
        self.message = message
        self.color = color
        self.start_time = time.time()
        self.animation_start_time = time.time()
        self.is_active = True
    
    def update(self, delta_time):
        """Update feedback state"""
        if not self.is_active:
            return
        
        current_time = time.time()
        if current_time - self.start_time >= self.duration:
            self.is_active = False
    
    def get_animation_progress(self):
        """Get the current animation progress (0.0 to 1.0)"""
        if not self.is_active:
            return 0.0
        
        current_time = time.time()
        if current_time - self.animation_start_time >= self.animation_duration:
            return 1.0
        
        return (current_time - self.animation_start_time) / self.animation_duration
    
    def is_animating(self):
        """Check if the feedback is currently animating"""
        if not self.is_active:
            return False
        
        current_time = time.time()
        return current_time - self.animation_start_time < self.animation_duration

class ContentState:
    """Manages all content state"""
    
    def __init__(self, video_player, bg_color):
        self.current_type = ContentType.WAITING
        self.image_content = ImageContent()
        self.video_content = VideoContent(video_player)
        self.text_content = TextContent(bg_color)
        self.waiting_content = WaitingScreenContent(bg_color)
    
    def update(self, delta_time):
        """Update content state based on type"""
        if self.current_type == ContentType.IMAGE:
            # If image display has ended, return to waiting screen
            if not self.image_content.update(delta_time):
                self.current_type = ContentType.WAITING
                return True
        elif self.current_type == ContentType.TEXT:
            # If text display has ended, return to waiting screen
            if not self.text_content.update(delta_time):
                self.current_type = ContentType.WAITING
                return True
        elif self.current_type == ContentType.WAITING:
            self.waiting_content.update(delta_time)
        elif self.current_type == ContentType.VIDEO:
            # Check if the video has completed
            frame, is_complete = self.video_content.video_player.update()
            if is_complete:
                # Video has completed, return to waiting screen
                self.video_content.stop()
                self.current_type = ContentType.WAITING
                return True
        
        return False
    
    def set_image(self, image, display_time=DEFAULT_DISPLAY_TIME):
        """Set image content"""
        self.video_content.stop()
        self.image_content.set_image(image, display_time)
        self.current_type = ContentType.IMAGE
    
    def set_video(self, channel_index):
        """Set video content by channel index"""
        success, channel_name = self.video_content.play_channel(channel_index)
        if success:
            self.current_type = ContentType.VIDEO
            return True
        elif channel_name:
            # We need to pass the font from AppState, so we'll return False and let AppState handle it
            return False, channel_name
        return False, None
    
    def set_video_by_filename(self, video_filename):
        """Set video content by filename"""
        if self.video_content.video_player.play_video(video_filename):
            self.video_content.is_playing = True
            self.current_type = ContentType.VIDEO
            return True
        return False
    
    def set_text(self, text, font=None, display_time=3.0, screen_width=800, screen_height=600):
        """Set text content"""
        self.video_content.stop()
        if font:
            self.text_content.set_text(text, font, display_time, screen_width, screen_height)
            self.current_type = ContentType.TEXT
            return True
        return False
    
    def set_waiting(self):
        """Set waiting screen content"""
        self.video_content.stop()
        self.current_type = ContentType.WAITING
    
    def change_video_channel(self, direction):
        """Change video channel"""
        if self.current_type == ContentType.VIDEO:
            success, channel_name = self.video_content.change_channel(direction)
            if not success and channel_name:
                # We need to pass the font from AppState, so we'll return False and let AppState handle it
                return False, channel_name
            return success, None
        return False, None

class AppState:
    """Main application state class"""
    
    def __init__(self, video_player, tts_handler, bg_color, font, feedback_font, screen_width, screen_height):
        self.mode = Mode.WAITING
        self.input_state = InputState()
        self.content_state = ContentState(video_player, bg_color)
        self.feedback_state = FeedbackState()
        self.tts_handler = tts_handler
        self.font = font
        self.feedback_font = feedback_font
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.paw_cursor = None  # Will be set externally
    
    def update(self, delta_time):
        """Update application state"""
        # Update feedback state
        self.feedback_state.update(delta_time)
        
        # Update content state
        mode_changed = self.content_state.update(delta_time)
        
        # Handle mode changes
        if mode_changed:
            if self.content_state.current_type == ContentType.WAITING:
                self.mode = Mode.WAITING
            elif self.content_state.current_type == ContentType.IMAGE:
                self.mode = Mode.IMAGE
            elif self.content_state.current_type == ContentType.VIDEO:
                self.mode = Mode.VIDEO
            elif self.content_state.current_type == ContentType.TEXT:
                self.mode = Mode.TEXT
    
    def handle_key_press(self, key):
        """Handle a key press event"""
        # Check for input cooldown
        if not self.input_state.is_input_allowed():
            self.show_feedback("Too fast! Wait a moment", (255, 255, 0))  # Yellow for rejection
            print(f"Input rejected: too rapid (cooldown: {self.input_state.input_cooldown}s)")
            return
        
        # Exit waiting screen on any key press
        if self.mode == Mode.WAITING:
            # Just exit waiting screen, don't return - continue processing the key
            self.show_feedback("Input accepted!", (0, 0, 255))  # Blue for acceptance
            self.input_state.record_input()
        
        # Handle number keys for commands
        if key in KEY_MAPPINGS:
            mapping = KEY_MAPPINGS[key]
            
            # Record input
            self.input_state.record_input()
            
            # Show feedback
            command_name = mapping.get("command", "Command")
            self.show_feedback(f"{command_name.capitalize()} selected!", (0, 0, 255))  # Blue for acceptance
            
            # Play sound
            if "sound" in mapping:
                try:
                    self.play_sound(mapping["sound"])
                except Exception as e:
                    print(f"Error playing sound: {e}")
            
            # Speak command using TTS
            if "command" in mapping:
                try:
                    self.tts_handler.speak(mapping["command"])
                except Exception as e:
                    print(f"Error with TTS: {e}")
            
            # Try to play video first, fall back to image if video doesn't exist
            if "command" in mapping:
                # Construct video filename from command name
                video_filename = mapping["command"] + ".mp4"
                video_path = os.path.join("videos", video_filename)
                video_placeholder_path = video_path + ".txt"
                
                # If we're already playing this video, ignore the command
                if (self.mode == Mode.VIDEO and 
                    self.content_state.video_content.is_playing and 
                    hasattr(self.content_state.video_content, 'current_video_filename') and
                    self.content_state.video_content.current_video_filename == video_filename):
                    print(f"Already playing video: {video_filename}, ignoring repeat command")
                    return
                
                # Check if video or placeholder exists
                if os.path.exists(video_path):
                    # Play the actual video
                    print(f"Playing video for command: {mapping['command']}")
                    result = self.content_state.set_video_by_filename(video_filename)
                    if result:
                        self.mode = Mode.VIDEO
                        # Store the current video filename for repeat detection
                        self.content_state.video_content.current_video_filename = video_filename
                    else:
                        # Fall back to image if video playback fails
                        self._display_image_fallback(mapping)
                elif os.path.exists(video_placeholder_path):
                    # If we have a placeholder, display the image with a message
                    print(f"Video placeholder found for command: {mapping['command']}, displaying image instead")
                    self._display_image_fallback(mapping)
                    # Show feedback about placeholder
                    self.show_feedback("Video placeholder - using image instead", (0, 0, 255))
                else:
                    # Fall back to image
                    self._display_image_fallback(mapping)
            elif "image" in mapping:
                # Just use the image directly if no command is specified
                self._display_image_fallback(mapping)
        
        # Handle arrow keys for video channels
        elif key in ARROW_KEY_MAPPINGS:
            # Record input
            self.input_state.record_input()
            
            channel_index = ARROW_KEY_MAPPINGS[key]
            if 0 <= channel_index < len(VIDEO_CHANNELS):
                channel = VIDEO_CHANNELS[channel_index]
                print(f"Switched to channel: {channel['name']}")
                
                # Show feedback
                self.show_feedback(f"Channel: {channel['name']}", (0, 0, 255))  # Blue for acceptance
                
                # Speak the channel name
                self.tts_handler.speak(channel['name'])
                
                # Play the video
                result = self.content_state.set_video(channel_index)
                if isinstance(result, tuple):
                    success, channel_name = result
                    if not success and channel_name:
                        # Display channel name as text
                        self.content_state.set_text(f"Channel: {channel_name}", self.font, 3.0, self.screen_width, self.screen_height)
                        self.mode = Mode.TEXT
                elif result:
                    self.mode = Mode.VIDEO
    
    def _display_image_fallback(self, mapping):
        """Display image as fallback when video is not available"""
        if "image" in mapping:
            # Load and display the image
            image = self.load_image(mapping["image"])
            if image:
                display_time = mapping.get("display_time", DEFAULT_DISPLAY_TIME)
                self.content_state.set_image(image, display_time)
                self.mode = Mode.IMAGE
    
    def handle_joystick(self, joystick):
        """Handle joystick input"""
        if not joystick:
            return
        
        # Check for input cooldown
        if not self.input_state.is_input_allowed():
            return
        
        # Exit waiting screen on any joystick movement
        if self.mode == Mode.WAITING:
            # Check if joystick is moved significantly
            x_axis = joystick.get_axis(0)
            y_axis = joystick.get_axis(1)
            
            if abs(x_axis) > 0.5 or abs(y_axis) > 0.5:
                self.content_state.set_waiting()  # Reset waiting screen state
                self.mode = Mode.WAITING
                self.show_feedback("Input accepted!", (0, 0, 255))  # Blue for acceptance
                self.input_state.record_input()
            return
        
        # Check joystick axis for channel changes
        x_axis = joystick.get_axis(0)
        y_axis = joystick.get_axis(1)
        
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
        # Prevent rapid channel changes
        if not self.input_state.is_channel_change_allowed():
            self.show_feedback("Too fast! Wait a moment", (255, 255, 0))  # Yellow for rejection
            return
        
        # Record channel change
        self.input_state.record_channel_change()
        
        # Show feedback
        self.show_feedback("Channel changed!", (0, 0, 255))  # Blue for acceptance
        
        # Change channel
        result = self.content_state.change_video_channel(direction)
        if isinstance(result, tuple):
            success, channel_name = result
            if not success and channel_name:
                # Display channel name as text
                channel_index = (self.content_state.video_content.current_channel + direction) % len(VIDEO_CHANNELS)
                channel = VIDEO_CHANNELS[channel_index]
                print(f"Changed to channel: {channel['name']}")
                
                # Speak the channel name
                self.tts_handler.speak(channel['name'])
                
                # Display channel name as text
                self.content_state.set_text(f"Channel: {channel_name}", self.font, 3.0, self.screen_width, self.screen_height)
                self.mode = Mode.TEXT
        elif result:
            self.mode = Mode.VIDEO
    
    def show_feedback(self, message, color):
        """Show feedback with the given message and color"""
        self.feedback_state.show_feedback(message, color)
    
    def load_image(self, image_name):
        """Load an image (to be implemented by the main class)"""
        # This is a placeholder - the actual implementation will be in the main class
        return None
    
    def play_sound(self, sound_name):
        """Play a sound (to be implemented by the main class)"""
        # This is a placeholder - the actual implementation will be in the main class
        pass
    
    def cleanup(self):
        """Clean up resources"""
        self.content_state.video_content.stop()
        self.tts_handler.stop()
