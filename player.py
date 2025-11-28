"""
Player class for Turkey Shoot
"""
import pygame
from constants import (
    PLAYER_WIDTH, PLAYER_HEIGHT, PLAYER_SPEED, PLAYER_COLOR,
    SCREEN_WIDTH, SCREEN_HEIGHT, PLAYER_SHOOT_COOLDOWN,
    FIRE_RATE_MODIFIER, SPEED_BOOST_MODIFIER
)


class Player:
    """Player controlled character"""

    def __init__(self):
        self.width = PLAYER_WIDTH
        self.height = PLAYER_HEIGHT
        self.x = SCREEN_WIDTH // 2 - self.width // 2
        self.y = SCREEN_HEIGHT - self.height - 10
        self.speed = PLAYER_SPEED
        self.color = PLAYER_COLOR
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.last_shot = 0
        self.shoot_cooldown = PLAYER_SHOOT_COOLDOWN

        # Powerup effect tracking
        self.active_effects = {}  # {effect_type: expiration_time}
        self.speed_modifier = 1.0
        self.cooldown_modifier = 1.0

    def move_left(self):
        """Move player left"""
        self.x -= self.speed * self.speed_modifier
        if self.x < 0:
            self.x = 0
        self.update_rect()

    def move_right(self):
        """Move player right"""
        self.x += self.speed * self.speed_modifier
        if self.x > SCREEN_WIDTH - self.width:
            self.x = SCREEN_WIDTH - self.width
        self.update_rect()

    def update_rect(self):
        """Update collision rectangle"""
        self.rect.x = self.x
        self.rect.y = self.y

    def can_shoot(self, current_time):
        """Check if player can shoot based on cooldown"""
        return current_time - self.last_shot >= (self.shoot_cooldown * self.cooldown_modifier)

    def shoot(self, current_time):
        """Mark that a shot was fired"""
        self.last_shot = current_time

    def draw(self, screen):
        """Draw the player on screen"""
        # Draw body (rectangle)
        pygame.draw.rect(screen, self.color, self.rect)

        # Draw turret/gun on top
        gun_width = 8
        gun_height = 15
        gun_x = self.x + self.width // 2 - gun_width // 2
        gun_y = self.y - gun_height
        pygame.draw.rect(screen, self.color, (gun_x, gun_y, gun_width, gun_height))

    def get_gun_position(self):
        """Get the position where bullets should spawn"""
        gun_x = self.x + self.width // 2
        gun_y = self.y - 15
        return gun_x, gun_y

    def apply_powerup(self, effect_type, duration, current_time):
        """Apply a powerup effect to the player"""
        if duration > 0:
            # Timed effect
            self.active_effects[effect_type] = current_time + duration
        # Instant effects (like extra_life) are handled in game.py

        # Recalculate modifiers
        self.update_modifiers()

    def update_effects(self, current_time):
        """Update active effects and remove expired ones. Returns list of expired effects."""
        # Remove expired effects
        expired = [effect for effect, expiration in self.active_effects.items()
                   if current_time >= expiration]
        for effect in expired:
            del self.active_effects[effect]

        # Recalculate modifiers if any effects expired
        if expired:
            self.update_modifiers()

        return expired

    def update_modifiers(self):
        """Recalculate speed and cooldown modifiers based on active effects"""
        self.speed_modifier = 1.0
        self.cooldown_modifier = 1.0

        if 'speed_boost' in self.active_effects:
            self.speed_modifier *= SPEED_BOOST_MODIFIER

        if 'fire_rate' in self.active_effects:
            self.cooldown_modifier *= FIRE_RATE_MODIFIER
