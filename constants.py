# constants.py

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800

# Grid dimensions
GRID_WIDTH = 10
GRID_HEIGHT = 20
CELL_SIZE = 30
GRID_X_OFFSET = 200
GRID_Y_OFFSET = 50

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
