# main.py

import pygame
from game import Game
from constants import SCREEN_WIDTH, SCREEN_HEIGHT

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Tetris")
    clock = pygame.time.Clock()
    game = Game(screen)

    while True:
        game.handle_events()
        game.update()
        game.draw()
        pygame.display.flip()
        clock.tick(60)  # Limit to 60 frames per second

if __name__ == "__main__":
    main()
