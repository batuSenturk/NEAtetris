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
        self.lines_to_clear = []

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
        self.lines_to_clear = []
        for y in range(self.height - 1, -1, -1):
            if all(self.cells[y][x] != 0 for x in range(self.width)):
                self.lines_to_clear.append(y)
        
        if self.lines_to_clear:
            self.remove_lines()
        
        return len(self.lines_to_clear)

    def remove_lines(self):
        new_cells = [[0 for _ in range(self.width)] for _ in range(len(self.lines_to_clear))]
        old_cells = [row for i, row in enumerate(self.cells) if i not in self.lines_to_clear]
        self.cells = new_cells + old_cells
        self.lines_to_clear = []

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

    def is_board_clear(self):
        """Check if the entire board is clear"""
        return all(cell == 0 for row in self.cells for cell in row)
