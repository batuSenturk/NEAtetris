# button.py

import pygame
from constants import BUTTON_COLOR, BUTTON_HOVER_COLOR, BUTTON_TEXT_COLOR, FONT_NAME, FONT_SIZE

class Button:
    def __init__(self, rect, text, action=None):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.action = action
        self.font = pygame.font.Font(FONT_NAME, FONT_SIZE)
        self.hovered = False

    def draw(self, screen):
        color = BUTTON_HOVER_COLOR if self.hovered else BUTTON_COLOR
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, BUTTON_TEXT_COLOR, self.rect, 2)

        text_surf = self.font.render(self.text, True, BUTTON_TEXT_COLOR)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def handle_event(self, event, game):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.hovered and self.action:
                self.action(game)
