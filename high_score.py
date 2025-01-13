# high_score.py

import json
import os
from constants import HIGH_SCORE_FILE, MAX_HIGH_SCORES

class HighScore:
    def __init__(self):
        self.scores = []
        self.load_scores()

    def load_scores(self):
        """Load high scores from a JSON file."""
        if os.path.exists(HIGH_SCORE_FILE):
            with open(HIGH_SCORE_FILE, 'r') as file:
                self.scores = json.load(file)
        else:
            self.scores = []

    def is_high_score(self, score):
        """Check if the given score qualifies as a high score."""
        if len(self.scores) < MAX_HIGH_SCORES:
            return True
        return any(score > entry['score'] for entry in self.scores)

    def add_score(self, name, score):
        """Add a new score to the high score list."""
        self.scores.append({'name': name, 'score': score})
        # Sort scores in descending order
        self.scores = sorted(self.scores, key=lambda x: x['score'], reverse=True)
        # Keep only top MAX_HIGH_SCORES
        self.scores = self.scores[:MAX_HIGH_SCORES]
        self.save_scores()
    
    def save_scores(self):
        """Save high scores to a JSON file."""
        with open(HIGH_SCORE_FILE, 'w') as file:
            json.dump(self.scores, file, indent=4)