try:
    from moviepy.editor import VideoFileClip
    print("Successfully imported VideoFileClip from moviepy.editor")
except Exception as e:
    print(f"Error importing from moviepy.editor: {e}")

try:
    from moviepy import VideoFileClip
    print("Successfully imported VideoFileClip directly from moviepy")
except Exception as e:
    print(f"Error importing directly from moviepy: {e}")

import moviepy
print(f"Moviepy version: {moviepy.__version__}")
print(f"Available in moviepy: {dir(moviepy)}")
