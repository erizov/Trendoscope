"""
API routers for Trendoscope2.
Each router handles a specific domain of endpoints.
"""
# Import routers lazily to avoid circular dependencies
__all__ = [
    'news_router',
    'tts_router',
    'email_router',
    'telegram_router',
    'rutube_router',
    'admin_router',
]

# Lazy imports - will be imported when needed
def _get_routers():
    """Get all routers - lazy import to avoid circular deps."""
    from .news import router as news_router
    from .tts import router as tts_router
    from .email import router as email_router
    from .telegram import router as telegram_router
    from .rutube import router as rutube_router
    from .admin import router as admin_router
    
    return {
        'news_router': news_router,
        'tts_router': tts_router,
        'email_router': email_router,
        'telegram_router': telegram_router,
        'rutube_router': rutube_router,
        'admin_router': admin_router,
    }
