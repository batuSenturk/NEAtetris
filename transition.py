import pygame
from constants import SCREEN_WIDTH, SCREEN_HEIGHT

class Transition:
    def __init__(self):
        self.progress = 0
        self.duration = 1.0  # Duration of the transition in seconds
        self.is_active = False

    def start(self):
        self.progress = 0
        self.is_active = True

    def update(self, dt):
        if self.is_active:
            self.progress += dt / self.duration
            if self.progress >= 1:
                self.progress = 1
                self.is_active = False

    def draw(self, screen):
        if self.is_active:
            alpha = int(255 * (1 - self.progress))  # Fade in effect
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(alpha)
            overlay.fill((0, 0, 0))
            screen.blit(overlay, (0, 0))
