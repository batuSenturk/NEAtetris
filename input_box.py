# input_box.py

import pygame
from constants import FONT_NAME, FONT_SIZE, COLORS

class InputBox:
    def __init__(self, x, y, w, h, text=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.color_inactive = COLORS['white']
        self.color_active = COLORS['white']
        self.color = self.color_inactive
        self.text = text
        self.txt_surface = pygame.font.Font(FONT_NAME, FONT_SIZE).render(text, True, self.color)
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Toggle the active state if the user clicked on the input_box
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
            self.color = self.color_active if self.active else self.color_inactive
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    return self.text
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    if len(self.text) < 10:  # Limit name length
                        self.text += event.unicode
                # Re-render the text
                self.txt_surface = pygame.font.Font(FONT_NAME, FONT_SIZE).render(self.text, True, self.color)
        return None

    def draw(self, screen):
        # Blit the text
        screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))
        # Blit the rect
        pygame.draw.rect(screen, self.color, self.rect, 2)
