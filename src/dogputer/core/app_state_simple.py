import pygame
from enum import Enum
from dogputer.core.commands import Command, ContentCommand, ExitCommand # Ensure commands are imported

class Mode(Enum):
    """Enum for different application modes"""
    WAITING = 0  # Waiting for input
    PLAYING = 1  # Playing a video
    EXITING = 2 # Added for clean exit

class AppState:
    """Application state class for DogPuter"""
    
    def __init__(self, video_player, tts_handler, background_color, 
                 font, feedback_font, screen_width, screen_height):
        """Initialize the application state"""
        self.mode = Mode.WAITING
        self.video_player = video_player
        self.background_color = background_color
        self.font = font
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Video state
        self.current_video = None
        self.video_frame = None
        self.video_complete = False
        
        # Feedback message
        self.feedback_text = None
        self.feedback_surface = None
        self.feedback_rect = None
        self.feedback_time = 0
        self.feedback_duration = 2.0
        
        # Waiting text
        self.waiting_text = "Press a button to play a video"
        self.waiting_text_surface = None
        self.waiting_text_rect = None
        
        # Pre-render waiting text
        self._update_waiting_text()
    
    def _update_waiting_text(self):
        """Update waiting text surface"""
        self.waiting_text_surface = self.font.render(self.waiting_text, True, (255, 255, 255))
        text_width, text_height = self.waiting_text_surface.get_size()
        self.waiting_text_rect = pygame.Rect(
            (self.screen_width - text_width) // 2,
            (self.screen_height - text_height) // 2,
            text_width, text_height
        )
    
    def _update_feedback_surface(self):
        """Helper to update the feedback surface and rect"""
        if self.feedback_text:
            self.feedback_surface = self.font.render(self.feedback_text, True, (255, 255, 255))
            text_width, text_height = self.feedback_surface.get_size()
            self.feedback_rect = pygame.Rect(
                (self.screen_width - text_width) // 2,
                self.screen_height - text_height - 20,
                text_width, text_height
            )
        else:
            self.feedback_surface = None
            self.feedback_rect = None

    def handle_command(self, command):
        """Handle incoming commands"""
        if isinstance(command, ExitCommand):
            print("Exit command received, setting mode to EXITING")
            self.mode = Mode.EXITING # Use the EXITING mode
        elif self.mode == Mode.PLAYING:
            # Ignore all non-exit commands while a video is playing
            print("Ignoring command while video is playing")
            return
        elif isinstance(command, ContentCommand):
            # Handle content command (e.g., play video)
            # Check if ContentCommand has content_id, otherwise use content_name as fallback
            if hasattr(command, 'content_id'):
                content_id = command.content_id
            elif hasattr(command, 'content_name'):
                content_id = command.content_name # Fallback to content_name
            else:
                print("Warning: ContentCommand has neither content_id nor content_name")
                return # Cannot process command

            print(f"Content command received: {content_id}")
            
            # We're in WAITING mode now (PLAYING is handled above)
            self.play_video(content_id)
            self.show_feedback(f"Playing: {content_id}")

        elif hasattr(command, 'name'): # Fallback for other potential simple commands
            command_name = command.name.lower()
            print(f"Received named command: {command_name}")
            # Handle named commands if necessary
            # We're in WAITING mode now (PLAYING is handled above)
            self.play_video(command_name)
            self.show_feedback(f"Playing: {command_name}")
        else:
            print(f"Warning: Received unknown command type: {type(command)}")

    def play_video(self, content_id):
        """Play a video for the given content identifier"""
        self.mode = Mode.PLAYING
        self.current_video = content_id
        video_played = self.video_player.play_video(f"{content_id}.mp4") # Assuming content_id is the base name

        if video_played:
            # Try to play a matching sound
            sound_file = f"{content_id}.wav" # Assuming sound file matches content_id
            self.play_sound(sound_file)
        else:
            # Handle video playback failure (e.g., file not found)
            self.show_feedback(f"Error: Video '{content_id}.mp4' not found", (255, 0, 0)) # Red for error
            self.mode = Mode.WAITING # Go back to waiting

    def show_feedback(self, text, color=(255, 255, 255)): # Added color parameter
        """Show feedback text"""
        self.feedback_text = text
        # Render with the specified color
        self.feedback_surface = self.font.render(text, True, color)
        text_width, text_height = self.feedback_surface.get_size()
        self.feedback_rect = pygame.Rect(
            (self.screen_width - text_width) // 2,
            self.screen_height - text_height - 20,
            text_width, text_height
        )
        self.feedback_time = 0 # Reset timer
    
    def update(self, delta_time):
        """Update the application state"""
        # Update feedback timer
        if self.feedback_text:
            self.feedback_time += delta_time
            if self.feedback_time >= self.feedback_duration:
                self.feedback_text = None
                self.feedback_surface = None
        
        # Update video frame
        if self.mode == Mode.PLAYING:
            self.video_frame, self.video_complete = self.video_player.update()
            
            # Handle video completion
            if self.video_complete:
                self.mode = Mode.WAITING
    
    def play_sound(self, sound_name):
        """Play a sound (implemented by parent class)"""
        pass  # Implemented in DogPuter class
    
    def cleanup(self):
        """Clean up resources"""
        if self.video_player:
            self.video_player.cleanup()
