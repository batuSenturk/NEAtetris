# menu.py

import pygame
from button import Button
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, MENU_BACKGROUND_COLOR, FONT_NAME, FONT_SIZE, BUTTON_WIDTH, BUTTON_HEIGHT

class Menu:
    def __init__(self, game):
        self.game = game
        self.font = pygame.font.Font(FONT_NAME, 36)
        self.title_font = pygame.font.Font(FONT_NAME, 72)
        self.state = 'main'  # Possible states: 'main', 'rules'
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
                SCREEN_HEIGHT - 150,
                150,
                50
            ),
            text="Play",
            action=self.start_game
        )

        # Back button in 'rules' state
        self.back_button = Button(
            rect=(20, 20, 100, 40),
            text="Back",
            action=self.go_back
        )

    def select_mode(self, mode):
        self.selected_mode = mode
        self.state = 'rules'

    def start_game(self, game):
        # Start the game with the selected mode
        self.game.mode = self.selected_mode
        self.game.start_new_game()
        self.game.current_screen = 'game'

    def go_back(self, game):
        self.state = 'main'

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            # Handle events based on the current state
            if self.state == 'main':
                for button in self.buttons:
                    button.handle_event(event, self.game)
            elif self.state == 'rules':
                self.play_button.handle_event(event, self.game)
                self.back_button.handle_event(event, self.game)

    def draw(self, screen):
        screen.fill(MENU_BACKGROUND_COLOR)
        if self.state == 'main':
            title_text = self.title_font.render("Tetris", True, (255, 255, 255))
            title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 150))
            screen.blit(title_text, title_rect)
            for button in self.buttons:
                button.draw(screen)
        elif self.state == 'rules':
            # Display rules and controls
            self.draw_rules(screen)
            self.play_button.draw(screen)
            self.back_button.draw(screen)

    def update(self):
        mouse_pos = pygame.mouse.get_pos()
        if self.state == 'main':
            for button in self.buttons:
                button.hovered = button.rect.collidepoint(mouse_pos)
        elif self.state == 'rules':
            self.play_button.hovered = self.play_button.rect.collidepoint(mouse_pos)
            self.back_button.hovered = self.back_button.rect.collidepoint(mouse_pos)

    def draw_rules(self, screen):
        # Display the rules and controls for the selected mode
        rules_text = [
            f"Mode: {self.selected_mode}",
            "",
            "Controls:",
            "Left Arrow - Move Left",
            "Right Arrow - Move Right",
            "Up Arrow - Rotate",
            "Down Arrow - Soft Drop",
            "Space - Hard Drop",
            "P - Pause",
            "",
            "Objective:",
            "Clear lines by filling them completely.",
            "The game ends when the pieces reach the top."
        ]
        y_offset = 200
        for line in rules_text:
            text_surf = self.font.render(line, True, (255, 255, 255))
            text_rect = text_surf.get_rect(center=(SCREEN_WIDTH // 2, y_offset))
            screen.blit(text_surf, text_rect)
            y_offset += 40
