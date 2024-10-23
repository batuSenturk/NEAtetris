# score.py

from constants import SCORING_TABLE, LINES_PER_LEVEL

class Score:
    def __init__(self):
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.combo = 0
        self.back_to_back = False

    def update(self, lines_cleared, t_spin_type, mini_t_spin, drop_height, soft_drop_count, hard_drop_count):
        turn_score = 0

        # Line clear scores
        line_clear_scores = {
            1: 100,
            2: 300,
            3: 500,
            4: 800
        }

        # T-Spin scores
        t_spin_scores = {
            0: 400,
            1: 800,
            2: 1200,
            3: 1600
        }

        # Mini T-Spin scores
        mini_t_spin_scores = {
            0: 100,
            1: 200,
            2: 1200
        }

        # Calculate base score
        if t_spin_type:
            if mini_t_spin:
                turn_score = mini_t_spin_scores.get(lines_cleared, 0)
            else:
                turn_score = t_spin_scores.get(lines_cleared, 0)
        else:
            turn_score = line_clear_scores.get(lines_cleared, 0)

        # Apply level multiplier
        turn_score *= self.level

        # Back-to-Back bonus
        if self.back_to_back and (lines_cleared == 4 or t_spin_type):
            turn_score = int(turn_score * 1.5)

        # Update Back-to-Back status
        if lines_cleared == 4 or t_spin_type:
            self.back_to_back = True
        elif lines_cleared > 0:
            self.back_to_back = False

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

        # Create a list of score notifications
        notifications = []
        
        # Line clear notifications
        if lines_cleared > 0:
            clear_types = {
                1: "Single",
                2: "Double",
                3: "Triple",
                4: "Tetris"
            }
            base_score = line_clear_scores.get(lines_cleared, 0) * self.level
            notifications.append({
                'text': f"{clear_types[lines_cleared]} Clear! +{base_score}",
                'color': (255, 255, 255),
                'lifetime': 60  # frames the notification will stay
            })

        # T-Spin notifications
        if t_spin_type:
            t_spin_name = "Mini T-Spin" if mini_t_spin else "T-Spin"
            if lines_cleared > 0:
                t_spin_name += f" {['Single', 'Double', 'Triple'][lines_cleared-1]}"
            base_score = (mini_t_spin_scores if mini_t_spin else t_spin_scores).get(lines_cleared, 0) * self.level
            notifications.append({
                'text': f"{t_spin_name}! +{base_score}",
                'color': (255, 100, 255),
                'lifetime': 60
            })

        # Back-to-Back bonus
        if self.back_to_back and (lines_cleared == 4 or t_spin_type):
            notifications.append({
                'text': "Back-to-Back! +50% bonus!",
                'color': (255, 200, 0),
                'lifetime': 60
            })

        # Combo notifications
        if self.combo > 1:
            combo_score = 50 * self.combo * self.level
            notifications.append({
                'text': f"{self.combo} Combo! +{combo_score}",
                'color': (100, 255, 100),
                'lifetime': 60
            })

        # Drop notifications
        if soft_drop_count > 0:
            notifications.append({
                'text': f"Soft Drop +{soft_drop_count}",
                'color': (200, 200, 200),
                'lifetime': 30
            })
        
        if hard_drop_count > 0:
            notifications.append({
                'text': f"Hard Drop +{hard_drop_count * 2}",
                'color': (200, 200, 200),
                'lifetime': 30
            })

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
