import pygame

# Key mappings configuration
# Format: pygame key constant: {"sound": sound_file, "image": image_file, "display_time": seconds, "command": text_to_speak}
KEY_MAPPINGS = {
    pygame.K_0: {"sound": "play.wav", "image": "play.jpg", "display_time": 5, "command": "play"},
    pygame.K_1: {"sound": "rope.wav", "image": "rope.jpg", "display_time": 5, "command": "rope"},
    pygame.K_2: {"sound": "ball.wav", "image": "ball.jpg", "display_time": 5, "command": "ball"},
    pygame.K_3: {"sound": "hugs.wav", "image": "hugs.jpg", "display_time": 5, "command": "hugs"},
    pygame.K_4: {"sound": "outside.wav", "image": "outside.jpg", "display_time": 5, "command": "outside"},
    pygame.K_5: {"sound": "walk.wav", "image": "walk.jpg", "display_time": 5, "command": "walk"},
    pygame.K_6: {"sound": "water.wav", "image": "water.jpg", "display_time": 5, "command": "water"},
    pygame.K_7: {"sound": "park.wav", "image": "park.jpg", "display_time": 5, "command": "park"},
    pygame.K_8: {"sound": "toy.wav", "image": "toy.jpg", "display_time": 5, "command": "toy"},
    pygame.K_9: {"sound": "bed.wav", "image": "bed.jpg", "display_time": 5, "command": "bed"},
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

# Arrow key mappings for video channels
ARROW_KEY_MAPPINGS = {
    pygame.K_UP: 0,     # Birds
    pygame.K_RIGHT: 1,  # Dogs
    pygame.K_DOWN: 2,   # Cats
    pygame.K_LEFT: 3,   # Squirrels
}

# Display settings
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BACKGROUND_COLOR = (30, 30, 30)  # Dark gray
DEFAULT_DISPLAY_TIME = 5  # seconds
