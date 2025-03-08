import pygame

class Renderer:
    """Handles rendering of view state to the screen"""
    
    def __init__(self, screen):
        """Initialize the renderer with a pygame screen"""
        self.screen = screen
    
    def render(self, view_state):
        """Render the view state to the screen"""
        # Clear the screen
        self.screen.fill((0, 0, 0))
        
        # Process each render command
        for command in view_state.render_commands:
            if command.type == "surface":
                self._render_surface(command)
            elif command.type == "rect":
                self._render_rect(command)
            elif command.type == "text":
                self._render_text(command)
    
    def _render_surface(self, command):
        """Render a surface to the screen"""
        if command.surface is None:
            return
        
        # Handle alpha if specified
        if command.alpha < 255:
            # Create a copy of the surface with the specified alpha
            temp_surface = command.surface.copy()
            temp_surface.set_alpha(command.alpha)
            self.screen.blit(temp_surface, command.position)
        else:
            # Blit the surface directly
            self.screen.blit(command.surface, command.position)
    
    def _render_rect(self, command):
        """Render a rectangle to the screen"""
        if command.position is None or command.color is None:
            return
        
        # Draw the rectangle
        pygame.draw.rect(
            self.screen,
            command.color,
            command.position,
            command.thickness
        )
    
    def _render_text(self, command):
        """Render text to the screen"""
        if command.text is None or command.font is None or command.position is None:
            return
        
        # Render the text
        text_surface = command.font.render(command.text, True, command.color)
        self.screen.blit(text_surface, command.position)
