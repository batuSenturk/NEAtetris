# hud.py

import pygame
from constants import FONT_NAME, FONT_SIZE, COLORS, CELL_SIZE, GRID_Y_OFFSET

class HUD:
    def __init__(self, game):
        self.game = game
        self.font = pygame.font.Font(FONT_NAME, FONT_SIZE)

    def draw(self, screen):
        # Display score
        score_text = self.font.render(f"Score: {self.game.score.score}", True, COLORS['white'])
        screen.blit(score_text, (500, GRID_Y_OFFSET))
        # Display level
        level_text = self.font.render(f"Level: {self.game.score.level}", True, COLORS['white'])
        screen.blit(level_text, (500, GRID_Y_OFFSET + 50))
        # Display next piece
        next_text = self.font.render("Next:", True, COLORS['white'])
        screen.blit(next_text, (500, GRID_Y_OFFSET + 100))

        # Draw next piece
        next_piece = self.game.next_piece
        block_size = CELL_SIZE
        offset_x = 16  # Adjust these offsets as needed
        offset_y = 6   # Adjusted to prevent overlap with HUD
        for y, row in enumerate(next_piece.shape):
            for x, cell in enumerate(row):
                if cell:
                    rect = pygame.Rect(
                        (offset_x + x) * block_size,
                        (offset_y + y) * block_size,
                        block_size,
                        block_size,
                    )
                    pygame.draw.rect(screen, next_piece.color, rect)
                    pygame.draw.rect(screen, COLORS['white'], rect, 1)
