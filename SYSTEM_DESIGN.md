# Turkey Shoot - System Design Document (AI Agent Reference)

## Architecture Overview

### Core Pattern
Event-driven game loop architecture using Pygame. Single-threaded execution with state machine pattern for game flow management. No networking, no persistence beyond JSON file I/O for high scores.

### Execution Flow
```
main.py → Game.__init__() → Game.run() → [event_loop → update → draw] @ 60 FPS
```

## Module Dependency Graph

```
main.py
  └─> game.py
       ├─> player.py → constants.py
       ├─> projectiles.py → constants.py
       ├─> powerups.py → constants.py
       ├─> enemies.py → constants.py
       ├─> collision.py → constants.py
       ├─> scoring.py → constants.py
       ├─> levels.py → constants.py, enemies.py
       ├─> ui.py → constants.py
       └─> constants.py
```

**Critical Path**: All modules depend on `constants.py`. Modifying constants requires no code changes. Game loop in `game.py` orchestrates all other modules.

## State Machine (game.py:GameState)

```python
States: MENU | PLAYING | PAUSED | GAME_OVER | HIGH_SCORES | NAME_INPUT

Transitions:
MENU → {PLAYING (difficulty selected), HIGH_SCORES, EXIT}
PLAYING → {GAME_OVER (lives=0), MENU (ESC)}
GAME_OVER → {NAME_INPUT (is_high_score), MENU}
NAME_INPUT → GAME_OVER (after name submitted)
HIGH_SCORES → MENU
```

**Note**: Level progression occurs immediately within PLAYING state with a notification message (no separate transition state).

**State Persistence**: `self.state` (GameState enum), transitions handled in `handle_events()` and `update()`. No state history maintained.

## Core Systems

### 1. Player System (player.py)

**Class**: `Player`

**State**:
- Position: `(x, y)` - x clamped [0, SCREEN_WIDTH-width], y fixed at bottom
- Dimensions: `(width, height)` from constants
- Shooting: `last_shot` timestamp, `shoot_cooldown` (250ms)
- Collision: `rect` (pygame.Rect) updated in `update_rect()`

**Behavior**:
- Movement: `move_left()`, `move_right()` at PLAYER_SPEED (5 px/frame)
- Shooting: `can_shoot(current_time)` checks cooldown, `shoot(current_time)` marks timestamp
- Rendering: Green rectangle body + gun turret (8×15 px centered on top)

**API**:
```python
get_gun_position() -> (x, y)  # Bullet spawn point
```

### 2. Projectile System (projectiles.py)

**Class**: `Bullet`

**State**:
- Position: `(x, y)` - x centered on gun, y moves upward
- Velocity: -BULLET_SPEED (7 px/frame, negative = upward)
- Active flag: `active` (bool) - false when off-screen or collision

**Lifecycle**:
```python
__init__(x, y) → update() [moves, checks bounds] → deactivate() [on collision/off-screen]
```

**Collision**: Rectangle-based via `pygame.Rect`. Bullets removed from game.bullets list when `not is_active()`.

### 3. PowerUp System (powerups.py)

**Class**: `PowerUp`

**Type Configuration** (POWERUP_TYPES dict in constants.py):
```python
{
  'fire_rate': {radius, color, speed, effect_type: 'fire_rate', duration: 15000},
  'extra_life': {radius, color, speed, effect_type: 'extra_life', duration: 0},
  'speed_boost': {radius, color, speed, effect_type: 'speed_boost', duration: 15000},
  'slow_enemies': {radius, color, speed, effect_type: 'slow_enemies', duration: 15000}
}
```

**State**:
- Type identifier: `self.type` (string key)
- Position: `(x, y)` - x random spawn, y starts at -radius
- Visual: Circle with radius, color from config (or sprite if available)
- Speed: Fixed at 2 px/frame (moves downward like enemies)
- Effect: `effect_type` and `duration` from config
- Sprite: `self.sprite` (optional, loaded if available)
- Sprite size: `sprite_size = radius * 2` (square that fits the circle)

**Rendering**:
- **With sprite**: Blits PNG sprite scaled to fit circle dimensions (radius * 2)
- **Without sprite**: Circle using `pygame.draw.circle()` + white border for visibility (fallback)

**Sprite System**:
```python
# Class-level cache: {(powerup_type, sprite_size): scaled_surface}
_sprite_cache = {}

# Loading (in __init__):
sprite_path = f"{SPRITE_DIR}/{powerup_type}.png"
try:
    original = pygame.image.load(sprite_path)
    scaled = pygame.transform.scale(original, (sprite_size, sprite_size))
    _sprite_cache[cache_key] = scaled
except (pygame.error, FileNotFoundError):
    sprite = None  # Fallback to circle
```

**Available Sprites**:
- fire_rate (30x30)
- speed_boost (30x30)

**Circle Fallback** (no sprite):
- extra_life (30x30)
- slow_enemies (30x30)

**Collision**: Rectangle-based bounding box via `pygame.Rect` around circle/sprite

**Factory**: `spawn_powerup(powerup_type=None)` → returns PowerUp with random x position and random type if not specified

**Effect Application** (in game.py):
```python
# Player-specific effects (tracked in Player.active_effects)
fire_rate: Reduces shoot_cooldown by 10% (cooldown_modifier = 0.9)
speed_boost: Increases movement speed by 10% (speed_modifier = 1.1)

# Global effects (tracked in Game state)
slow_enemies: Reduces all enemy speeds by 10% (enemy_speed_modifier = 0.9)

# Instant effects
extra_life: Immediately adds 1 life (no duration tracking)
```

**Effect Timing**:
- Timed effects: Stored with expiration timestamp (current_time + duration)
- Player effects: Checked/expired in `Player.update_effects(current_time)`
- Global effects: Checked/expired in `Game.update_playing()`
- Duration: 15000ms (15 seconds) for temporary effects, 0 for instant

### 4. Enemy System (enemies.py)

**Class**: `Enemy` (unified class for all enemy types)

**Type Configuration** (ENEMY_TYPES dict in constants.py):
```python
{
  'turkey': {width, height, color, speed, health, points, movement: 'straight'},
  'pumpkin_pie': {..., movement: 'zigzag'},
  'cranberry': {..., movement: 'straight'},
  'stuffing': {..., health: 2, movement: 'straight'},
  'mashed_potato': {..., movement: 'straight'},
  'green_bean_casserole': {..., health: 3, movement: 'track_player'},
  'gravy_boat': {..., health: 5, movement: 'sine_wave'}  # Boss
}
```

**State**:
- Type identifier: `self.type` (string key)
- Position: `(x, y)` - x random spawn, y starts at -height
- Health: `health` / `max_health` - decremented by `take_damage(damage=1)`
- Movement state: `initial_x`, `time_offset`, `zigzag_direction` (movement-specific)
- Speed: `base_speed * speed_multiplier` (from difficulty + level)
- Player reference: `self.player` (optional, required for track_player movement)

**Movement Algorithms**:
```python
# Straight
y += speed

# Zigzag
y += speed
x += zigzag_direction * 2
if x <= 0 or x >= SCREEN_WIDTH - width:
    zigzag_direction *= -1

# Sine Wave (boss)
y += speed
amplitude = 100
frequency = 0.05
x = initial_x + amplitude * sin(frequency * y + time_offset)
x = clamp(x, 0, SCREEN_WIDTH - width)

# Track Player (green_bean_casserole)
if player:
    dx = (player.x + player.width/2) - (self.x + self.width/2)
    dy = (player.y + player.height/2) - (self.y + self.height/2)
    distance = sqrt(dx**2 + dy**2)
    if distance > 0:
        x += (dx / distance) * speed  # Normalized direction
        y += (dy / distance) * speed
    x = clamp(x, 0, SCREEN_WIDTH - width)
else:
    y += speed  # Fallback to straight if no player reference
```

**Rendering**:
- **With sprite**: Blits 150x150 PNG sprite scaled to enemy dimensions
- **Without sprite**: Colored rectangle + white border (fallback)
- **Health bar**: Multi-health enemies show health bar (5px tall, red background, green foreground proportional to health%)

**Sprite System**:
```python
# Class-level cache: {(enemy_type, width, height): scaled_surface}
_sprite_cache = {}

# Loading (in __init__):
sprite_path = f"{SPRITE_DIR}/{enemy_type}.png"
try:
    original = pygame.image.load(sprite_path)
    scaled = pygame.transform.scale(original, (width, height))
    _sprite_cache[cache_key] = scaled
except (pygame.error, FileNotFoundError):
    sprite = None  # Fallback to rectangle
```

**Available Sprites** (150x150 PNG, scaled to fit):
- turkey (45x45)
- cranberry (30x30)
- pumpkin_pie (40x40)
- stuffing (35x35)

**Rectangle Fallback** (no sprite):
- mashed_potato (40x40)
- green_bean_casserole (45x45)
- gravy_boat (60x50 - boss)

**Factory**: `spawn_enemy(enemy_type, speed_multiplier, player=None)` → returns Enemy with random x position. Player reference required for track_player movement type.

### 5. Collision System (collision.py)

**Pure Functions** (no state):

```python
check_bullet_enemy_collisions(bullets, enemies) -> (collisions: list[(bullet, enemy)], score_gained: int)
  # Uses pygame.Rect.colliderect()
  # Deactivates bullet on hit
  # Calls enemy.take_damage(), deactivates enemy if destroyed
  # Aggregates points from destroyed enemies
  # Early exit: bullet breaks on first hit

check_enemy_player_collision(enemies, player) -> bool
  # Returns True if any active enemy collides with player
  # Deactivates colliding enemy

check_enemies_reached_bottom(enemies) -> int
  # Returns count of enemies at y >= SCREEN_HEIGHT
  # Deactivates those enemies

check_powerup_player_collision(powerups, player) -> PowerUp | None
  # Returns collected powerup if collision detected
  # Deactivates collected powerup
  # Returns None if no collision
```

**Called from**: `game.py:update_playing()` every frame.

### 6. Scoring System (scoring.py)

**Class**: `ScoreManager`

**State**:
- Current score: `current_score` (int, reset per game)
- High scores: `high_scores` (dict[difficulty][list[score_entry]])
  - Score entry: `{name: str, score: int, level: int, date: str}`
  - Sorted descending by score
  - Max 10 per difficulty

**Persistence**:
- File: `data/highscores.json`
- Format: `{"easy": [...], "medium": [...], "hard": [...]}`
- Loaded on init, saved on `add_high_score()`

**API**:
```python
add_points(points)
get_score() -> int
reset_score()
is_high_score(score, difficulty) -> bool  # True if score > 10th place or list < 10
add_high_score(name, score, difficulty, level)  # Auto-sorts and trims to top 10
get_high_scores(difficulty) -> list[dict]
```

### 7. Level System (levels.py)

**Class**: `LevelManager`

**State**:
- Level number: `current_level` (starts at 1)
- Spawn tracking: `enemies_in_level`, `enemies_spawned`, `last_spawn_time`
- Difficulty: `difficulty` (string: 'easy'|'medium'|'hard')
- Spawn rate: `spawn_rate` (ms between spawns, from difficulty settings)

**Level Progression Logic**:

```python
# Enemy count per level
base_count = 10
level_factor = 1 + (current_level - 1) * 0.2  # 20% increase per level
difficulty_factor = DIFFICULTY_SETTINGS[difficulty]['enemy_count_multiplier']
total = int(base_count * level_factor * difficulty_factor)
if is_boss_level(): total = total // 2 + 1  # Fewer enemies + boss

# Speed multiplier
base = DIFFICULTY_SETTINGS[difficulty]['speed_multiplier']
level_boost = 1 + ((current_level - 1) // 3) * 0.1  # 10% per 3 levels
total = base * level_boost

# Boss levels
is_boss_level = (current_level % 5 == 0)
```

**Enemy Unlocks** (ENEMY_UNLOCKS in constants.py):
```python
{
  1: ['turkey', 'cranberry'],
  2: ['pumpkin_pie'],
  4: ['stuffing'],
  6: ['mashed_potato'],
  8: ['green_bean_casserole'],
  5: ['gravy_boat']  # Only spawns on boss levels
}
```

**Spawn Algorithm**:
```python
can_spawn_enemy(current_time):
    return (enemies_spawned < enemies_in_level) and
           (current_time - last_spawn_time >= spawn_rate)

spawn_next_enemy(current_time, player=None):
    if is_boss_level() and enemies_spawned == 0:
        return spawn_enemy('gravy_boat', speed_multiplier, player)
    else:
        available = get_available_enemy_types()  # Based on current_level and unlocks
        return spawn_enemy(random.choice(available), speed_multiplier, player)
```

**Level Completion**:
```python
is_level_complete(active_enemies_count):
    return enemies_spawned >= enemies_in_level and active_enemies_count == 0

advance_level():
    current_level += 1
    start_level()  # Recalculates enemies_in_level, resets spawn tracking
```

### 8. Message Notification System (ui.py:MessageQueue)

**Class**: `MessageQueue`

**State**:
- Messages list: `messages` - List of (text, color, expiration_time) tuples
- Auto-expiring: Messages removed after duration expires (default 3000ms)
- Max visible: 5 messages shown at once

**API**:
```python
add_message(text, color, current_time, duration=MESSAGE_DURATION)
  # Adds new message with expiration timestamp
  # Automatically trims to MESSAGE_MAX_VISIBLE

update(current_time)
  # Removes expired messages
  # Called every frame in update_playing()

get_visible_messages() -> list[(text, color)]
  # Returns list of non-expired messages for rendering
```

**Message Types**:
```python
# Powerup collection (GREEN)
"Rapid Fire!", "Extra Life!", "Speed Boost!", "Slow Enemies!"

# Powerup expiration (YELLOW)
"Rapid Fire! ended", "Speed Boost! ended", "Slow Enemies! ended"

# Enemy kills (WHITE)
"Killed Turkey", "Killed Cranberry", etc.

# Level progression (BLUE, 4s duration)
"Level 2!", "Level 3!", etc.
```

**Display**:
- Location: Bottom-right corner (x: SCREEN_WIDTH - 250, y: SCREEN_HEIGHT - 150)
- Semi-transparent black background (alpha 180)
- White border
- Stack vertically, newest at bottom
- Small font (20px)

**Triggered From**:
- `game.py:apply_powerup_effect()` - powerup collection
- `game.py:update_playing()` - effect expirations, enemy kills, level advancement

### 9. UI System (ui.py)

**Class**: `UI`

**Fonts**: pygame.Font(None, size) for SMALL (20), MEDIUM (36), LARGE (48)

**Button System**:
```python
class Button:
    rect: pygame.Rect
    text: str
    color, hover_color: tuple[int, int, int]
    is_hovered: bool

    check_hover(mouse_pos)  # Sets is_hovered
    is_clicked(mouse_pos) -> bool
    draw(screen, font)
```

**Screens** (all return dict[str, Button]):

1. **Main Menu** (`draw_main_menu()`):
   - Buttons: easy, medium, hard, high_scores, quit
   - Title: "TURKEY SHOOT" (ORANGE, LARGE)

2. **HUD** (`draw_hud(score, lives, level)`):
   - Top-left: Score (WHITE), Lives (RED)
   - Top-right: Level (YELLOW)

3. **Game Over** (`draw_game_over(score, level, is_high_score)`):
   - Semi-transparent overlay (BLACK, alpha=200)
   - Displays: final score, level reached, "NEW HIGH SCORE!" if applicable
   - Buttons: retry, menu

4. **High Scores** (`draw_high_scores(score_manager)`):
   - 3 columns: EASY (GREEN), MEDIUM (YELLOW), HARD (RED)
   - Top 10 per column, format: "rank. score"
   - Button: back

5. **Name Input** (`draw_name_input(current_name)`):
   - "NEW HIGH SCORE!" header
   - Input box (300×50 px, centered)
   - Current name displayed, max 15 chars
   - Instruction: "Press ENTER to submit"

6. **Message Notifications** (`draw_messages(message_queue)`):
   - Bottom-right corner box
   - Semi-transparent background (BLACK, alpha=180)
   - White border
   - Messages stacked vertically (newest at bottom)
   - Max 5 messages visible

**Rendering**: All text rendered with `font.render(text, True, color)`, blitted to screen at calculated positions (center=True uses `get_rect(center=(x,y))`).

## Game Loop (game.py:Game.run())

### Frame Execution Order
```python
while running:
    1. handle_events()     # Process input, state transitions
    2. update()            # Game logic based on current state
    3. draw()              # Render current state
    4. clock.tick(60)      # Cap at 60 FPS
```

### State-Specific Updates

**PLAYING State** (`update_playing()`):
```python
1. Update message queue (remove expired messages)
2. Update player effects (remove expired, trigger expiration messages, returns list)
3. Update enemy speed modifier (remove if expired, trigger expiration message)
4. Process continuous input (LEFT/RIGHT/A/D keys, SPACE for shooting)
5. Update player position (apply speed_modifier)
6. Update all bullets (move up, remove if off-screen)
7. Spawn powerups (time-based, every POWERUP_SPAWN_RATE ms)
8. Update all powerups (move down, remove if off-screen)
9. Check powerup-player collision → apply_powerup_effect() + add collection message
10. Spawn enemies (if can_spawn_enemy() and level_manager allows, apply enemy_speed_modifier)
11. Update all enemies (move based on pattern, remove if off-screen)
12. Check bullet-enemy collisions → add score + add kill messages
13. Check player-enemy collisions → lose_life()
14. Check enemies reached bottom → lose_life()
15. Check level completion → advance_level() immediately + add level message (no state change)
```

### Life Management
```python
lose_life():
    lives -= 1
    if lives <= 0:
        game_over()

game_over():
    if score_manager.is_high_score(score, difficulty):
        state = NAME_INPUT
    else:
        state = GAME_OVER
```

## Data Structures

### Collections in Game Loop
```python
self.bullets: list[Bullet]           # Active projectiles
self.enemies: list[Enemy]            # Active enemies
self.powerups: list[PowerUp]         # Active powerups
self.message_queue: MessageQueue     # Notification messages
```

**List Management**:
- Append on spawn/shoot
- Remove when `not obj.is_active()` (checked every frame)
- Iterate with `for obj in list[:]` (slice copy) when removing during iteration

### Message Tracking

**Message Queue** (ui.py:MessageQueue):
```python
self.messages: list[(text, color, expiration_time)]  # Timed message queue
```

**Message Flow**:
1. Event occurs (powerup collected, effect expires, enemy killed, level up)
2. Game logic calls `message_queue.add_message(text, color, current_time, duration)`
3. Message added with expiration timestamp
4. `message_queue.update(current_time)` removes expired messages every frame
5. `ui.draw_messages(message_queue)` renders visible messages in bottom-right corner

### Effect Tracking

**Player Effects** (player.py):
```python
self.active_effects: dict[str, int]  # {effect_type: expiration_time}
self.speed_modifier: float           # Recalculated from active_effects
self.cooldown_modifier: float        # Recalculated from active_effects
```

**Global Effects** (game.py):
```python
self.enemy_speed_modifier: float              # Applied to all spawned enemies
self.enemy_speed_modifier_expiration: int     # Timestamp when effect expires
self.last_powerup_spawn: int                  # Timestamp of last powerup spawn
```

### Configuration (constants.py)

**Screen**: 800×600, 60 FPS

**Sprites**: Directory `assets/sprites` contains 150x150 PNG sprites for some enemies

**Difficulty Settings**:
```python
{
  'easy': {lives: 5, speed_multiplier: 1.0, enemy_count_multiplier: 0.8, spawn_rate: 2000},
  'medium': {lives: 3, speed_multiplier: 1.5, enemy_count_multiplier: 1.0, spawn_rate: 1500},
  'hard': {lives: 2, speed_multiplier: 2.0, enemy_count_multiplier: 1.3, spawn_rate: 1000}
}
```

**Colors**: RGB tuples (BLACK, WHITE, RED, GREEN, BLUE, YELLOW, ORANGE, BROWN, PURPLE, DARK_RED)

## Event Handling

### Input Mapping
```python
# Menu: pygame.MOUSEBUTTONDOWN → button.is_clicked(mouse_pos)
# Playing (continuous): pygame.key.get_pressed() → K_LEFT/K_RIGHT/K_a/K_d
# Playing (discrete): pygame.KEYDOWN → K_SPACE (shoot), K_ESCAPE (to menu)
# Name input: pygame.KEYDOWN → K_RETURN (submit), K_BACKSPACE (delete), unicode char (append)
```

### Event Router
```python
handle_events():
    for event in pygame.event.get():
        if event.type == QUIT: running = False

        match self.state:
            MENU: handle_menu_events(event)
            PLAYING: handle_playing_events(event)
            GAME_OVER: handle_game_over_events(event)
            HIGH_SCORES: handle_high_scores_events(event)
            NAME_INPUT: handle_name_input_events(event)
```

## Timing System

**Clock**: `pygame.time.Clock()` capped at 60 FPS via `clock.tick(FPS)`

**Timestamps**: `pygame.time.get_ticks()` → milliseconds since pygame.init()

**Cooldowns**:
- Player shoot: 250ms (`last_shot` + `PLAYER_SHOOT_COOLDOWN * cooldown_modifier`)
- Enemy spawn: Variable per difficulty (`last_spawn_time` + `spawn_rate`)
- Powerup spawn: 8000ms (`last_powerup_spawn` + `POWERUP_SPAWN_RATE`)

**Effect Durations**:
- Fire rate boost: 15000ms (15 seconds)
- Speed boost: 15000ms (15 seconds)
- Slow enemies: 15000ms (15 seconds)
- Extra life: Instant (0ms duration)

**Message Durations**:
- Default: 3000ms (3 seconds)
- Level up: 4000ms (4 seconds)

## Rendering Pipeline

### Draw Order (back to front)
```python
1. screen.fill(BLACK)                    # Clear screen
2. Player (if exists)                    # Bottom of screen
3. All bullets                           # Moving upward
4. All powerups                          # Moving downward (circles)
5. All enemies                           # Moving downward
6. HUD (score, lives, level)             # Top overlay
7. Message notifications                 # Bottom-right corner
8. State-specific overlays (if any)      # Menu, game over, etc.
9. pygame.display.flip()                 # Swap buffers
```

**Coordinate System**: Origin (0,0) at top-left, +x right, +y down

## Critical Algorithms

### Collision Detection (pygame.Rect.colliderect)
```python
# AABB (Axis-Aligned Bounding Box)
rect1.colliderect(rect2):
    return not (rect1.right < rect2.left or
                rect1.left > rect2.right or
                rect1.bottom < rect2.top or
                rect1.top > rect2.bottom)
```

### Score Sorting & Trimming
```python
# After adding new score
high_scores[difficulty].sort(key=lambda x: x['score'], reverse=True)
high_scores[difficulty] = high_scores[difficulty][:10]
```

### Enemy Type Selection
```python
# Gather all unlocked types up to current level
available = []
for level, types in sorted(ENEMY_UNLOCKS.items()):
    if level <= current_level:
        for t in types:
            if t == 'gravy_boat':
                if is_boss_level(): available.append(t)
            else:
                if t not in available: available.append(t)

# Boss level: first enemy is gravy_boat, rest are random non-boss
# Normal level: random from available (excluding gravy_boat)
```

## File I/O

**High Scores** (`data/highscores.json`):
```python
# Load
with open(HIGH_SCORE_FILE, 'r') as f:
    high_scores = json.load(f)

# Save
os.makedirs(os.path.dirname(HIGH_SCORE_FILE), exist_ok=True)
with open(HIGH_SCORE_FILE, 'w') as f:
    json.dump(high_scores, f, indent=2)
```

**Error Handling**: Try-except blocks return default `{'easy': [], 'medium': [], 'hard': []}` on load failure, print error message on save failure.

## Performance Characteristics

**Complexity**:
- Collision detection: O(n*m + p*1) where n=bullets, m=enemies, p=powerups (typical: n≈5, m≈10-30, p≈0-2)
- Enemy spawning: O(1) per frame
- Powerup spawning: O(1) per frame (8-second intervals)
- List cleanup: O(n) per frame (bullets + enemies + powerups)
- Effect expiration: O(e) where e=active player effects (max 2: fire_rate + speed_boost)
- Message cleanup: O(m) where m=messages (max 5)
- Rendering: O(n+m) draw calls per frame

**Memory**: Minimal. Max ~50 enemies + ~2 powerups on screen simultaneously (hard mode, high levels). Sprites cached at class level: enemy sprites (4 × ~90KB ≈ 360KB) + powerup sprites (2 × ~50KB ≈ 100KB) ≈ 460KB total. Geometric primitives for non-sprite entities.

**Frame Budget**: 16.67ms @ 60 FPS. No observed bottlenecks with current implementation.

## Extensibility Points

### Adding New Enemy Type
1. Add entry to `ENEMY_TYPES` in constants.py
2. Add to `ENEMY_UNLOCKS` with level number
3. (Optional) Implement new movement type in `Enemy.update()`

### Modifying Power-up Effects
1. Adjust effect modifiers in `constants.py` (FIRE_RATE_MODIFIER, SPEED_BOOST_MODIFIER, SLOW_ENEMIES_MODIFIER)
2. Adjust spawn rate via POWERUP_SPAWN_RATE (8000ms = every 8 seconds)
3. Adjust effect duration in POWERUP_TYPES (15000ms default)
4. Add new powerup type:
   - Add entry to POWERUP_TYPES in constants.py
   - Handle in `game.py:apply_powerup_effect()`
   - Add to `player.py:update_modifiers()` if player-specific

### Adding Sounds
1. Load sounds in `Game.__init__()`: `pygame.mixer.Sound('path')`
2. Play on events: `sound.play()` in collision handlers, shoot(), etc.

### Adding Sprites
1. Load images in class `__init__()`: `pygame.image.load('path')`
2. Replace `pygame.draw.rect()` with `screen.blit(image, rect)`

## Testing Entry Points

**Manual Testing**:
```bash
python main.py  # Full game loop
```

**Unit Testing Targets** (if implementing):
- `collision.py` functions (pure, no side effects)
- `scoring.py` high score logic (mock file I/O)
- `levels.py` calculations (deterministic given inputs)
- `enemies.py` movement algorithms (position verification)

## Debugging Hooks

**Print State**:
```python
# In game.py:update_playing(), add:
print(f"Lives: {self.lives}, Score: {self.score_manager.get_score()}, " +
      f"Enemies: {len(self.enemies)}, Bullets: {len(self.bullets)}")
```

**Visualize Hitboxes**:
```python
# In draw methods, add:
pygame.draw.rect(screen, (255, 0, 0), self.rect, 1)  # Red border
```

**Slow Motion**:
```python
# In game.py:run(), change:
self.clock.tick(10)  # 10 FPS instead of 60
```

## Initialization Sequence

```python
1. pygame.init()
2. Create display surface (800×600)
3. Create clock
4. Initialize ScoreManager (loads highscores.json)
5. Initialize UI (creates fonts)
6. Set state = MENU
7. Enter main loop
```

**On Game Start** (reset_game(difficulty)):
```python
1. Create LevelManager(difficulty)
2. Call level_manager.start_level() → calculates enemy count
3. Create Player() → positions at bottom center
4. Clear bullets and enemies lists
5. Reset score to 0
6. Set lives from difficulty settings
7. Set state = PLAYING
```

## Configuration Tuning

**Difficulty Tuning**:
- Increase `lives`: Easier
- Decrease `speed_multiplier`: Easier
- Increase `spawn_rate`: Easier (more time between enemies)
- Decrease `enemy_count_multiplier`: Easier

**Balance Levers** (constants.py):
- `LEVEL_ENEMY_INCREASE`: 0.2 (20% more per level) → higher = steeper curve
- `LEVEL_SPEED_INCREASE`: 0.1 (10% per 3 levels) → higher = faster escalation
- `BOSS_LEVEL_INTERVAL`: 5 → lower = more frequent bosses
- `PLAYER_SHOOT_COOLDOWN`: 250ms → lower = rapid fire
- `BULLET_SPEED`: 7 px/frame → higher = bullets reach top faster

**Enemy Balance**:
- High HP + slow = high points (mashed_potato, gravy_boat)
- Low HP + fast = low points (cranberry)
- Complex movement = bonus points (pumpkin_pie, gravy_boat)

## Edge Cases Handled

1. **No enemies on boss level**: `total = total // 2 + 1` ensures at least 1 (the boss)
2. **Empty high scores list**: `is_high_score()` checks `len(scores) < MAX_HIGH_SCORES`
3. **Player at screen edge**: Movement clamped to `[0, SCREEN_WIDTH - width]`
4. **Bullet hits multiple enemies**: Early exit after first hit prevents double collision
5. **Enemies off-screen**: Deactivated if `y > SCREEN_HEIGHT` or `y < -height`
6. **Name input overflow**: `len(player_name) < 15` limit enforced
7. **Boss unlock on non-boss level**: `gravy_boat` only added to available types if `is_boss_level()`
8. **JSON file missing**: Returns default structure, creates directory on save

## State Invariants

**PLAYING State**:
- `self.player is not None`
- `self.level_manager is not None`
- `self.lives >= 0` (checked after every lose_life())

**NAME_INPUT State**:
- `self.is_high_score == True`
- `self.player_name` valid string (can be empty until submit)

**Active Objects**:
- All objects in `self.bullets` have `is_active() == True`
- All objects in `self.enemies` have `is_active() == True`
- All objects in `self.powerups` have `is_active() == True`
- Inactive objects removed at end of update loop

**Effect Expiration**:
- Player effects expire when `current_time >= expiration_time` in `active_effects`
- Global enemy slow expires when `current_time >= enemy_speed_modifier_expiration`
- Modifiers recalculated immediately upon expiration

**Level Completion**:
- `enemies_spawned >= enemies_in_level` (all spawned)
- `active_enemies_count == 0` (all destroyed or off-screen)

## Critical Dependencies

**Pygame Modules Used**:
- `pygame.display`: Window management
- `pygame.time`: Clock, timestamps
- `pygame.event`: Input handling
- `pygame.key`: Keyboard state
- `pygame.mouse`: Mouse position
- `pygame.font`: Text rendering
- `pygame.draw`: Primitive rendering (rect)
- `pygame.Rect`: Collision detection

**Python Stdlib**:
- `json`: High score persistence
- `os`: Path operations
- `datetime`: Timestamp formatting
- `math`: Sine wave calculations
- `random`: Enemy spawn positions, type selection

## Modification Guidelines for AI Agents

1. **Changing game balance**: Modify `constants.py` only. No code changes needed.
2. **Adding content**: New enemy types require 3 file edits (constants.py, possibly enemies.py for new movement, levels.py for unlocks).
3. **UI changes**: Modify `ui.py` methods. Button layout requires updating x/y coordinates in draw methods.
4. **Game flow changes**: Modify state machine in `game.py`. Update `GameState` enum and transition logic in event handlers.
5. **Performance optimization**: Target collision detection (O(n*m) → spatial partitioning) or rendering (batch draw calls).

## Non-Obvious Behaviors

1. **Level progression is immediate**: No pause between levels - enemies clear, level advances, and a message appears, but gameplay continues uninterrupted.
2. **Lives lost per frame**: Multiple enemies hitting player in same frame = multiple life losses (rare but possible).
3. **Boss spawn timing**: Boss always first enemy on boss level, then normal enemies fill remaining count.
4. **Zigzag boundary**: Enemies reverse direction on wall hit, not at screen center. Can cause clustering.
5. **Sine wave amplitude**: Fixed at 100px. Boss can still move full screen width on high levels due to long path.
6. **Score not saved until name entered**: Closing game during NAME_INPUT state loses high score.
7. **Powerup effect stacking**: Same effect type resets expiration (extends duration, doesn't stack multiplier).
8. **Slow enemies affects existing**: When slow_enemies powerup collected, existing enemies immediately slowed (not just new spawns).
9. **Effect modifiers multiplicative**: Multiple effects combine multiplicatively (e.g., 1.1 * 1.1 = 1.21x if hypothetically stacked).
10. **Powerup collision uses bounding box**: Circular powerups use rectangular Rect for collision (slightly larger hit area).
11. **Message flooding**: Rapidly killing many enemies can fill message queue (only 5 visible, older messages pushed out).
12. **Message timing**: All messages use game time, so pausing (if implemented) would freeze expiration.
13. **Player-tracking enemies**: Green bean casserole enemies require player reference passed through spawn chain (Game → LevelManager → spawn_enemy). Without player reference, they fall back to straight movement.

---

**Document Version**: 1.0
**Last Updated**: 2025-11-27
**Target Audience**: AI agents requiring comprehensive system understanding for modification/extension tasks
