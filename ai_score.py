# ai_score.py

import json
from pathlib import Path

class AIScore:
    def __init__(self):
        self.file_path = Path(__file__).parent / 'ai_scores.json'
        self.scores = self.load_scores()

    def load_scores(self):
        if not self.file_path.exists():
            return {"scores": []}
        
        with open(self.file_path, 'r') as f:
            return json.load(f)

    def save_scores(self):
        with open(self.file_path, 'w') as f:
            json.dump(self.scores, f, indent=4)

    def add_score(self, score_data):
        if "scores" not in self.scores:
            self.scores["scores"] = []
            
        self.scores["scores"].append(score_data)
        self.save_scores()

    def get_placement(self, score_difference, delay):
        # Filter scores with the same delay
        delay_scores = [s["score_difference"] for s in self.scores["scores"] if s["delay"] == delay]
        if not delay_scores:
            return 1  # First score with this delay
        
        # Count how many scores are higher
        placement = sum(1 for s in delay_scores if s >= score_difference)
        return placement

    def get_total_games(self, delay):
        return sum(1 for s in self.scores["scores"] if s["delay"] == delay)
