"""
Scoring and high score management for Turkey Shoot
"""
import json
import os
from datetime import datetime
from constants import HIGH_SCORE_FILE, MAX_HIGH_SCORES


class ScoreManager:
    """Manages scores and high scores"""

    def __init__(self):
        self.current_score = 0
        self.high_scores = self.load_high_scores()

    def add_points(self, points):
        """Add points to current score"""
        self.current_score += points

    def get_score(self):
        """Get current score"""
        return self.current_score

    def reset_score(self):
        """Reset current score to 0"""
        self.current_score = 0

    def load_high_scores(self):
        """Load high scores from file"""
        try:
            if os.path.exists(HIGH_SCORE_FILE):
                with open(HIGH_SCORE_FILE, 'r') as f:
                    return json.load(f)
            return {'easy': [], 'medium': [], 'hard': []}
        except Exception as e:
            print(f"Error loading high scores: {e}")
            return {'easy': [], 'medium': [], 'hard': []}

    def save_high_scores(self):
        """Save high scores to file"""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(HIGH_SCORE_FILE), exist_ok=True)

            with open(HIGH_SCORE_FILE, 'w') as f:
                json.dump(self.high_scores, f, indent=2)
        except Exception as e:
            print(f"Error saving high scores: {e}")

    def is_high_score(self, score, difficulty):
        """Check if score qualifies as a high score"""
        scores = self.high_scores.get(difficulty, [])

        if len(scores) < MAX_HIGH_SCORES:
            return True

        # Check if score is higher than lowest high score
        if scores and score > scores[-1]['score']:
            return True

        return False

    def add_high_score(self, name, score, difficulty, level):
        """Add a new high score"""
        if difficulty not in self.high_scores:
            self.high_scores[difficulty] = []

        new_score = {
            'name': name,
            'score': score,
            'level': level,
            'date': datetime.now().strftime('%Y-%m-%d %H:%M')
        }

        self.high_scores[difficulty].append(new_score)

        # Sort by score (descending)
        self.high_scores[difficulty].sort(key=lambda x: x['score'], reverse=True)

        # Keep only top MAX_HIGH_SCORES
        self.high_scores[difficulty] = self.high_scores[difficulty][:MAX_HIGH_SCORES]

        self.save_high_scores()

    def get_high_scores(self, difficulty):
        """Get high scores for a difficulty"""
        return self.high_scores.get(difficulty, [])

    def get_all_high_scores(self):
        """Get all high scores"""
        return self.high_scores
