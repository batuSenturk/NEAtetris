# hud.py

import pygame
from constants import FONT_NAME, FONT_SIZE, COLORS, CELL_SIZE, GRID_Y_OFFSET, SCREEN_WIDTH

class HUD:
    def __init__(self, game):
        self.game = game
        self.font = pygame.font.Font(FONT_NAME, FONT_SIZE)
        self.small_font = pygame.font.Font(FONT_NAME, FONT_SIZE - 8)
        self.notifications = []  # List of active notifications

    def add_notifications(self, new_notifications):
        # Add new notifications to the list
        for notif in new_notifications:
            self.notifications.append({
                'text': notif['text'],
                'color': notif['color'],
                'lifetime': notif['lifetime'],
                'y_pos': 150  # Starting y position
            })

    def update(self):
        # Update notifications
        for notif in self.notifications[:]:
            notif['lifetime'] -= 1
            if notif['lifetime'] <= 0:
                self.notifications.remove(notif)

    def draw(self, screen):
        # Display score
        score_text = self.font.render(f"Score: {self.game.score.score}", True, COLORS['white'])
        screen.blit(score_text, (500, GRID_Y_OFFSET))
        # Display level
        level_text = self.font.render(f"Level: {self.game.score.level}", True, COLORS['white'])
        screen.blit(level_text, (500, GRID_Y_OFFSET + 50))
        # Display next piece text
        next_text = self.font.render("Next:", True, COLORS['white'])
        screen.blit(next_text, (500, GRID_Y_OFFSET + 100))

        # Draw next piece
        next_piece = self.game.next_piece
        block_size = CELL_SIZE
        offset_x = 17  # Adjusted to move the piece slightly to the right
        offset_y = 7   # Adjusted to move the piece down, below the "Next:" text
        for y, row in enumerate(next_piece.shape):
            for x, cell in enumerate(row):
                if cell:
                    rect = pygame.Rect(
                        500 + (x * block_size),  # Use absolute positioning
                        GRID_Y_OFFSET + 140 + (y * block_size),  # Use absolute positioning and move down
                        block_size,
                        block_size,
                    )
                    pygame.draw.rect(screen, next_piece.color, rect)
                    pygame.draw.rect(screen, COLORS['white'], rect, 1)

        # Draw notifications
        for idx, notif in enumerate(self.notifications):
            text_surface = self.small_font.render(notif['text'], True, notif['color'])
            text_rect = text_surface.get_rect(center=(SCREEN_WIDTH - 200, GRID_Y_OFFSET + 300 + idx * 30))
            screen.blit(text_surface, text_rect)
