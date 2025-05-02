import pygame

class Renderer:
    """Simplified renderer class for DogPuter"""
    
    def __init__(self, screen):
        """Initialize the renderer"""
        self.screen = screen
    
    def render(self, view_state):
        """Render the view state to the screen"""
        # Fill screen with background color
        self.screen.fill(view_state.background_color)
        
        # Render current video frame if available
        if view_state.video_frame:
            self.screen.blit(view_state.video_frame, (0, 0))
        
        # Render feedback text if available
        if view_state.feedback_text:
            self.screen.blit(view_state.feedback_text, view_state.feedback_rect)
        
        # Render waiting text if available
        if view_state.waiting_text:
            self.screen.blit(view_state.waiting_text, view_state.waiting_text_rect)
