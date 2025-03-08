import pygame

# Key mappings configuration
# Format: pygame key constant: {"sound": sound_file, "image": image_file, "display_time": seconds}
KEY_MAPPINGS = {
    pygame.K_a: {"sound": "play.wav", "image": "play.jpg", "display_time": 5},
    pygame.K_s: {"sound": "rope.wav", "image": "rope.jpg", "display_time": 5},
    pygame.K_d: {"sound": "ball.wav", "image": "ball.jpg", "display_time": 5},
    pygame.K_f: {"sound": "treat.wav", "image": "treat.jpg", "display_time": 5},
    pygame.K_g: {"sound": "outside.wav", "image": "outside.jpg", "display_time": 5},
    pygame.K_h: {"sound": "walk.wav", "image": "walk.jpg", "display_time": 5},
    # Add more key mappings as needed
}

# Video channels configuration
# Format: {"name": channel_name, "video": video_file}
VIDEO_CHANNELS = [
    {"name": "Squirrels", "video": "squirrels.mp4"},
    {"name": "Birds", "video": "birds.mp4"},
    {"name": "Dogs", "video": "dogs.mp4"},
    {"name": "Cats", "video": "cats.mp4"},
    {"name": "Water", "video": "water.mp4"},
    # Add more video channels as needed
]

# Display settings
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BACKGROUND_COLOR = (30, 30, 30)  # Dark gray
DEFAULT_DISPLAY_TIME = 5  # seconds
