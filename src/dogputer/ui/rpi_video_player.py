#!/usr/bin/env python3
"""
Hardware-accelerated video player module for DogPuter on Raspberry Pi
This module provides video playback functionality using OMXPlayer for hardware acceleration.
It serves as a drop-in replacement for the standard VideoPlayer class.
"""

import os
import pygame
import sys
import time
import signal
import subprocess
import threading

class RPiVideoPlayer:
    """Video player class for DogPuter using hardware acceleration on Raspberry Pi"""
    
    def __init__(self, screen, videos_dir="media/videos"):
        """Initialize the video player"""
        self.screen = screen
        self.videos_dir = videos_dir
        self.current_process = None
        self.is_playing = False
        self.video_ended = threading.Event()
        self.lock = threading.Lock()
        self.paused = False
        
        # Create videos directory if it doesn't exist
        os.makedirs(self.videos_dir, exist_ok=True)
        
        # For text-based frames (placeholders)
        self.video_surface = None
        
        # For compatibility with the original player API
        self.current_video = None
        
    def play_video(self, video_file):
        """Play a video file using OMXPlayer with hardware acceleration"""
        try:
            with self.lock:
                if self.is_playing:
                    self.stop()
                    
                video_path = os.path.join(self.videos_dir, video_file)
                placeholder_path = video_path + ".txt"
                
                # Check if the file is a placeholder text file
                if os.path.exists(placeholder_path):
                    # Handle text placeholders same as original player
                    with open(placeholder_path, "r") as f:
                        placeholder_text = f.read().strip()
                    
                    self._create_text_frame(placeholder_text, video_file)
                    print(f"Displaying placeholder for video: {video_file}")
                    return True
                
                # Check if the video file exists
                if not os.path.exists(video_path):
                    print(f"Video not found: {video_path}")
                    return False
                
                # Clear the event before starting playback
                self.video_ended.clear()
                
                # Get screen dimensions
                screen_width, screen_height = self.screen.get_size()
                
                # Construct OMXPlayer command
                cmd = [
                    "omxplayer",
                    "--no-osd",                # No on-screen display
                    "--no-keys",               # Disable keyboard controls
                    "--win",                   # Window position parameters
                    f"0 0 {screen_width} {screen_height}",
                    "--orientation", "0",      # No rotation
                    "--layer", "2",            # Layer for display
                    "--loop",                  # Loop the video 
                    video_path
                ]
                
                # Start the process
                self.current_process = subprocess.Popen(
                    cmd, 
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    preexec_fn=os.setsid  # Allows terminating the process group
                )
                
                self.is_playing = True
                self.paused = False
                
                # Start monitoring thread
                threading.Thread(target=self._monitor_playback, daemon=True).start()
                
                print(f"Playing video: {video_file} with OMXPlayer")
                return True
                
        except Exception as e:
            print(f"Error playing video: {e}")
            self.is_playing = False
            return False
    
    def _monitor_playback(self):
        """Monitor video playback and set flag when complete"""
        if self.current_process:
            self.current_process.wait()
            with self.lock:
                if self.is_playing:  # Only if not stopped manually
                    self.is_playing = False
                    self.video_ended.set()
    
    def stop(self):
        """Stop the currently playing video"""
        with self.lock:
            if self.current_process:
                try:
                    os.killpg(os.getpgid(self.current_process.pid), signal.SIGTERM)
                except (ProcessLookupError, OSError):
                    pass  # Process already terminated
                self.current_process = None
                self.is_playing = False
                self.video_ended.set()
    
    def pause(self):
        """Pause the current video"""
        if self.is_playing and not self.paused:
            try:
                # Send 'p' command to omxplayer to pause
                if self.current_process:
                    # OMXPlayer uses DBUS for control, we'll send 'p' to stdin as fallback
                    # but this won't work in all cases
                    self.current_process.stdin.write(b'p')
                    self.current_process.stdin.flush()
                self.paused = True
            except Exception as e:
                print(f"Error pausing video: {e}")
    
    def resume(self):
        """Resume the paused video"""
        if self.is_playing and self.paused:
            try:
                # Send 'p' command to omxplayer to unpause
                if self.current_process:
                    self.current_process.stdin.write(b'p')
                    self.current_process.stdin.flush()
                self.paused = False
            except Exception as e:
                print(f"Error resuming video: {e}")
    
    def toggle_pause(self):
        """Toggle pause state"""
        if self.paused:
            self.resume()
        else:
            self.pause()
    
    def wait_for_complete(self, timeout=None):
        """Wait for video playback to complete"""
        return self.video_ended.wait(timeout)
    
    def is_video_playing(self):
        """Check if a video is currently playing"""
        with self.lock:
            if self.is_playing and self.current_process:
                # Check if process is still running
                if self.current_process.poll() is not None:
                    self.is_playing = False
                    self.video_ended.set()
                    return False
                return True
            return False
    
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
        
        return surface
    
    def update(self):
        """Update the video frame - for compatibility with original player API"""
        # If we're displaying a text placeholder, return the surface
        if self.video_surface is not None:
            return self.video_surface, False  # Not completed
            
        # External player handles the video rendering, just check status
        if self.is_video_playing():
            # No frame to return since OMXPlayer renders directly
            return None, False
        else:
            # Video has ended or wasn't started
            return None, not self.is_playing
            
def main():
    """Main function for testing the video player"""
    # Initialize pygame
    pygame.init()
    
    # Set up display
    screen_width = 800
    screen_height = 600
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("DogPuter RPi Video Player Test")
    
    # Create video player
    player = RPiVideoPlayer(screen)
    
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
        
        # Clear the screen (only needed for areas not covered by video)
        screen.fill((0, 0, 0))
        
        # Update video status
        frame, is_complete = player.update()
        
        if frame:
            screen.blit(frame, (0, 0))
        
        # Update the display (for UI elements, not video)
        pygame.display.flip()
        
        # Cap the frame rate for UI updates
        clock.tick(30)
    
    # Clean up
    player.stop()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
