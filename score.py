# score.py

from constants import SCORING_TABLE, LINES_PER_LEVEL

class Score:
    def __init__(self):
        self.score = 0
        self.level = 1
        self.lines_cleared = 0

    def update(self, lines_cleared):
        self.lines_cleared += lines_cleared
        self.score += SCORING_TABLE.get(lines_cleared, 0) * self.level

    def update_level(self):
        self.level = self.lines_cleared // LINES_PER_LEVEL + 1
