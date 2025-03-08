import pygame

# Dog-friendly color palette
# Dogs see primarily in blue and yellow spectrum, so we optimize for those colors
# Main colors
BLUE_PRIMARY = (0, 102, 170)       # Medium blue - primary background
YELLOW_PRIMARY = (255, 204, 0)     # Bold yellow - primary interactive elements
WHITE = (255, 255, 255)            # White - high contrast text
LIGHT_BLUE = (153, 204, 255)       # Light blue - secondary elements
CREAM = (255, 255, 204)            # Cream - secondary interactive elements

# Feedback colors
SUCCESS_COLOR = (102, 204, 255)    # Bright blue - success feedback
ALERT_COLOR = (255, 255, 153)      # Light yellow - alerts/notifications
ERROR_COLOR = (255, 153, 0)        # Orange - errors/warnings
FEEDBACK_DURATION = 1.8            # Longer feedback duration for dogs (seconds)

# Particle effect settings
PARTICLE_MAX_COUNT = 40            # Maximum particles for Raspberry Pi 3B performance
PARTICLE_DEFAULT_LIFETIME = 1.0    # Default particle lifetime in seconds
PARTICLE_SIZE_RANGE = (3, 10)      # Min/max particle size range
PARTICLE_SPEED_RANGE = (20, 80)    # Min/max particle speed in pixels/second

# Animation timings
TRANSITION_DURATION = 0.8          # Duration for transitions between states
FEEDBACK_DURATION = 0.8            # Duration for feedback messages
WAITING_ANIMATION_SPEED = 1.5      # Speed multiplier for waiting screen animations

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
BACKGROUND_COLOR = BLUE_PRIMARY  # Changed from dark gray to dog-friendly blue
DEFAULT_DISPLAY_TIME = 5  # seconds

# UI element sizes
PAW_CURSOR_SIZE = 120              # Increased from 80 to 120 for better visibility
BUTTON_HIGHLIGHT_THICKNESS = 4     # Thickness of button highlights
FEEDBACK_HEIGHT = 80               # Increased height of feedback bar
WAITING_TEXT_SIZE = 72             # Size of waiting screen text
FEEDBACK_TEXT_SIZE = 40            # Size of feedback text
