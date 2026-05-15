"""Domain errors for deterministic CLI behavior."""

from __future__ import annotations


class GameStudioError(Exception):
    """Base error for game studio CLI failures."""


class ValidationError(GameStudioError):
    """Raised when project or document validation fails."""


class NotFoundError(GameStudioError):
    """Raised when required files or directories are missing."""
