"""
Main game loop and state management for Turkey Shoot
"""
import pygame
from constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, TITLE, BLACK,
    DIFFICULTY_SETTINGS, WHITE, POWERUP_SPAWN_RATE,
    SLOW_ENEMIES_MODIFIER
)
from player import Player
from projectiles import Bullet
from enemies import Enemy
from powerups import spawn_powerup
from collision import (
    check_bullet_enemy_collisions,
    check_enemy_player_collision,
    check_enemies_reached_bottom,
    check_powerup_player_collision
)
from scoring import ScoreManager
from levels import LevelManager
from ui import UI


class GameState:
    """Game state enumeration"""
    MENU = 'menu'
    PLAYING = 'playing'
    PAUSED = 'paused'
    GAME_OVER = 'game_over'
    HIGH_SCORES = 'high_scores'
    LEVEL_TRANSITION = 'level_transition'
    NAME_INPUT = 'name_input'


class Game:
    """Main game class"""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.running = True

        # Game state
        self.state = GameState.MENU
        self.difficulty = 'medium'

        # Managers
        self.score_manager = ScoreManager()
        self.level_manager = None
        self.ui = UI(self.screen)

        # Game objects
        self.player = None
        self.bullets = []
        self.enemies = []
        self.powerups = []

        # Game variables
        self.lives = 0
        self.level_transition_time = 0
        self.level_transition_duration = 2000  # 2 seconds

        # Powerup tracking
        self.last_powerup_spawn = 0
        self.enemy_speed_modifier = 1.0
        self.enemy_speed_modifier_expiration = 0

        # Name input
        self.player_name = ""
        self.is_high_score = False

    def reset_game(self, difficulty):
        """Reset game for new play session"""
        self.difficulty = difficulty
        self.level_manager = LevelManager(difficulty)
        self.level_manager.start_level()

        self.player = Player()
        self.bullets = []
        self.enemies = []
        self.powerups = []

        self.score_manager.reset_score()
        self.lives = DIFFICULTY_SETTINGS[difficulty]['lives']

        # Reset powerup state
        self.last_powerup_spawn = 0
        self.enemy_speed_modifier = 1.0
        self.enemy_speed_modifier_expiration = 0

        self.state = GameState.PLAYING

    def handle_events(self):
        """Handle input events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            # Menu state
            if self.state == GameState.MENU:
                self.handle_menu_events(event)

            # Playing state
            elif self.state == GameState.PLAYING:
                self.handle_playing_events(event)

            # Game over state
            elif self.state == GameState.GAME_OVER:
                self.handle_game_over_events(event)

            # High scores state
            elif self.state == GameState.HIGH_SCORES:
                self.handle_high_scores_events(event)

            # Name input state
            elif self.state == GameState.NAME_INPUT:
                self.handle_name_input_events(event)

    def handle_menu_events(self, event):
        """Handle menu events"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            buttons = self.menu_buttons

            if buttons['easy'].is_clicked(mouse_pos):
                self.reset_game('easy')
            elif buttons['medium'].is_clicked(mouse_pos):
                self.reset_game('medium')
            elif buttons['hard'].is_clicked(mouse_pos):
                self.reset_game('hard')
            elif buttons['high_scores'].is_clicked(mouse_pos):
                self.state = GameState.HIGH_SCORES
            elif buttons['quit'].is_clicked(mouse_pos):
                self.running = False

    def handle_playing_events(self, event):
        """Handle playing state events"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.shoot()
            elif event.key == pygame.K_ESCAPE:
                self.state = GameState.MENU

    def handle_game_over_events(self, event):
        """Handle game over events"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            buttons = self.game_over_buttons

            if buttons['retry'].is_clicked(mouse_pos):
                self.reset_game(self.difficulty)
            elif buttons['menu'].is_clicked(mouse_pos):
                self.state = GameState.MENU

    def handle_high_scores_events(self, event):
        """Handle high scores screen events"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            buttons = self.high_score_buttons

            if buttons['back'].is_clicked(mouse_pos):
                self.state = GameState.MENU

    def handle_name_input_events(self, event):
        """Handle name input events"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                if self.player_name:
                    # Save high score
                    self.score_manager.add_high_score(
                        self.player_name,
                        self.score_manager.get_score(),
                        self.difficulty,
                        self.level_manager.get_current_level()
                    )
                    self.state = GameState.GAME_OVER
            elif event.key == pygame.K_BACKSPACE:
                self.player_name = self.player_name[:-1]
            elif len(self.player_name) < 15:  # Limit name length
                if event.unicode.isprintable():
                    self.player_name += event.unicode

    def shoot(self):
        """Player shoots a bullet"""
        if self.player and self.player.can_shoot(pygame.time.get_ticks()):
            gun_x, gun_y = self.player.get_gun_position()
            bullet = Bullet(gun_x, gun_y)
            self.bullets.append(bullet)
            self.player.shoot(pygame.time.get_ticks())

    def update(self):
        """Update game state"""
        if self.state == GameState.PLAYING:
            self.update_playing()
        elif self.state == GameState.LEVEL_TRANSITION:
            self.update_level_transition()

    def update_playing(self):
        """Update playing state"""
        current_time = pygame.time.get_ticks()

        # Update player effects
        self.player.update_effects(current_time)

        # Update enemy speed modifier expiration
        if self.enemy_speed_modifier_expiration > 0 and current_time >= self.enemy_speed_modifier_expiration:
            self.enemy_speed_modifier = 1.0
            self.enemy_speed_modifier_expiration = 0

        # Update player movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.player.move_left()
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.player.move_right()
        if keys[pygame.K_SPACE]:
            self.shoot()

        # Update bullets
        for bullet in self.bullets[:]:
            bullet.update()
            if not bullet.is_active():
                self.bullets.remove(bullet)

        # Spawn powerups
        if current_time - self.last_powerup_spawn >= POWERUP_SPAWN_RATE:
            powerup = spawn_powerup()
            self.powerups.append(powerup)
            self.last_powerup_spawn = current_time

        # Update powerups
        for powerup in self.powerups[:]:
            powerup.update()
            if not powerup.is_active():
                self.powerups.remove(powerup)

        # Check powerup-player collision
        collected_powerup = check_powerup_player_collision(self.powerups, self.player)
        if collected_powerup:
            self.apply_powerup_effect(collected_powerup, current_time)
            self.powerups.remove(collected_powerup)

        # Spawn enemies (apply slow modifier to speed)
        enemy = self.level_manager.spawn_next_enemy(current_time)
        if enemy:
            # Apply slow enemies modifier if active
            enemy.speed *= self.enemy_speed_modifier
            self.enemies.append(enemy)

        # Update enemies
        for enemy in self.enemies[:]:
            enemy.update()
            if not enemy.is_active():
                self.enemies.remove(enemy)

        # Check collisions
        collisions, score_gained = check_bullet_enemy_collisions(self.bullets, self.enemies)
        if score_gained > 0:
            self.score_manager.add_points(score_gained)

        # Check player-enemy collision
        if check_enemy_player_collision(self.enemies, self.player):
            self.lose_life()

        # Check enemies reaching bottom
        enemies_escaped = check_enemies_reached_bottom(self.enemies)
        if enemies_escaped > 0:
            self.lose_life()

        # Check level completion
        active_enemies = len([e for e in self.enemies if e.is_active()])
        if self.level_manager.is_level_complete(active_enemies):
            self.start_level_transition()

    def update_level_transition(self):
        """Update level transition state"""
        current_time = pygame.time.get_ticks()
        if current_time - self.level_transition_time >= self.level_transition_duration:
            self.level_manager.advance_level()
            self.state = GameState.PLAYING

    def start_level_transition(self):
        """Start level transition"""
        self.state = GameState.LEVEL_TRANSITION
        self.level_transition_time = pygame.time.get_ticks()

    def apply_powerup_effect(self, powerup, current_time):
        """Apply powerup effect based on type"""
        effect_type = powerup.effect_type
        duration = powerup.duration

        if effect_type == 'extra_life':
            # Instant effect: add a life
            self.lives += 1
        elif effect_type == 'slow_enemies':
            # Global effect: slow all future enemies
            self.enemy_speed_modifier = SLOW_ENEMIES_MODIFIER
            self.enemy_speed_modifier_expiration = current_time + duration
            # Also slow existing enemies
            for enemy in self.enemies:
                enemy.speed *= SLOW_ENEMIES_MODIFIER
        else:
            # Player-specific effects (fire_rate, speed_boost)
            self.player.apply_powerup(effect_type, duration, current_time)

    def lose_life(self):
        """Player loses a life"""
        self.lives -= 1
        if self.lives <= 0:
            self.game_over()

    def game_over(self):
        """Handle game over"""
        score = self.score_manager.get_score()
        level = self.level_manager.get_current_level()

        # Check if high score
        if self.score_manager.is_high_score(score, self.difficulty):
            self.is_high_score = True
            self.player_name = ""
            self.state = GameState.NAME_INPUT
        else:
            self.is_high_score = False
            self.state = GameState.GAME_OVER

    def draw(self):
        """Draw current game state"""
        self.screen.fill(BLACK)

        if self.state == GameState.MENU:
            self.menu_buttons = self.ui.draw_main_menu()

        elif self.state == GameState.PLAYING:
            self.draw_playing()

        elif self.state == GameState.GAME_OVER:
            self.draw_playing()  # Show game in background
            self.game_over_buttons = self.ui.draw_game_over(
                self.score_manager.get_score(),
                self.level_manager.get_current_level(),
                self.is_high_score
            )

        elif self.state == GameState.HIGH_SCORES:
            self.high_score_buttons = self.ui.draw_high_scores(self.score_manager)

        elif self.state == GameState.LEVEL_TRANSITION:
            self.draw_playing()
            self.ui.draw_level_transition(self.level_manager.get_current_level() + 1)

        elif self.state == GameState.NAME_INPUT:
            self.draw_playing()
            self.ui.draw_name_input(self.player_name)

        pygame.display.flip()

    def draw_playing(self):
        """Draw playing state"""
        # Draw player
        if self.player:
            self.player.draw(self.screen)

        # Draw bullets
        for bullet in self.bullets:
            bullet.draw(self.screen)

        # Draw powerups
        for powerup in self.powerups:
            powerup.draw(self.screen)

        # Draw enemies
        for enemy in self.enemies:
            enemy.draw(self.screen)

        # Draw HUD
        self.ui.draw_hud(
            self.score_manager.get_score(),
            self.lives,
            self.level_manager.get_current_level()
        )

    def run(self):
        """Main game loop"""
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()
