# menu.py

import pygame
from button import Button
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, MENU_BACKGROUND_COLOR, FONT_NAME, FONT_SIZE, BUTTON_WIDTH, BUTTON_HEIGHT

class Menu:
    def __init__(self, game):
        self.game = game
        self.font = pygame.font.Font(FONT_NAME, 36)
        self.title_font = pygame.font.Font(FONT_NAME, 72)
        self.state = 'main'  # Possible states: 'main', 'rules', 'high_scores'
        self.selected_mode = None

        # Define buttons for game modes
        modes = ['Classic Mode', 'Endless Mode', 'Time Attack']
        self.buttons = []
        for i, mode in enumerate(modes):
            button = Button(
                rect=(
                    SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2,
                    SCREEN_HEIGHT // 2 - 100 + i * 70,
                    BUTTON_WIDTH,
                    BUTTON_HEIGHT
                ),
                text=mode,
                action=lambda g, m=mode: self.select_mode(m)
            )
            self.buttons.append(button)

        # Play button in 'rules' state
        self.play_button = Button(
            rect=(
                SCREEN_WIDTH // 2 - 75,
                SCREEN_HEIGHT - 100,  # Moved up by 50 pixels
                150,
                50
            ),
            text="Play",
            action=self.start_game
        )

        # Back button in 'rules' and 'high_scores' state
        self.back_button = Button(
            rect=(20, 20, 100, 40),
            text="Back",
            action=self.go_back
        )

        # High Scores button in main menu
        self.high_scores_button = Button(
            rect=(
                SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2,
                SCREEN_HEIGHT // 2 + 150,
                BUTTON_WIDTH,
                BUTTON_HEIGHT
            ),
            text="High Scores",
            action=self.show_high_scores
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

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            # Handle events based on the current state
            if self.state == 'main':
                for button in self.buttons:
                    button.handle_event(event, self.game)
                self.high_scores_button.handle_event(event, self.game)
            elif self.state == 'rules':
                self.play_button.handle_event(event, self.game)
                self.back_button.handle_event(event, self.game)
            elif self.state == 'high_scores':
                # High scores are handled in the Game class
                pass

    def draw(self, screen):
        screen.fill(MENU_BACKGROUND_COLOR)
        if self.state == 'main':
            title_text = self.title_font.render("Tetris", True, (255, 255, 255))
            title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 150))
            screen.blit(title_text, title_rect)
            for button in self.buttons:
                button.draw(screen)
            self.high_scores_button.draw(screen)
        elif self.state == 'rules':
            # Display rules and controls
            self.draw_rules(screen)
            self.play_button.draw(screen)
            self.back_button.draw(screen)
        elif self.state == 'high_scores':
            # Display high scores
            self.draw_high_scores(screen)

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

    def draw_rules(self, screen):
        # Update the rules text to include hold mechanic
        rules_text = [
            f"Mode: {self.selected_mode}",
            "",
            "Controls:",
            "Left Arrow - Move Left",
            "Right Arrow - Move Right",
            "Up Arrow - Rotate",
            "Down Arrow - Soft Drop",
            "Space - Hard Drop",
            "C - Hold Piece",  # Add this line
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
        y_offset = 150  # Start higher up
        for line in rules_text:
            text_surf = self.font.render(line, True, (255, 255, 255))
            text_rect = text_surf.get_rect(center=(SCREEN_WIDTH // 2, y_offset))
            screen.blit(text_surf, text_rect)
            y_offset += 35  # Reduced vertical spacing

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
