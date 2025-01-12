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

    def add_score(self, score, delay):
        if "scores" not in self.scores:
            self.scores["scores"] = []
            
        self.scores["scores"].append({
            "score": score,
            "delay": delay
        })
        self.save_scores()

    def get_placement(self, score, delay):
        # Filter scores with the same delay
        delay_scores = [s["score"] for s in self.scores["scores"] if s["delay"] == delay]
        if not delay_scores:
            return 1  # First score with this delay
        
        # Count how many scores are higher
        placement = sum(1 for s in delay_scores if s >= score) + 1
        return placement

    def get_total_games(self, delay):
        return sum(1 for s in self.scores["scores"] if s["delay"] == delay)
