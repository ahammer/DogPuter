import pygame
import math
import time
import random
from dogputer.core.app_state import Mode, ContentType

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
        
        # Create background with a more dog-friendly color
        bg_surface = pygame.Surface((self.screen_width, self.screen_height))
        bg_surface.fill(waiting_content.bg_color)
        
        # Add subtle, non-chaotic background pattern (less random, more harmonious)
        current_time = time.time()
        
        # Create a few gentle gradients in the background
        for i in range(5):  # Reduced from 20 to 5 to be less chaotic
            # Use more predictable positions instead of fully random
            angle = math.pi * 2 * (i / 5) + current_time * 0.1  # Slow rotation
            distance = self.screen_height / 4
            
            x = int(self.screen_width/2 + math.cos(angle) * distance)
            y = int(self.screen_height/2 + math.sin(angle) * distance)
            
            size = 100  # Fixed size instead of random
            alpha = 15  # Fixed low alpha for subtlety
            
            # Create gradient glow
            for radius in range(size, 0, -10):
                fade_alpha = int(alpha * (radius / size))
                gradient_surface = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
                pygame.draw.circle(
                    gradient_surface, 
                    (255, 255, 255, fade_alpha), 
                    (radius, radius), 
                    radius
                )
                bg_surface.blit(gradient_surface, (x - radius, y - radius))
            
        view_state.add_command(RenderCommand("surface", surface=bg_surface, position=(0, 0), z_index=0))
        
        # Get current time for animations
        current_time = time.time()
        
        # Calculate enhanced pulse scale for text - more pronounced for dogs
        pulse_scale = 1.0 + 0.15 * abs(math.sin(current_time * 1.5))
        
        # Main message - larger and with contrasting colors
        from dogputer.core.config import YELLOW_PRIMARY, BLUE_PRIMARY, WHITE
        
        # Create a glowing background for text
        glow_surface = pygame.Surface((500, 200), pygame.SRCALPHA)
        glow_radius = 100 + int(20 * abs(math.sin(current_time * 1.2)))
        for radius in range(glow_radius, glow_radius - 20, -5):
            alpha = 5 + abs(math.sin(current_time * 2)) * 10
            pygame.draw.ellipse(
                glow_surface, 
                (*YELLOW_PRIMARY, alpha),
                (250 - radius, 100 - radius//2, radius * 2, radius),
            )
        glow_rect = glow_surface.get_rect(center=(self.screen_width/2, self.screen_height/2 - 50))
        view_state.add_command(RenderCommand("surface", surface=glow_surface, position=glow_rect, z_index=1))
        
        # Main message text with enhanced visibility
        main_font = pygame.font.SysFont(None, int(90 * pulse_scale))  # Larger text
        main_text = main_font.render("PAW A BUTTON", True, YELLOW_PRIMARY)
        
        # Create outline for better visibility
        outline_text = main_font.render("PAW A BUTTON", True, BLUE_PRIMARY)
        for offset in [(2, 2), (-2, 2), (2, -2), (-2, -2)]:  # Outline offsets
            outline_rect = outline_text.get_rect(center=(self.screen_width/2 + offset[0], self.screen_height/2 - 50 + offset[1]))
            view_state.add_command(RenderCommand("surface", surface=outline_text, position=outline_rect, z_index=2))
        
        main_rect = main_text.get_rect(center=(self.screen_width/2, self.screen_height/2 - 50))
        view_state.add_command(RenderCommand("surface", surface=main_text, position=main_rect, z_index=3))
        
        # Subtitle with better contrast
        sub_font = pygame.font.SysFont(None, 48)  # Larger text
        sub_text = sub_font.render("to play", True, WHITE)
        sub_rect = sub_text.get_rect(center=(self.screen_width/2, self.screen_height/2 + 30))
        view_state.add_command(RenderCommand("surface", surface=sub_text, position=sub_rect, z_index=2))
        
        # Draw animated paw cursor with enhanced animation
        if app_state.paw_cursor:
            # More dynamic animation curve for more interesting motion
            curve_x = self.screen_width/2 + math.sin(current_time * 1.5) * 200
            curve_y = self.screen_height/2 + 100 + math.cos(current_time * 1.2) * 50
            
            # Position based on animation frame but with added motion
            base_positions = [
                (self.screen_width/2 - 180, self.screen_height/2 + 100),  # Left
                (self.screen_width/2 - 60, self.screen_height/2 + 120),   # Middle-left
                (self.screen_width/2 + 60, self.screen_height/2 + 120),   # Middle-right
                (self.screen_width/2 + 180, self.screen_height/2 + 100)   # Right
            ]
            
            # Add some randomness to make more interesting for dogs
            jitter_x = random.randint(-5, 5)
            jitter_y = random.randint(-5, 5)
            
            # Get base position and add dynamic movement
            base_pos = base_positions[waiting_content.animation_frame]
            paw_x = base_pos[0] + jitter_x
            paw_y = base_pos[1] + jitter_y
            
            # Add animation path guidance
            next_frame = (waiting_content.animation_frame + 1) % 4
            next_pos = base_positions[next_frame]
            
            # Draw a hint path to the next position
            path_surface = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
            for i in range(1, 5):
                # Interpolate points between current and next position
                t = i / 5.0
                path_x = int(base_pos[0] + (next_pos[0] - base_pos[0]) * t)
                path_y = int(base_pos[1] + (next_pos[1] - base_pos[1]) * t)
                path_size = int(10 * (1 - t))  # Decreasing size along the path
                
                # Skip drawing paths on first frame
                if waiting_content.animation_frame == 0 and next_frame == 1:
                    pygame.draw.circle(
                        path_surface, 
                        (*YELLOW_PRIMARY, 100 * (1 - t)),
                        (path_x, path_y), 
                        path_size
                    )
            
            view_state.add_command(RenderCommand("surface", surface=path_surface, position=(0, 0), z_index=2))
            view_state.add_command(RenderCommand("surface", surface=app_state.paw_cursor, position=(paw_x, paw_y), z_index=3))
    
    def _generate_image_view(self, view_state, app_state):
        """Generate view state for image display with enhanced dog-friendly features"""
        from dogputer.core.config import YELLOW_PRIMARY, BLUE_PRIMARY
        
        image_content = app_state.content_state.image_content
        
        # Create a background frame to make it more visually distinctive for dogs
        # Dogs notice borders and frames more easily as it creates contrast
        frame_surface = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        
        # Draw a dog-friendly colored frame
        frame_thickness = 20
        frame_color = YELLOW_PRIMARY
        
        # Top frame
        pygame.draw.rect(frame_surface, frame_color, 
                         pygame.Rect(0, 0, self.screen_width, frame_thickness))
        # Bottom frame
        pygame.draw.rect(frame_surface, frame_color, 
                         pygame.Rect(0, self.screen_height - frame_thickness, 
                                    self.screen_width, frame_thickness))
        # Left frame
        pygame.draw.rect(frame_surface, frame_color, 
                         pygame.Rect(0, 0, frame_thickness, self.screen_height))
        # Right frame
        pygame.draw.rect(frame_surface, frame_color, 
                         pygame.Rect(self.screen_width - frame_thickness, 0, 
                                    frame_thickness, self.screen_height))
        
        # Add corner accents - dogs notice corners as focus points
        corner_size = 40
        
        # Top-left corner
        pygame.draw.rect(frame_surface, BLUE_PRIMARY, 
                        pygame.Rect(0, 0, corner_size, corner_size))
        # Top-right corner
        pygame.draw.rect(frame_surface, BLUE_PRIMARY, 
                        pygame.Rect(self.screen_width - corner_size, 0, 
                                   corner_size, corner_size))
        # Bottom-left corner
        pygame.draw.rect(frame_surface, BLUE_PRIMARY, 
                        pygame.Rect(0, self.screen_height - corner_size, 
                                   corner_size, corner_size))
        # Bottom-right corner
        pygame.draw.rect(frame_surface, BLUE_PRIMARY, 
                        pygame.Rect(self.screen_width - corner_size, 
                                   self.screen_height - corner_size, 
                                   corner_size, corner_size))
        
        if image_content.in_transition and image_content.previous_image and image_content.next_image:
            # Handle image transition with slower, more noticeable transition for dogs
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
            
            # Add transition effect - a sweeping highlight that moves across the screen
            sweep_width = 200
            sweep_x = int((self.screen_width + sweep_width) * eased_progress) - sweep_width
            
            sweep_surface = pygame.Surface((sweep_width, self.screen_height), pygame.SRCALPHA)
            for x in range(sweep_width):
                # Create a gradient effect
                alpha = int(100 * (1 - abs(x - sweep_width/2) / (sweep_width/2)))
                for y in range(0, self.screen_height, 4):  # Draw in strips for better performance
                    pygame.draw.line(
                        sweep_surface,
                        (*YELLOW_PRIMARY, alpha),
                        (x, y),
                        (x, y + 2),
                        1
                    )
            
            view_state.add_command(RenderCommand(
                "surface", 
                surface=sweep_surface, 
                position=(sweep_x, 0), 
                z_index=2
            ))
            
        elif image_content.current_image:
            # Display the current image
            view_state.add_command(RenderCommand(
                "surface", 
                surface=image_content.current_image, 
                position=(0, 0),
                z_index=0
            ))
            
            # Add subtle movement to corners to maintain dog's attention
            current_time = time.time()
            pulse_corner_size = int(corner_size + math.sin(current_time * 3) * 5)
            
            corner_surface = pygame.Surface((pulse_corner_size, pulse_corner_size), pygame.SRCALPHA)
            pygame.draw.rect(corner_surface, BLUE_PRIMARY, 
                           pygame.Rect(0, 0, pulse_corner_size, pulse_corner_size))
            pygame.draw.rect(corner_surface, YELLOW_PRIMARY, 
                           pygame.Rect(2, 2, pulse_corner_size-4, pulse_corner_size-4), 2)
            
            # Apply to one corner at a time, rotating for subtle motion
            corner_index = int(current_time) % 4
            if corner_index == 0:
                corner_pos = (0, 0)  # Top-left
            elif corner_index == 1:
                corner_pos = (self.screen_width - pulse_corner_size, 0)  # Top-right
            elif corner_index == 2:
                corner_pos = (0, self.screen_height - pulse_corner_size)  # Bottom-left
            else:
                corner_pos = (self.screen_width - pulse_corner_size, 
                             self.screen_height - pulse_corner_size)  # Bottom-right
                
            view_state.add_command(RenderCommand(
                "surface", 
                surface=corner_surface, 
                position=corner_pos,
                z_index=3
            ))
        
        # Draw frame on top
        view_state.add_command(RenderCommand(
            "surface", 
            surface=frame_surface, 
            position=(0, 0),
            z_index=5
        ))
    
    def _generate_video_view(self, view_state, app_state):
        """Generate view state for video display with dog-friendly enhancements"""
        from dogputer.core.config import BLUE_PRIMARY, YELLOW_PRIMARY, WHITE, VIDEO_CHANNELS
        
        video_content = app_state.content_state.video_content
        
        # Get the current video frame from the video player
        frame_result = video_content.video_player.update()
        
        # Handle the new return format (frame, is_complete)
        if isinstance(frame_result, tuple):
            frame, is_complete = frame_result
        else:
            # Backward compatibility for older version
            frame = frame_result
            is_complete = False
            
        if frame:
            # Display the frame
            view_state.add_command(RenderCommand(
                "surface", 
                surface=frame, 
                position=(0, 0),
                z_index=0
            ))
            
            # Create a TV-like frame that's distinctive from image frame
            # Dogs notice borders and frames more easily as it creates contrast
            frame_surface = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
            
            # Current time for animations
            current_time = time.time()
            
            # Create a rounded rectangle frame for video (different from image frame)
            frame_thickness = 25
            
            # Draw animated corners to catch dog's attention
            corner_length = 80
            angle_offset = math.sin(current_time * 2) * 0.1  # Small oscillation
            
            # Top left corner
            start_pos = (0, corner_length)
            end_pos = (corner_length, 0)
            pygame.draw.line(frame_surface, BLUE_PRIMARY, start_pos, end_pos, frame_thickness)
            
            # Top right corner
            start_pos = (self.screen_width - corner_length, 0)
            end_pos = (self.screen_width, corner_length)
            pygame.draw.line(frame_surface, BLUE_PRIMARY, start_pos, end_pos, frame_thickness)
            
            # Bottom left corner
            start_pos = (0, self.screen_height - corner_length)
            end_pos = (corner_length, self.screen_height)
            pygame.draw.line(frame_surface, BLUE_PRIMARY, start_pos, end_pos, frame_thickness)
            
            # Bottom right corner
            start_pos = (self.screen_width - corner_length, self.screen_height)
            end_pos = (self.screen_width, self.screen_height - corner_length)
            pygame.draw.line(frame_surface, BLUE_PRIMARY, start_pos, end_pos, frame_thickness)
            
            # Add pulsing indicator to show this is a video
            pulse_alpha = int(100 + 100 * abs(math.sin(current_time * 3)))
            indicator_size = 30
            
            # Create a small "playing" indicator in one corner
            indicator_surface = pygame.Surface((indicator_size * 3, indicator_size), pygame.SRCALPHA)
            
            # Draw three circles in a row (like a play symbol)
            pygame.draw.circle(indicator_surface, 
                              (*YELLOW_PRIMARY, pulse_alpha), 
                              (indicator_size // 2, indicator_size // 2), 
                              indicator_size // 2 - 2)
            pygame.draw.circle(indicator_surface, 
                              (*YELLOW_PRIMARY, pulse_alpha), 
                              (indicator_size + indicator_size // 2, indicator_size // 2), 
                              indicator_size // 2 - 2)
            pygame.draw.circle(indicator_surface, 
                              (*YELLOW_PRIMARY, pulse_alpha), 
                              (2 * indicator_size + indicator_size // 2, indicator_size // 2), 
                              indicator_size // 2 - 2)
            
            # Position in top-right corner, inside the frame
            indicator_pos = (self.screen_width - 3 * indicator_size - 20, 20)
            frame_surface.blit(indicator_surface, indicator_pos)
            
            # Removed channel name overlay per feedback - channels should be treated like any other button press
            
            view_state.add_command(RenderCommand(
                "surface", 
                surface=frame_surface, 
                position=(0, 0),
                z_index=5
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
        """Generate view state for feedback overlay with dog-friendly icons instead of text"""
        from dogputer.core.config import (
            BLUE_PRIMARY, YELLOW_PRIMARY, WHITE, FEEDBACK_HEIGHT,
            SUCCESS_COLOR, ERROR_COLOR, FEEDBACK_DURATION
        )
        
        feedback_state = app_state.feedback_state
        
        # Determine icon type based on feedback message
        is_success = "accepted" in feedback_state.message.lower() or "selected" in feedback_state.message.lower()
        is_error = "rejected" in feedback_state.message.lower() or "too fast" in feedback_state.message.lower()
        is_channel = "channel" in feedback_state.message.lower()
        
        # Skip channels as per feedback instructions - this will be handled differently
        if is_channel:
            return
        
        # Create and position the feedback icon in the center of the screen
        icon_size = 120  # Large size for dogs to see clearly
        icon_surface = pygame.Surface((icon_size, icon_size), pygame.SRCALPHA)
        
        # Calculate animation progress with easing
        progress = 0
        if feedback_state.is_animating():
            raw_progress = feedback_state.get_animation_progress()
            # Ease in and out for smoother animation
            progress = math.sin(raw_progress * math.pi / 2)
        else:
            progress = 1.0
            
        # Create a growing/shrinking effect
        scale_factor = 0.8 + 0.4 * progress
        current_size = int(icon_size * scale_factor)
        
        # Draw appropriate icon based on feedback type
        if is_success:
            # Draw checkmark for success
            icon_color = YELLOW_PRIMARY
            thickness = max(6, int(10 * progress))  # Thicker lines for visibility
            
            # Draw circular background
            bg_radius = current_size // 2 - 5
            pygame.draw.circle(
                icon_surface,
                BLUE_PRIMARY,
                (icon_size // 2, icon_size // 2),
                bg_radius
            )
            
            # Draw checkmark
            start_x = icon_size // 4
            mid_x = icon_size // 2.5
            mid_y = icon_size * 3 // 4
            end_x = icon_size * 3 // 4
            end_y = icon_size // 3
            
            # Draw first line of checkmark
            pygame.draw.line(
                icon_surface,
                icon_color,
                (start_x, mid_y),
                (mid_x, mid_y),
                thickness
            )
            
            # Draw second line of checkmark
            pygame.draw.line(
                icon_surface,
                icon_color,
                (mid_x, mid_y),
                (end_x, end_y),
                thickness
            )
            
            # Add a glowing outline
            glow_radius = bg_radius + 6
            glow_alpha = int(150 * progress)
            glow_surface = pygame.Surface((icon_size, icon_size), pygame.SRCALPHA)
            pygame.draw.circle(
                glow_surface,
                (*YELLOW_PRIMARY, glow_alpha),
                (icon_size // 2, icon_size // 2),
                glow_radius
            )
            
            # Blit glow behind the icon
            icon_surface.blit(glow_surface, (0, 0), special_flags=pygame.BLEND_ALPHA_SDL2)
            
        elif is_error:
            # Draw X for error/rejection
            icon_color = ERROR_COLOR
            thickness = max(6, int(10 * progress))  # Thicker lines for visibility
            
            # Draw circular background
            bg_radius = current_size // 2 - 5
            pygame.draw.circle(
                icon_surface,
                BLUE_PRIMARY,
                (icon_size // 2, icon_size // 2),
                bg_radius
            )
            
            # Calculate X positions
            padding = icon_size // 4
            
            # Draw first line of X
            pygame.draw.line(
                icon_surface,
                icon_color,
                (padding, padding),
                (icon_size - padding, icon_size - padding),
                thickness
            )
            
            # Draw second line of X
            pygame.draw.line(
                icon_surface,
                icon_color,
                (icon_size - padding, padding),
                (padding, icon_size - padding),
                thickness
            )
            
            # Add a glowing outline for error
            glow_radius = bg_radius + 6
            glow_alpha = int(150 * progress)
            glow_surface = pygame.Surface((icon_size, icon_size), pygame.SRCALPHA)
            pygame.draw.circle(
                glow_surface,
                (*ERROR_COLOR, glow_alpha),
                (icon_size // 2, icon_size // 2),
                glow_radius
            )
            
            # Blit glow behind the icon
            icon_surface.blit(glow_surface, (0, 0), special_flags=pygame.BLEND_ALPHA_SDL2)
        else:
            # Generic feedback - blue circle
            bg_radius = current_size // 2
            pygame.draw.circle(
                icon_surface,
                feedback_state.color,
                (icon_size // 2, icon_size // 2),
                bg_radius
            )
            
            # Add outline
            outline_radius = bg_radius - 3
            pygame.draw.circle(
                icon_surface,
                WHITE,
                (icon_size // 2, icon_size // 2),
                outline_radius,
                3
            )
        
        # Position icon in center of screen
        icon_position = (
            (self.screen_width - icon_size) // 2,
            (self.screen_height - icon_size) // 2
        )
        
        # Add to view state
        view_state.add_command(RenderCommand(
            "surface", 
            surface=icon_surface, 
            position=icon_position,
            z_index=15  # Always on top
        ))
        
        # Add a whole-screen flash if animating
        if feedback_state.is_animating():
            # Create a quick flash that fades out
            flash_alpha = int(80 * (1 - progress))  # Less intense flash
            
            # Choose appropriate flash color
            flash_color = YELLOW_PRIMARY if is_success else ERROR_COLOR if is_error else feedback_state.color
            
            flash_surface = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
            flash_surface.fill((*flash_color, flash_alpha))
            
            view_state.add_command(RenderCommand(
                "surface", 
                surface=flash_surface, 
                position=(0, 0),
                z_index=14  # Just below the feedback but above everything else
            ))
