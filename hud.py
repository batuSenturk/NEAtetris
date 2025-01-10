# hud.py

import pygame
from constants import FONT_NAME, FONT_SIZE, COLORS, CELL_SIZE, GRID_Y_OFFSET, SCREEN_WIDTH, HOLD_X_OFFSET, HOLD_Y_OFFSET

class HUD:
    def __init__(self, game):
        self.game = game
        self.font = pygame.font.Font(FONT_NAME, FONT_SIZE)
        self.small_font = pygame.font.Font(FONT_NAME, FONT_SIZE - 8)
        self.player_notifications = []  # List of active player notifications
        self.ai_notifications = []  # List of active AI notifications
        self.notifications = []  # For classic mode

    def add_notifications(self, new_notifications, is_ai=False):
        if self.game.mode == "AI":
            # Add new notifications to the appropriate list in AI mode
            target_list = self.ai_notifications if is_ai else self.player_notifications
            for notif in new_notifications:
                target_list.append({
                    'text': notif['text'],
                    'color': notif['color'],
                    'lifetime': notif['lifetime'],
                    'y_pos': 150  # Starting y position
                })
        else:
            # Add to single list in classic mode
            for notif in new_notifications:
                self.notifications.append({
                    'text': notif['text'],
                    'color': notif['color'],
                    'lifetime': notif['lifetime'],
                    'y_pos': 150  # Starting y position
                })

    def update(self):
        if self.game.mode == "AI":
            # Update player notifications
            for notif in self.player_notifications[:]:
                notif['lifetime'] -= 1
                if notif['lifetime'] <= 0:
                    self.player_notifications.remove(notif)
            
            # Update AI notifications
            for notif in self.ai_notifications[:]:
                notif['lifetime'] -= 1
                if notif['lifetime'] <= 0:
                    self.ai_notifications.remove(notif)
        else:
            # Update classic mode notifications
            for notif in self.notifications[:]:
                notif['lifetime'] -= 1
                if notif['lifetime'] <= 0:
                    self.notifications.remove(notif)

    def draw(self, screen):
        if self.game.mode == "AI":
            # Draw player HUD on the left
            self.draw_player_hud(screen)
            # Draw AI HUD on the right
            self.draw_ai_hud(screen)
        else:
            # Draw centered HUD for non-AI modes
            self.draw_centered_hud(screen)

    def draw_player_hud(self, screen):
        # Calculate positions
        player_grid_right = self.game.grid.x_offset + (self.game.grid.width * self.game.grid.cell_size)
        hud_x = player_grid_right + 50  # Add some padding
        hold_x = self.game.grid.x_offset - 150  # Position hold piece to the left of grid

        # Player score and level on the right of player grid
        score_text = self.font.render(f"Score: {self.game.score.score}", True, COLORS['white'])
        level_text = self.font.render(f"Level: {self.game.score.level}", True, COLORS['white'])
        
        screen.blit(score_text, (hud_x, GRID_Y_OFFSET))
        screen.blit(level_text, (hud_x, GRID_Y_OFFSET + 50))

        # Next pieces text and preview for player
        next_text = self.font.render("Next:", True, COLORS['white'])
        screen.blit(next_text, (hud_x, GRID_Y_OFFSET + 100))
        
        # Draw player's next pieces
        if self.game.next_pieces:
            self.draw_next_pieces(screen, self.game.next_pieces, hud_x)

        # Draw player's hold piece on the left
        hold_text = self.font.render("Hold:", True, COLORS['white'])
        screen.blit(hold_text, (hold_x, HOLD_Y_OFFSET))
        if self.game.held_piece:
            self.draw_hold_piece(screen, hold_x)

        # Draw player notifications under the hold piece
        for idx, notif in enumerate(self.player_notifications):
            text_surface = self.small_font.render(notif['text'], True, notif['color'])
            text_rect = text_surface.get_rect(center=(hold_x + 60, HOLD_Y_OFFSET + 150 + idx * 30))
            screen.blit(text_surface, text_rect)

    def draw_ai_hud(self, screen):
        # Calculate positions
        ai_grid_right = self.game.ai_grid.x_offset + (self.game.ai_grid.width * self.game.ai_grid.cell_size)
        hud_x = ai_grid_right + 50  # Add some padding
        hold_x = self.game.ai_grid.x_offset - 150  # Position hold piece to the left of grid

        # AI score and level on the right of AI grid
        score_text = self.font.render(f"AI Score: {self.game.ai_score.score}", True, COLORS['white'])
        level_text = self.font.render(f"AI Level: {self.game.ai_score.level}", True, COLORS['white'])
        
        screen.blit(score_text, (hud_x, GRID_Y_OFFSET))
        screen.blit(level_text, (hud_x, GRID_Y_OFFSET + 50))

        # Next pieces for AI
        next_text = self.font.render("Next:", True, COLORS['white'])
        screen.blit(next_text, (hud_x, GRID_Y_OFFSET + 100))

        # Draw AI's next pieces
        if self.game.ai_next_pieces:
            self.draw_next_pieces(screen, self.game.ai_next_pieces, hud_x)

        # Draw AI's held piece on the left
        hold_text = self.font.render("Hold:", True, COLORS['white'])
        screen.blit(hold_text, (hold_x, HOLD_Y_OFFSET))
        if self.game.ai_held_piece:
            self.draw_hold_piece(screen, hold_x, is_ai=True)

        # Draw AI notifications under the hold piece
        for idx, notif in enumerate(self.ai_notifications):
            text_surface = self.small_font.render(notif['text'], True, notif['color'])
            text_rect = text_surface.get_rect(center=(hold_x + 60, HOLD_Y_OFFSET + 150 + idx * 30))
            screen.blit(text_surface, text_rect)

    def draw_centered_hud(self, screen):
        # Original HUD drawing for non-AI modes
        score_text = self.font.render(f"Score: {self.game.score.score}", True, COLORS['white'])
        screen.blit(score_text, (1000, GRID_Y_OFFSET))
        
        level_text = self.font.render(f"Level: {self.game.score.level}", True, COLORS['white'])
        screen.blit(level_text, (1000, GRID_Y_OFFSET + 50))
        
        next_text = self.font.render("Next:", True, COLORS['white'])
        screen.blit(next_text, (1000, GRID_Y_OFFSET + 100))

        # Draw next pieces
        self.draw_next_pieces(screen, self.game.next_pieces, 1000)

        # Draw notifications
        for idx, notif in enumerate(self.notifications):
            text_surface = self.small_font.render(notif['text'], True, notif['color'])
            text_rect = text_surface.get_rect(center=(HOLD_X_OFFSET + 50, HOLD_Y_OFFSET + 150 + idx * 30))
            screen.blit(text_surface, text_rect)

        # Draw hold piece
        self.draw_hold_piece(screen, HOLD_X_OFFSET)

    def draw_next_pieces(self, screen, pieces, x_offset):
        if not pieces:
            return
            
        block_size = CELL_SIZE
        for piece_idx, next_piece in enumerate(pieces):
            piece_offset = piece_idx * (block_size * 3 + 20)
            piece_width = len(next_piece.shape[0]) * block_size
            x_centering = (4 * block_size - piece_width) // 2
            
            for y, row in enumerate(next_piece.shape):
                for x, cell in enumerate(row):
                    if cell:
                        rect = pygame.Rect(
                            x_offset + x_centering + (x * block_size),
                            GRID_Y_OFFSET + 140 + piece_offset + (y * block_size),
                            block_size,
                            block_size,
                        )
                        pygame.draw.rect(screen, next_piece.color, rect)
                        pygame.draw.rect(screen, COLORS['white'], rect, 1)

    def draw_hold_piece(self, screen, x_offset, is_ai=False):
        piece = self.game.ai_held_piece if is_ai else self.game.held_piece
        if not piece:
            return
            
        block_size = CELL_SIZE
        for y, row in enumerate(piece.shape):
            for x, cell in enumerate(row):
                if cell:
                    rect = pygame.Rect(
                        x_offset + (x * block_size),
                        HOLD_Y_OFFSET + 40 + (y * block_size),
                        block_size,
                        block_size,
                    )
                    pygame.draw.rect(screen, piece.color, rect)
                    pygame.draw.rect(screen, COLORS['white'], rect, 1)
