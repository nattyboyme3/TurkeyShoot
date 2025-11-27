"""
Collision detection for Turkey Shoot
"""
import pygame


def check_bullet_enemy_collisions(bullets, enemies):
    """
    Check for collisions between bullets and enemies.
    Returns list of (bullet, enemy) tuples that collided and score gained.
    """
    collisions = []
    score_gained = 0

    for bullet in bullets:
        if not bullet.is_active():
            continue

        for enemy in enemies:
            if not enemy.is_active():
                continue

            if bullet.rect.colliderect(enemy.rect):
                bullet.deactivate()
                destroyed = enemy.take_damage()

                if destroyed:
                    score_gained += enemy.get_points()
                    collisions.append((bullet, enemy))

                break  # Bullet can only hit one enemy

    return collisions, score_gained


def check_enemy_player_collision(enemies, player):
    """
    Check if any enemy has collided with the player.
    Returns True if collision occurred.
    """
    for enemy in enemies:
        if not enemy.is_active():
            continue

        if enemy.rect.colliderect(player.rect):
            enemy.active = False  # Enemy is destroyed
            return True

    return False


def check_enemies_reached_bottom(enemies):
    """
    Check if any active enemies have reached the bottom of the screen.
    Returns count of enemies that reached bottom and deactivates them.
    """
    from constants import SCREEN_HEIGHT

    count = 0
    for enemy in enemies:
        if enemy.is_active() and enemy.y >= SCREEN_HEIGHT:
            enemy.active = False
            count += 1

    return count
