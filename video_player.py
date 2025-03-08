#!/usr/bin/env python3
"""
Video player module for DogPuter
This module provides video playback functionality using moviepy.
It can be integrated with the main DogPuter application to enable video playback.
"""

import os
import pygame
import sys
import time
from moviepy import VideoFileClip

class VideoPlayer:
    """Video player class for DogPuter"""
    
    def __init__(self, screen, videos_dir="videos"):
        """Initialize the video player"""
        self.screen = screen
        self.videos_dir = videos_dir
        self.current_video = None
        self.video_surface = None
        self.start_time = 0
        self.paused = False
        self.pause_time = 0
        
        # Create videos directory if it doesn't exist
        os.makedirs(self.videos_dir, exist_ok=True)
    
    def play_video(self, video_file):
        """Play a video file"""
        try:
            # Stop any currently playing video
            self.stop()
            
            # Load the new video
            video_path = os.path.join(self.videos_dir, video_file)
            self.current_video = VideoFileClip(video_path)
            
            # Set up the video surface
            self.video_surface = pygame.Surface((self.screen.get_width(), self.screen.get_height()))
            
            # Start playing
            self.start_time = time.time()
            self.paused = False
            
            print(f"Playing video: {video_file}")
            return True
        except Exception as e:
            print(f"Error playing video: {e}")
            self.current_video = None
            return False
    
    def stop(self):
        """Stop the current video"""
        if self.current_video:
            self.current_video.close()
            self.current_video = None
            self.video_surface = None
            self.paused = False
    
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
    
    def update(self):
        """Update the video frame"""
        if not self.current_video or self.paused:
            return None
        
        # Calculate the current position in the video
        current_time = time.time() - self.start_time
        
        # Check if the video has ended
        if current_time > self.current_video.duration:
            # Loop the video by resetting the start time
            self.start_time = time.time()
            current_time = 0
        
        try:
            # Get the current frame
            frame = self.current_video.get_frame(current_time)
            
            # Convert the frame to a pygame surface
            frame_surface = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
            
            # Scale the frame to fit the screen
            frame_surface = pygame.transform.scale(frame_surface, 
                                                 (self.screen.get_width(), self.screen.get_height()))
            
            return frame_surface
        except Exception as e:
            print(f"Error updating video frame: {e}")
            return None

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
        frame = player.update()
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
