#!/usr/bin/env python3
"""
Video player module for DogPuter
This module provides video playback functionality using moviepy.
It can be integrated with the main DogPuter application to enable video playback.
Includes transition effects between videos.
"""

import os
import pygame
import sys
import time
import numpy as np
from moviepy import VideoFileClip

class VideoPlayer:
    """Video player class for DogPuter"""
    
    def __init__(self, screen, videos_dir="media/videos"):
        """Initialize the video player"""
        self.screen = screen
        self.videos_dir = videos_dir
        self.current_video = None
        self.video_surface = None
        self.start_time = 0
        self.paused = False
        self.pause_time = 0
        
        # Transition settings
        self.transition_duration = 1.0  # seconds
        self.in_transition = False
        self.transition_start_time = 0
        self.previous_frame = None
        self.next_video = None
        
        # Create videos directory if it doesn't exist
        os.makedirs(self.videos_dir, exist_ok=True)
    
    def _scale_preserve_ratio(self, surface):
        """
        Scale a surface to fit the screen while preserving aspect ratio.
        This will crop the video if needed to ensure the screen is filled.
        """
        # Get dimensions
        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()
        surface_width = surface.get_width()
        surface_height = surface.get_height()
        
        # Calculate aspect ratios
        screen_ratio = screen_width / screen_height
        surface_ratio = surface_width / surface_height
        
        # Calculate new dimensions that preserve aspect ratio
        if screen_ratio > surface_ratio:
            # Screen is wider than video, fit to width and crop height
            new_width = screen_width
            new_height = int(new_width / surface_ratio)
        else:
            # Screen is taller than video, fit to height and crop width
            new_height = screen_height
            new_width = int(new_height * surface_ratio)
        
        # Scale the surface
        scaled_surface = pygame.transform.scale(surface, (new_width, new_height))
        
        # Create a new surface for the final result
        result_surface = pygame.Surface((screen_width, screen_height))
        
        # Calculate position to center the content (may be negative if cropping)
        x_offset = (screen_width - new_width) // 2
        y_offset = (screen_height - new_height) // 2
        
        # Blit the scaled surface onto the result surface
        result_surface.blit(scaled_surface, (x_offset, y_offset))
        
        return result_surface
    
    def play_video(self, video_file):
        """Play a video file or handle placeholder text files"""
        try:
            video_path = os.path.join(self.videos_dir, video_file)
            placeholder_path = video_path + ".txt"
            
            # Check if the file is a placeholder text file
            if os.path.exists(placeholder_path):
                # It's a placeholder text file, read its content
                with open(placeholder_path, "r") as f:
                    placeholder_text = f.read().strip()
                
                # Create a text frame to display
                self._create_text_frame(placeholder_text, video_file)
                print(f"Displaying placeholder for video: {video_file}")
                return True
            
            # Check if the actual video file exists
            elif os.path.exists(video_path):
                # If a video is already playing, start a transition
                if self.current_video:
                    # Store the current frame for transition
                    current_time = time.time() - self.start_time
                    if current_time > self.current_video.duration:
                        current_time = 0
                    try:
                        frame = self.current_video.get_frame(current_time)
                        frame_surface = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
                        frame_surface = self._scale_preserve_ratio(frame_surface)
                        self.previous_frame = frame_surface
                    except Exception:
                        self.previous_frame = None
                    
                    # Set up transition
                    self.in_transition = True
                    self.transition_start_time = time.time()
                    
                    # Load the new video but don't start playing yet
                    self.next_video = VideoFileClip(video_path)
                    
                    print(f"Transitioning to video: {video_file}")
                    return True
                else:
                    # No video playing, just start the new one
                    self.current_video = VideoFileClip(video_path)
                    
                    # Set up the video surface
                    self.video_surface = pygame.Surface((self.screen.get_width(), self.screen.get_height()))
                    
                    # Start playing
                    self.start_time = time.time()
                    self.paused = False
                    
                    print(f"Playing video: {video_file}")
                    return True
            else:
                # Neither the video nor a placeholder exists
                print(f"Video not found: {video_file}")
                return False
        except Exception as e:
            print(f"Error playing video: {e}")
            self.current_video = None
            self.next_video = None
            self.in_transition = False
            return False
    
    def stop(self):
        """Stop the current video"""
        if self.current_video:
            self.current_video.close()
            self.current_video = None
            self.video_surface = None
            self.paused = False
        
        if self.next_video:
            self.next_video.close()
            self.next_video = None
        
        self.in_transition = False
        self.previous_frame = None
    
    def pause(self):
        """Pause the current video"""
        if self.current_video and not self.paused:
            self.paused = True
            self.pause_time = time.time() - self.start_time
    
    def resume(self):
        """Resume the paused video"""
        if self.current_video and self.paused:
            self.paused = False
            self.start_time = time.time() - self.pause_time
    
    def toggle_pause(self):
        """Toggle pause state"""
        if self.paused:
            self.resume()
        else:
            self.pause()
    
    def _create_text_frame(self, text, title):
        """Create a frame with text for placeholder videos"""
        # Create a surface for the text frame
        surface = pygame.Surface((self.screen.get_width(), self.screen.get_height()))
        surface.fill((30, 30, 30))  # Dark gray background
        
        # Create a font for the title and text
        title_font = pygame.font.SysFont(None, 48)
        text_font = pygame.font.SysFont(None, 36)
        
        # Render the title
        title_text = title_font.render(f"Channel: {title.replace('.mp4', '')}", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(self.screen.get_width()/2, 100))
        surface.blit(title_text, title_rect)
        
        # Render the placeholder text
        lines = text.split('\n')
        y_pos = 200
        for line in lines:
            if line.strip():  # Skip empty lines
                text_surface = text_font.render(line, True, (200, 200, 200))
                text_rect = text_surface.get_rect(center=(self.screen.get_width()/2, y_pos))
                surface.blit(text_surface, text_rect)
                y_pos += 40
        
        # Store this as our "video" frame
        self.video_surface = surface
        self.start_time = time.time()
        
        # Set a fake duration
        self.current_video = None
        
        return surface
        
    def update(self):
        """Update the video frame"""
        # If we're displaying a text placeholder, just return the surface
        if self.current_video is None and self.video_surface is not None:
            return self.video_surface, False  # Return (surface, is_complete)
        # Handle transition between videos
        if self.in_transition:
            transition_time = time.time() - self.transition_start_time
            
            # If transition is complete, switch to the next video
            if transition_time >= self.transition_duration:
                if self.current_video:
                    self.current_video.close()
                
                self.current_video = self.next_video
                self.next_video = None
                self.in_transition = False
                self.previous_frame = None
                self.start_time = time.time()
                
                # Return the first frame of the new video
                if self.current_video:
                    try:
                        frame = self.current_video.get_frame(0)
                        frame_surface = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
                        frame_surface = self._scale_preserve_ratio(frame_surface)
                        return frame_surface, False  # Not in transition, not complete
                    except Exception as e:
                        print(f"Error getting first frame of new video: {e}")
                        return None
            
            # Create transition effect (fade)
            elif self.previous_frame and self.next_video:
                try:
                    # Calculate transition progress (0.0 to 1.0)
                    progress = transition_time / self.transition_duration
                    
                    # Get frame from the next video
                    next_frame = self.next_video.get_frame(0)
                    next_surface = pygame.surfarray.make_surface(next_frame.swapaxes(0, 1))
                    next_surface = self._scale_preserve_ratio(next_surface)
                    
                    # Create a new surface for the blended frame
                    blended_surface = pygame.Surface((self.screen.get_width(), self.screen.get_height()))
                    
                    # Set alpha values for the blend
                    self.previous_frame.set_alpha(int(255 * (1 - progress)))
                    next_surface.set_alpha(int(255 * progress))
                    
                    # Blit both surfaces onto the blended surface
                    blended_surface.blit(self.previous_frame, (0, 0))
                    blended_surface.blit(next_surface, (0, 0))
                    
                    return blended_surface, False  # Not complete
                except Exception as e:
                    print(f"Error creating transition: {e}")
                    # If transition fails, just switch to the next video
                    self.in_transition = False
                    if self.current_video:
                        self.current_video.close()
                    self.current_video = self.next_video
                    self.next_video = None
                    self.start_time = time.time()
        
        # Normal video playback
        if not self.current_video or self.paused:
            return None, False  # Not complete
        
        # Calculate the current position in the video
        current_time = time.time() - self.start_time
        
        # Check if the video has ended
        if current_time > self.current_video.duration:
            # Signal that the video has completed
            return None, True
        
        try:
            # Get the current frame
            frame = self.current_video.get_frame(current_time)
            
            # Convert the frame to a pygame surface
            frame_surface = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
            
            # Scale the frame to fit the screen while preserving aspect ratio
            frame_surface = self._scale_preserve_ratio(frame_surface)
            
            return frame_surface, False  # Not complete
        except Exception as e:
            print(f"Error updating video frame: {e}")
            return None, False

def main():
    """Main function for testing the video player"""
    # Initialize pygame
    pygame.init()
    
    # Set up display
    screen_width = 800
    screen_height = 600
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("DogPuter Video Player Test")
    
    # Create video player
    player = VideoPlayer(screen)
    
    # Check if a video file was specified
    if len(sys.argv) > 1:
        video_file = sys.argv[1]
    else:
        # Default test video
        video_file = "squirrels.mp4"
    
    # Try to play the video
    if not player.play_video(video_file):
        print(f"Could not play video: {video_file}")
        print("Please make sure the video file exists in the 'videos' directory.")
        pygame.quit()
        sys.exit(1)
    
    # Main loop
    running = True
    clock = pygame.time.Clock()
    
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    player.toggle_pause()
        
        # Clear the screen
        screen.fill((0, 0, 0))
        
        # Update and display the video frame
        frame_result = player.update()
        
        # Handle the new return format (frame, is_complete)
        if isinstance(frame_result, tuple):
            frame, is_complete = frame_result
        else:
            # Backward compatibility for older code
            frame = frame_result
            is_complete = False
            
        if frame:
            screen.blit(frame, (0, 0))
        
        # Update the display
        pygame.display.flip()
        
        # Cap the frame rate
        clock.tick(30)
    
    # Clean up
    player.stop()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
