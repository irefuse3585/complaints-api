"""
src/models/__init__.py

SQLAlchemy declarative base for all ORM models.
"""

from sqlalchemy.orm import declarative_base

# This Base class is used by all models in this package.
Base = declarative_base()
