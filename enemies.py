"""
Enemy classes for Turkey Shoot
"""
import pygame
import math
import random
from constants import (
    ENEMY_TYPES, SCREEN_WIDTH, SCREEN_HEIGHT,
    ENEMY_SPAWN_MARGIN, WHITE, SPRITE_DIR
)


class Enemy:
    """Base enemy class"""

    # Class-level sprite cache: {(enemy_type, width, height): scaled_surface}
    _sprite_cache = {}

    def __init__(self, enemy_type, x, y, speed_multiplier=1.0, player=None):
        config = ENEMY_TYPES[enemy_type]
        self.type = enemy_type
        self.width = config['width']
        self.height = config['height']
        self.color = config['color']
        self.base_speed = config['speed']
        self.speed = self.base_speed * speed_multiplier
        self.health = config['health']
        self.max_health = config['health']
        self.points = config['points']
        self.movement_type = config['movement']

        self.x = x
        self.y = y
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

        # Reference to player for tracking movement
        self.player = player

        # Load sprite if available
        cache_key = (enemy_type, self.width, self.height)
        if cache_key in Enemy._sprite_cache:
            self.sprite = Enemy._sprite_cache[cache_key]
        else:
            sprite_path = f"{SPRITE_DIR}/{enemy_type}.png"
            try:
                original = pygame.image.load(sprite_path)
                scaled = pygame.transform.scale(original, (self.width, self.height))
                Enemy._sprite_cache[cache_key] = scaled
                self.sprite = scaled
            except (pygame.error, FileNotFoundError):
                self.sprite = None  # Fallback to rectangle rendering

        # Movement specific variables
        self.initial_x = x
        self.time_offset = random.uniform(0, 2 * math.pi)
        self.zigzag_direction = 1 if random.random() > 0.5 else -1
        self.active = True

    def update(self):
        """Update enemy position based on movement type"""
        if self.movement_type == 'straight':
            self.move_straight()
        elif self.movement_type == 'zigzag':
            self.move_zigzag()
        elif self.movement_type == 'sine_wave':
            self.move_sine_wave()
        elif self.movement_type == 'track_player':
            self.move_track_player()

        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

        # Deactivate if off screen
        if self.y > SCREEN_HEIGHT:
            self.active = False

    def move_straight(self):
        """Move straight down"""
        self.y += self.speed

    def move_zigzag(self):
        """Move in a zigzag pattern"""
        self.y += self.speed
        self.x += self.zigzag_direction * 2

        # Reverse direction if hitting edges
        if self.x <= 0 or self.x >= SCREEN_WIDTH - self.width:
            self.zigzag_direction *= -1

    def move_sine_wave(self):
        """Move in a sine wave pattern"""
        self.y += self.speed
        amplitude = 100
        frequency = 0.05
        self.x = self.initial_x + amplitude * math.sin(frequency * self.y + self.time_offset)

        # Keep within bounds
        if self.x < 0:
            self.x = 0
        elif self.x > SCREEN_WIDTH - self.width:
            self.x = SCREEN_WIDTH - self.width

    def move_track_player(self):
        """Move toward the player's position"""
        if not self.player:
            # Fallback to straight movement if no player reference
            self.move_straight()
            return

        # Calculate direction vector to player
        player_center_x = self.player.x + self.player.width / 2
        player_center_y = self.player.y + self.player.height / 2
        enemy_center_x = self.x + self.width / 2
        enemy_center_y = self.y + self.height / 2

        dx = player_center_x - enemy_center_x
        dy = player_center_y - enemy_center_y

        # Calculate distance and normalize
        distance = math.sqrt(dx**2 + dy**2)
        if distance > 0:
            # Move toward player at enemy's speed
            self.x += (dx / distance) * self.speed
            self.y += (dy / distance) * self.speed

        # Keep within bounds
        if self.x < 0:
            self.x = 0
        elif self.x > SCREEN_WIDTH - self.width:
            self.x = SCREEN_WIDTH - self.width

    def take_damage(self, damage=1):
        """Reduce health by damage amount"""
        self.health -= damage
        if self.health <= 0:
            self.active = False
            return True  # Enemy destroyed
        return False  # Enemy still alive

    def draw(self, screen):
        """Draw the enemy"""
        # Draw enemy (sprite if available, otherwise rectangle)
        if self.sprite:
            screen.blit(self.sprite, (self.x, self.y))
        else:
            # Fallback to rectangle rendering
            pygame.draw.rect(screen, self.color, self.rect)
            pygame.draw.rect(screen, WHITE, self.rect, 2)

        # Draw health bar if enemy has more than 1 HP
        if self.max_health > 1:
            health_bar_width = self.width
            health_bar_height = 5
            health_percentage = self.health / self.max_health

            # Background (red)
            pygame.draw.rect(
                screen,
                (255, 0, 0),
                (self.x, self.y - 8, health_bar_width, health_bar_height)
            )

            # Foreground (green)
            pygame.draw.rect(
                screen,
                (0, 255, 0),
                (self.x, self.y - 8, health_bar_width * health_percentage, health_bar_height)
            )

    def is_active(self):
        """Check if enemy is still active"""
        return self.active

    def get_points(self):
        """Return point value of enemy"""
        return self.points


def spawn_enemy(enemy_type, speed_multiplier=1.0, player=None):
    """Factory function to spawn a random enemy of given type"""
    config = ENEMY_TYPES[enemy_type]
    x = random.randint(ENEMY_SPAWN_MARGIN, SCREEN_WIDTH - config['width'] - ENEMY_SPAWN_MARGIN)
    y = -config['height']
    return Enemy(enemy_type, x, y, speed_multiplier, player)
