"""
Powerup system for Turkey Shoot
"""
import pygame
import random
from constants import (
    POWERUP_TYPES, SCREEN_HEIGHT, SCREEN_WIDTH,
    POWERUP_SPAWN_MARGIN, SPRITE_DIR, WHITE, ASSETS_DIR
)
from utils import resource_path


class PowerUp:
    """Powerup collectible"""

    # Class-level sprite cache: {(powerup_type, size): scaled_surface}
    _sprite_cache = {}

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

        # Calculate sprite size (square that fits the circle)
        self.sprite_size = self.radius * 2

        # Load sprite if available
        cache_key = (powerup_type, self.sprite_size)
        if cache_key in PowerUp._sprite_cache:
            self.sprite = PowerUp._sprite_cache[cache_key]
        else:
            sprite_filename = f"{powerup_type}.png"
            try:
                original = pygame.image.load(resource_path(ASSETS_DIR, SPRITE_DIR, sprite_filename))
                scaled = pygame.transform.scale(original, (self.sprite_size, self.sprite_size))
                PowerUp._sprite_cache[cache_key] = scaled
                self.sprite = scaled
            except (pygame.error, FileNotFoundError):
                self.sprite = None  # Fallback to circle rendering

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
        """Draw the powerup"""
        # Draw powerup (sprite if available, otherwise circle)
        if self.sprite:
            # Calculate top-left position for sprite (centered on x, y)
            sprite_x = int(self.x - self.radius)
            sprite_y = int(self.y - self.radius)
            screen.blit(self.sprite, (sprite_x, sprite_y))
        else:
            # Fallback to circle rendering
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
            # Draw white border for visibility
            pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.radius, 2)

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
