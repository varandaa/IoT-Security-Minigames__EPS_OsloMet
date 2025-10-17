"""Minigames package: contains separate minigame modules (camera, router).

This package groups game-specific logic so the main application can
delegate tasks (bruteforce, router exploit) to the appropriate module.
"""

__all__ = ["camera", "router"]
