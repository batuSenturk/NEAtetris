import pygame
import random

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 300
SCREEN_HEIGHT = 600
GRID_WIDTH = 10
GRID_HEIGHT = 20
CELL_SIZE = 30

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)

# Shapes
SHAPES = [
    [[1, 1, 1],
     [0, 1, 0]],

    [[0, 1, 1],
     [1, 1, 0]],

    [[1, 1, 0],
     [0, 1, 1]],

    [[1, 1, 1, 1]],

    [[1, 1],
     [1, 1]],

    [[1, 1, 1],
     [1, 0, 0]],

    [[1, 1, 1],
     [0, 0, 1]]
]

# Initialize the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Tetris')

# Function to draw the grid
def draw_grid():
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, GRAY, rect, 1)

# Function to draw a piece
def draw_piece(piece, offset):
    shape = SHAPES[piece]
    off_x, off_y = offset
    for y, row in enumerate(shape):
        for x, cell in enumerate(row):
            if cell:
                rect = pygame.Rect((off_x + x) * CELL_SIZE, (off_y + y) * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(screen, WHITE, rect)

# Function to check collision
def check_collision(grid, shape, offset):
    off_x, off_y = offset
    for y, row in enumerate(shape):
        for x, cell in enumerate(row):
            if cell:
                if x + off_x < 0 or x + off_x >= GRID_WIDTH or y + off_y >= GRID_HEIGHT:
                    return True
                if y + off_y < 0 or grid[y + off_y][x + off_x]:
                    return True
    return False

# Function to lock a piece in place
def lock_piece(grid, shape, offset):
    off_x, off_y = offset
    for y, row in enumerate(shape):
        for x, cell in enumerate(row):
            if cell:
                grid[y + off_y][x + off_x] = 1

# Function to clear completed lines
def clear_lines(grid):
    new_grid = [row for row in grid if any(cell == 0 for cell in row)]
    lines_cleared = GRID_HEIGHT - len(new_grid)
    new_grid = [[0] * GRID_WIDTH for _ in range(lines_cleared)] + new_grid
    return new_grid, lines_cleared

# Function to draw the grid cells
def draw_grid_cells(grid):
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            if grid[y][x]:
                rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(screen, WHITE, rect)

# Main game loop
def main():
    global grid
    grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
    clock = pygame.time.Clock()
    piece = random.randint(0, len(SHAPES) - 1)
    piece_x = GRID_WIDTH // 2 - len(SHAPES[piece][0]) // 2
    piece_y = 0
    score = 0
    running = True
    game_over = False

    while running:
        screen.fill(BLACK)
        draw_grid()
        draw_grid_cells(grid)
        draw_piece(piece, (piece_x, piece_y))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    if not check_collision(grid, SHAPES[piece], (piece_x - 1, piece_y)):
                        piece_x -= 1
                elif event.key == pygame.K_RIGHT:
                    if not check_collision(grid, SHAPES[piece], (piece_x + 1, piece_y)):
                        piece_x += 1
                elif event.key == pygame.K_UP:
                    rotated_piece = list(zip(*SHAPES[piece][::-1]))
                    if not check_collision(grid, rotated_piece, (piece_x, piece_y)):
                        SHAPES[piece] = rotated_piece
                elif event.key == pygame.K_DOWN:
                    if not check_collision(grid, SHAPES[piece], (piece_x, piece_y + 1)):
                        piece_y += 1
                elif event.key == pygame.K_SPACE:
                    while not check_collision(grid, SHAPES[piece], (piece_x, piece_y + 1)):
                        piece_y += 1

        if not check_collision(grid, SHAPES[piece], (piece_x, piece_y + 1)):
            piece_y += 1
        else:
            lock_piece(grid, SHAPES[piece], (piece_x, piece_y))
            grid, lines_cleared = clear_lines(grid)
            score += lines_cleared * 100
            piece = random.randint(0, len(SHAPES) - 1)
            piece_x = GRID_WIDTH // 2 - len(SHAPES[piece][0]) // 2
            piece_y = 0
            if check_collision(grid, SHAPES[piece], (piece_x, piece_y)):
                game_over = True

        if game_over:
            font = pygame.font.Font(None, 36)
            text = font.render("Game Over", True, WHITE)
            screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 - text.get_height() // 2))
            pygame.display.flip()
            pygame.time.wait(2000)
            running = False

        clock.tick(10)

    pygame.quit()

if __name__ == '__main__':
    main()
