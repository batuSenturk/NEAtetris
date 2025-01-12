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
    INITIAL_DROP_SPEED, MIN_DROP_SPEED, SPEED_INCREMENT, GHOST_ALPHA,
    LOCK_DELAY, MAX_LOCK_MOVES
)
from tetromino import Tetromino
from particle import ParticleSystem
import random
from transition import Transition
from tetris_ai import TetrisAI
from ai_score import AIScore

# Add these new constants
INITIAL_DELAY = 170  # Milliseconds before key repeat starts
REPEAT_DELAY = 50    # Milliseconds between repeated movements
AI_MOVE_DELAY = 0  # Milliseconds between AI moves

class Game:
    def __init__(self, screen):
        self.screen = screen
        self.current_screen = 'menu'  # Possible screens: 'menu', 'game', 'pause', 'game_over', 'enter_name', 'high_scores'
        self.menu = Menu(self)
        self.high_score = HighScore()
        self.mode = 'Classic Mode'  # Default game mode
        self.grid = None
        self.piece_generator = None
        self.ai_piece_generator = None  # Separate piece generator for AI
        self.current_piece = None
        self.next_pieces = None
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
        self.held_piece = None
        self.can_hold = True  # Can only hold once per piece
        self.ai = TetrisAI(self)
        self.ai_debug_timer = 0
        self.ai_debug_interval = 1000  # Print debug info every 1000ms
        self.ai_grid = None
        self.ai_score = None
        self.ai_current_piece = None
        self.ai_next_pieces = None
        self.ai_held_piece = None
        self.ai_move_timer = 0  # Timer for AI move delay
        self.ai_move_delay = AI_MOVE_DELAY  # Use the configurable AI move delay
        self.ai_game_timer = 60  # 60 seconds for AI game mode
        self.ai_game_started = False
        self.keys_per_piece = []  # List to store number of keys for each piece
        self.current_piece_keys = 0  # Counter for current piece
        self.game_start_time = None  # Track game start time
        self.total_pieces = 0  # Track total pieces placed
        self.game_end_time = None  # Track game end time
        # Initialize AI score tracker
        self.ai_score_tracker = AIScore()

        self.back_to_menu_button = Button(
            rect=(SCREEN_WIDTH // 2 - 75, SCREEN_HEIGHT - 100, 150, 50),
            text="Menu",
            action=self.return_to_menu
        )

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

        # Add these new variables to the existing __init__ method
        self.left_pressed = False
        self.right_pressed = False
        self.down_pressed = False
        self.left_press_time = 0
        self.right_press_time = 0
        self.down_press_time = 0
        self.last_movement_time = 0

    def start_new_game(self, game=None):
        if self.mode == "AI":
            # Player grid and pieces on the left
            self.grid = Grid(10, 20, 'left')
            self.piece_generator = PieceGenerator(self.grid)
            self.current_piece = None
            self.next_pieces = self.piece_generator.preview_next_pieces()
            
            # AI grid and pieces on the right
            self.ai_grid = Grid(10, 20, 'right')
            self.ai_piece_generator = PieceGenerator(self.ai_grid)  # Separate generator for AI
            self.ai_current_piece = None
            self.ai_next_pieces = self.ai_piece_generator.preview_next_pieces()
            self.ai_score = Score()
            self.ai_held_piece = None
            
            # Reset statistics for new game
            self.keys_per_piece = []
            self.current_piece_keys = 0
            self.game_start_time = pygame.time.get_ticks() / 1000  # Convert to seconds
            self.total_pieces = 0
            self.ai_game_timer = 60  # Reset timer to 60 seconds
        else:
            # Single centered grid for other modes
            self.grid = Grid(10, 20, 'center')
            self.piece_generator = PieceGenerator(self.grid)
            self.current_piece = None
            self.next_pieces = self.piece_generator.preview_next_pieces()
            # Initialize statistics for all modes
            self.game_start_time = pygame.time.get_ticks() / 1000  # Convert to seconds
            self.total_pieces = 0
        
        self.score = Score()
        self.hud = HUD(self)
        self.is_paused = False
        self.game_over = False
        self.drop_timer = 0
        self.drop_speed = INITIAL_DROP_SPEED
        self.last_update_time = pygame.time.get_ticks()
        self.current_screen = 'transition_to_game'
        self.countdown_timer = None  # Will be set after transition
        self.held_piece = None
        self.can_hold = True
        
        # Reset AI's first piece flag
        self.ai.first_held_piece = True
        
        # Clear all particles
        self.particle_system = ParticleSystem()

    def return_to_menu(self, game=None):
        """Return to the main menu."""
        self.current_screen = 'menu'
        self.is_paused = False
        self.game_over = False

    def handle_events(self):
        current_time = pygame.time.get_ticks()
        
        if self.current_screen == 'menu':
            events = pygame.event.get()
            self.menu.handle_events(events)
        elif self.current_screen == 'ai_score':
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                self.back_to_menu_button.handle_event(event, self)
        elif self.current_screen == 'game':
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                
                # Handle pause button regardless of pause state
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.return_to_menu()
                    elif event.key == pygame.K_p:
                        if self.current_screen == 'game':
                            self.is_paused = not self.is_paused
                    # Track key presses for statistics
                    if self.mode == "AI":
                        self.current_piece_keys += 1
                
                # Handle back button and skip other inputs if paused
                if self.is_paused:
                    self.back_button.handle_event(event, self)  
                    continue
                    
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.left_pressed = True
                        self.left_press_time = current_time
                        if self.current_piece and not self.is_paused and not self.game_over:
                            if self.current_piece.move(-1, 0):
                                self.last_move_was_rotation = False
                                if self.current_piece.is_touching_ground():
                                    self.current_piece.reset_lock_delay()
                    elif event.key == pygame.K_RIGHT:
                        self.right_pressed = True
                        self.right_press_time = current_time
                        if self.current_piece and not self.is_paused and not self.game_over:
                            if self.current_piece.move(1, 0):
                                self.last_move_was_rotation = False
                                if self.current_piece.is_touching_ground():
                                    self.current_piece.reset_lock_delay()
                    elif event.key == pygame.K_DOWN:
                        self.down_pressed = True
                        self.down_press_time = current_time
                        if self.current_piece and not self.is_paused and not self.game_over:
                            if self.current_piece.move(0, 1):
                                self.soft_drop_count += 1
                                self.last_move_was_rotation = False
                                if self.current_piece.is_touching_ground():
                                    self.current_piece.reset_lock_delay()
                    elif event.key == pygame.K_UP:
                        old_pos = (self.current_piece.x, self.current_piece.y)
                        old_state = self.current_piece.rotation_state
                        
                        if self.current_piece.rotate():
                            new_pos = (self.current_piece.x, self.current_piece.y)
                            new_state = self.current_piece.rotation_state
                            
                            if old_state != new_state or old_pos != new_pos:
                                self.last_move_was_rotation = True
                                if self.current_piece.is_touching_ground():
                                    self.current_piece.reset_lock_delay()
                            else:
                                self.last_move_was_rotation = False
                        else:
                            self.last_move_was_rotation = False
                    elif event.key == pygame.K_SPACE:
                        self.hard_drop_count = self.current_piece.hard_drop()
                        self.last_move_was_rotation = False
                    elif event.key == pygame.K_c:  # Hold piece
                        if self.can_hold:
                            self.hold_piece()
                            self.can_hold = False

                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT:
                        self.left_pressed = False
                    elif event.key == pygame.K_RIGHT:
                        self.right_pressed = False
                    elif event.key == pygame.K_DOWN:
                        self.down_pressed = False

            # Handle continuous movement
            if not self.is_paused and not self.game_over and self.current_piece:
                if self.left_pressed and current_time - self.left_press_time >= INITIAL_DELAY:
                    if current_time - self.last_movement_time >= REPEAT_DELAY:
                        if self.current_piece.move(-1, 0):
                            self.last_move_was_rotation = False
                            if self.current_piece.is_touching_ground():
                                self.current_piece.reset_lock_delay()
                        self.last_movement_time = current_time

                if self.right_pressed and current_time - self.right_press_time >= INITIAL_DELAY:
                    if current_time - self.last_movement_time >= REPEAT_DELAY:
                        if self.current_piece.move(1, 0):
                            self.last_move_was_rotation = False
                            if self.current_piece.is_touching_ground():
                                self.current_piece.reset_lock_delay()
                        self.last_movement_time = current_time

                if self.down_pressed and current_time - self.down_press_time >= INITIAL_DELAY:
                    if current_time - self.last_movement_time >= REPEAT_DELAY:
                        if self.current_piece.move(0, 1):
                            self.soft_drop_count += 1
                            self.last_move_was_rotation = False
                            if self.current_piece.is_touching_ground():
                                self.current_piece.reset_lock_delay()
                        self.last_movement_time = current_time

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
                self.next_pieces = self.piece_generator.preview_next_pieces()
                self.can_hold = True
                if self.mode == "AI":
                    self.ai_game_started = True
                    self.game_start_time = pygame.time.get_ticks() / 1000  # Initialize game start time
        elif self.current_screen == 'game':
            # Always update particles
            self.particle_system.update(1/60)

            if self.start_timer is not None:
                self.start_timer -= 1/60
                if self.start_timer <= 0:
                    self.start_timer = None
                    self.current_piece = self.piece_generator.get_next_piece()
                    self.next_pieces = self.piece_generator.preview_next_pieces()
                    self.can_hold = True
                return

            if self.is_paused:
                return

            if self.mode == "AI":
                # Update AI game timer
                if self.ai_game_started:
                    self.ai_game_timer -= 1/60
                    if self.ai_game_timer <= 0:
                        self.game_over = True
                        self.handle_game_over()  # Call handle_game_over when timer ends
                        return

            if self.game_over:
                return

            current_time = pygame.time.get_ticks()
            delta_time = current_time - self.last_update_time
            self.drop_timer += delta_time
            self.last_update_time = current_time

            if self.current_piece:
                self.current_piece.update_position()

                # AI Mode handling
                if self.mode == "AI" and not self.is_paused:
                    current_time = pygame.time.get_ticks()
                    
                    if self.ai_current_piece is None:
                        self.ai_current_piece = self.ai_piece_generator.get_next_piece()
                        self.ai_current_piece.grid = self.ai_grid
                        self.ai_next_pieces = self.ai_piece_generator.preview_next_pieces()
                        self.ai_move_timer = current_time  # Reset timer for new piece
                    
                    # Only execute AI moves after delay
                    if current_time - self.ai_move_timer >= self.ai_move_delay:
                        self.ai_move_timer = current_time  # Reset timer
                        
                        # Get and execute AI moves
                        best_move = self.ai.get_best_move(self.ai_grid, self.ai_current_piece)
                        if best_move:
                            # Handle piece holding for AI
                            if best_move['requires_hold']:
                                if self.ai_held_piece is None:
                                    self.ai_held_piece = Tetromino(self.ai_current_piece.shape_name, self.ai_grid)
                                    self.ai_current_piece = self.ai_piece_generator.get_next_piece()
                                    self.ai_next_pieces = self.ai_piece_generator.preview_next_pieces()
                                else:
                                    temp_shape_name = self.ai_current_piece.shape_name
                                    self.ai_current_piece = Tetromino(self.ai_held_piece.shape_name, self.ai_grid)
                                    self.ai_current_piece.reset_position()
                                    self.ai_held_piece = Tetromino(temp_shape_name, self.ai_grid)
                                return

                            # Execute one move at a time with proper validation and visual updates
                            moved = False
                            if self.ai_current_piece.rotation_state != best_move['rotation']:
                                # Rotate once
                                moved = self.ai_current_piece.rotate()
                                if moved:
                                    self.ai_current_piece.update_position()  # Update visual position
                            elif self.ai_current_piece.x < best_move['x']:
                                # Move right once
                                moved = self.ai_current_piece.move(1, 0)
                                if moved:
                                    self.ai_current_piece.update_position()  # Update visual position
                            elif self.ai_current_piece.x > best_move['x']:
                                # Move left once
                                moved = self.ai_current_piece.move(-1, 0)
                                if moved:
                                    self.ai_current_piece.update_position()  # Update visual position
                            else:
                                # Position reached, perform hard drop
                                drop_distance = self.ai_current_piece.hard_drop()
                                # Update visual position before locking
                                self.ai_current_piece.target_y = self.ai_current_piece.y * self.ai_grid.cell_size + self.ai_grid.y_offset
                                self.ai_current_piece.update_position()
                                self.ai_grid.lock_piece(self.ai_current_piece)
                                
                                # Add hard drop score before line clearing
                                turn_score, notifications = self.ai_score.update(
                                    0,  # no lines cleared yet
                                    False,  # no T-spin
                                    False,  # no back-to-back
                                    drop_distance,
                                    0,  # no soft drop
                                    drop_distance * 2  # hard drop bonus
                                )
                                
                                # Handle line clearing and scoring
                                lines_to_clear = []
                                for y in range(self.ai_grid.height - 1, -1, -1):
                                    if all(self.ai_grid.cells[y][x] != 0 for x in range(self.ai_grid.width)):
                                        lines_to_clear.append(y)
                                
                                lines_cleared = len(lines_to_clear)
                                if lines_cleared > 0:
                                    # Create particles before clearing the lines
                                    for y in lines_to_clear:
                                        for x in range(self.ai_grid.width):
                                            if self.ai_grid.cells[y][x] != 0:
                                                particle_x = self.ai_grid.x_offset + x * self.ai_grid.cell_size + self.ai_grid.cell_size // 2
                                                particle_y = self.ai_grid.y_offset + y * self.ai_grid.cell_size + self.ai_grid.cell_size // 2
                                                color = self.ai_grid.cells[y][x]
                                                for _ in range(5):
                                                    self.particle_system.add_particle(particle_x, particle_y, color)
                                    
                                    # Clear the lines
                                    self.ai_grid.clear_lines()
                                    
                                    # Update AI score and get notifications
                                    turn_score, notifications = self.ai_score.update(
                                        lines_cleared,
                                        False,  # No T-spin for AI
                                        False,  # No back-to-back for AI
                                        drop_distance,
                                        0,  # No soft drop for AI
                                        drop_distance * 2  # Hard drop bonus
                                    )
                                    
                                    # Add notifications to HUD
                                    if notifications:
                                        self.hud.add_notifications(notifications, is_ai=True)
                                    
                                    # Check for level up
                                    self.ai_score.update_level()
                                    
                                    # Check for board clear bonus
                                    if self.ai_grid.is_board_clear():
                                        tetris_clear_bonus = self.ai_score.add_tetris_clear_bonus()
                                
                                # Get next piece
                                self.ai_current_piece = self.ai_piece_generator.get_next_piece()
                                self.ai_current_piece.grid = self.ai_grid
                                self.ai_next_pieces = self.ai_piece_generator.preview_next_pieces()

                # Store the current last_move_was_rotation state before any automatic movements
                was_rotation = self.last_move_was_rotation

                if self.drop_timer > self.drop_speed:
                    self.current_piece.move(0, 1)
                    self.drop_timer = 0
                    self.drop_height += 1

                # Handle lock delay
                if self.current_piece.lock_delay_active:
                    self.current_piece.lock_delay_timer += delta_time
                    if (self.current_piece.lock_delay_timer >= LOCK_DELAY or 
                        self.current_piece.lock_moves_count >= MAX_LOCK_MOVES):
                        # Only lock if actually touching ground
                        if self.current_piece.is_touching_ground():
                            self.current_piece.is_locked = True
                        else:
                            # Reset lock delay if not touching ground
                            self.current_piece.lock_delay_active = False
                            self.current_piece.lock_moves_count = 0
                            self.current_piece.lock_delay_timer = 0

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
                        # Create particles before clearing the lines
                        self.create_line_clear_particles(lines_to_clear)  # Pass the lines to clear
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
                        self.hud.add_notifications(notifications, is_ai=False)
                    
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
                    self.next_pieces = self.piece_generator.preview_next_pieces()
                    self.can_hold = True  # Reset hold ability for new piece

                    if self.mode == "AI":
                        self.on_piece_placed()

                    if self.grid.is_collision(self.current_piece):
                        self.game_over = True
                        self.handle_game_over()
                        self.check_high_score()

            self.transition.update(1/60)
            if self.level_up_effect is not None:
                self.level_up_effect -= 1/60
                if self.level_up_effect <= 0:
                    self.level_up_effect = None

            self.hud.update()

    def handle_game_over(self):
        # Set game end time when game ends
        self.game_end_time = pygame.time.get_ticks() / 1000
        
        if self.mode == "AI":
            stats = self.calculate_statistics()

            if stats:
                self.ai_score_tracker.add_score(stats)
            self.current_screen = 'ai_score'  # Change to ai_score screen instead of menu
            self.game_over = False  # Reset game over state
        elif self.mode == "Classic Mode":
            if self.score.score > 0:
                self.current_screen = 'enter_name'
                self.input_box = InputBox(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2, 200, 32)
        elif self.mode == "Sprint Mode":
            if self.lines_cleared >= 40:
                self.current_screen = 'enter_name'
                self.input_box = InputBox(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2, 200, 32)
        elif self.mode == "Ultra Mode":
            if self.score.score > 0:
                self.current_screen = 'enter_name'
                self.input_box = InputBox(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2, 200, 32)

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
            # Draw AI grid in AI mode during transition
            if self.mode == "AI":
                self.ai_grid.draw(self.screen)
            self.hud.draw(self.screen)
            self.particle_system.draw(self.screen)
        elif self.current_screen == 'countdown':
            self.screen.fill(COLORS['background'])
            self.grid.draw(self.screen)
            # Draw AI grid in AI mode during countdown
            if self.mode == "AI":
                self.ai_grid.draw(self.screen)
            self.hud.draw(self.screen)
            self.particle_system.draw(self.screen)
            self.draw_countdown()
        elif self.current_screen == 'game':
            self.screen.fill(COLORS['background'])
            
            # Draw main grid
            self.grid.draw(self.screen)
            
            # Draw AI grid in AI mode
            if self.mode == "AI":
                self.ai_grid.draw(self.screen)
                if self.ai_current_piece:
                    self.draw_ghost_piece(self.ai_current_piece, is_ai=True)  # Draw AI ghost piece
                    self.ai_current_piece.draw(self.screen)
            
            if not self.game_over and self.current_piece:
                self.draw_ghost_piece()  # Draw player ghost piece
                self.current_piece.draw(self.screen)
            
            self.hud.draw(self.screen)
            self.particle_system.draw(self.screen)
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
        elif self.current_screen == 'ai_score':
            self.screen.fill(COLORS['background'])
            font = pygame.font.Font(FONT_NAME, 48)
            text = font.render("AI Game Results", True, COLORS['white'])
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, 100))
            self.screen.blit(text, text_rect)

            # Display scores and difference
            font_small = pygame.font.Font(FONT_NAME, 36)
            score_diff = self.score.score - self.ai_score.score
            color = COLORS['green'] if score_diff >= 0 else COLORS['red']
            
            player_text = font_small.render(f"Your Score: {self.score.score}", True, COLORS['white'])
            ai_text = font_small.render(f"AI Score: {self.ai_score.score}", True, COLORS['white'])
            diff_text = font_small.render(f"Score Difference: {abs(score_diff)}", True, color)
            delay_text = font_small.render(f"AI Move Delay: {self.ai_move_delay}ms", True, COLORS['white'])
            kpp_text = font_small.render(f"Keys Per Piece: {round(sum(self.keys_per_piece) / len(self.keys_per_piece) if self.keys_per_piece else 0, 2)}", True, COLORS['white'])
            pps_text = font_small.render(f"Pieces Per Second: {round(self.total_pieces / (self.game_end_time - self.game_start_time), 2)}", True, COLORS['white'])
            
            # Get placement from ai_scores.json
            from ai_score import AIScore
            ai_score_handler = AIScore()
            placement = ai_score_handler.get_placement(score_diff, self.ai_move_delay)
            placement_text = font_small.render(f"Your Placement: {placement}", True, COLORS['white'])

            # Position all text elements
            player_rect = player_text.get_rect(center=(SCREEN_WIDTH // 2, 180))
            ai_rect = ai_text.get_rect(center=(SCREEN_WIDTH // 2, 230))
            diff_rect = diff_text.get_rect(center=(SCREEN_WIDTH // 2, 280))
            delay_rect = delay_text.get_rect(center=(SCREEN_WIDTH // 2, 330))
            kpp_rect = kpp_text.get_rect(center=(SCREEN_WIDTH // 2, 380))
            pps_rect = pps_text.get_rect(center=(SCREEN_WIDTH // 2, 430))
            placement_rect = placement_text.get_rect(center=(SCREEN_WIDTH // 2, 480))

            # Draw all text elements
            self.screen.blit(player_text, player_rect)
            self.screen.blit(ai_text, ai_rect)
            self.screen.blit(diff_text, diff_rect)
            self.screen.blit(delay_text, delay_rect)
            self.screen.blit(kpp_text, kpp_rect)
            self.screen.blit(pps_text, pps_rect)
            self.screen.blit(placement_text, placement_rect)

            # Draw back to menu button
            self.back_to_menu_button.draw(self.screen)

        # Always draw the transition last
        self.transition.draw(self.screen)

    def draw_ghost_piece(self, piece=None, is_ai=False):
        """Draw ghost piece for either player or AI"""
        piece = piece or self.current_piece
        if not piece:
            return
        
        # Get ghost piece using get_ghost_position which properly handles rotations
        ghost_piece = piece.get_ghost_position()
        
        # Draw ghost piece with transparency
        for x, y in ghost_piece.get_block_positions():
            rect = pygame.Rect(
                piece.grid.x_offset + x * piece.grid.cell_size,
                piece.grid.y_offset + y * piece.grid.cell_size,
                piece.grid.cell_size,
                piece.grid.cell_size,
            )
            # Create a transparent surface for the ghost piece
            ghost_surface = pygame.Surface((piece.grid.cell_size, piece.grid.cell_size), pygame.SRCALPHA)
            r, g, b = piece.color
            ghost_surface.fill((r, g, b, GHOST_ALPHA))
            self.screen.blit(ghost_surface, rect)
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

    def create_line_clear_particles(self, lines_to_clear):
        """Create particles for each block in the cleared lines"""
        for y in lines_to_clear:
            for x in range(self.grid.width):
                if self.grid.cells[y][x] != 0:  # If there's a block at this position
                    # Calculate the actual pixel position
                    particle_x = self.grid.x_offset + x * self.grid.cell_size + self.grid.cell_size // 2
                    particle_y = self.grid.y_offset + y * self.grid.cell_size + self.grid.cell_size // 2
                    color = self.grid.cells[y][x]  # Get the color of the block
                    
                    # Create multiple particles per block
                    for _ in range(5):  # Create 5 particles per block
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

    def hold_piece(self):
        """Handle the piece hold mechanic"""
        if self.held_piece is None:
            # First hold
            self.held_piece = Tetromino(self.current_piece.shape_name, self.grid)
            self.current_piece = self.piece_generator.get_next_piece()
            self.next_pieces = self.piece_generator.preview_next_pieces()
        else:
            # Swap current and held pieces
            temp_shape_name = self.current_piece.shape_name
            self.current_piece = Tetromino(self.held_piece.shape_name, self.grid)
            self.current_piece.reset_position()  # Reset position of the swapped piece
            self.held_piece = Tetromino(temp_shape_name, self.grid)

    def on_piece_placed(self):
        # Track total pieces for all modes
        self.total_pieces += 1
        
        if self.mode == "AI":
            self.keys_per_piece.append(self.current_piece_keys)
            self.current_piece_keys = 0

    def calculate_statistics(self):
        if not self.game_start_time:
            return None
            
        self.game_end_time = pygame.time.get_ticks() / 1000
        game_duration = self.game_end_time - self.game_start_time
        avg_keys_per_piece = sum(self.keys_per_piece) / len(self.keys_per_piece) if self.keys_per_piece else 0
        pieces_per_second = self.total_pieces / game_duration if game_duration > 0 else 0
        
        return {
            "score": self.score.score,
            "ai_score": self.ai_score.score if hasattr(self, 'ai_score') else 0,
            "score_difference": self.score.score - self.ai_score.score if hasattr(self, 'ai_score') else 0,
            "keys_per_piece": round(avg_keys_per_piece, 2),
            "pieces_per_second": round(pieces_per_second, 2),
            "delay": self.ai_move_delay,
            "total_pieces": self.total_pieces,
            "game_duration": round(game_duration, 2)
        }
