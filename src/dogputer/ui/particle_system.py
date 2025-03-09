"""
Particle system for DogPuter. Provides visual effects that attract dog attention.
Designed to be lightweight for Raspberry Pi 3B performance.
"""

import random
import math
import pygame
from dogputer.core.config import (
    PARTICLE_MAX_COUNT, PARTICLE_DEFAULT_LIFETIME,
    PARTICLE_SIZE_RANGE, PARTICLE_SPEED_RANGE,
    BLUE_PRIMARY, YELLOW_PRIMARY, LIGHT_BLUE, CREAM
)

class Particle:
    """Individual particle with position, velocity, color, and lifetime"""
    
    def __init__(self, x, y, color=None, size=None, lifetime=None, 
                 speed=None, direction=None):
        """Initialize a particle with position and attributes"""
        self.x = x
        self.y = y
        self.color = color or random.choice([YELLOW_PRIMARY, LIGHT_BLUE, CREAM])
        self.size = size or random.randint(*PARTICLE_SIZE_RANGE)
        self.lifetime = lifetime or PARTICLE_DEFAULT_LIFETIME
        self.max_lifetime = self.lifetime
        self.alpha = 255
        
        # Set velocity based on speed and direction
        speed = speed or random.uniform(*PARTICLE_SPEED_RANGE)
        direction = direction if direction is not None else random.uniform(0, 2 * math.pi)
        self.vel_x = speed * math.cos(direction)
        self.vel_y = speed * math.sin(direction)
    
    def update(self, delta_time):
        """Update particle position and attributes"""
        # Apply pattern-based motion if the particle has a pattern
        if hasattr(self, 'pattern'):
            # Update pattern time
            if not hasattr(self, 'pattern_time'):
                self.pattern_time = 0
            self.pattern_time += delta_time
            
            # Apply pattern-specific motion
            if self.pattern == 'wiggle':
                # Side-to-side wiggle effect
                wiggle_strength = 2.0
                wiggle_speed = 5.0
                # Add a sideways velocity component that oscillates
                self.vel_x += math.sin(self.pattern_time * wiggle_speed) * wiggle_strength
                
            elif self.pattern == 'spiral':
                # Spiral effect - circular motion combined with upward drift
                spiral_radius = 1.0
                spiral_speed = 3.0
                # Calculate spiral motion components
                spiral_x = math.cos(self.pattern_time * spiral_speed) * spiral_radius
                spiral_y = math.sin(self.pattern_time * spiral_speed) * spiral_radius
                # Add to velocity
                self.vel_x = spiral_x * 2
                self.vel_y = -1.5 + spiral_y  # Upward drift with spiral
        
        # Update position
        self.x += self.vel_x * delta_time
        self.y += self.vel_y * delta_time
        
        # Update lifetime
        self.lifetime -= delta_time
        
        # Update alpha based on remaining lifetime
        life_percentage = self.lifetime / self.max_lifetime
        self.alpha = int(255 * life_percentage)
        
        # Apply some drag to slow particles over time
        self.vel_x *= 0.98
        self.vel_y *= 0.98
        
        # Decrease size slightly over time, but slower for better visibility
        if self.size > 1:
            # Slower size reduction for better visibility
            size_reduction_rate = 1.0 if hasattr(self, 'pattern') else 2.0
            self.size = max(1, self.size - (delta_time * size_reduction_rate))
        
        return self.lifetime > 0
    
    def draw(self, surface):
        """Draw particle to surface"""
        # Skip if zero size or fully transparent
        if self.size <= 0 or self.alpha <= 0:
            return
            
        # Create a surface for this particle
        particle_surface = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        
        # Set the color with alpha
        color_with_alpha = (*self.color, self.alpha)
        
        # Draw the particle as a circle
        pygame.draw.circle(
            particle_surface, 
            color_with_alpha, 
            (self.size, self.size), 
            self.size
        )
        
        # Blit to the main surface
        surface.blit(particle_surface, (int(self.x - self.size), int(self.y - self.size)))


class ParticleSystem:
    """Manages multiple particles and provides different effect types"""
    
    def __init__(self, screen_width, screen_height):
        """Initialize the particle system"""
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.particles = []
        
    def update(self, delta_time):
        """Update all particles"""
        # Update each particle and keep only active ones
        self.particles = [p for p in self.particles if p.update(delta_time)]
    
    def draw(self, surface):
        """Draw all particles to a surface"""
        for particle in self.particles:
            particle.draw(surface)
    
    def add_particle(self, x, y, color=None, size=None, lifetime=None, 
                     speed=None, direction=None):
        """Add a single particle"""
        # Only add if we're under the maximum count
        if len(self.particles) < PARTICLE_MAX_COUNT:
            particle = Particle(x, y, color, size, lifetime, speed, direction)
            self.particles.append(particle)
    
    def create_burst(self, x, y, count=10, color=None, spread=360, 
                     min_speed=None, max_speed=None, size_range=None):
        """Create a burst of particles from a point"""
        # Determine default speeds
        min_speed = min_speed or PARTICLE_SPEED_RANGE[0]
        max_speed = max_speed or PARTICLE_SPEED_RANGE[1]
        size_range = size_range or PARTICLE_SIZE_RANGE
        
        # Add particles evenly across the specified spread
        for i in range(min(count, PARTICLE_MAX_COUNT - len(self.particles))):
            # Calculate direction within spread
            if spread >= 360:
                direction = random.uniform(0, 2 * math.pi)
            else:
                # Convert spread to radians
                spread_rad = math.radians(spread)
                # Choose a direction within the spread
                center_angle = 0  # Default center angle (right)
                direction = center_angle + random.uniform(-spread_rad/2, spread_rad/2)
            
            # Create particle with calculated direction
            speed = random.uniform(min_speed, max_speed)
            size = random.randint(*size_range)
            self.add_particle(
                x, y, 
                color=color, 
                speed=speed, 
                direction=direction,
                size=size
            )
    
    def create_trail(self, start_x, start_y, end_x, end_y, count=5, color=None):
        """Create a trail of particles between two points"""
        # Calculate step for distributing particles along the line
        if count <= 1:
            step_x, step_y = 0, 0
        else:
            step_x = (end_x - start_x) / (count - 1)
            step_y = (end_y - start_y) / (count - 1)
        
        # Add particles along the trail
        for i in range(min(count, PARTICLE_MAX_COUNT - len(self.particles))):
            x = start_x + step_x * i
            y = start_y + step_y * i
            size = random.randint(*PARTICLE_SIZE_RANGE)
            self.add_particle(x, y, color=color, size=size)
    
    def create_ambient(self, region_rect=None, count=10, color=None, 
                       gravity=0, min_lifetime=0.5, max_lifetime=2.0):
        """Create ambient particles within a region with enhanced visuals for dogs"""
        region_rect = region_rect or pygame.Rect(0, 0, self.screen_width, self.screen_height)
        
        # Enhanced version with more directed, intentional motion that dogs can track
        for i in range(min(count, PARTICLE_MAX_COUNT - len(self.particles))):
            # Random position within region
            x = random.uniform(region_rect.left, region_rect.right)
            y = random.uniform(region_rect.top, region_rect.bottom)
            
            # Longer lifetime for better visibility to dogs
            lifetime = random.uniform(min_lifetime * 1.5, max_lifetime * 1.5)
            
            # More varied motion patterns - dogs notice change and movement
            pattern = random.choice([
                'float_up',   # Gentle upward drift
                'wiggle',     # Side-to-side wiggle
                'spiral',     # Spiral motion
                'random',     # Random motion
            ])
            
            # Create particle with pattern-specific settings
            if pattern == 'float_up':
                # Upward motion
                direction = random.uniform(math.pi/4, 3*math.pi/4)  # Upward-ish
                speed = random.uniform(10, 25)  # Slightly faster
                
            elif pattern == 'wiggle':
                # Horizontal motion with wiggle
                direction = random.choice([0, math.pi])  # Left or right
                speed = random.uniform(5, 15)
                
            elif pattern == 'spiral':
                # Upward spiral starting direction
                direction = math.pi/2  # Up
                speed = random.uniform(5, 15)
                
            else:  # random
                direction = random.uniform(0, 2 * math.pi)
                speed = random.uniform(5, 20)
            
            # Create base particle
            particle = Particle(x, y, color=color, lifetime=lifetime,
                                speed=speed, direction=direction)
            
            # Store pattern for update logic
            particle.pattern = pattern
            particle.pattern_time = 0
            
            # Add gravity effect if specified
            if gravity != 0:
                particle.vel_y += gravity
                
            # Make particles slightly larger for better dog visibility
            particle.size *= 1.2
                
            self.particles.append(particle)
    
    def create_directed_flow(self, start_x, start_y, angle, count=5, 
                             spread=30, color=None, speed_range=None):
        """Create a directed flow of particles from a point"""
        # Use default speed range if not specified
        speed_range = speed_range or PARTICLE_SPEED_RANGE
        
        # Convert angle to radians
        angle_rad = math.radians(angle)
        spread_rad = math.radians(spread)
        
        for i in range(min(count, PARTICLE_MAX_COUNT - len(self.particles))):
            # Calculate direction within spread
            direction = angle_rad + random.uniform(-spread_rad/2, spread_rad/2)
            
            # Create particle with calculated direction
            speed = random.uniform(*speed_range)
            self.add_particle(
                start_x, start_y, 
                color=color, 
                speed=speed, 
                direction=direction
            )
    
    def clear_particles(self):
        """Clear all particles"""
        self.particles = []
