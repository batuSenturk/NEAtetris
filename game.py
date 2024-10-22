# game.py

import pygame
from grid import Grid
from piece_generator import PieceGenerator
from score import Score
from hud import HUD
from menu import Menu
from button import Button
from high_score import HighScore
from input_box import InputBox
from constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, COLORS, FONT_NAME,
    INITIAL_DROP_SPEED, MIN_DROP_SPEED, SPEED_INCREMENT, GHOST_ALPHA
)
from tetromino import Tetromino

class Game:
    def __init__(self, screen):
        self.screen = screen
        self.current_screen = 'menu'  # Possible screens: 'menu', 'game', 'pause', 'game_over', 'enter_name', 'high_scores'
        self.menu = Menu(self)
        self.high_score = HighScore()
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
        self.soft_drop_count = 0
        self.drop_height = 0
        self.last_rotation = False
        self.last_move_was_rotation = False
        self.hard_drop_count = 0

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

        # Input box for entering name
        self.input_box = None  # Initialized when needed

        # Buttons for high score display
        self.high_score_buttons = [
            Button(
                rect=(SCREEN_WIDTH // 2 - 75, SCREEN_HEIGHT - 150, 150, 50),
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
                            self.last_move_was_rotation = False
                        elif event.key == pygame.K_RIGHT:
                            self.current_piece.move(1, 0)
                            self.last_move_was_rotation = False
                        elif event.key == pygame.K_DOWN:
                            if self.current_piece.move(0, 1):
                                self.soft_drop_count += 1
                            self.last_move_was_rotation = False
                        elif event.key == pygame.K_UP:
                            self.last_rotation = self.current_piece.rotate()
                            self.last_move_was_rotation = True
                        elif event.key == pygame.K_SPACE:
                            self.hard_drop_count = self.current_piece.hard_drop()
                            self.last_move_was_rotation = False
                        elif event.key == pygame.K_p:
                            self.is_paused = True
        elif self.current_screen == 'enter_name':
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                name = self.input_box.handle_event(event)
                if name is not None:
                    self.high_score.add_score(name, self.score.score)
                    self.current_screen = 'high_scores'
        elif self.current_screen == 'high_scores':
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                for button in self.high_score_buttons:
                    button.handle_event(event, self)

    def update(self):
        if self.current_screen == 'menu':
            self.menu.update()
        elif self.current_screen == 'game':
            if self.game_over or self.is_paused:
                return

            current_time = pygame.time.get_ticks()
            delta_time = current_time - self.last_update_time
            self.drop_timer += delta_time
            self.last_update_time = current_time

            if self.drop_timer > self.drop_speed:
                self.current_piece.move(0, 1)
                self.drop_timer = 0
                self.drop_height += 1
                self.last_move_was_rotation = False

            if self.current_piece.is_locked:
                # Check for T-spin
                t_spin_type = self.check_t_spin()
                mini_t_spin = self.check_mini_t_spin() if t_spin_type else False

                self.grid.lock_piece(self.current_piece)
                lines_cleared = self.grid.clear_lines()
                
                # Calculate score
                turn_score = self.score.update(
                    lines_cleared,
                    t_spin_type,
                    mini_t_spin,
                    self.drop_height,
                    self.soft_drop_count,
                    self.hard_drop_count
                )
                
                # Reset drop counters
                self.drop_height = 0
                self.soft_drop_count = 0
                self.hard_drop_count = 0
                self.last_rotation = False
                self.last_move_was_rotation = False

                if lines_cleared > 0:
                    self.score.update_level()
                    self.update_drop_speed()
                    self.grid.trigger_line_clear_animation(lines_cleared)

                # Check for Tetris Clear (entire board clear)
                if self.grid.is_board_clear():
                    tetris_clear_bonus = self.score.add_tetris_clear_bonus()
                    # You might want to trigger a special animation or sound here

                self.current_piece = self.piece_generator.get_next_piece()
                self.next_piece = self.piece_generator.preview_next_piece()

                if self.grid.is_collision(self.current_piece):
                    self.game_over = True
                    self.current_screen = 'game_over'
                    self.check_high_score()

            # Update animations
            self.grid.update_animation()

    def check_high_score(self):
        """Check if the current score qualifies as a high score."""
        if self.high_score.is_high_score(self.score.score):
            # Prompt the player to enter their name
            self.input_box = InputBox(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 50, 200, 50)
            self.current_screen = 'enter_name'
        else:
            # No high score achieved, go directly to high scores
            self.current_screen = 'high_scores'

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
                # Draw the ghost piece
                self.draw_ghost_piece()
                # Draw the current piece
                self.current_piece.draw(self.screen)
            self.hud.draw(self.screen)
            if self.is_paused:
                self.draw_pause_overlay()
                # Draw back button when paused
                self.back_button.draw(self.screen)
            if self.game_over:
                self.draw_game_over()
        elif self.current_screen == 'game_over':
            self.draw_game_over()
        elif self.current_screen == 'enter_name':
            self.draw_enter_name()
        elif self.current_screen == 'high_scores':
            self.draw_high_scores()

    def draw_ghost_piece(self):
        ghost_piece = self.current_piece.get_ghost_position()
        for x, y in ghost_piece.get_block_positions():
            if y >= 0:
                rect = pygame.Rect(
                    self.grid.x_offset + x * self.grid.cell_size,
                    self.grid.y_offset + y * self.grid.cell_size,
                    self.grid.cell_size,
                    self.grid.cell_size,
                )
                # Use a semi-transparent version of the piece's color
                ghost_surface = pygame.Surface((self.grid.cell_size, self.grid.cell_size), pygame.SRCALPHA)
                r, g, b = self.current_piece.color
                ghost_surface.fill((r, g, b, GHOST_ALPHA))
                self.screen.blit(ghost_surface, rect.topleft)
                pygame.draw.rect(self.screen, COLORS['white'], rect, 1)

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

    def draw_enter_name(self):
        self.screen.fill(COLORS['background'])
        font = pygame.font.Font(FONT_NAME, 48)
        prompt = font.render("New High Score! Enter your name:", True, COLORS['white'])
        prompt_rect = prompt.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(prompt, prompt_rect)

        # Draw input box
        self.input_box.draw(self.screen)

    def draw_high_scores(self):
        self.screen.fill(COLORS['background'])
        font = pygame.font.Font(FONT_NAME, 48)
        title = font.render("High Scores", True, COLORS['white'])
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 100))
        self.screen.blit(title, title_rect)

        # Display high scores
        font_small = pygame.font.Font(FONT_NAME, 36)
        for idx, entry in enumerate(self.high_score.scores):
            score_text = font_small.render(f"{idx + 1}. {entry['name']} - {entry['score']}", True, COLORS['white'])
            score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, 200 + idx * 50))
            self.screen.blit(score_text, score_rect)

        # Draw buttons
        for button in self.high_score_buttons:
            button.draw(self.screen)

    def check_t_spin(self):
        if self.current_piece.shape_name != 'T' or not self.last_move_was_rotation:
            return False
        
        center_x, center_y = self.current_piece.x + 1, self.current_piece.y + 1
        corners = [
            (center_x - 1, center_y - 1),
            (center_x + 1, center_y - 1),
            (center_x - 1, center_y + 1),
            (center_x + 1, center_y + 1)
        ]
        
        filled_corners = sum(1 for x, y in corners if self.is_cell_filled(x, y))
        return filled_corners >= 3

    def check_mini_t_spin(self):
        if self.current_piece.shape_name != 'T' or not self.last_move_was_rotation:
            return False
        
        center_x, center_y = self.current_piece.x + 1, self.current_piece.y + 1
        front_corners = self.get_front_corners(self.current_piece)
        
        filled_front_corners = sum(1 for x, y in front_corners if self.is_cell_filled(x, y))
        return filled_front_corners == 1

    def is_cell_filled(self, x, y):
        if x < 0 or x >= self.grid.width or y < 0 or y >= self.grid.height:
            return True
        return bool(self.grid.cells[y][x])

    def get_front_corners(self, piece):
        if piece.rotation_state == 0:  # T
            return [(piece.x, piece.y + 2), (piece.x + 2, piece.y + 2)]
        elif piece.rotation_state == 1:  # ⊢
            return [(piece.x, piece.y), (piece.x, piece.y + 2)]
        elif piece.rotation_state == 2:  # ⊥
            return [(piece.x, piece.y), (piece.x + 2, piece.y)]
        else:  # ⊣
            return [(piece.x + 2, piece.y), (piece.x + 2, piece.y + 2)]
