import pygame
import random

pygame.init()

#dimensions
SCREEN_WIDTH = 300
SCREEN_HEIGHT = 600
GRID_WIDTH = 10
GRID_HEIGHT = 20
CELL_SIZE = 30

#colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

#shapes
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

#initialising the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Tetris')

#initialising the grid
grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]

#drawing the grid
def draw_grid():
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, WHITE, rect, 1)

#drawing a piece
def draw_piece(piece, offset):
    shape = SHAPES[piece]
    off_x, off_y = offset
    for y, row in enumerate(shape):
        for x, cell in enumerate(row):
            if cell:
                rect = pygame.Rect((off_x + x) * CELL_SIZE, (off_y + y) * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(screen, WHITE, rect)

#main game loop
def main():
    clock = pygame.time.Clock()
    piece = random.randint(0, len(SHAPES) - 1)
    piece_x = GRID_WIDTH // 2 - len(SHAPES[piece][0]) // 2
    piece_y = 0

    running = True
    while running:
        screen.fill(BLACK)
        draw_grid()
        draw_piece(piece, (piece_x, piece_y))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    piece_x -= 1
                elif event.key == pygame.K_RIGHT:
                    piece_x += 1
                elif event.key == pygame.K_UP:
                    # Rotation logic will be added later
                    pass
                elif event.key == pygame.K_DOWN:
                    piece_y += 1
                elif event.key == pygame.K_SPACE:
                    # Instant drop logic will be added later
                    pass
        clock.tick(10)

    pygame.quit()

if __name__ == '__main__':
    main()