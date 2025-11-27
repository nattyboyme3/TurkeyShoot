# Instructions for AI Agents

## Before Making Any Changes

**REQUIRED**: Read `SYSTEM_DESIGN.md` in full before modifying any code.

The system design document contains:
- Complete architecture overview
- Module dependency graph
- State machine transitions
- All core systems with algorithms
- Data structures and API contracts
- Critical invariants and edge cases
- Extension points and modification guidelines

**Why this matters**: Turkey Shoot uses interconnected systems. Changes in one module can break invariants in another. The system design document maps all dependencies and critical paths.

## Making Changes

### 1. Understand the Change Scope

Before editing code:
- Identify which system(s) the change affects (refer to "Module Dependency Graph" in SYSTEM_DESIGN.md)
- Check "State Invariants" section to ensure your change won't violate assumptions
- Review "Edge Cases Handled" to see if similar scenarios are already covered
- Consult "Extensibility Points" for the recommended approach

### 2. Common Modification Patterns

**Configuration changes** (balance, difficulty, timing):
- Edit `constants.py` only
- No other code changes needed
- Refer to "Configuration Tuning" section for balance levers

**Adding new content**:
- New enemy type → See "Adding New Enemy Type" in SYSTEM_DESIGN.md
- New power-up → See "Adding Power-ups" in SYSTEM_DESIGN.md
- New game state → Update state machine in `game.py`, document in SYSTEM_DESIGN.md

**UI changes**:
- Modify `ui.py` methods
- Maintain button dictionary return pattern
- Keep coordinate calculations consistent with existing screens

**Game mechanics changes**:
- Identify affected system in SYSTEM_DESIGN.md
- Check all modules that depend on that system
- Update collision logic in `collision.py` if needed
- Update game loop in `game.py:update_playing()` if needed

### 3. Testing Changes

After modifications:
1. Run syntax check: `python -m py_compile <modified_file>.py`
2. Run the game: `python main.py`
3. Test the specific feature changed
4. Test state transitions if you modified `game.py`
5. Check high score persistence if you modified `scoring.py`

**Critical test paths**:
- Main menu → Game → Death → High score entry → Main menu
- Level completion and transition
- All three difficulty levels
- Boss level (reach level 5)
- Edge cases documented in SYSTEM_DESIGN.md

### 4. After Making Changes

**REQUIRED**: Update `SYSTEM_DESIGN.md` if you made structural changes.

**Structural changes include**:
- New modules or classes
- Modified state machine (new states or transitions)
- Changed APIs (function signatures, return types)
- New algorithms or data structures
- Modified game loop execution order
- New configuration options
- Changed file formats or persistence layer
- New dependencies

**What to update in SYSTEM_DESIGN.md**:
- Module dependency graph (if imports changed)
- State machine diagram (if states/transitions changed)
- System breakdown for affected module (state, API, algorithms)
- Data structures section (if new collections added)
- Configuration tuning (if new balance levers added)
- Edge cases (if new edge cases handled)
- Non-obvious behaviors (if new gotchas introduced)

**Non-structural changes** (don't require SYSTEM_DESIGN.md updates):
- Bug fixes that don't change APIs
- Constant value tweaks in `constants.py`
- UI text or color changes
- Performance optimizations that don't change algorithms

### 5. Commit to Git

**REQUIRED**: Commit changes to git regularly with brief, descriptive commit messages.

**When to commit**:
- After completing a logical unit of work (feature, bug fix, refactor)
- After testing confirms the change works
- After updating SYSTEM_DESIGN.md (if applicable)
- Before starting a new feature or major change

**Commit message format**:
```bash
git add <files>
git commit -m "<brief description of what changed>"
```

**Good commit messages** (brief, specific, present tense):
- `Add sine wave movement to enemies`
- `Fix collision detection for multi-health enemies`
- `Update spawn rate for hard difficulty`
- `Refactor level progression calculations`
- `Add power-up system with rapid fire`
- `Update SYSTEM_DESIGN.md with power-up system`

**Bad commit messages** (vague, overly long, past tense):
- `Updated stuff`
- `Fixed bug`
- `Changes to make the game work better with new features I added`
- `Fixed the issue where enemies were spawning incorrectly`

**Commit granularity**:
- **Too small**: One commit per line changed → creates noise
- **Too large**: 10 files changed across 3 systems → hard to rollback
- **Just right**: One logical change (e.g., "Add health bar rendering" touches `enemies.py` and `ui.py`)

**Example workflow**:
```bash
# Make changes to player.py
python -m py_compile player.py
python main.py  # Test
git add player.py
git commit -m "Add rapid fire cooldown modifier to player"

# Update documentation
git add SYSTEM_DESIGN.md
git commit -m "Document rapid fire mechanics in SYSTEM_DESIGN.md"
```

**Multi-file commits** (when changes are coupled):
```bash
# Adding a new enemy type
git add constants.py enemies.py levels.py
git commit -m "Add corn enemy with bouncing movement"

git add SYSTEM_DESIGN.md
git commit -m "Document corn enemy in SYSTEM_DESIGN.md"
```

**Why commit regularly**:
- Enables rollback to specific working states
- Documents progression of changes
- Makes debugging easier (binary search through commits)
- Prevents loss of work
- Creates checkpoints during complex changes

### 6. Documentation Style

When updating SYSTEM_DESIGN.md:
- **Be dense**: No fluff, technical details only
- **Show code**: Include algorithms as Python code blocks
- **Specify complexity**: O(n) notation for new algorithms
- **Map dependencies**: Update dependency graph if imports change
- **Document invariants**: What must be true for the system to work
- **Note edge cases**: How the code handles boundary conditions

**Format example**:
```markdown
### New System (newsystem.py)

**Class**: `NewClass`

**State**:
- Variable: `name` (type) - description

**API**:
```python
method_name(params) -> return_type
```

**Algorithm**:
```python
# Pseudocode or actual implementation
```

**Complexity**: O(n) time, O(1) space

**Called from**: `module.py:function()`
```

## Quick Reference

### File Purposes
- `main.py` - Entry point only, no game logic
- `game.py` - Game loop, state machine, orchestration
- `player.py` - Player state and behavior
- `enemies.py` - Enemy types and movement
- `projectiles.py` - Bullet system
- `collision.py` - Collision detection (pure functions)
- `scoring.py` - Score tracking and persistence
- `levels.py` - Level progression and spawn management
- `ui.py` - All screens and HUD
- `constants.py` - Configuration (ONLY file for tuning)

### State Machine States
`MENU | PLAYING | PAUSED | GAME_OVER | HIGH_SCORES | LEVEL_TRANSITION | NAME_INPUT`

### Critical Invariants
- All active objects in `bullets`/`enemies` lists have `is_active() == True`
- `PLAYING` state requires `player is not None` and `level_manager is not None`
- High scores sorted descending by score, max 10 per difficulty
- Player position clamped to screen bounds
- Bullets break on first enemy hit (no piercing)

### Performance Notes
- Collision detection is O(bullets × enemies), typically ~50 checks/frame
- No spatial partitioning, acceptable for current enemy counts
- Target optimization here if adding more enemies or bullets

## Emergency Rollback

If changes break the game:
1. Identify what changed: `git diff` (if using git)
2. Check error message against SYSTEM_DESIGN.md invariants
3. Verify all imports are correct (check dependency graph)
4. Ensure state transitions are valid (check state machine)
5. Revert to last working state if needed

## Questions to Ask Before Changing Code

1. Have I read the relevant section in SYSTEM_DESIGN.md?
2. Which other modules depend on this one?
3. What invariants must this code maintain?
4. Are there edge cases I need to handle?
5. Does this change affect the state machine?
6. Will this require updating SYSTEM_DESIGN.md?

---

**Remember**: This is a small, tightly-coupled game. Understanding the whole system (via SYSTEM_DESIGN.md) before making changes prevents cascading bugs.

**Document Version**: 1.0
**Last Updated**: 2025-11-27
