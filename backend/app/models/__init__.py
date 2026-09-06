"""SQLAlchemy models.

Populated in Phase 2 (database models & migrations). Kept importable so
the application factory can register metadata with SQLAlchemy/Migrate.
"""

from ..extensions import db

__all__ = ["db"]