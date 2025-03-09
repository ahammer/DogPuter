#!/usr/bin/env python3
"""
Unit tests for the VideoPlayer class
"""

import os
import sys
import pygame
import pytest
import time
from unittest.mock import patch, MagicMock, mock_open
import numpy as np

# Add src directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "src")))

# Import the VideoPlayer from the package structure
from dogputer.ui.video_player import VideoPlayer

class TestVideoPlayer:
    """Test cases for the VideoPlayer class"""
    
    @pytest.fixture
    def mock_pygame_surface(self):
        """Create a mock pygame surface"""
        surface = MagicMock(spec=pygame.Surface)
        surface.get_width.return_value = 800
        surface.get_height.return_value = 600
        return surface
    
    @pytest.fixture
    def mock_video_file_clip(self):
        """Create a mock MoviePy VideoFileClip"""
        clip = MagicMock()
        clip.duration = 10.0
        
        # Mock get_frame to return a numpy array simulating a video frame
        def mock_get_frame(t):
            # Create a simple colored frame based on the time
            # This allows us to get different frames at different times
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
            # Add some color that changes with time
            frame[:, :, 0] = int(255 * (t / 10.0))  # Red channel varies with time
            frame[:, :, 1] = 100                     # Fixed green
            frame[:, :, 2] = 150                     # Fixed blue
            return frame
            
        clip.get_frame.side_effect = mock_get_frame
        return clip
    
    @patch('pygame.Surface')
    def test_init(self, mock_surface, mock_pygame_surface):
        """Test initialization of VideoPlayer"""
        # Setup
        screen = mock_pygame_surface
        
        # Execute
        player = VideoPlayer(screen, "test_videos")
        
        # Verify
        assert player.screen == screen
        assert player.videos_dir == "test_videos"
        assert player.current_video is None
        assert player.video_surface is None
        assert player.paused is False
        assert player.in_transition is False
    
    def test_play_video_file_not_found(self, mock_pygame_surface):
        """Test playing a non-existent video"""
        # Setup
        player = VideoPlayer(mock_pygame_surface)
        
        # Make sure the video file does not exist (mock both checks)
        with patch('os.path.exists', return_value=False):
            # Execute
            result = player.play_video("nonexistent.mp4")
            
            # Verify
            assert result is False
            assert player.current_video is None
    
    def test_play_video_with_placeholder(self, mock_pygame_surface):
        """Test playing a video with a placeholder text file"""
        # Setup
        player = VideoPlayer(mock_pygame_surface)
        placeholder_content = "This is a placeholder for the video"
        
        # Mock the text frame creation
        mock_surface = MagicMock(spec=pygame.Surface)
        
        # Set up the mock os.path.exists to handle checks
        def mock_exists(path):
            return path.endswith(".txt")
        
        # The tricky part: we need to set video_surface when _create_text_frame is called
        def mock_create_text(text, title):
            player.video_surface = mock_surface
            return mock_surface
        
        # Patch player._create_text_frame method 
        with patch.object(player, '_create_text_frame', side_effect=mock_create_text):
            # Mock file existence and file open
            with patch('os.path.exists', side_effect=mock_exists):
                with patch('builtins.open', mock_open(read_data=placeholder_content)):
                    # Execute
                    result = player.play_video("placeholder.mp4")
                    
                    # Verify
                    assert result is True
                    assert player.current_video is None
                    assert player.video_surface == mock_surface
    
    @patch('dogputer.ui.video_player.VideoFileClip')
    def test_play_video_success(self, mock_video_clip_class, mock_pygame_surface, mock_video_file_clip):
        """Test successfully playing a video file"""
        # Setup
        player = VideoPlayer(mock_pygame_surface)
        mock_video_clip_class.return_value = mock_video_file_clip
        
        # Set up mock for os.path.exists to return True for the video file
        with patch('os.path.exists', side_effect=lambda path: not path.endswith(".txt")):
            # Execute
            result = player.play_video("testvideo.mp4")
            
            # Verify
            assert result is True
            assert player.current_video == mock_video_file_clip
            assert player.paused is False
            mock_video_clip_class.assert_called_once_with(os.path.join(player.videos_dir, "testvideo.mp4"))
    
    @patch('dogputer.ui.video_player.VideoFileClip')
    def test_transition_between_videos(self, mock_video_clip_class, mock_pygame_surface, mock_video_file_clip):
        """Test transitioning between videos"""
        # Setup
        player = VideoPlayer(mock_pygame_surface)
        mock_video_clip_class.return_value = mock_video_file_clip
        
        # Mock time to control the transition timing
        with patch('time.time', return_value=100.0):
            # Mock os.path.exists to simulate video file existing
            with patch('os.path.exists', side_effect=lambda path: not path.endswith(".txt")):
                # First play a video
                player.play_video("video1.mp4")
                assert player.current_video == mock_video_file_clip
                
                # Now play another video which should start a transition
                player.play_video("video2.mp4")
                
                # Verify transition is set up correctly
                assert player.in_transition is True
                assert player.next_video == mock_video_file_clip
    
    @patch('dogputer.ui.video_player.VideoFileClip')
    def test_stop_video(self, mock_video_clip_class, mock_pygame_surface, mock_video_file_clip):
        """Test stopping video playback"""
        # Setup
        player = VideoPlayer(mock_pygame_surface)
        mock_video_clip_class.return_value = mock_video_file_clip
        
        # Play a video first
        with patch('os.path.exists', side_effect=lambda path: not path.endswith(".txt")):
            player.play_video("testvideo.mp4")
            
        # Execute
        player.stop()
        
        # Verify
        assert player.current_video is None
        assert player.video_surface is None
        assert player.paused is False
        mock_video_file_clip.close.assert_called_once()
    
    @patch('dogputer.ui.video_player.VideoFileClip')
    def test_pause_resume_toggle(self, mock_video_clip_class, mock_pygame_surface, mock_video_file_clip):
        """Test pausing, resuming, and toggling video playback"""
        # Setup
        player = VideoPlayer(mock_pygame_surface)
        mock_video_clip_class.return_value = mock_video_file_clip
        
        # Play a video first - need to patch time.time for start_time
        with patch('os.path.exists', side_effect=lambda path: not path.endswith(".txt")):
            with patch('time.time', return_value=100.0):
                player.play_video("testvideo.mp4")
                
                # Test pause - in the same time.time context
                player.pause()
                assert player.paused is True
                assert player.pause_time == 0.0  # Should be exactly 0.0 since start_time and time.time() are both 100.0
            
        # Test resume with a later time
        with patch('time.time', return_value=105.0):
            player.resume()
            assert player.paused is False
            assert player.start_time == 105.0  # Current time (105) - pause_time (0)
            
            # Test toggle pause (pause again)
            player.toggle_pause()
            assert player.paused is True
            
            # Test toggle pause (resume again)
            player.toggle_pause()
            assert player.paused is False
    
    @patch('dogputer.ui.video_player.VideoFileClip')
    @patch('pygame.surfarray.make_surface')
    def test_update_returns_frame(self, mock_make_surface, mock_video_clip_class, mock_pygame_surface, mock_video_file_clip):
        """Test that update returns a frame for a playing video"""
        # Setup
        player = VideoPlayer(mock_pygame_surface)
        mock_video_clip_class.return_value = mock_video_file_clip
        
        # Create a mock for the frame surface
        mock_frame_surface = MagicMock(spec=pygame.Surface)
        mock_frame_surface.get_width.return_value = 640
        mock_frame_surface.get_height.return_value = 480
        mock_make_surface.return_value = mock_frame_surface
        
        # Mock the numpy array returned by get_frame to prevent int conversion issues
        frame_data = np.zeros((480, 640, 3), dtype=np.uint8)
        mock_video_file_clip.get_frame.return_value = frame_data
        
        # Mock _scale_preserve_ratio to return the surface directly
        with patch.object(player, '_scale_preserve_ratio', return_value=mock_frame_surface):
            # Play a video first
            with patch('os.path.exists', side_effect=lambda path: not path.endswith(".txt")):
                with patch('time.time', return_value=100.0):
                    player.play_video("testvideo.mp4")
                
            # Set time to within the video duration
            with patch('time.time', return_value=105.0):  # 5 seconds into 10-second video
                # Call update
                frame, is_complete = player.update()
                
                # Verify
                assert frame == mock_frame_surface
                assert is_complete is False
                mock_video_file_clip.get_frame.assert_called_with(5.0)
    
    @patch('dogputer.ui.video_player.VideoFileClip')
    def test_update_signals_completion(self, mock_video_clip_class, mock_pygame_surface, mock_video_file_clip):
        """Test that update signals completion when video ends"""
        # Setup
        player = VideoPlayer(mock_pygame_surface)
        mock_video_clip_class.return_value = mock_video_file_clip
        mock_video_file_clip.duration = 10.0
        
        # Mock the get_frame method to avoid int conversion issues
        frame_data = np.zeros((480, 640, 3), dtype=np.uint8)
        mock_video_file_clip.get_frame.return_value = frame_data
        
        # Play a video first
        with patch('os.path.exists', side_effect=lambda path: not path.endswith(".txt")):
            with patch('time.time', return_value=100.0):
                player.play_video("testvideo.mp4")
                
        # Set time to after the video duration
        with patch('time.time', return_value=111.0):  # 11 seconds into 10-second video
            # Need to also patch pygame.surfarray.make_surface to avoid the exception
            with patch('pygame.surfarray.make_surface') as mock_make_surface:
                # Call update - no need to patch get_frame since we won't reach that code
                frame, is_complete = player.update()
                
                # Verify
                assert frame is None
                assert is_complete is True
