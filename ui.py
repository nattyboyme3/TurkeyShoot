"""
UI elements for Turkey Shoot including menus, HUD, and screens
"""
import pygame
from constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, BLACK, RED, GREEN, BLUE,
    YELLOW, ORANGE, FONT_SIZE_SMALL, FONT_SIZE_MEDIUM, FONT_SIZE_LARGE,
    MENU_BUTTON_WIDTH, MENU_BUTTON_HEIGHT, MENU_BUTTON_SPACING
)


class Button:
    """Simple button class"""

    def __init__(self, x, y, width, height, text, color=BLUE):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = (min(color[0] + 30, 255),
                           min(color[1] + 30, 255),
                           min(color[2] + 30, 255))
        self.is_hovered = False

    def draw(self, screen, font):
        """Draw the button"""
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, WHITE, self.rect, 3)

        text_surface = font.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def check_hover(self, mouse_pos):
        """Check if mouse is hovering over button"""
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def is_clicked(self, mouse_pos):
        """Check if button was clicked"""
        return self.rect.collidepoint(mouse_pos)


class UI:
    """UI manager for all screens and HUD"""

    def __init__(self, screen):
        self.screen = screen
        self.small_font = pygame.font.Font(None, FONT_SIZE_SMALL)
        self.medium_font = pygame.font.Font(None, FONT_SIZE_MEDIUM)
        self.large_font = pygame.font.Font(None, FONT_SIZE_LARGE)

    def draw_text(self, text, font, color, x, y, center=False):
        """Draw text on screen"""
        text_surface = font.render(text, True, color)
        if center:
            text_rect = text_surface.get_rect(center=(x, y))
            self.screen.blit(text_surface, text_rect)
        else:
            self.screen.blit(text_surface, (x, y))

    def draw_hud(self, score, lives, level):
        """Draw heads-up display during gameplay"""
        # Score
        self.draw_text(f"Score: {score}", self.small_font, WHITE, 10, 10)

        # Lives
        lives_text = f"Lives: {lives}"
        self.draw_text(lives_text, self.small_font, RED, 10, 35)

        # Level
        level_text = f"Level: {level}"
        self.draw_text(level_text, self.small_font, YELLOW, SCREEN_WIDTH - 120, 10)

    def draw_main_menu(self):
        """Draw main menu and return buttons"""
        self.screen.fill(BLACK)

        # Title
        self.draw_text("TURKEY SHOOT", self.large_font, ORANGE,
                      SCREEN_WIDTH // 2, 100, center=True)

        # Subtitle
        self.draw_text("A Thanksgiving Shooting Game", self.small_font, WHITE,
                      SCREEN_WIDTH // 2, 150, center=True)

        # Create buttons
        button_x = SCREEN_WIDTH // 2 - MENU_BUTTON_WIDTH // 2
        start_y = 250

        buttons = {
            'easy': Button(button_x, start_y, MENU_BUTTON_WIDTH,
                          MENU_BUTTON_HEIGHT, "Easy", GREEN),
            'medium': Button(button_x, start_y + MENU_BUTTON_HEIGHT + MENU_BUTTON_SPACING,
                           MENU_BUTTON_WIDTH, MENU_BUTTON_HEIGHT, "Medium", YELLOW),
            'hard': Button(button_x, start_y + (MENU_BUTTON_HEIGHT + MENU_BUTTON_SPACING) * 2,
                          MENU_BUTTON_WIDTH, MENU_BUTTON_HEIGHT, "Hard", RED),
            'high_scores': Button(button_x, start_y + (MENU_BUTTON_HEIGHT + MENU_BUTTON_SPACING) * 3,
                                 MENU_BUTTON_WIDTH, MENU_BUTTON_HEIGHT, "High Scores", BLUE),
            'quit': Button(button_x, start_y + (MENU_BUTTON_HEIGHT + MENU_BUTTON_SPACING) * 4,
                          MENU_BUTTON_WIDTH, MENU_BUTTON_HEIGHT, "Quit", (100, 100, 100))
        }

        # Draw buttons
        mouse_pos = pygame.mouse.get_pos()
        for button in buttons.values():
            button.check_hover(mouse_pos)
            button.draw(self.screen, self.small_font)

        return buttons

    def draw_game_over(self, score, level, is_high_score=False):
        """Draw game over screen"""
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))

        # Game Over text
        self.draw_text("GAME OVER", self.large_font, RED,
                      SCREEN_WIDTH // 2, 150, center=True)

        # Score
        self.draw_text(f"Final Score: {score}", self.medium_font, WHITE,
                      SCREEN_WIDTH // 2, 220, center=True)

        # Level reached
        self.draw_text(f"Level Reached: {level}", self.medium_font, WHITE,
                      SCREEN_WIDTH // 2, 270, center=True)

        # High score notification
        if is_high_score:
            self.draw_text("NEW HIGH SCORE!", self.medium_font, YELLOW,
                          SCREEN_WIDTH // 2, 320, center=True)

        # Create buttons
        button_x = SCREEN_WIDTH // 2 - MENU_BUTTON_WIDTH // 2
        start_y = 380

        buttons = {
            'retry': Button(button_x, start_y, MENU_BUTTON_WIDTH,
                          MENU_BUTTON_HEIGHT, "Play Again", GREEN),
            'menu': Button(button_x, start_y + MENU_BUTTON_HEIGHT + MENU_BUTTON_SPACING,
                         MENU_BUTTON_WIDTH, MENU_BUTTON_HEIGHT, "Main Menu", BLUE)
        }

        mouse_pos = pygame.mouse.get_pos()
        for button in buttons.values():
            button.check_hover(mouse_pos)
            button.draw(self.screen, self.small_font)

        return buttons

    def draw_high_scores(self, score_manager):
        """Draw high scores screen"""
        self.screen.fill(BLACK)

        # Title
        self.draw_text("HIGH SCORES", self.large_font, YELLOW,
                      SCREEN_WIDTH // 2, 40, center=True)

        # Draw scores for each difficulty
        difficulties = ['easy', 'medium', 'hard']
        colors = [GREEN, YELLOW, RED]
        column_width = SCREEN_WIDTH // 3

        for i, (difficulty, color) in enumerate(zip(difficulties, colors)):
            x = column_width * i + column_width // 2

            # Difficulty header
            self.draw_text(difficulty.upper(), self.medium_font, color,
                          x, 100, center=True)

            # Scores
            scores = score_manager.get_high_scores(difficulty)
            y = 140

            if not scores:
                self.draw_text("No scores yet", self.small_font, WHITE,
                              x, y, center=True)
            else:
                for j, score_entry in enumerate(scores[:10], 1):
                    score_text = f"{j}. {score_entry['score']}"
                    self.draw_text(score_text, self.small_font, WHITE,
                                  x, y, center=True)
                    y += 25

        # Back button
        button_x = SCREEN_WIDTH // 2 - MENU_BUTTON_WIDTH // 2
        back_button = Button(button_x, SCREEN_HEIGHT - 80,
                            MENU_BUTTON_WIDTH, MENU_BUTTON_HEIGHT,
                            "Back", BLUE)

        mouse_pos = pygame.mouse.get_pos()
        back_button.check_hover(mouse_pos)
        back_button.draw(self.screen, self.small_font)

        return {'back': back_button}

    def draw_level_transition(self, level):
        """Draw level transition screen"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))

        self.draw_text(f"LEVEL {level}", self.large_font, YELLOW,
                      SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, center=True)

    def draw_name_input(self, current_name):
        """Draw name input screen for high score"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))

        self.draw_text("NEW HIGH SCORE!", self.large_font, YELLOW,
                      SCREEN_WIDTH // 2, 150, center=True)

        self.draw_text("Enter your name:", self.medium_font, WHITE,
                      SCREEN_WIDTH // 2, 220, center=True)

        # Draw input box
        input_box = pygame.Rect(SCREEN_WIDTH // 2 - 150, 270, 300, 50)
        pygame.draw.rect(self.screen, WHITE, input_box, 3)

        # Draw current name
        self.draw_text(current_name, self.medium_font, WHITE,
                      SCREEN_WIDTH // 2, 295, center=True)

        self.draw_text("Press ENTER to submit", self.small_font, WHITE,
                      SCREEN_WIDTH // 2, 350, center=True)
