"""Bot router aggregation."""

from aiogram import Router

from app.presentation.bot.routers import (
    admin,
    catalog,
    compare,
    errors,
    recommendation,
    search,
    start,
)


def setup_routers() -> Router:
    """Create and configure the root router with all sub-routers."""
    root = Router(name="root")
    root.include_router(errors.router)
    root.include_router(start.router)
    root.include_router(recommendation.router)
    root.include_router(catalog.router)
    root.include_router(search.router)
    root.include_router(compare.router)
    root.include_router(admin.router)
    return root
