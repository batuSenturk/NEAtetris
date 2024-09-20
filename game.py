# game.py

import pygame
from grid import Grid
from piece_generator import PieceGenerator
from score import Score
from hud import HUD
from menu import Menu
from button import Button
from constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, COLORS, FONT_NAME,
    INITIAL_DROP_SPEED, MIN_DROP_SPEED, SPEED_INCREMENT
)

class Game:
    def __init__(self, screen):
        self.screen = screen
        self.current_screen = 'menu'  # Possible screens: 'menu', 'game', 'pause', 'game_over'
        self.menu = Menu(self)
        self.mode = 'Classic Mode'  # Default game mode
        self.grid = None
        self.piece_generator = None
        self.current_piece = None
        self.next_piece = None
        self.score = None
        self.hud = None
        self.is_paused = False
        self.game_over = False
        self.drop_timer = 0
        self.drop_speed = INITIAL_DROP_SPEED
        self.last_update_time = pygame.time.get_ticks()

        # Back button when game is paused
        self.back_button = Button(
            rect=(20, 20, 100, 40),
            text="Back",
            action=self.return_to_menu
        )

        # Buttons for game over screen
        self.game_over_buttons = [
            Button(
                rect=(SCREEN_WIDTH // 2 - 75, SCREEN_HEIGHT // 2 + 20, 150, 50),
                text="Play Again",
                action=self.start_new_game
            ),
            Button(
                rect=(SCREEN_WIDTH // 2 - 75, SCREEN_HEIGHT // 2 + 80, 150, 50),
                text="Menu",
                action=self.return_to_menu
            )
        ]

    def start_new_game(self, game=None):
        # Initialize or reset game variables
        self.grid = Grid(10, 20)
        self.piece_generator = PieceGenerator(self.grid)
        self.current_piece = self.piece_generator.get_next_piece()
        self.next_piece = self.piece_generator.preview_next_piece()
        self.score = Score()
        self.hud = HUD(self)
        self.is_paused = False
        self.game_over = False
        self.drop_timer = 0
        self.drop_speed = INITIAL_DROP_SPEED
        self.last_update_time = pygame.time.get_ticks()
        self.current_screen = 'game'  # Ensure we're in the game screen

    def return_to_menu(self, game=None):
        self.current_screen = 'menu'
        self.is_paused = False
        self.game_over = False

    def handle_events(self):
        if self.current_screen == 'menu':
            self.menu.handle_events()
        elif self.current_screen == 'game':
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if self.game_over:
                    for button in self.game_over_buttons:
                        button.handle_event(event, self)
                    continue
                if self.is_paused:
                    # Handle events for the back button when paused
                    self.back_button.handle_event(event, self)
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                        self.is_paused = False
                else:
                    # Handle input events
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_LEFT:
                            self.current_piece.move(-1, 0)
                        elif event.key == pygame.K_RIGHT:
                            self.current_piece.move(1, 0)
                        elif event.key == pygame.K_DOWN:
                            self.current_piece.move(0, 1)
                        elif event.key == pygame.K_UP:
                            self.current_piece.rotate()
                        elif event.key == pygame.K_SPACE:
                            self.current_piece.hard_drop()
                        elif event.key == pygame.K_p:
                            self.is_paused = True

    def update(self):
        if self.current_screen == 'menu':
            self.menu.update()
        elif self.current_screen == 'game':
            if self.game_over or self.is_paused:
                # Do not update the game state if the game is over or paused
                return
            current_time = pygame.time.get_ticks()
            delta_time = current_time - self.last_update_time
            self.drop_timer += delta_time
            self.last_update_time = current_time

            if self.drop_timer > self.drop_speed:
                self.current_piece.move(0, 1)
                self.drop_timer = 0

            if self.current_piece.is_locked:
                # Before spawning a new piece, check if the locked piece is above the grid
                for x, y in self.current_piece.get_block_positions():
                    if y < 0:
                        self.game_over = True
                        return  # Exit update to prevent spawning a new piece
                self.grid.lock_piece(self.current_piece)
                lines_cleared = self.grid.clear_lines()
                if lines_cleared > 0:
                    self.score.update(lines_cleared)
                    self.score.update_level()
                    self.update_drop_speed()
                self.current_piece = self.piece_generator.get_next_piece()
                self.next_piece = self.piece_generator.preview_next_piece()
                # Check for collision immediately after spawning the new piece
                if self.grid.is_collision(self.current_piece):
                    self.game_over = True

    def update_drop_speed(self):
        self.drop_speed = max(
            MIN_DROP_SPEED,
            INITIAL_DROP_SPEED - (self.score.level - 1) * SPEED_INCREMENT
        )

    def draw(self):
        if self.current_screen == 'menu':
            self.menu.draw(self.screen)
        elif self.current_screen == 'game':
            self.screen.fill(COLORS['background'])
            self.grid.draw(self.screen)
            if not self.game_over:
                self.current_piece.draw(self.screen)
            self.hud.draw(self.screen)
            if self.is_paused:
                self.draw_pause_overlay()
                # Draw back button when paused
                self.back_button.draw(self.screen)
            if self.game_over:
                self.draw_game_over()

    def draw_pause_overlay(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        font = pygame.font.Font(FONT_NAME, 72)
        text = font.render("Paused", True, COLORS['white'])
        rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(text, rect)

    def draw_game_over(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        font = pygame.font.Font(FONT_NAME, 72)
        text = font.render("Game Over", True, COLORS['white'])
        rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 80))
        self.screen.blit(text, rect)

        # Draw buttons
        for button in self.game_over_buttons:
            button.draw(self.screen)
