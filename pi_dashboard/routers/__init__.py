"""Routers for the Pi Dashboard API."""

from .container_router import ContainerRouter
from .notes_router import NotesRouter
from .system_router import SystemRouter

__all__ = [
    "ContainerRouter",
    "NotesRouter",
    "SystemRouter",
]
