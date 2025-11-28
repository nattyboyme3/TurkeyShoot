"""
Powerup system for Turkey Shoot
"""
import pygame
import random
from constants import (
    POWERUP_TYPES, SCREEN_HEIGHT, SCREEN_WIDTH,
    POWERUP_SPAWN_MARGIN
)


class PowerUp:
    """Powerup collectible"""

    def __init__(self, x, y, powerup_type):
        config = POWERUP_TYPES[powerup_type]
        self.type = powerup_type
        self.radius = config['radius']
        self.color = config['color']
        self.speed = config['speed']
        self.effect_type = config['effect_type']
        self.duration = config['duration']

        self.x = x
        self.y = y
        self.active = True

        # Create rect for collision detection (bounding box around circle)
        self.rect = pygame.Rect(
            self.x - self.radius,
            self.y - self.radius,
            self.radius * 2,
            self.radius * 2
        )

    def update(self):
        """Move powerup downward"""
        self.y += self.speed

        # Update collision rect
        self.rect.x = self.x - self.radius
        self.rect.y = self.y - self.radius

        # Deactivate if off screen
        if self.y > SCREEN_HEIGHT + self.radius:
            self.active = False

    def draw(self, screen):
        """Draw the powerup as a circle"""
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        # Draw white border for visibility
        pygame.draw.circle(screen, (255, 255, 255), (int(self.x), int(self.y)), self.radius, 2)

    def is_active(self):
        """Check if powerup is still active"""
        return self.active

    def deactivate(self):
        """Mark powerup as inactive"""
        self.active = False


def spawn_powerup(powerup_type=None):
    """Factory function to spawn a random powerup"""
    if powerup_type is None:
        # Randomly select a powerup type
        powerup_type = random.choice(list(POWERUP_TYPES.keys()))

    config = POWERUP_TYPES[powerup_type]
    x = random.randint(POWERUP_SPAWN_MARGIN, SCREEN_WIDTH - POWERUP_SPAWN_MARGIN)
    y = -config['radius']
    return PowerUp(x, y, powerup_type)
