#!/usr/bin/env python3
"""
Simple transitions module for DogPuter on Raspberry Pi
This module provides simplified transition effects that minimize resource usage.
"""

import pygame
import time

class SimpleTransitions:
    """
    Simplified transitions for Raspberry Pi that minimize resource usage.
    These transitions are designed to work efficiently on Raspberry Pi hardware.
    """
    
    @staticmethod
    def fade_to_black(screen, duration=0.5, fps=15):
        """
        Simple fade to black transition that's light on resources.
        Uses fewer steps than a full 256-step fade.
        
        Args:
            screen: The pygame screen to apply the transition to
            duration: Length of the transition in seconds
            fps: Frames per second for the transition (lower = less CPU usage)
        """
        width, height = screen.get_size()
        overlay = pygame.Surface((width, height))
        overlay.fill((0, 0, 0))
        
        # Reduce number of steps for better performance
        steps = int(fps * duration)
        steps = min(steps, 10)  # Cap at 10 steps maximum
        
        for alpha in range(0, 256, 256 // steps):
            overlay.set_alpha(alpha)
            # Create a copy to avoid modifying the original
            temp = screen.copy()
            temp.blit(overlay, (0, 0))
            screen.blit(temp, (0, 0))
            pygame.display.flip()
            time.sleep(1/fps)
    
    @staticmethod
    def fade_from_black(screen, background, duration=0.5, fps=15):
        """
        Simple fade from black transition that's light on resources.
        
        Args:
            screen: The pygame screen to apply the transition to
            background: The background image/surface to fade to
            duration: Length of the transition in seconds
            fps: Frames per second for the transition (lower = less CPU usage)
        """
        width, height = screen.get_size()
        overlay = pygame.Surface((width, height))
        overlay.fill((0, 0, 0))
        
        # Reduce number of steps for better performance
        steps = int(fps * duration)
        steps = min(steps, 10)  # Cap at 10 steps maximum
        
        for alpha in range(255, -1, -256 // steps):
            # Draw background first
            screen.blit(background, (0, 0))
            # Then overlay with adjustable transparency
            overlay.set_alpha(alpha)
            screen.blit(overlay, (0, 0))
            pygame.display.flip()
            time.sleep(1/fps)
    
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
    
    @staticmethod
    def crossfade(screen, old_surface, new_surface, duration=0.3, fps=15):
        """
        Simple crossfade between two surfaces with minimal steps
        
        Args:
            screen: The pygame screen to apply the transition to
            old_surface: The current surface being displayed
            new_surface: The new surface to transition to
            duration: Length of the transition in seconds
            fps: Frames per second for the transition (lower = less CPU usage)
        """
        steps = int(fps * duration)
        steps = min(steps, 8)  # Even fewer steps for crossfade as it's more resource intensive
        
        for i in range(steps + 1):
            # Calculate alpha values
            alpha_new = int(255 * i / steps)
            
            # Make a copy of the old surface
            screen.blit(old_surface, (0, 0))
            
            # Blit the new surface with transparency
            new_surface.set_alpha(alpha_new)
            screen.blit(new_surface, (0, 0))
            
            # Update display
            pygame.display.flip()
            time.sleep(1/fps)
        
        # Ensure final frame is at full opacity
        new_surface.set_alpha(255)
        screen.blit(new_surface, (0, 0))
        pygame.display.flip()
