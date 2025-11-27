"""
Projectile/Bullet system for Turkey Shoot
"""
import pygame
from constants import (
    BULLET_WIDTH, BULLET_HEIGHT, BULLET_SPEED, BULLET_COLOR,
    SCREEN_HEIGHT
)


class Bullet:
    """Player's bullet projectile"""

    def __init__(self, x, y):
        self.width = BULLET_WIDTH
        self.height = BULLET_HEIGHT
        self.x = x - self.width // 2  # Center on gun
        self.y = y
        self.speed = BULLET_SPEED
        self.color = BULLET_COLOR
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.active = True

    def update(self):
        """Move bullet upward"""
        self.y -= self.speed
        self.rect.y = self.y

        # Deactivate if off screen
        if self.y < -self.height:
            self.active = False

    def draw(self, screen):
        """Draw the bullet"""
        pygame.draw.rect(screen, self.color, self.rect)

    def is_active(self):
        """Check if bullet is still active"""
        return self.active

    def deactivate(self):
        """Mark bullet as inactive"""
        self.active = False
