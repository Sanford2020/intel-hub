"""
Centralized configuration module.

Re-exports settings from the backend config for use by all services.
All configuration is driven by environment variables.
"""

from app.config import Settings, settings

__all__ = ["Settings", "settings"]
