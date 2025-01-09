# score.py

from constants import SCORING_TABLE, LINES_PER_LEVEL

class Score:
    def __init__(self):
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.combo = 0
        self.back_to_back = False

    def update(self, lines_cleared, t_spin_type, _, drop_height, soft_drop_count, hard_drop_count):
        turn_score = 0
        notifications = []

        # Line clear scores (no T-spin)
        line_clear_scores = {
            1: 100,   # Single
            2: 300,   # Double
            3: 500,   # Triple
            4: 800    # Tetris
        }

        # T-Spin scores (normal)
        t_spin_scores = {
            0: 400,   # T-spin no lines
            1: 800,   # T-spin Single
            2: 1200,  # T-spin Double
            3: 1600   # T-spin Triple
        }

        # Mini T-Spin scores
        mini_t_spin_scores = {
            0: 100,   # Mini T-spin no lines
            1: 200,   # Mini T-spin Single
            2: 400    # Mini T-spin Double
        }

        # Calculate base score
        if t_spin_type == "normal":
            turn_score = t_spin_scores.get(lines_cleared, 0)
        elif t_spin_type == "mini":
            turn_score = mini_t_spin_scores.get(lines_cleared, 0)
        else:
            turn_score = line_clear_scores.get(lines_cleared, 0)

        # Apply level multiplier
        turn_score *= self.level

        # Back-to-Back bonus (applies to Tetrises and any T-spin with lines)
        if self.back_to_back and (lines_cleared == 4 or (t_spin_type and lines_cleared > 0)):
            turn_score = int(turn_score * 1.5)
            notifications.append({
                'text': "Back-to-Back! +50% bonus!",
                'color': (255, 200, 0),
                'lifetime': 60
            })

        # Update Back-to-Back status
        if lines_cleared == 4 or (t_spin_type and lines_cleared > 0):
            self.back_to_back = True
        elif lines_cleared > 0:
            self.back_to_back = False

        # Add score notifications
        if t_spin_type:
            t_spin_name = "Mini T-Spin" if t_spin_type == "mini" else "T-Spin"
            if lines_cleared > 0:
                t_spin_name += f" {['Single', 'Double', 'Triple'][lines_cleared-1]}"
            base_score = (mini_t_spin_scores if t_spin_type == "mini" else t_spin_scores).get(lines_cleared, 0) * self.level
            notifications.append({
                'text': f"{t_spin_name}! +{base_score}",
                'color': (255, 100, 255),
                'lifetime': 60
            })
        elif lines_cleared > 0:
            clear_types = {1: "Single", 2: "Double", 3: "Triple", 4: "Tetris"}
            base_score = line_clear_scores[lines_cleared] * self.level
            notifications.append({
                'text': f"{clear_types[lines_cleared]} Clear! +{base_score}",
                'color': (255, 255, 255),
                'lifetime': 60
            })

        # Combo bonus
        if lines_cleared > 0:
            self.combo += 1
            turn_score += 50 * self.combo * self.level
        else:
            self.combo = 0

        # Soft drop bonus
        turn_score += soft_drop_count

        # Hard drop bonus
        turn_score += hard_drop_count * 2

        # Update total score
        self.score += turn_score

        # Update lines cleared
        self.lines_cleared += lines_cleared

        # Update level
        self.update_level()

        return turn_score, notifications

    def update_level(self):
        """Update the level based on lines cleared"""
        # Calculate new level (every 10 lines = 1 level)
        new_level = (self.lines_cleared // LINES_PER_LEVEL) + 1
        
        # Only update if the level has increased
        if new_level > self.level:
            self.level = new_level

    def add_tetris_clear_bonus(self):
        """Add bonus for clearing the entire board"""
        tetris_clear_bonus = 10000 * self.level
        self.score += tetris_clear_bonus
        return tetris_clear_bonus

    def update_silent(self, lines_cleared, drop_distance):
        """Update score without generating notifications"""
        # Line clear scores
        line_clear_scores = {
            1: 100,   # Single
            2: 300,   # Double
            3: 500,   # Triple
            4: 800    # Tetris
        }
        
        # Calculate base score
        turn_score = line_clear_scores.get(lines_cleared, 0)
        
        # Apply level multiplier
        turn_score *= self.level
        
        # Add hard drop bonus
        turn_score += drop_distance * 2
        
        # Update total score
        self.score += turn_score
        
        # Update lines cleared
        self.lines_cleared += lines_cleared
        
        # Update level
        self.update_level()
