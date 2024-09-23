# grid.py

import pygame
from constants import CELL_SIZE, GRID_X_OFFSET, GRID_Y_OFFSET, COLORS, ANIMATION_SPEED

class Grid:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.cells = [[0 for _ in range(width)] for _ in range(height)]
        self.cell_size = CELL_SIZE
        self.x_offset = GRID_X_OFFSET
        self.y_offset = GRID_Y_OFFSET

        # Animation related
        self.animating_lines = []  # List of y positions currently animating
        self.animation_alpha = 255  # Start fully opaque

    def is_collision(self, piece):
        for x, y in piece.get_block_positions():
            if x < 0 or x >= self.width or y >= self.height:
                return True
            if y >= 0 and self.cells[y][x]:
                return True
        return False

    def lock_piece(self, piece):
        for x, y in piece.get_block_positions():
            if y >= 0:
                self.cells[y][x] = piece.color

    def clear_lines(self):
        lines_cleared = 0
        animating = []
        for y in range(self.height):
            if all(self.cells[y][x] != 0 for x in range(self.width)):
                lines_cleared += 1
                animating.append(y)
        if lines_cleared > 0:
            self.animating_lines = animating
            self.animation_alpha = 255  # Reset alpha for new animation
        return lines_cleared

    def trigger_line_clear_animation(self, lines_cleared):
        """Start the line clear animation."""
        # Already handled in clear_lines by setting animating_lines and animation_alpha
        pass

    def update_animation(self):
        if self.animating_lines:
            # Decrease alpha for fade-out effect
            self.animation_alpha -= ANIMATION_SPEED
            if self.animation_alpha <= 0:
                # Lines to remove
                lines_to_remove = self.animating_lines.copy()
                self.animating_lines = []
                self.animation_alpha = 255
                # Remove the lines from cells
                self.cells = [row for y, row in enumerate(self.cells) if y not in lines_to_remove]
                # Add empty lines at the top
                for _ in lines_to_remove:
                    self.cells.insert(0, [0 for _ in range(self.width)])

    def draw(self, screen):
        for y in range(self.height):
            for x in range(self.width):
                rect = pygame.Rect(
                    self.x_offset + x * self.cell_size,
                    self.y_offset + y * self.cell_size,
                    self.cell_size,
                    self.cell_size,
                )
                if self.cells[y][x]:
                    pygame.draw.rect(screen, self.cells[y][x], rect)
                    pygame.draw.rect(screen, COLORS['white'], rect, 1)
                else:
                    pygame.draw.rect(screen, COLORS['grid_line'], rect, 1)

        # Draw animating lines with fading effect
        if self.animating_lines:
            for y in self.animating_lines:
                for x in range(self.width):
                    rect = pygame.Rect(
                        self.x_offset + x * self.cell_size,
                        self.y_offset + y * self.cell_size,
                        self.cell_size,
                        self.cell_size,
                    )
                    # Create a surface with the current alpha
                    anim_surface = pygame.Surface((self.cell_size, self.cell_size), pygame.SRCALPHA)
                    anim_surface.fill((255, 255, 255, self.animation_alpha))
                    screen.blit(anim_surface, rect.topleft)
                    pygame.draw.rect(screen, COLORS['white'], rect, 1)
