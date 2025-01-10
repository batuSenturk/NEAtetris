# constants.py

import pygame

# Screen dimensions
SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 800

# Grid dimensions
GRID_WIDTH = 10
GRID_HEIGHT = 20
CELL_SIZE = 30
GRID_X_OFFSET = 200
GRID_Y_OFFSET = 100

# Colors (RGB tuples)
COLORS = {
    'I': (0, 255, 255),
    'O': (255, 255, 0),
    'T': (128, 0, 128),
    'S': (0, 255, 0),
    'Z': (255, 0, 0),
    'J': (0, 0, 255),
    'L': (255, 165, 0),
    'grid_line': (50, 50, 50),
    'background': (0, 0, 0),
    'white': (255, 255, 255),
}

# Shapes (2D Matrices)
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
    'JLSTZ': {
        (0, 1): [(0, 0), (-1, 0), (-1, +1), (0, -2), (-1, -2)],
        (1, 0): [(0, 0), (+1, 0), (+1, -1), (0, +2), (+1, +2)],
        (1, 2): [(0, 0), (+1, 0), (+1, +1), (0, -2), (+1, -2)],
        (2, 1): [(0, 0), (-1, 0), (-1, -1), (0, +2), (-1, +2)],
        (2, 3): [(0, 0), (+1, 0), (+1, -1), (0, +2), (+1, +2)],
        (3, 2): [(0, 0), (-1, 0), (-1, +1), (0, -2), (-1, -2)],
        (3, 0): [(0, 0), (-1, 0), (-1, -1), (0, +2), (-1, +2)],
        (0, 3): [(0, 0), (+1, 0), (+1, +1), (0, -2), (+1, -2)],
    },
    'I': {
        (0, 1): [(0, 0), (-2, 0), (+1, 0), (-2, -1), (+1, +2)],
        (1, 0): [(0, 0), (+2, 0), (-1, 0), (+2, +1), (-1, -2)],
        (1, 2): [(0, 0), (-1, 0), (+2, 0), (-1, +2), (+2, -1)],
        (2, 1): [(0, 0), (+1, 0), (-2, 0), (+1, -2), (-2, +1)],
        (2, 3): [(0, 0), (+2, 0), (-1, 0), (+2, +1), (-1, -2)],
        (3, 2): [(0, 0), (-2, 0), (+1, 0), (-2, -1), (+1, +2)],
        (3, 0): [(0, 0), (+1, 0), (-2, 0), (+1, -2), (-2, +1)],
        (0, 3): [(0, 0), (-1, 0), (+2, 0), (-1, +2), (+2, -1)],
    },
}

# Drop speed (milliseconds per drop)
INITIAL_DROP_SPEED = 500
MIN_DROP_SPEED = 100
SPEED_INCREMENT = 20

# Scoring
SCORING_TABLE = {1: 40, 2: 100, 3: 300, 4: 1200}
LINES_PER_LEVEL = 10

# Fonts
FONT_NAME = None  # Default font
FONT_SIZE = 36

# Menu dimensions
MENU_BACKGROUND_COLOR = (30, 30, 30)
BUTTON_COLOR = (70, 70, 70)
BUTTON_HOVER_COLOR = (100, 100, 100)
BUTTON_TEXT_COLOR = (255, 255, 255)
BUTTON_WIDTH = 300
BUTTON_HEIGHT = 50

# Define ghost piece transparency
GHOST_ALPHA = 50  # Transparency level (0-255)

# High Score Constants
HIGH_SCORE_FILE = 'highscores.json'
MAX_HIGH_SCORES = 5

# Animation constants
ANIMATION_SPEED = 0.5  # Slow - 0.0, Fast - 1.0

# Lock delay settings
LOCK_DELAY = 500  # 500ms = 0.5 seconds
MAX_LOCK_MOVES = 10  # Maximum number of moves before forcing lock

# After GRID_Y_OFFSET
HOLD_X_OFFSET = 500  # X position for hold piece display
HOLD_Y_OFFSET = 100  # Y position for hold piece display

# In the scoring section, add:
HOLD_KEY = pygame.K_c  # Key to hold pieces
