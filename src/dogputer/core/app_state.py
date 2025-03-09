import os
import time
import enum
import pygame
from dogputer.core.config import (
    INPUT_MAPPINGS, VIDEO_CHANNELS,
    DEFAULT_DISPLAY_TIME
)

class Mode(enum.Enum):
    """Application modes"""
    WAITING = 0
    VIDEO = 1
    TEXT = 2  # Only used for fallback when videos can't be loaded

class ContentType(enum.Enum):
    """Content types"""
    NONE = 0
    VIDEO = 1
    TEXT = 2  # Only used for fallback when videos can't be loaded
    WAITING = 3

class InputState:
    """Manages input state and cooldown"""
    
    def __init__(self, cooldown=1.5, max_cooldown=5.0):  # Base cooldown and maximum cooldown
        self.last_input_time = 0
        self.base_cooldown = cooldown
        self.max_cooldown = max_cooldown
        self.input_cooldown = cooldown  # Current cooldown duration
        self.last_channel_change = 0
        self.rejected_inputs_count = 0  # Count of rejected inputs
    
    def is_input_allowed(self):
        """Check if input is allowed based on cooldown"""
        current_time = time.time()
        time_since_last_input = current_time - self.last_input_time
        
        print(f"Input check: Time since last input: {time_since_last_input:.2f}s, Current cooldown: {self.input_cooldown:.2f}s")
        
        if time_since_last_input >= self.input_cooldown:
            # If enough time has passed, reset cooldown to base value
            old_cooldown = self.input_cooldown
            self.input_cooldown = self.base_cooldown
            self.rejected_inputs_count = 0
            print(f"Input allowed: Resetting cooldown from {old_cooldown:.2f}s to {self.input_cooldown:.2f}s")
            return True
        else:       
            return False
    
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
    
    def set_text(self, text, font, display_time=5.0, screen_width=800, screen_height=600):
        """Set the text to display in the top left corner"""
        self.text = text
        
        # Create a surface for the text
        self.surface = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        
        # Render the text
        from dogputer.core.config import YELLOW_PRIMARY, BLUE_PRIMARY
        
        # Create a larger, more visible font for dogs
        large_font = pygame.font.SysFont(None, 72)
        
        # Add a contrasting background for better visibility
        text_bg_surface = large_font.render(text, True, BLUE_PRIMARY)
        text_fg_surface = large_font.render(text, True, YELLOW_PRIMARY)
        
        # Position in top left with some padding
        padding = 20
        text_rect = text_fg_surface.get_rect(topleft=(padding, padding))
        
        # Draw text with outline for better visibility
        outline_thickness = 3
        for offset_x in range(-outline_thickness, outline_thickness + 1, outline_thickness):
            for offset_y in range(-outline_thickness, outline_thickness + 1, outline_thickness):
                if offset_x == 0 and offset_y == 0:
                    continue
                shadow_rect = text_rect.copy()
                shadow_rect.x += offset_x
                shadow_rect.y += offset_y
                self.surface.blit(text_bg_surface, shadow_rect)
        
        # Draw main text
        self.surface.blit(text_fg_surface, text_rect)
        
        # Set display time to 5 seconds for fallback text display
        self.display_end_time = time.time() + display_time
    
    def update(self, delta_time):
        """Update text state"""
        return time.time() < self.display_end_time

class WaitingScreenContent:
    """Manages waiting screen content state"""
    
    def __init__(self, bg_color):
        self.animation_time = 0
        self.bg_color = bg_color
        self.paw_cursor = None
        # Remove animation_frame as we now use continuous smooth animation
        # in view_state.py instead of discrete frames
    
    def update(self, delta_time):
        """Update waiting screen state"""
        # We no longer need to update animation frames
        # The view_state now handles continuous smooth animation
        # based on the current time
        return True

class FeedbackState:
    """Manages feedback state"""
    
    def __init__(self, duration=None, animation_duration=0.2):
        from dogputer.core.config import FEEDBACK_DURATION
        self.message = ""
        self.color = (0, 0, 255)  # Blue by default
        self.start_time = 0
        self.duration = duration if duration is not None else FEEDBACK_DURATION
        self.animation_start_time = 0
        self.animation_duration = animation_duration
        self.is_active = False
        self.input_rejected = False  # Flag to track if input was rejected
    
    def show_feedback(self, message, color):
        """Show feedback with the given message and color"""
        self.message = message
        self.color = color
        self.start_time = time.time()
        self.animation_start_time = time.time()
        self.is_active = True
        
        # Check if this is a rejection message
        if "too fast" in message.lower() or color == (255, 255, 0):
            self.input_rejected = True
        else:
            self.input_rejected = False
    
    def update(self, delta_time, input_state=None):
        """Update feedback state"""
        if not self.is_active:
            return
        
        current_time = time.time()
        
        # If input was rejected, keep feedback visible until input is allowed again
        if self.input_rejected and input_state:
            # Only clear the feedback if input is now allowed
            if input_state.is_input_allowed():
                self.is_active = False
                self.input_rejected = False
        # Otherwise use normal duration
        elif current_time - self.start_time >= self.duration:
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
        if self.current_type == ContentType.TEXT:
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
            print(f"ContentState: Setting current_type to VIDEO")
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
        self.feedback_state.update(delta_time, self.input_state)
        
        # Always sync mode with content type for consistency
        if self.content_state.current_type == ContentType.WAITING and self.mode != Mode.WAITING:
            print(f"Syncing state: Setting mode to WAITING to match content type")
            self.mode = Mode.WAITING
        elif self.content_state.current_type == ContentType.VIDEO and self.mode != Mode.VIDEO:
            print(f"Syncing state: Setting mode to VIDEO to match content type")
            self.mode = Mode.VIDEO
        elif self.content_state.current_type == ContentType.TEXT and self.mode != Mode.TEXT:
            print(f"Syncing state: Setting mode to TEXT to match content type")
            self.mode = Mode.TEXT
        
        # Update content state
        mode_changed = self.content_state.update(delta_time)
        
        # Handle mode changes
        if mode_changed:
            print(f"Content update triggered mode change. ContentType is now: {self.content_state.current_type}")
            if self.content_state.current_type == ContentType.WAITING:
                self.mode = Mode.WAITING
                print(f"Mode changed to WAITING")
            elif self.content_state.current_type == ContentType.VIDEO:
                self.mode = Mode.VIDEO
                print(f"Mode changed to VIDEO")
            elif self.content_state.current_type == ContentType.TEXT:
                self.mode = Mode.TEXT
                print(f"Mode changed to TEXT")
    
    def handle_key_press(self, key):
        """
        Legacy method for backward compatibility.
        Will convert the key press to a command and handle it.
        New code should use handle_command directly instead.
        """
        try:
            key_name = pygame.key.name(key)
        except:
            key_name = f"Unknown key ({key})"
            
        print(f"AppState.handle_key_press: {key_name} (code: {key})")
        
        # Check for input cooldown
        if not self.input_state.is_input_allowed():
            # Show feedback with the current cooldown time
            cooldown_time = round(self.input_state.input_cooldown, 1)
            self.show_feedback(f"Too fast! Wait {cooldown_time}s", (255, 255, 0))
            print(f"Input rejected: too rapid (cooldown: {self.input_state.input_cooldown}s)")
            return
            
        # Exit waiting screen on any key press
        if self.mode == Mode.WAITING:
            self.show_feedback("Input accepted!", (0, 0, 255))
            self.input_state.record_input()
            print(f"Exiting waiting mode, processing key: {key_name}")
        
        # Convert key to command using input mappings
        command_name = None
        
        # Special handling for z key (code 122) with X-Arcade keyboard mapping
        if key == pygame.K_z and pygame.key.name(key) == 'z':
            command_name = "ball"
        # Handle keys with mappings in INPUT_MAPPINGS
        elif key in INPUT_MAPPINGS:
            command_name = INPUT_MAPPINGS[key]
        
        # If we found a command name, create and execute the command
        if command_name:
            # Import here to avoid circular import
            from dogputer.core.commands import ContentCommand, VideoChannelCommand
            
            # Create the appropriate command
            if command_name.startswith("video_"):
                # This is handled directly in the main.py file
                print(f"Video command detected: {command_name}")
                self.input_state.record_input()
                return
            else:
                # Create a content command
                command = ContentCommand(command_name)
                self.handle_command(command)
        else:
            # No command found for this key
            print(f"No mapping found for key: {key_name}")
            
    def handle_command(self, command):
        """Handle a command object"""
        print(f"Handling command: {command}")
        
        # Check for input cooldown
        if not self.input_state.is_input_allowed():
            # Show feedback with the current cooldown time
            cooldown_time = round(self.input_state.input_cooldown, 1)
            self.show_feedback(f"Too fast! Wait {cooldown_time}s", (255, 255, 0))  # Yellow for rejection
            print(f"Command rejected: too rapid (cooldown: {self.input_state.input_cooldown}s)")
            return
        
        # Exit waiting screen on any command
        if self.mode == Mode.WAITING:
            self.show_feedback("Input accepted!", (0, 0, 255))  # Blue for acceptance
            self.input_state.record_input()
            print(f"Exiting waiting mode, processing command: {command}")
        
        # Record input and execute command
        self.input_state.record_input()
        command.execute(self)
    
    def _display_image_fallback(self, mapping):
        """Display image as fallback when video is not available"""
        if "image" in mapping:
            # Load and display the image
            image_name = mapping["image"]
            print(f"Loading image fallback: {image_name}")
            image = self.load_image(image_name)
            if image:
                display_time = mapping.get("display_time", DEFAULT_DISPLAY_TIME)
                print(f"Image loaded successfully, displaying for {display_time} seconds, switching to IMAGE mode")
                self.content_state.set_image(image, display_time)
                self.mode = Mode.IMAGE
            else:
                print(f"Failed to load image: {image_name}")
                self.show_feedback(f"Failed to load image: {image_name}", (255, 0, 0))  # Red for error
    
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
            # Show feedback with current cooldown time similar to key presses
            cooldown_time = round(1.5, 1)  # Using the hardcoded 1.5s for channel changes
            self.show_feedback(f"Too fast! Wait {cooldown_time}s", (255, 255, 0))  # Yellow for rejection
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
