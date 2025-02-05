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

    def quicksort(self, arr):

        ######################################
        # GROUP A SKILL :Recursive Algorithm #
        ######################################

        ####################################
        # GROUP A SKILL :Sorting Algorithm #
        ####################################

        if len(arr) <= 1:
            return arr
        
        a = arr[0]        
        b = arr[len(arr) // 2]
        c = arr[-1]

        pivot = a if (b <= a <= c) or (c <= a <= b) else b if (a <= b <= c) or (c <= b <= a) else c

        left = [x for x in arr if x > pivot]  # Greater than pivot for descending order
        middle = [x for x in arr if x == pivot]
        right = [x for x in arr if x < pivot]  # Less than pivot for descending order
        
        return self.quicksort(left) + middle + self.quicksort(right)

    def get_placement(self, score_difference, delay):
        # Group scores by delay
        delay_groups = {}
        for score in self.scores["scores"]:
            if score["delay"] not in delay_groups:
                delay_groups[score["delay"]] = []
            delay_groups[score["delay"]].append(score["score_difference"])

        # Sort the scores for the specified delay
        if delay not in delay_groups:
            return 1  # No scores for this delay, so placement is 1

        delay_scores = delay_groups[delay]
        delay_scores = self.quicksort(delay_scores)

        # Find placement
        placement = 1
        for s in delay_scores:
            if s > score_difference:
                placement += 1

        return placement

    def get_total_games(self, delay):
        return sum(1 for s in self.scores["scores"] if s["delay"] == delay)
