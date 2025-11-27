#!/usr/bin/env python3
"""
Turkey Shoot - A Quirky Thanksgiving Shooting Game
Main entry point
"""
from game import Game


def main():
    """Initialize and run the game"""
    print("=" * 50)
    print("TURKEY SHOOT - Thanksgiving Shooting Game")
    print("=" * 50)
    print("\nControls:")
    print("  Arrow Keys / A,D - Move left/right")
    print("  SPACE - Shoot")
    print("  ESC - Return to menu (during game)")
    print("\nStarting game...")
    print("=" * 50)

    game = Game()
    game.run()

    print("\nThanks for playing Turkey Shoot!")


if __name__ == "__main__":
    main()
