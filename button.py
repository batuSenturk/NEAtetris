# button.py

import pygame
from constants import BUTTON_COLOR, BUTTON_HOVER_COLOR, BUTTON_TEXT_COLOR, FONT_NAME, FONT_SIZE, BUTTON_WIDTH, BUTTON_HEIGHT

class Button:
    def __init__(self, rect, text, action=None):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.action = action
        self.font = pygame.font.Font(FONT_NAME, FONT_SIZE)
        self.hovered = False

        # For smooth color transition
        self.current_color = pygame.Color(*BUTTON_COLOR)
        self.target_color = pygame.Color(*BUTTON_COLOR)
        self.transition_speed = 15  # Adjust for faster/slower transitions

    def draw(self, screen):
        # Update current_color towards target_color
        self.current_color.r = self._approach(self.current_color.r, self.target_color.r, self.transition_speed)
        self.current_color.g = self._approach(self.current_color.g, self.target_color.g, self.transition_speed)
        self.current_color.b = self._approach(self.current_color.b, self.target_color.b, self.transition_speed)

        # Draw the button rectangle with the current_color
        pygame.draw.rect(screen, self.current_color, self.rect)
        pygame.draw.rect(screen, BUTTON_TEXT_COLOR, self.rect, 2)

        # Render the text
        text_surf = self.font.render(self.text, True, BUTTON_TEXT_COLOR)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def handle_event(self, event, game):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
            # Update target_color based on hover state
            self.target_color = pygame.Color(*BUTTON_HOVER_COLOR) if self.hovered else pygame.Color(*BUTTON_COLOR)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.hovered and self.action:
                self.action(game)

    def _approach(self, current, target, speed):
        """Helper method to smoothly approach the target value."""
        if current < target:
            current += speed
            if current > target:
                current = target
        elif current > target:
            current -= speed
            if current < target:
                current = target
        return current
