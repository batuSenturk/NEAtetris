# tetromino.py

import pygame
from constants import COLORS

SHAPES = {
    'I': [[1, 1, 1, 1]],
    'O': [[1, 1],
          [1, 1]],
    'T': [[0, 1, 0],
          [1, 1, 1]],
    'S': [[0, 1, 1],
          [1, 1, 0]],
    'Z': [[1, 1, 0],
          [0, 1, 1]],
    'J': [[1, 0, 0],
          [1, 1, 1]],
    'L': [[0, 0, 1],
          [1, 1, 1]],
}

class Tetromino:
    def __init__(self, shape_name, grid):
        self.shape_name = shape_name
        self.shape = SHAPES[shape_name]
        self.color = COLORS[shape_name]
        self.grid = grid
        self.x = grid.width // 2 - len(self.shape[0]) // 2
        self.y = -2  # Start above the grid
        self.is_locked = False

    def move(self, dx, dy):
        self.x += dx
        self.y += dy
        if self.grid.is_collision(self):
            self.x -= dx
            self.y -= dy
            if dy > 0:
                self.is_locked = True

    def rotate(self):
        old_shape = self.shape
        self.shape = [list(row) for row in zip(*self.shape[::-1])]
        if self.grid.is_collision(self):
            self.shape = old_shape  # Undo rotation

    def hard_drop(self):
        while not self.is_locked:
            self.move(0, 1)

    def get_block_positions(self):
        positions = []
        for y, row in enumerate(self.shape):
            for x, cell in enumerate(row):
                if cell:
                    positions.append((self.x + x, self.y + y))
        return positions

    def draw(self, screen):
        for x, y in self.get_block_positions():
            if y >= 0:
                rect = pygame.Rect(
                    self.grid.x_offset + x * self.grid.cell_size,
                    self.grid.y_offset + y * self.grid.cell_size,
                    self.grid.cell_size,
                    self.grid.cell_size,
                )
                pygame.draw.rect(screen, self.color, rect)
                pygame.draw.rect(screen, COLORS['white'], rect, 1)
