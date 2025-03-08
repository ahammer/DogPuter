import pygame
import math
import time
from app_state import Mode, ContentType

class RenderCommand:
    """A command to render something to the screen"""
    
    def __init__(self, type_name, surface=None, position=None, color=None, alpha=255, z_index=0, thickness=1, text=None, font=None):
        self.type = type_name  # "surface", "rect", "text"
        self.surface = surface
        self.position = position  # Rect or (x, y) tuple
        self.color = color
        self.alpha = alpha
        self.z_index = z_index
        self.thickness = thickness
        self.text = text
        self.font = font

class ViewState:
    """Represents the current view state to be rendered"""
    
    def __init__(self):
        self.render_commands = []
    
    def add_command(self, command):
        """Add a render command to the view state"""
        self.render_commands.append(command)
    
    def sort_commands(self):
        """Sort render commands by z-index"""
        self.render_commands.sort(key=lambda cmd: cmd.z_index)

class ViewStateGenerator:
    """Generates a view state from the application state"""
    
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
    
    def generate_view_state(self, app_state):
        """Generate a view state from the application state"""
        view_state = ViewState()
        
        # Generate view based on current mode
        if app_state.mode == Mode.WAITING:
            self._generate_waiting_screen_view(view_state, app_state)
        elif app_state.mode == Mode.IMAGE:
            self._generate_image_view(view_state, app_state)
        elif app_state.mode == Mode.VIDEO:
            self._generate_video_view(view_state, app_state)
        elif app_state.mode == Mode.TEXT:
            self._generate_text_view(view_state, app_state)
        
        # Add feedback overlay if active
        if app_state.feedback_state.is_active:
            self._generate_feedback_view(view_state, app_state)
        
        # Sort commands by z-index
        view_state.sort_commands()
        
        return view_state
    
    def _generate_waiting_screen_view(self, view_state, app_state):
        """Generate view state for waiting screen"""
        waiting_content = app_state.content_state.waiting_content
        
        # Create background
        bg_surface = pygame.Surface((self.screen_width, self.screen_height))
        bg_surface.fill(waiting_content.bg_color)
        view_state.add_command(RenderCommand("surface", surface=bg_surface, position=(0, 0), z_index=0))
        
        # Get current time for animations
        current_time = time.time()
        
        # Calculate pulse scale for text
        pulse_scale = 1.0 + 0.1 * abs(math.sin(current_time * 2))
        
        # Main message
        main_font = pygame.font.SysFont(None, int(72 * pulse_scale))
        main_text = main_font.render("Paw a Key", True, (255, 255, 255))
        main_rect = main_text.get_rect(center=(self.screen_width/2, self.screen_height/2 - 50))
        view_state.add_command(RenderCommand("surface", surface=main_text, position=main_rect, z_index=1))
        
        # Subtitle
        sub_font = pygame.font.SysFont(None, 36)
        sub_text = sub_font.render("to start", True, (200, 200, 200))
        sub_rect = sub_text.get_rect(center=(self.screen_width/2, self.screen_height/2 + 20))
        view_state.add_command(RenderCommand("surface", surface=sub_text, position=sub_rect, z_index=1))
        
        # Draw animated paw cursor
        if app_state.paw_cursor:
            # Position based on animation frame
            positions = [
                (self.screen_width/2 - 150, self.screen_height/2 + 100),  # Left
                (self.screen_width/2 - 50, self.screen_height/2 + 120),   # Middle-left
                (self.screen_width/2 + 50, self.screen_height/2 + 120),   # Middle-right
                (self.screen_width/2 + 150, self.screen_height/2 + 100)   # Right
            ]
            
            paw_pos = positions[waiting_content.animation_frame]
            view_state.add_command(RenderCommand("surface", surface=app_state.paw_cursor, position=paw_pos, z_index=1))
    
    def _generate_image_view(self, view_state, app_state):
        """Generate view state for image display"""
        image_content = app_state.content_state.image_content
        
        if image_content.in_transition and image_content.previous_image and image_content.next_image:
            # Handle image transition
            progress = image_content.get_transition_progress()
            
            # Use sine easing for smoother transition
            eased_progress = math.sin(progress * math.pi / 2)
            
            # Add previous image with fading alpha
            prev_alpha = int(255 * (1 - eased_progress))
            view_state.add_command(RenderCommand(
                "surface", 
                surface=image_content.previous_image, 
                position=(0, 0), 
                alpha=prev_alpha,
                z_index=0
            ))
            
            # Add next image with increasing alpha
            next_alpha = int(255 * eased_progress)
            view_state.add_command(RenderCommand(
                "surface", 
                surface=image_content.next_image, 
                position=(0, 0), 
                alpha=next_alpha,
                z_index=1
            ))
        elif image_content.current_image:
            # Just display the current image
            view_state.add_command(RenderCommand(
                "surface", 
                surface=image_content.current_image, 
                position=(0, 0),
                z_index=0
            ))
    
    def _generate_video_view(self, view_state, app_state):
        """Generate view state for video display"""
        video_content = app_state.content_state.video_content
        
        # Get the current video frame from the video player
        frame = video_content.video_player.update()
        if frame:
            view_state.add_command(RenderCommand(
                "surface", 
                surface=frame, 
                position=(0, 0),
                z_index=0
            ))
    
    def _generate_text_view(self, view_state, app_state):
        """Generate view state for text display"""
        text_content = app_state.content_state.text_content
        
        if text_content.surface:
            view_state.add_command(RenderCommand(
                "surface", 
                surface=text_content.surface, 
                position=(0, 0),
                z_index=0
            ))
    
    def _generate_feedback_view(self, view_state, app_state):
        """Generate view state for feedback overlay"""
        feedback_state = app_state.feedback_state
        
        # Create semi-transparent overlay for feedback
        feedback_surface = pygame.Surface((self.screen_width, 50), pygame.SRCALPHA)
        feedback_surface.fill((0, 0, 0, 180))  # Semi-transparent black
        
        # Render feedback text
        feedback_text = app_state.feedback_font.render(feedback_state.message, True, feedback_state.color)
        feedback_rect = feedback_text.get_rect(center=(self.screen_width/2, 25))
        
        # Blit to feedback surface
        feedback_surface.blit(feedback_text, feedback_rect)
        
        # Add feedback surface to view state
        view_state.add_command(RenderCommand(
            "surface", 
            surface=feedback_surface, 
            position=(0, self.screen_height - 50),
            z_index=10  # Always on top
        ))
        
        # Add animated outline if within animation duration
        if feedback_state.is_animating():
            # Calculate animation progress (0.0 to 1.0)
            progress = feedback_state.get_animation_progress()
            
            # Calculate outline thickness based on animation progress (starts thick, gets thinner)
            thickness = int(10 * (1 - progress))
            
            # Add rectangle outline to view state
            view_state.add_command(RenderCommand(
                "rect", 
                position=pygame.Rect(0, 0, self.screen_width, self.screen_height), 
                color=feedback_state.color,
                thickness=thickness,
                z_index=20  # Always on top of everything
            ))
