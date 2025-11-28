"""
Level progression and enemy wave management for Turkey Shoot
"""
import random
from constants import (
    LEVEL_ENEMY_INCREASE, LEVEL_SPEED_INCREASE,
    BOSS_LEVEL_INTERVAL, ENEMY_UNLOCKS, DIFFICULTY_SETTINGS
)
from enemies import spawn_enemy


class LevelManager:
    """Manages level progression and enemy spawning"""

    def __init__(self, difficulty='medium'):
        self.difficulty = difficulty
        self.current_level = 1
        self.enemies_in_level = 0
        self.enemies_spawned = 0
        self.difficulty_settings = DIFFICULTY_SETTINGS[difficulty]
        self.spawn_rate = self.difficulty_settings['spawn_rate']
        self.last_spawn_time = 0

    def get_current_level(self):
        """Get current level number"""
        return self.current_level

    def is_boss_level(self):
        """Check if current level is a boss level"""
        return self.current_level % BOSS_LEVEL_INTERVAL == 0

    def get_available_enemy_types(self):
        """Get list of enemy types available at current level"""
        available = []

        for level, enemy_types in sorted(ENEMY_UNLOCKS.items()):
            if level <= self.current_level:
                for enemy_type in enemy_types:
                    # Only add gravy_boat on boss levels
                    if enemy_type == 'turkey':
                        if self.is_boss_level():
                            available.append(enemy_type)
                    else:
                        if enemy_type not in available:
                            available.append(enemy_type)

        return available if available else ['turkey']

    def get_speed_multiplier(self):
        """Calculate speed multiplier based on level and difficulty"""
        base_multiplier = self.difficulty_settings['speed_multiplier']

        # Increase speed every 3 levels
        level_multiplier = 1 + ((self.current_level - 1) // 3) * LEVEL_SPEED_INCREASE

        return base_multiplier * level_multiplier

    def get_enemies_for_level(self):
        """Calculate number of enemies for current level"""
        base_count = 10  # Base enemy count for level 1

        # Apply level increase
        level_factor = 1 + (self.current_level - 1) * LEVEL_ENEMY_INCREASE

        # Apply difficulty multiplier
        difficulty_factor = self.difficulty_settings['enemy_count_multiplier']

        total = int(base_count * level_factor * difficulty_factor)

        # Boss levels have fewer regular enemies
        if self.is_boss_level():
            total = total // 2 + 1  # Half the enemies plus the boss

        return max(total, 5)  # Minimum 5 enemies

    def start_level(self):
        """Initialize a new level"""
        self.enemies_in_level = self.get_enemies_for_level()
        self.enemies_spawned = 0

    def can_spawn_enemy(self, current_time):
        """Check if it's time to spawn a new enemy"""
        if self.enemies_spawned >= self.enemies_in_level:
            return False

        if current_time - self.last_spawn_time >= self.spawn_rate:
            return True

        return False

    def spawn_next_enemy(self, current_time, player=None):
        """Spawn the next enemy for this level"""
        if not self.can_spawn_enemy(current_time):
            return None

        available_types = self.get_available_enemy_types()
        speed_multiplier = self.get_speed_multiplier()

        # Boss spawning logic
        if self.is_boss_level() and self.enemies_spawned == 0:
            # First enemy on boss level is always the boss
            enemy_type = 'turkey'
        elif 'turkey' in available_types:
            # Remove boss from normal spawn pool
            available_types = [t for t in available_types if t != 'turkey']
            enemy_type = random.choice(available_types)
        else:
            enemy_type = random.choice(available_types)

        enemy = spawn_enemy(enemy_type, speed_multiplier, player)

        self.enemies_spawned += 1
        self.last_spawn_time = current_time

        return enemy

    def is_level_complete(self, active_enemies_count):
        """Check if current level is complete"""
        return (self.enemies_spawned >= self.enemies_in_level and
                active_enemies_count == 0)

    def advance_level(self):
        """Advance to next level"""
        self.current_level += 1
        self.start_level()

    def reset(self):
        """Reset level manager"""
        self.current_level = 1
        self.enemies_in_level = 0
        self.enemies_spawned = 0
        self.last_spawn_time = 0
