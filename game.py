# game.py

import pygame
from grid import Grid
from piece_generator import PieceGenerator
from score import Score
from hud import HUD
from constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, COLORS,
    INITIAL_DROP_SPEED, MIN_DROP_SPEED, SPEED_INCREMENT, FONT_NAME
)

class Game:
    def __init__(self, screen):
        self.screen = screen
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

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            # Handle input events
            elif event.type == pygame.KEYDOWN:
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
                    self.is_paused = not self.is_paused

    def update(self):
        if not self.is_paused and not self.game_over:
            current_time = pygame.time.get_ticks()
            delta_time = current_time - self.last_update_time
            self.drop_timer += delta_time
            self.last_update_time = current_time

            if self.drop_timer > self.drop_speed:
                self.current_piece.move(0, 1)
                self.drop_timer = 0

            if self.current_piece.is_locked:
                self.grid.lock_piece(self.current_piece)
                lines_cleared = self.grid.clear_lines()
                if lines_cleared > 0:
                    self.score.update(lines_cleared)
                    self.score.update_level()
                    self.update_drop_speed()
                self.current_piece = self.piece_generator.get_next_piece()
                self.next_piece = self.piece_generator.preview_next_piece()
                if self.grid.is_collision(self.current_piece):
                    self.game_over = True

    def update_drop_speed(self):
        self.drop_speed = max(
            MIN_DROP_SPEED,
            INITIAL_DROP_SPEED - (self.score.level - 1) * SPEED_INCREMENT
        )

    def draw(self):
        self.screen.fill(COLORS['background'])
        self.grid.draw(self.screen)
        self.current_piece.draw(self.screen)
        self.hud.draw(self.screen)
        if self.is_paused:
            self.draw_pause_overlay()
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
        rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(text, rect)
