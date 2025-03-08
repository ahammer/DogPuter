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
        
        # Decrease size slightly over time
        if self.size > 1:
            self.size = max(1, self.size - (delta_time * 2))
        
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
        """Create ambient particles within a region"""
        region_rect = region_rect or pygame.Rect(0, 0, self.screen_width, self.screen_height)
        
        for i in range(min(count, PARTICLE_MAX_COUNT - len(self.particles))):
            # Random position within region
            x = random.uniform(region_rect.left, region_rect.right)
            y = random.uniform(region_rect.top, region_rect.bottom)
            
            # Create particle with gentle upward motion (good for ambient effects)
            lifetime = random.uniform(min_lifetime, max_lifetime)
            
            # Gentle random motion with optional gravity
            direction = random.uniform(math.pi/4, 3*math.pi/4)  # Upward-ish
            speed = random.uniform(5, 20)  # Gentle
            
            particle = Particle(x, y, color=color, lifetime=lifetime,
                               speed=speed, direction=direction)
            
            # Add gravity effect if specified
            if gravity != 0:
                particle.vel_y += gravity
                
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
