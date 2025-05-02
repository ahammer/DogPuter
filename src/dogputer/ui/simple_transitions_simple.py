"""
Simple transitions module for DogPuter on Raspberry Pi
This module provides simplified transition effects that minimize resource usage.
"""

import pygame

class SimpleTransitions:
    """
    Simplified transitions for Raspberry Pi that minimize resource usage.
    These transitions are designed to work efficiently on Raspberry Pi hardware.
    """
    
    @staticmethod
    def simple_cut(screen, new_surface):
        """
        Instant cut transition (no animation)
        This is the most performant transition option.
        
        Args:
            screen: The pygame screen to apply the transition to
            new_surface: The new surface to display
        """
        screen.blit(new_surface, (0, 0))
        pygame.display.flip()
    
    # For compatibility with existing code, provide stub methods that all use simple_cut
    
    @staticmethod
    def fade_to_black(screen, duration=0.5, fps=15):
        """Stub - uses no fade for performance"""
        pass  # No operation, handled by the app_state
    
    @staticmethod
    def fade_from_black(screen, background, duration=0.5, fps=15):
        """Stub - uses no fade for performance"""
        SimpleTransitions.simple_cut(screen, background)
    
    @staticmethod
    def crossfade(screen, old_surface, new_surface, duration=0.3, fps=15):
        """Stub - uses direct cut for performance"""
        SimpleTransitions.simple_cut(screen, new_surface)
