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
from particle import ParticleSystem
import random
from transition import Transition

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
        self.particle_system = ParticleSystem()
        self.transition = Transition()
        self.level_up_effect = None
        self.level_up_duration = 1.0  # Duration of the level-up effect in seconds
        self.start_timer = None
        self.start_timer_duration = 3  # 3 seconds
        self.countdown_timer = None

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
                rect=(SCREEN_WIDTH // 2 - 75, SCREEN_HEIGHT - 100, 150, 50),
                text="Menu",
                action=self.return_to_menu
            )
        ]

    def start_new_game(self, game=None):
        # Initialize or reset game variables
        self.grid = Grid(10, 20)
        self.piece_generator = PieceGenerator(self.grid)
        self.current_piece = None  # Set to None initially
        self.next_piece = self.piece_generator.preview_next_piece()
        self.score = Score()
        self.hud = HUD(self)
        self.is_paused = False
        self.game_over = False
        self.drop_timer = 0
        self.drop_speed = INITIAL_DROP_SPEED
        self.last_update_time = pygame.time.get_ticks()
        self.current_screen = 'transition_to_game'
        self.countdown_timer = None  # Will be set after transition

    def return_to_menu(self, game=None):
        """Return to the main menu."""
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
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.return_to_menu()
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
                            old_pos = (self.current_piece.x, self.current_piece.y)
                            old_state = self.current_piece.rotation_state
                            
                            if self.current_piece.rotate():
                                # Check if the piece actually changed position or rotation state
                                new_pos = (self.current_piece.x, self.current_piece.y)
                                new_state = self.current_piece.rotation_state
                                
                                if old_state != new_state or old_pos != new_pos:
                                    self.last_move_was_rotation = True
                                    print(f"Rotation successful - Position changed from {old_pos} to {new_pos}, State from {old_state} to {new_state}")
                                else:
                                    self.last_move_was_rotation = False
                                    print("Rotation succeeded but piece didn't change")
                            else:
                                self.last_move_was_rotation = False
                                print("Rotation failed completely")
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
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.return_to_menu()
                name = self.input_box.handle_event(event)
                if name is not None and name.strip():  # Check if name is not empty
                    self.high_score.add_score(name, self.score.score)
                    self.current_screen = 'high_scores'  # Direct assignment instead of change_screen
        elif self.current_screen == 'high_scores':
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.return_to_menu()
                for button in self.high_score_buttons:
                    button.handle_event(event, self)

    def update(self):
        if self.current_screen == 'menu':
            self.menu.update()
        elif self.current_screen == 'transition_to_game':
            self.transition.update(1/60)  # Assume 60 FPS
            if not self.transition.is_active:
                self.current_screen = 'countdown'
                self.countdown_timer = 3
        elif self.current_screen == 'countdown':
            self.countdown_timer -= 1/60  # Assume 60 FPS
            if self.countdown_timer <= 0:
                self.current_screen = 'game'
                self.current_piece = self.piece_generator.get_next_piece()
                self.next_piece = self.piece_generator.preview_next_piece()
        elif self.current_screen == 'game':
            # Always update particles
            self.particle_system.update(1/60)

            if self.start_timer is not None:
                self.start_timer -= 1/60
                if self.start_timer <= 0:
                    self.start_timer = None
                    self.current_piece = self.piece_generator.get_next_piece()
                    self.next_piece = self.piece_generator.preview_next_piece()
                return

            if self.game_over or self.is_paused:
                return

            current_time = pygame.time.get_ticks()
            delta_time = current_time - self.last_update_time
            self.drop_timer += delta_time
            self.last_update_time = current_time

            if self.current_piece:
                self.current_piece.update_position()

                # Store the current last_move_was_rotation state before any automatic movements
                was_rotation = self.last_move_was_rotation

                if self.drop_timer > self.drop_speed:
                    self.current_piece.move(0, 1)
                    self.drop_timer = 0
                    self.drop_height += 1
                    # Don't reset last_move_was_rotation here anymore

                if self.current_piece.is_locked:
                    # Use the stored rotation state for T-spin detection
                    t_spin_type = self.check_t_spin() if was_rotation else False

                    # Lock the piece first
                    self.grid.lock_piece(self.current_piece)
                    
                    # Clear lines and handle scoring
                    lines_to_clear = []
                    for y in range(self.grid.height - 1, -1, -1):
                        if all(self.grid.cells[y][x] != 0 for x in range(self.grid.width)):
                            lines_to_clear.append(y)
                    
                    lines_cleared = len(lines_to_clear)
                    if lines_cleared > 0:
                        self.grid.clear_lines()
                    
                    # Calculate score with the correct number of lines cleared
                    turn_score, notifications = self.score.update(
                        lines_cleared,
                        t_spin_type,  # This now returns "normal", "mini", or False
                        False,  # Remove this parameter since we don't need it anymore
                        self.drop_height,
                        self.soft_drop_count,
                        self.hard_drop_count
                    )
                    
                    # Add notifications to HUD
                    if notifications:
                        self.hud.add_notifications(notifications)
                    
                    # Only reset flags after all scoring is done
                    self.drop_height = 0
                    self.soft_drop_count = 0
                    self.hard_drop_count = 0
                    self.last_rotation = False
                    self.last_move_was_rotation = False  # Reset this last

                    if lines_cleared > 0:
                        self.score.update_level()
                        self.update_drop_speed()

                    if self.grid.is_board_clear():
                        tetris_clear_bonus = self.score.add_tetris_clear_bonus()

                    self.current_piece = self.piece_generator.get_next_piece()
                    self.next_piece = self.piece_generator.preview_next_piece()

                    if self.grid.is_collision(self.current_piece):
                        self.game_over = True
                        self.current_screen = 'game_over'
                        self.check_high_score()

            self.transition.update(1/60)
            if self.level_up_effect is not None:
                self.level_up_effect -= 1/60
                if self.level_up_effect <= 0:
                    self.level_up_effect = None

            self.hud.update()

    def check_high_score(self):
        """Check if the current score qualifies as a high score."""
        if self.high_score.is_high_score(self.score.score):
            # Prompt the player to enter their name
            self.input_box = InputBox(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 50, 200, 50)
            self.current_screen = 'enter_name'  # Changed from change_screen to direct assignment
        else:
            # No high score achieved, go directly to high scores
            self.current_screen = 'high_scores'  # Changed from change_screen to direct assignment

    def update_drop_speed(self):
        self.drop_speed = max(
            MIN_DROP_SPEED,
            INITIAL_DROP_SPEED - (self.score.level - 1) * SPEED_INCREMENT
        )

    def draw(self):
        if self.current_screen == 'menu':
            self.menu.draw(self.screen)
        elif self.current_screen == 'transition_to_game':
            self.screen.fill(COLORS['background'])
            self.grid.draw(self.screen)
            self.hud.draw(self.screen)
            self.particle_system.draw(self.screen)  # Add particle drawing
        elif self.current_screen == 'countdown':
            self.screen.fill(COLORS['background'])
            self.grid.draw(self.screen)
            self.hud.draw(self.screen)
            self.particle_system.draw(self.screen)  # Add particle drawing
            self.draw_countdown()
        elif self.current_screen == 'game':
            self.screen.fill(COLORS['background'])
            self.grid.draw(self.screen)
            if not self.game_over and self.current_piece:
                self.draw_ghost_piece()
                self.current_piece.draw(self.screen)
            self.hud.draw(self.screen)
            self.particle_system.draw(self.screen)  # Make sure particles are drawn
            if self.is_paused:
                self.draw_pause_overlay()
                self.back_button.draw(self.screen)
            if self.game_over:
                self.draw_game_over()
        elif self.current_screen == 'game_over':
            self.draw_game_over()
        elif self.current_screen == 'enter_name':
            self.draw_enter_name()
        elif self.current_screen == 'high_scores':
            self.draw_high_scores()

        # Always draw the transition last
        self.transition.draw(self.screen)

    def draw_ghost_piece(self):
        if self.current_piece:
            ghost_piece = self.current_piece.get_ghost_position()
            for x, y in ghost_piece.get_block_positions():
                if y >= 0:
                    rect = pygame.Rect(
                        self.grid.x_offset + x * self.grid.cell_size,
                        self.grid.y_offset + y * self.grid.cell_size,
                        self.grid.cell_size,
                        self.grid.cell_size,
                    )
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
        # First draw the game state underneath
        self.screen.fill(COLORS['background'])
        self.grid.draw(self.screen)
        self.hud.draw(self.screen)
        
        # Then draw the overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        font = pygame.font.Font(FONT_NAME, 72)
        text = font.render("Game Over", True, COLORS['white'])
        rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 80))
        self.screen.blit(text, rect)

        # Draw score
        score_font = pygame.font.Font(FONT_NAME, 48)
        score_text = score_font.render(f"Score: {self.score.score}", True, COLORS['white'])
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(score_text, score_rect)

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
        # Only check for T-spins if it's a T piece and the last move was a rotation
        if self.current_piece.shape_name != 'T' or not self.last_move_was_rotation:
            return False
        
        # Get the T piece's center coordinates
        center_x = self.current_piece.x + 1
        center_y = self.current_piece.y + 1
        
        # Check all four corners around the T piece's center
        corners = [
            (center_x - 1, center_y - 1),  # Top-left
            (center_x + 1, center_y - 1),  # Top-right
            (center_x - 1, center_y + 1),  # Bottom-left
            (center_x + 1, center_y + 1)   # Bottom-right
        ]
        
        # Count filled corners
        filled_corners = sum(1 for x, y in corners if self.is_cell_filled(x, y))
        
        # Get the two front corners based on rotation state
        front_corners = self.get_front_corners(self.current_piece)
        back_corners = self.get_back_corners(self.current_piece)
        
        filled_front_corners = sum(1 for x, y in front_corners if self.is_cell_filled(x, y))
        filled_back_corners = sum(1 for x, y in back_corners if self.is_cell_filled(x, y))
        
        # T-spin conditions:
        # Normal T-spin: 3 or more corners filled but doesn't meet mini T-spin requirements
        # Mini T-spin: 3 or more corners filled with at least 2 front corners filled
        if filled_corners >= 3:
            if filled_front_corners >= 2:
                return "mini"
            else:
                return "normal"
        
        return False

    def get_back_corners(self, piece):
        # Get the two back corners based on rotation state
        if piece.rotation_state == 0:  # T pointing up
            return [(piece.x, piece.y), (piece.x + 2, piece.y)]  # Top corners
        elif piece.rotation_state == 1:  # T pointing right
            return [(piece.x + 2, piece.y), (piece.x + 2, piece.y + 2)]  # Right corners
        elif piece.rotation_state == 2:  # T pointing down
            return [(piece.x, piece.y + 2), (piece.x + 2, piece.y + 2)]  # Bottom corners
        else:  # T pointing left (3)
            return [(piece.x, piece.y), (piece.x, piece.y + 2)]  # Left corners

    def is_cell_filled(self, x, y):
        # Consider out-of-bounds cells as filled
        if x < 0 or x >= self.grid.width or y < 0 or y >= self.grid.height:
            return True
        # Check if the cell contains a block
        return bool(self.grid.cells[y][x])

    def get_front_corners(self, piece):
        # Get the two front corners based on rotation state
        if piece.rotation_state == 0:  # T pointing up
            return [(piece.x, piece.y + 2), (piece.x + 2, piece.y + 2)]  # Bottom corners
        elif piece.rotation_state == 1:  # T pointing right
            return [(piece.x, piece.y), (piece.x, piece.y + 2)]  # Left corners
        elif piece.rotation_state == 2:  # T pointing down
            return [(piece.x, piece.y), (piece.x + 2, piece.y)]  # Top corners
        else:  # T pointing left (3)
            return [(piece.x + 2, piece.y), (piece.x + 2, piece.y + 2)]  # Right corners

    def create_line_clear_particles(self, lines_cleared):
        for y in self.grid.lines_to_clear:
            for x in range(self.grid.width):
                if self.grid.cells[y][x] != 0:
                    particle_x = self.grid.x_offset + x * self.grid.cell_size + self.grid.cell_size // 2
                    particle_y = self.grid.y_offset + y * self.grid.cell_size + self.grid.cell_size // 2
                    color = self.grid.cells[y][x]
                    for _ in range(5):  # Create 5 particles per cell
                        self.particle_system.add_particle(particle_x, particle_y, color)

    def change_screen(self, new_screen):
        self.transition.start()
        self.current_screen = new_screen

    def update_level(self):
        old_level = self.score.level
        self.score.update_level()
        if self.score.level > old_level:
            self.level_up_effect = self.level_up_duration

    def draw_level_up_effect(self):
        alpha = int(255 * (self.level_up_effect / self.level_up_duration))
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((255, 255, 255, alpha))
        self.screen.blit(overlay, (0, 0))
        
        font = pygame.font.Font(None, 72)
        text = font.render(f"Level {self.score.level}", True, COLORS['white'])
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(text, text_rect)

    def draw_start_timer(self):
        font = pygame.font.Font(FONT_NAME, 72)
        text = font.render(str(max(1, int(self.start_timer + 1))), True, COLORS['white'])
        rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(text, rect)

    def draw_countdown(self):
        font = pygame.font.Font(FONT_NAME, 72)
        text = font.render(str(max(1, int(self.countdown_timer + 1))), True, COLORS['white'])
        rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(text, rect)

