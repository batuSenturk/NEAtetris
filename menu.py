# menu.py

import pygame
from button import Button
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, MENU_BACKGROUND_COLOR, FONT_NAME, FONT_SIZE, BUTTON_WIDTH, BUTTON_HEIGHT
from input_box import InputBox

class Menu:
    def __init__(self, game):
        self.game = game
        self.font = pygame.font.Font(FONT_NAME, 36)
        self.title_font = pygame.font.Font(FONT_NAME, 72)
        self.state = 'main'  # Possible states: 'main', 'rules', 'high_scores', 'ai', 'modes', 'sprint_rules', 'ultra_rules'
        self.selected_mode = None

        # Define main menu buttons
        self.buttons = [
            Button(
                rect=(
                    SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2,
                    SCREEN_HEIGHT // 2 - 120,
                    BUTTON_WIDTH,
                    BUTTON_HEIGHT
                ),
                text="Classic",
                action=lambda g: self.select_mode("Classic Mode")
            ),
            Button(
                rect=(
                    SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2,
                    SCREEN_HEIGHT // 2 - 50,
                    BUTTON_WIDTH,
                    BUTTON_HEIGHT
                ),
                text="Modes",
                action=self.show_modes_screen
            ),
            Button(
                rect=(
                    SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2,
                    SCREEN_HEIGHT // 2 + 30,
                    BUTTON_WIDTH,
                    BUTTON_HEIGHT
                ),
                text="AI",
                action=self.show_ai_screen
            )
        ]

        # AI screen buttons
        self.ai_button = Button(
            rect=(
                SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2,
                SCREEN_HEIGHT // 2 + 100,
                BUTTON_WIDTH,
                BUTTON_HEIGHT
            ),
            text="Play",
            action=self.start_ai_game
        )

        # Play button in 'rules' state
        self.play_button = Button(
            rect=(
                SCREEN_WIDTH // 2 - 75,
                SCREEN_HEIGHT - 100,
                150,
                50
            ),
            text="Play",
            action=self.start_game
        )

        # Back button for all secondary screens
        self.back_button = Button(
            rect=(20, 20, 100, 40),
            text="Back",
            action=self.go_back
        )

        # High Scores button in main menu
        self.high_scores_button = Button(
            rect=(
                SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2,
                SCREEN_HEIGHT // 2 + 110,
                BUTTON_WIDTH,
                BUTTON_HEIGHT
            ),
            text="High Scores",
            action=self.show_high_scores
        )

        # Input box for AI move delay
        self.ai_delay_input = InputBox(
            SCREEN_WIDTH // 2 - 100,  # x position
            420,  # y position
            200,  # width
            40,   # height
            text=''  # default empty
        )

        # Add buttons for Sprint and Ultra modes
        self.sprint_button = Button(
            rect=(
                SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2,
                SCREEN_HEIGHT // 2 - 50,
                BUTTON_WIDTH,
                BUTTON_HEIGHT
            ),
            text="Sprint",
            action=lambda g: self.show_mode_rules("Sprint Mode")
        )

        self.ultra_button = Button(
            rect=(
                SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2,
                SCREEN_HEIGHT // 2 + 30,
                BUTTON_WIDTH,
                BUTTON_HEIGHT
            ),
            text="Ultra",
            action=lambda g: self.show_mode_rules("Ultra Mode")
        )

        # Start button for mode rules screens
        self.start_button = Button(
            rect=(
                SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2,
                SCREEN_HEIGHT - 150,
                BUTTON_WIDTH,
                BUTTON_HEIGHT
            ),
            text="Start",
            action=self.start_game
        )

    def select_mode(self, mode):
        self.selected_mode = mode
        self.state = 'rules'

    def start_game(self, game):
        # Start the game with the selected mode
        game.mode = self.selected_mode
        game.transition.start()
        game.current_screen = 'transition_to_game'
        game.start_new_game()

    def go_back(self, game=None):
        self.state = 'main'

    def show_high_scores(self, game=None):
        self.game.current_screen = 'high_scores'

    def show_ai_screen(self, game=None):
        self.state = 'ai'

    def show_modes_screen(self, game=None):
        self.state = 'modes'

    def start_ai_game(self, game):
        """Start AI game mode"""
        # Get the delay value from input box, default to 0 if empty or invalid
        try:
            delay = int(self.ai_delay_input.text) if self.ai_delay_input.text else 0
        except ValueError:
            delay = 0
            
        game.ai_move_delay = delay
        game.mode = "AI"
        game.transition.start()
        game.current_screen = 'transition_to_game'
        game.start_new_game()

    def show_mode_rules(self, mode):
        self.selected_mode = mode
        if mode == "Sprint Mode":
            self.state = 'sprint_rules'
        elif mode == "Ultra Mode":
            self.state = 'ultra_rules'

    def handle_events(self, events):
        """Handle menu events"""
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            
            # Handle input box events
            if self.state == 'ai':
                delay_input = self.ai_delay_input.handle_event(event)
                if delay_input is not None:
                    try:
                        self.game.ai_move_delay = int(delay_input)
                    except ValueError:
                        self.game.ai_move_delay = 0

            # Handle events based on the current state
            if self.state == 'main':
                for button in self.buttons:
                    button.handle_event(event, self.game)
                self.high_scores_button.handle_event(event, self.game)
            elif self.state == 'rules':
                self.play_button.handle_event(event, self.game)
                self.back_button.handle_event(event, self.game)
            elif self.state == 'ai':
                self.ai_button.handle_event(event, self.game)
                self.back_button.handle_event(event, self.game)
                self.ai_button.handle_event(event, self.game)
            elif self.state == 'modes':
                self.back_button.handle_event(event, self.game)
                self.sprint_button.handle_event(event, self.game)
                self.ultra_button.handle_event(event, self.game)
            elif self.state == 'sprint_rules':
                self.start_button.handle_event(event, self.game)
                self.back_button.handle_event(event, self.game)
            elif self.state == 'ultra_rules':
                self.start_button.handle_event(event, self.game)
                self.back_button.handle_event(event, self.game)
            elif self.state == 'high_scores':
                self.back_button.handle_event(event, self.game)

    def draw(self, screen):
        screen.fill(MENU_BACKGROUND_COLOR)
        
        if self.state == 'main':
            self.draw_main_menu(screen)
        elif self.state == 'rules':
            self.draw_rules(screen)
            self.play_button.draw(screen)
            self.back_button.draw(screen)
        elif self.state == 'ai':
            self.draw_ai_screen(screen)
            self.ai_button.draw(screen)
            self.back_button.draw(screen)
            self.ai_delay_input.draw(screen)
        elif self.state == 'modes':
            self.draw_modes_screen(screen)
            self.back_button.draw(screen)
            self.sprint_button.draw(screen)
            self.ultra_button.draw(screen)
        elif self.state == 'sprint_rules':
            self.draw_sprint_rules(screen)
            self.start_button.draw(screen)
            self.back_button.draw(screen)
        elif self.state == 'ultra_rules':
            self.draw_ultra_rules(screen)
            self.start_button.draw(screen)
            self.back_button.draw(screen)
        elif self.state == 'high_scores':
            self.draw_high_scores(screen)

    def draw_modes_screen(self, screen):
        # Draw a blank screen with a back button
        title = self.title_font.render("Modes", True, (255, 255, 255))
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 150))
        screen.blit(title, title_rect)

    def draw_ai_screen(self, screen):

        # Draw description
        description_lines = [
            "AI Mode:",
            "Play against an AI in Tetris!",
            "",
            "You can adjust the difficulty level",
            "using the input box below.",
            "",
            "Enter the wanted time delay between",
            "AI moves in milliseconds.",
            "",
            "Press 'Play' to begin!"
        ]

        y_offset = 50
        for line in description_lines:
            text = self.font.render(line, True, (255, 255, 255))
            rect = text.get_rect(center=(SCREEN_WIDTH // 2, y_offset))
            screen.blit(text, rect)
            y_offset += 30

    def draw_sprint_rules(self, screen):
        rules_text = [
            "Sprint Mode Rules:",
            "",
            "Clear 40 lines as quickly as possible!",
            "",
            "Controls:",
            "Left Arrow - Move Left",
            "Right Arrow - Move Right",
            "Down Arrow - Soft Drop",
            "Up Arrow - Rotate Right",
            "Z - Rotate Left",
            "Space - Hard Drop",
            "C - Hold Piece",
            "",
            "The timer starts when you make",
            "your first move.",
            "",
            "Good luck!"
        ]
        y_offset = 50
        for line in rules_text:
            text_surf = self.font.render(line, True, (255, 255, 255))
            text_rect = text_surf.get_rect(center=(SCREEN_WIDTH // 2, y_offset))
            screen.blit(text_surf, text_rect)
            y_offset += 35

    def draw_ultra_rules(self, screen):
        rules_text = [
            "Ultra Mode Rules:",
            "",
            "Score as many points as possible",
            "in 2 minutes!",
            "",
            "Controls:",
            "Left Arrow - Move Left",
            "Right Arrow - Move Right",
            "Down Arrow - Soft Drop",
            "Up Arrow - Rotate Right",
            "Z - Rotate Left",
            "Space - Hard Drop",
            "C - Hold Piece",
            "",
            "The timer starts when you make",
            "your first move.",
            "",
            "Good luck!"
        ]
        y_offset = 50
        for line in rules_text:
            text_surf = self.font.render(line, True, (255, 255, 255))
            text_rect = text_surf.get_rect(center=(SCREEN_WIDTH // 2, y_offset))
            screen.blit(text_surf, text_rect)
            y_offset += 35

    def draw_main_menu(self, screen):
        title_text = self.title_font.render("Tetris", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 150))
        screen.blit(title_text, title_rect)
        for button in self.buttons:
            button.draw(screen)
        self.high_scores_button.draw(screen)

    def draw_rules(self, screen):

        rules_text = [
            f"{self.selected_mode} Rules:",
            "Controls:",
            "Left Arrow - Move Left",
            "Right Arrow - Move Right",
            "Up Arrow - Rotate",
            "Down Arrow - Soft Drop",
            "Space - Hard Drop",
            "C - Hold Piece",
            "P - Pause",
            "",
            "Hold Feature:",
            "Press C to store current piece",
            "or swap with held piece",
            "(Can only hold once per piece)",
            "",
            "Objective:",
            "Clear lines by filling them completely.",
            "The game ends when the pieces reach the top."
        ]
        y_offset = 50
        for line in rules_text:
            text_surf = self.font.render(line, True, (255, 255, 255))
            text_rect = text_surf.get_rect(center=(SCREEN_WIDTH // 2, y_offset))
            screen.blit(text_surf, text_rect)
            y_offset += 35

    def draw_high_scores(self, screen):
        # Display the high scores
        high_scores = self.game.high_score.scores
        font = pygame.font.Font(FONT_NAME, 48)
        title = font.render("High Scores", True, (255, 255, 255))
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 100))
        screen.blit(title, title_rect)

        # Display high scores
        font_small = pygame.font.Font(FONT_NAME, 36)
        for idx, entry in enumerate(high_scores):
            score_text = font_small.render(f"{idx + 1}. {entry['name']} - {entry['score']}", True, (255, 255, 255))
            score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, 200 + idx * 50))
            screen.blit(score_text, score_rect)

        # Draw back button
        self.back_button.draw(screen)

    def update(self):
        mouse_pos = pygame.mouse.get_pos()
        if self.state == 'main':
            for button in self.buttons:
                button.hovered = button.rect.collidepoint(mouse_pos)
            self.high_scores_button.hovered = self.high_scores_button.rect.collidepoint(mouse_pos)
        elif self.state == 'rules':
            self.play_button.hovered = self.play_button.rect.collidepoint(mouse_pos)
            self.back_button.hovered = self.back_button.rect.collidepoint(mouse_pos)
        elif self.state == 'high_scores':
            # High scores buttons handled in Game class
            pass
