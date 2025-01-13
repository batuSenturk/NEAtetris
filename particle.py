# particle.py

import pygame
import random
import math
from constants import SCREEN_WIDTH, SCREEN_HEIGHT

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.original_size = random.randint(4, 8)
        self.size = self.original_size
        
        # Random angle and speed for natural movement
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(100, 300)
        self.speed_x = math.cos(angle) * speed
        self.speed_y = math.sin(angle) * speed
        
        self.lifetime = random.uniform(0.5, 1.0)
        self.max_lifetime = self.lifetime
        self.gravity = 400  # Add gravity effect

    def update(self, dt):
        # Update position with gravity
        self.speed_y += self.gravity * dt
        self.x += self.speed_x * dt
        self.y += self.speed_y * dt
        
        # Update lifetime and size
        self.lifetime -= dt
        life_ratio = self.lifetime / self.max_lifetime
        self.size = self.original_size * life_ratio

    def draw(self, screen):
        if self.lifetime > 0:
            # Calculate alpha based on remaining lifetime
            alpha = int(255 * (self.lifetime / self.max_lifetime))
            
            # Create a surface for the particle with transparency
            particle_surface = pygame.Surface((int(self.size * 2), int(self.size * 2)), pygame.SRCALPHA)
            
            # Get RGB values from the color and add alpha
            if isinstance(self.color, tuple):
                r, g, b = self.color[:3]
            else:  # If color is an integer (from grid cells)
                r, g, b = 255, 255, 255  # Default to white if color format is unexpected
            
            # Draw the particle with transparency
            pygame.draw.circle(
                particle_surface,
                (r, g, b, alpha),
                (int(self.size), int(self.size)),
                int(self.size)
            )
            
            # Blit the particle surface onto the screen
            screen.blit(
                particle_surface,
                (int(self.x - self.size), int(self.y - self.size))
            )

class ParticleSystem:
    def __init__(self):
        self.particles = []

    def add_particle(self, x, y, color):
        self.particles.append(Particle(x, y, color))

    def update(self, dt):
        # Update particles and remove dead ones
        self.particles = [p for p in self.particles if p.lifetime > 0]
        for particle in self.particles:
            particle.update(dt)

    def draw(self, screen):
        for particle in self.particles:
            particle.draw(screen)
