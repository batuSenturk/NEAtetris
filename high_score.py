# high_score.py

import json
import os
from constants import HIGH_SCORE_FILE, MAX_HIGH_SCORES, HIGH_SCORE_ENCRYPTION_KEY
from encrypt import Encrypt

class HighScore:
    def __init__(self):
        self.scores = []
        # Initialize the Encrypt instance using the fixed encryption key.
        self.encryptor = Encrypt(HIGH_SCORE_ENCRYPTION_KEY)
        self.load_scores()

    def load_scores(self):
        """Load high scores from an encrypted JSON file."""
        if os.path.exists(HIGH_SCORE_FILE):
            with open(HIGH_SCORE_FILE, 'r') as file:

                #############################
                # GROUP A SKILL :Encryption #
                #############################

                encrypted_data = file.read()
                if encrypted_data:  # Check if file is not empty
                    try:
                        # Decrypt the data and then parse the JSON.
                        json_data = self.encryptor.decrypt_text(encrypted_data)
                        self.scores = json.loads(json_data)
                    except Exception as e:
                        print("Failed to decrypt or parse high scores:", e)
                        self.scores = []
                else:
                    self.scores = []
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
        """Save high scores to an encrypted JSON file."""
        # Convert the scores to a JSON-formatted string.
        json_data = json.dumps(self.scores, indent=4)
        # Encrypt the JSON string.

        #############################
        # GROUP A SKILL :Encryption #
        #############################

        encrypted_data = self.encryptor.encrypt_text(json_data)
        with open(HIGH_SCORE_FILE, 'w') as file:
            file.write(encrypted_data)