#!/usr/bin/env python3
"""
Simplified video player module for DogPuter
This module provides basic video playback functionality using moviepy.
It focuses on minimal resource usage for low-powered hardware.
"""

import os
import pygame
import time
import numpy as np
from moviepy import VideoFileClip

class VideoPlayer:
    """Simplified video player class for DogPuter"""
    
    def __init__(self, screen, videos_dir="media/videos"):
        """Initialize the video player"""
        self.screen = screen
        self.videos_dir = videos_dir
        self.current_video = None
        self.start_time = 0
        self.paused = False
        
        # Queue for next video
        self.next_video_file = None
        
        # Create videos directory if it doesn't exist
        os.makedirs(self.videos_dir, exist_ok=True)
    
    def _scale_preserve_ratio(self, surface):
        """Scale a surface to fit the screen while preserving aspect ratio"""
        # Get dimensions
        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()
        surface_width = surface.get_width()
        surface_height = surface.get_height()
        
        # Calculate aspect ratios
        screen_ratio = screen_width / screen_height
        surface_ratio = surface_width / surface_height
        
        # Scale based on which dimension is the limiting factor
        if screen_ratio > surface_ratio:
            # Screen is wider than surface - scale to width
            scale_factor = screen_width / surface_width
        else:
            # Screen is taller than surface - scale to height
            scale_factor = screen_height / surface_height
        
        # Calculate new dimensions
        new_width = int(surface_width * scale_factor)
        new_height = int(surface_height * scale_factor)
        
        # Scale surface
        scaled_surface = pygame.transform.scale(surface, (new_width, new_height))
        
        # Create a new surface of screen size
        result_surface = pygame.Surface((screen_width, screen_height))
        
        # Center the scaled surface on the result surface
        x_offset = (screen_width - new_width) // 2
        y_offset = (screen_height - new_height) // 2
        
        # Blit the scaled surface onto the result surface
        result_surface.blit(scaled_surface, (x_offset, y_offset))
        
        return result_surface
    
    def play_video(self, video_file):
        """Play a video"""
        video_path = os.path.join(self.videos_dir, video_file)
        
        # Check if file exists
        if not os.path.exists(video_path):
            print(f"Video file not found: {video_path}")
            return False
        
        try:
            # Close current video if any
            if self.current_video:
                self.current_video.close()
            
            # Load new video
            self.current_video = VideoFileClip(video_path)
            self.start_time = time.time()
            self.paused = False
            print(f"Started playing video: {video_file}")
            return True
        except Exception as e:
            print(f"Error loading video: {e}")
            self.current_video = None
            return False
    
    def queue_video(self, video_file):
        """Queue a video to play after current video ends"""
        self.next_video_file = video_file
    
    def update(self):
        """Update the video player, return current frame"""
        # Check if we need to start the next video
        if not self.current_video and self.next_video_file:
            self.play_video(self.next_video_file)
            self.next_video_file = None
        
        # If no video is playing, return None
        if not self.current_video:
            return None, False
        
        try:
            # Calculate time position within video
            if self.paused:
                current_pos = self.pause_time
            else:
                current_pos = time.time() - self.start_time
            
            # Check if video is complete
            if current_pos >= self.current_video.duration:
                # If we have a queued video, play it next
                if self.next_video_file:
                    next_video = self.next_video_file
                    self.next_video_file = None
                    self.play_video(next_video)
                    return self.update()
                else:
                    # Video is complete
                    self.current_video.close()
                    self.current_video = None
                    return None, True
            
            # Get frame at current position
            try:
                frame = self.current_video.get_frame(current_pos)
                # Convert to pygame surface
                frame_surface = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
                frame_surface = self._scale_preserve_ratio(frame_surface)
                return frame_surface, False
            except Exception as e:
                print(f"Error getting frame: {e}")
                return None, False
        
        except Exception as e:
            print(f"Error updating video: {e}")
            self.current_video = None
            return None, True
    
    def pause(self):
        """Pause the video"""
        if self.current_video and not self.paused:
            self.paused = True
            self.pause_time = time.time() - self.start_time
    
    def resume(self):
        """Resume the video"""
        if self.current_video and self.paused:
            self.paused = False
            self.start_time = time.time() - self.pause_time
    
    def stop(self):
        """Stop the video"""
        if self.current_video:
            self.current_video.close()
            self.current_video = None
    
    def cleanup(self):
        """Clean up resources"""
        if self.current_video:
            self.current_video.close()
