# tetromino.py

import pygame
from constants import COLORS, ANIMATION_SPEED, MAX_LOCK_MOVES
import copy

SHAPES = {
    'I': [[0, 0, 0, 0],
          [1, 1, 1, 1],
          [0, 0, 0, 0],
          [0, 0, 0, 0]],
    'O': [[1, 1],
          [1, 1]],
    'T': [[0, 1, 0],
          [1, 1, 1],
          [0, 0, 0]],
    'S': [[0, 1, 1],
          [1, 1, 0],
          [0, 0, 0]],
    'Z': [[1, 1, 0],
          [0, 1, 1],
          [0, 0, 0]],
    'J': [[1, 0, 0],
          [1, 1, 1],
          [0, 0, 0]],
    'L': [[0, 0, 1],
          [1, 1, 1],
          [0, 0, 0]],
}

# Wall kick data (SRS)
WALL_KICK_DATA = {
    'JLSTZ': [
        [(0, 0), (-1, 0), (-1, 1), (0, -2), (-1, -2)],
        [(0, 0), (1, 0), (1, -1), (0, 2), (1, 2)],
        [(0, 0), (1, 0), (1, 1), (0, -2), (1, -2)],
        [(0, 0), (-1, 0), (-1, -1), (0, 2), (-1, 2)],
    ],
    'I': [
        [(0, 0), (-2, 0), (1, 0), (-2, -1), (1, 2)],
        [(0, 0), (-1, 0), (2, 0), (-1, 2), (2, -1)],
        [(0, 0), (2, 0), (-1, 0), (2, 1), (-1, -2)],
        [(0, 0), (1, 0), (-2, 0), (1, -2), (-2, 1)],
    ],
}

class Tetromino:
    def __init__(self, shape_name, grid):
        self.shape_name = shape_name
        self.shape = SHAPES[shape_name]
        self.color = COLORS[shape_name]
        self.grid = grid
        self.x = grid.width // 2 - len(self.shape[0]) // 2
        self.y = -1  # Start above the grid
        self.is_locked = False
        self.rotation_state = 0
        self.visual_x = self.x * grid.cell_size + grid.x_offset
        self.visual_y = self.y * grid.cell_size + grid.y_offset
        self.target_x = self.visual_x
        self.target_y = self.visual_y
        self.lock_delay_timer = 0
        self.lock_moves_count = 0
        self.lock_delay_active = False

    def move(self, dx, dy):
        old_x, old_y = self.x, self.y
        self.x += dx
        self.y += dy
        
        if self.grid.is_collision(self):
            self.x, self.y = old_x, old_y
            if dy > 0:  # If moving down caused collision
                if not self.lock_delay_active:
                    self.lock_delay_active = True
                    self.lock_delay_timer = 0
            return False
        
        # Reset lock delay if moving horizontally while touching ground
        if dx != 0 and self.is_touching_ground():
            self.reset_lock_delay()
        
        self.target_x = self.x * self.grid.cell_size + self.grid.x_offset
        self.target_y = self.y * self.grid.cell_size + self.grid.y_offset
        return True

    def update_position(self):
        self.visual_x += (self.target_x - self.visual_x) * ANIMATION_SPEED
        self.visual_y += (self.target_y - self.visual_y) * ANIMATION_SPEED

    def rotate(self, clockwise=True):
        old_shape = self.shape
        old_rotation_state = self.rotation_state

        if clockwise:
            self.shape = [list(row) for row in zip(*self.shape[::-1])]
            self.rotation_state = (self.rotation_state + 1) % 4
        else:
            self.shape = [list(row) for row in zip(*[row[::-1] for row in self.shape])]
            self.rotation_state = (self.rotation_state - 1) % 4

        # Try basic rotation first
        if not self.grid.is_collision(self):
            self.target_x = self.x * self.grid.cell_size + self.grid.x_offset
            self.target_y = self.y * self.grid.cell_size + self.grid.y_offset
            return True

        # If basic rotation fails, try wall kicks
        if self.wall_kick(old_rotation_state):
            self.target_x = self.x * self.grid.cell_size + self.grid.x_offset
            self.target_y = self.y * self.grid.cell_size + self.grid.y_offset
            return True

        # If all attempts fail, revert the rotation
        self.shape = old_shape
        self.rotation_state = old_rotation_state
        return False

    def wall_kick(self, old_rotation_state):
        if self.shape_name == 'O':
            return False  # O piece shouldn't need wall kicks

        kick_data = WALL_KICK_DATA['I'] if self.shape_name == 'I' else WALL_KICK_DATA['JLSTZ']
        kick_set = kick_data[old_rotation_state]

        for dx, dy in kick_set:
            self.x += dx
            self.y += dy
            if not self.grid.is_collision(self):
                print(f"Wall kick succeeded with offset: ({dx}, {dy})")  # Debug print
                return True
            self.x -= dx
            self.y -= dy

        print("All wall kicks failed")  # Debug print
        return False

    def is_touching_ground(self):
        # Check if piece is touching ground or other pieces
        self.y += 1
        collision = self.grid.is_collision(self)
        self.y -= 1
        return collision

    def reset_lock_delay(self):
        if self.lock_delay_active and self.lock_moves_count < MAX_LOCK_MOVES:
            self.lock_delay_timer = 0
            self.lock_moves_count += 1
            # If we're no longer touching ground after the move, deactivate lock delay
            if not self.is_touching_ground():
                self.lock_delay_active = False
                self.lock_moves_count = 0

    def hard_drop(self):
        drop_distance = 0
        while not self.grid.is_collision(self):
            self.y += 1
            drop_distance += 1
        self.y -= 1
        self.is_locked = True  # Immediately lock on hard drop
        return drop_distance - 1

    def get_ghost_position(self):
        """Calculate the ghost piece position."""
        ghost_tetromino = Tetromino(self.shape_name, self.grid)
        ghost_tetromino.shape = copy.deepcopy(self.shape)
        ghost_tetromino.color = self.color
        ghost_tetromino.x = self.x
        ghost_tetromino.y = self.y
        ghost_tetromino.is_locked = self.is_locked

        while not self.grid.is_collision(ghost_tetromino):
            ghost_tetromino.y += 1
        ghost_tetromino.y -= 1

        return ghost_tetromino

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
                    int(self.visual_x + (x - self.x) * self.grid.cell_size),
                    int(self.visual_y + (y - self.y) * self.grid.cell_size),
                    self.grid.cell_size,
                    self.grid.cell_size,
                )
                pygame.draw.rect(screen, self.color, rect)
                pygame.draw.rect(screen, COLORS['white'], rect, 1)
