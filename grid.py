# grid.py

import pygame
from constants import CELL_SIZE, GRID_X_OFFSET, GRID_Y_OFFSET, COLORS

class Grid:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.cells = [[0 for _ in range(width)] for _ in range(height)]
        self.cell_size = CELL_SIZE
        self.x_offset = GRID_X_OFFSET
        self.y_offset = GRID_Y_OFFSET

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
        new_cells = [row for row in self.cells if any(cell == 0 for cell in row)]
        lines_cleared = self.height - len(new_cells)
        for _ in range(lines_cleared):
            new_cells.insert(0, [0 for _ in range(self.width)])
        self.cells = new_cells
        return lines_cleared

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
