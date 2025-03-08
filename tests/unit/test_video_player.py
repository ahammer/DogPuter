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

# For tests before refactoring, we can use this:
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from video_player import VideoPlayer as OriginalVideoPlayer

# This import will work after refactoring:
# from dogputer.ui.video_player import VideoPlayer


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
    @patch('moviepy.VideoFileClip')
    def test_init(self, mock_video_file_clip, mock_surface, mock_pygame_surface):
        """Test initialization of VideoPlayer"""
        # Setup
        screen = mock_pygame_surface
        
        # Execute
        player = OriginalVideoPlayer(screen, "test_videos")
        
        # Verify
        assert player.screen == screen
        assert player.videos_dir == "test_videos"
        assert player.current_video is None
        assert player.video_surface is None
        assert player.paused is False
        assert player.in_transition is False
    
    @patch('moviepy.VideoFileClip')
    def test_play_video_success(self, mock_video_file_clip_class, mock_pygame_surface, mock_video_file_clip):
        """Test playing a video successfully"""
        # Setup
        mock_video_file_clip_class.return_value = mock_video_file_clip
        player = OriginalVideoPlayer(mock_pygame_surface)
        
        # Make sure the video file exists
        with patch('os.path.exists', return_value=True):
            # Execute
            result = player.play_video("test.mp4")
            
            # Verify
            assert result is True
            assert player.current_video == mock_video_file_clip
            assert not player.paused
            mock_video_file_clip_class.assert_called_once_with(os.path.join("videos", "test.mp4"))
    
    @patch('moviepy.VideoFileClip')
    def test_play_video_file_not_found(self, mock_video_file_clip_class, mock_pygame_surface):
        """Test playing a non-existent video"""
        # Setup
        player = OriginalVideoPlayer(mock_pygame_surface)
        
        # Make sure the video file does not exist
        with patch('os.path.exists', return_value=False):
            # Execute
            result = player.play_video("nonexistent.mp4")
            
            # Verify
            assert result is False
            assert player.current_video is None
            mock_video_file_clip_class.assert_not_called()
    
    @patch('moviepy.VideoFileClip')
    def test_play_video_with_placeholder(self, mock_video_file_clip_class, mock_pygame_surface):
        """Test playing a video with a placeholder text file"""
        # Setup
        player = OriginalVideoPlayer(mock_pygame_surface)
        placeholder_content = "This is a placeholder for the video"
        
        # Set up the mock os.path.exists to return True only for the placeholder
        def mock_exists(path):
            return path.endswith(".txt")
            
        # Mock the open function to return our placeholder content
        with patch('os.path.exists', side_effect=mock_exists):
            with patch('builtins.open', mock_open(read_data=placeholder_content)):
                # Execute
                result = player.play_video("placeholder.mp4")
                
                # Verify
                assert result is True
                assert player.current_video is None
                assert player.video_surface is not None
                mock_video_file_clip_class.assert_not_called()
    
    @patch('moviepy.VideoFileClip')
    def test_stop(self, mock_video_file_clip_class, mock_pygame_surface, mock_video_file_clip):
        """Test stopping video playback"""
        # Setup
        mock_video_file_clip_class.return_value = mock_video_file_clip
        player = OriginalVideoPlayer(mock_pygame_surface)
        
        # Start playing a video
        with patch('os.path.exists', return_value=True):
            player.play_video("test.mp4")
            assert player.current_video is not None
            
            # Execute
            player.stop()
            
            # Verify
            assert player.current_video is None
            assert player.video_surface is None
            assert player.paused is False
            mock_video_file_clip.close.assert_called_once()
    
    @patch('moviepy.VideoFileClip')
    def test_pause_and_resume(self, mock_video_file_clip_class, mock_pygame_surface, mock_video_file_clip):
        """Test pausing and resuming video playback"""
        # Setup
        mock_video_file_clip_class.return_value = mock_video_file_clip
        player = OriginalVideoPlayer(mock_pygame_surface)
        
        # Start playing a video
        with patch('os.path.exists', return_value=True):
            with patch('time.time', return_value=100.0):  # Fix time for predictable testing
                player.play_video("test.mp4")
                assert player.current_video is not None
                assert player.paused is False
                
                # Test pause
                player.pause()
                assert player.paused is True
                assert player.pause_time == 0.0  # Since we just started playing
                
                # Test resume
                with patch('time.time', return_value=105.0):  # 5 seconds later
                    player.resume()
                    assert player.paused is False
                    assert player.start_time == 105.0  # current time
    
    @patch('moviepy.VideoFileClip')
    @patch('pygame.surfarray.make_surface')
    def test_update_normal_playback(self, mock_make_surface, mock_video_file_clip_class, 
                                   mock_pygame_surface, mock_video_file_clip):
        """Test update during normal video playback"""
        # Setup
        mock_video_file_clip_class.return_value = mock_video_file_clip
        mock_frame_surface = MagicMock(spec=pygame.Surface)
        mock_make_surface.return_value = mock_frame_surface
        
        player = OriginalVideoPlayer(mock_pygame_surface)
        
        # Start playing a video
        with patch('os.path.exists', return_value=True):
            player.play_video("test.mp4")
            
            # Execute update with fixed current time (2 seconds into the video)
            with patch('time.time', return_value=player.start_time + 2.0):
                result, is_complete = player.update()
                
                # Verify
                assert result == mock_frame_surface
                assert is_complete is False
                mock_video_file_clip.get_frame.assert_called_with(2.0)
                mock_make_surface.assert_called_once()
    
    @patch('moviepy.VideoFileClip')
    def test_update_video_completed(self, mock_video_file_clip_class, mock_pygame_surface, mock_video_file_clip):
        """Test update when video has completed"""
        # Setup
        mock_video_file_clip_class.return_value = mock_video_file_clip
        mock_video_file_clip.duration = 5.0  # Set a short duration
        
        player = OriginalVideoPlayer(mock_pygame_surface)
        
        # Start playing a video
        with patch('os.path.exists', return_value=True):
            player.play_video("test.mp4")
            
            # Execute update with a time after the video ends
            with patch('time.time', return_value=player.start_time + 6.0):  # 6 seconds > 5 second duration
                result, is_complete = player.update()
                
                # Verify
                assert result is None
                assert is_complete is True
                # get_frame should not be called since we're past the end
                mock_video_file_clip.get_frame.assert_not_called()
