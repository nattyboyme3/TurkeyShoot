"""
Game constants and configuration for Turkey Shoot
"""

# Display settings
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
TITLE = "Turkey Shoot"

# Colors (R, G, B)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
BROWN = (139, 69, 19)
PURPLE = (128, 0, 128)
DARK_RED = (139, 0, 0)

# Player settings
PLAYER_WIDTH = 100
PLAYER_HEIGHT = 80
PLAYER_SPEED = 6
PLAYER_COLOR = BLACK
PLAYER_SHOOT_COOLDOWN = 175  # milliseconds

# Projectile settings
BULLET_WIDTH = 5
BULLET_HEIGHT = 15
BULLET_SPEED = 7
BULLET_COLOR = YELLOW

# Enemy settings
ENEMY_BASE_SPEED = 2
ENEMY_SPAWN_MARGIN = 50
SPRITE_DIR = 'assets/sprites'

# Enemy types configuration
ENEMY_TYPES = {
    'gravy_boat': {
        'width': 70,
        'height': 70,
        'color': BROWN,
        'speed': 2,
        'health': 4,
        'points': 100,
        'movement': 'straight'
    },
    'pumpkin_pie': {
        'width': 60,
        'height': 60,
        'color': ORANGE,
        'speed': 2,
        'health': 2,
        'points': 150,
        'movement': 'zigzag'
    },
    'cranberry': {
        'width': 45,
        'height': 45,
        'color': DARK_RED,
        'speed': 2.5,
        'health': 1,
        'points': 50,
        'movement': 'straight'
    },
    'mashed_potato': {
        'width': 65,
        'height': 65,
        'color': (210, 180, 140),
        'speed': 2,
        'health': 3,
        'points': 75,
        'movement': 'straight'
    },
    'stuffing': {
        'width': 85,
        'height': 85,
        'color': (245, 245, 220),
        'speed': 1.5,
        'health': 5,
        'points': 200,
        'movement': 'straight'
    },
    'green_bean_casserole': {
        'width': 100,
        'height': 100,
        'color': (100, 150, 50),
        'speed': 1.6,
        'health': 20,
        'points': 300,
        'movement': 'track_player'
    },
    'turkey': {
        'width': 90,
        'height': 90,
        'color': (101, 67, 33),
        'speed': 1.3,
        'health': 10,
        'points': 500,
        'movement': 'sine_wave'
    }
}

# Difficulty settings
DIFFICULTY_SETTINGS = {
    'easy': {
        'lives': 5,
        'speed_multiplier': 1.0,
        'enemy_count_multiplier': 1,
        'spawn_rate': 1250  # milliseconds
    },
    'medium': {
        'lives': 3,
        'speed_multiplier': 1.5,
        'enemy_count_multiplier': 1.2,
        'spawn_rate': 1000 # milliseconds
    },
    'hard': {
        'lives': 2,
        'speed_multiplier': 2.0,
        'enemy_count_multiplier': 1.4,
        'spawn_rate': 750 # milliseconds
    }
}

# Level progression
LEVEL_ENEMY_INCREASE = 0.35  # 35% more enemies per level
LEVEL_SPEED_INCREASE = 0.2  # 10% speed increase every 3 levels
BOSS_LEVEL_INTERVAL = 5  # Boss level every 5 levels

# Enemy unlocks by level
ENEMY_UNLOCKS = {
    1: ['turkey', 'cranberry'],
    2: ['pumpkin_pie'],
    4: ['stuffing'],
    6: ['mashed_potato'],
    8: ['green_bean_casserole'],
    5: ['gravy_boat']  # Boss only on boss levels
}

# UI settings
FONT_SIZE_SMALL = 20
FONT_SIZE_MEDIUM = 36
FONT_SIZE_LARGE = 48
MENU_BUTTON_WIDTH = 200
MENU_BUTTON_HEIGHT = 50
MENU_BUTTON_SPACING = 20

# High scores
MAX_HIGH_SCORES = 10
HIGH_SCORE_FILE = 'data/highscores.json'

# Powerup settings
POWERUP_SPAWN_MARGIN = 50
POWERUP_SPAWN_RATE = 8000  # milliseconds between powerup spawns

# Powerup types configuration
POWERUP_TYPES = {
    'fire_rate': {
        'radius': 25,
        'color': (0, 255, 255),  # Cyan
        'speed': 2,
        'effect_type': 'fire_rate',
        'duration': -1  # Persistent until life loss
    },
    'extra_life': {
        'radius': 25,
        'color': (255, 20, 147),  # Deep pink
        'speed': 2,
        'effect_type': 'extra_life',
        'duration': 0  # Instant effect
    },
    'speed_boost': {
        'radius': 30,
        'color': (144, 238, 144),  # Light green
        'speed': 2,
        'effect_type': 'speed_boost',
        'duration': -1  # Persistent until life loss
    },
    'slow_enemies': {
        'radius': 20,
        'color': (173, 216, 230),  # Light blue
        'speed': 2,
        'effect_type': 'slow_enemies',
        'duration': 10000  # 10 seconds
    }
}

# Powerup effect modifiers
FIRE_RATE_MODIFIER = 0.9  # 10% faster (cooldown reduced to 90%)
SPEED_BOOST_MODIFIER = 1.1  # 10% faster movement
SLOW_ENEMIES_MODIFIER = 0.5  # 50% slower enemies

# Message notification settings
MESSAGE_DURATION = 3000  # milliseconds messages stay on screen
MESSAGE_MAX_VISIBLE = 5  # maximum number of messages shown at once
MESSAGE_X = SCREEN_WIDTH - 250  # bottom-right corner
MESSAGE_Y = SCREEN_HEIGHT - 150
MESSAGE_WIDTH = 240
MESSAGE_LINE_HEIGHT = 22

# Friendly names for game events
ENEMY_NAMES = {
    'turkey': 'Turkey',
    'pumpkin_pie': 'Pumpkin Pie',
    'cranberry': 'Cranberry',
    'stuffing': 'Stuffing',
    'mashed_potato': 'Mashed Potato',
    'gravy_boat': 'Gravy Boat',
    'green_bean_casserole': 'Green Bean Casserole'
}

POWERUP_NAMES = {
    'fire_rate': 'Rapid Fire!',
    'extra_life': 'Extra Life!',
    'speed_boost': 'Speed Boost!',
    'slow_enemies': 'Slow Enemies!'
}
