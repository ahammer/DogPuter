import time
import math

class EasingFunctions:
    """Collection of easing functions for animations"""
    
    @staticmethod
    def linear(t):
        """Linear easing"""
        return t
    
    @staticmethod
    def ease_in_quad(t):
        """Quadratic ease in"""
        return t * t
    
    @staticmethod
    def ease_out_quad(t):
        """Quadratic ease out"""
        return t * (2 - t)
    
    @staticmethod
    def ease_in_out_quad(t):
        """Quadratic ease in and out"""
        return 2 * t * t if t < 0.5 else -1 + (4 - 2 * t) * t
    
    @staticmethod
    def ease_in_cubic(t):
        """Cubic ease in"""
        return t * t * t
    
    @staticmethod
    def ease_out_cubic(t):
        """Cubic ease out"""
        return (t - 1) * (t - 1) * (t - 1) + 1
    
    @staticmethod
    def ease_in_out_cubic(t):
        """Cubic ease in and out"""
        return 4 * t * t * t if t < 0.5 else (t - 1) * (2 * t - 2) * (2 * t - 2) + 1
    
    @staticmethod
    def ease_in_sine(t):
        """Sinusoidal ease in"""
        return 1 - math.cos(t * math.pi / 2)
    
    @staticmethod
    def ease_out_sine(t):
        """Sinusoidal ease out"""
        return math.sin(t * math.pi / 2)
    
    @staticmethod
    def ease_in_out_sine(t):
        """Sinusoidal ease in and out"""
        return -(math.cos(math.pi * t) - 1) / 2

class Animation:
    """Represents an animation with start time, duration, and easing function"""
    
    def __init__(self, duration, easing_function=None, start_value=0.0, end_value=1.0, loop=False):
        """Initialize the animation"""
        self.start_time = time.time()
        self.duration = duration
        self.easing_function = easing_function or EasingFunctions.linear
        self.start_value = start_value
        self.end_value = end_value
        self.loop = loop
        self.progress = 0.0
        self.completed = False
    
    def update(self, delta_time=None):
        """Update the animation progress"""
        if self.completed and not self.loop:
            return
        
        current_time = time.time()
        elapsed = current_time - self.start_time
        
        if elapsed >= self.duration:
            if self.loop:
                # Reset start time for looping
                self.start_time = current_time
                elapsed = 0
            else:
                self.progress = 1.0
                self.completed = True
                return
        
        # Calculate raw progress (0.0 to 1.0)
        self.progress = elapsed / self.duration
        
        # Apply easing function
        self.eased_progress = self.easing_function(self.progress)
    
    def get_value(self):
        """Get the current animation value"""
        # Apply easing and interpolate between start and end values
        return self.start_value + (self.end_value - self.start_value) * self.eased_progress
    
    def reset(self):
        """Reset the animation"""
        self.start_time = time.time()
        self.progress = 0.0
        self.completed = False

class AnimationSystem:
    """Manages multiple animations"""
    
    def __init__(self):
        """Initialize the animation system"""
        self.animations = {}
    
    def create_animation(self, animation_id, duration, easing_function=None, start_value=0.0, end_value=1.0, loop=False):
        """Create a new animation"""
        animation = Animation(duration, easing_function, start_value, end_value, loop)
        self.animations[animation_id] = animation
        return animation
    
    def update_animations(self, delta_time=None):
        """Update all animations"""
        for animation in self.animations.values():
            animation.update(delta_time)
    
    def get_animation_value(self, animation_id):
        """Get the current value of an animation"""
        if animation_id in self.animations:
            return self.animations[animation_id].get_value()
        return 0.0
    
    def is_animation_completed(self, animation_id):
        """Check if an animation is completed"""
        if animation_id in self.animations:
            return self.animations[animation_id].completed
        return True
    
    def reset_animation(self, animation_id):
        """Reset an animation"""
        if animation_id in self.animations:
            self.animations[animation_id].reset()
    
    def remove_animation(self, animation_id):
        """Remove an animation"""
        if animation_id in self.animations:
            del self.animations[animation_id]
