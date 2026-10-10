from .auth import router as auth_router
from .projects import router as projects_router
from .issues import router as issues_router
from .conflicts import router as conflicts_router
from .onsite import router as onsite_router
from .geocode import router as geocode_router
from .broadcasts import router as broadcasts_router

__all__ = [
    "auth_router",
    "projects_router",
    "issues_router",
    "conflicts_router",
    "onsite_router",
    "geocode_router",
    "broadcasts_router"
]
